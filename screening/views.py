import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Questionnaire, PredictionResult
from .forms import (
    QuestionnaireForm,
    HealthRecordForm,
    ClinicalDecisionForm,
    OCRUploadForm,
)
from .services.prediction_service import (
    create_prediction_result,
    calculate_age,
    build_feature_dict,
)
from .services.ocr_service import extract_health_data
from .ml_model import predict_risk_probability

@login_required
def screening_home(request):
    return render(
        request,
        "screening/screening_home.html",
        {
            "active_group": "screening",
            "active_menu": "questionnaire",
        }
    )


@login_required 
def questionnaire_create(request): 
    if request.method == "POST":
        form = QuestionnaireForm(request.POST)

        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.patient = request.user.patientprofile
            questionnaire.save()

            return redirect(
                "screening:health_record",
                questionnaire_id=questionnaire.id
            )

    else:
        form = QuestionnaireForm()

    return render(
        request,
        "screening/questionnaire_form.html",
        {
            "form": form,
            "active_group": "screening",
            "active_menu": "questionnaire",
        }
    )


@login_required
def health_record_create(request, questionnaire_id): 
    questionnaire = get_object_or_404(
        Questionnaire,
        id=questionnaire_id,
        patient=request.user.patientprofile
    )

    if request.method == "POST":
        form = HealthRecordForm(request.POST)

        if form.is_valid():
            health_record = form.save(commit=False)
            health_record.patient = request.user.patientprofile

            height_m = health_record.height / 100
            health_record.bmi = round(
                health_record.weight / (height_m ** 2),
                2
            )

            if health_record.bp_medication:
                health_record.hp_stage = 4
            else:
                sbp = health_record.sbp
                dbp = health_record.dbp

                if sbp is not None and dbp is not None:
                    if sbp < 120 and dbp < 80:
                        health_record.hp_stage = 1
                    elif 120 <= sbp < 130 and dbp < 80:
                        health_record.hp_stage = 2
                    elif 130 <= sbp < 140 or 80 <= dbp < 90:
                        health_record.hp_stage = 3
                    elif sbp >= 140 or dbp >= 90:
                        health_record.hp_stage = 4

            health_record.save()

            prediction = create_prediction_result(
                questionnaire,
                health_record
            )

            return render(
                request,
                "screening/submit_complete.html",
                {
                    "prediction_id": prediction.id,
                    "active_group": "screening",
                    "active_menu": "questionnaire",
                }
            )

    else:
        ocr_extracted = request.session.pop("ocr_extracted", None)
        ocr_success = bool(ocr_extracted)

        form = HealthRecordForm(initial=ocr_extracted)

    patient = request.user.patientprofile

    return render(
        request,
        "screening/health_record_form.html",
        {
            "form": form,
            "questionnaire": questionnaire,
            "patient": patient,
            "age": calculate_age(patient.birth_date),
            "ocr_success": ocr_success,
            "active_group": "screening",
            "active_menu": "questionnaire",
        }
    )


@login_required
def result_detail(request, prediction_id): 
    prediction = get_object_or_404(
        PredictionResult,
        id=prediction_id
    )

    return render(
        request,
        "screening/result_detail.html",
        {
            "prediction": prediction,
            "active_menu": "result_list",
            "active_group": "screening",
        }
    )


@login_required
def doctor_dashboard(request):
    sort = request.GET.get("sort", "priority")
    pending_filter = request.GET.get("pending_filter", "all")
    completed_sort = request.GET.get("completed_sort", "latest")
    decision_filter = request.GET.get("decision_filter", "all")

    pending_predictions = (
        PredictionResult.objects
        .filter(decision__isnull=True)
        .select_related(
            "questionnaire__patient__user"
        )
    )

    if pending_filter == "priority":
        pending_predictions = pending_predictions.filter(risk_probability__gte=0.4)
    elif pending_filter == "normal":
        pending_predictions = pending_predictions.filter(risk_probability__lt=0.4)

    if sort == "latest":
        pending_predictions = pending_predictions.order_by("-created_at")
    else:
        pending_predictions = pending_predictions.order_by("-risk_probability")

    priority_count = PredictionResult.objects.filter(
        decision__isnull=True,
        risk_probability__gte=0.4,
    ).count()

    pending_total_count = PredictionResult.objects.filter(
        decision__isnull=True
    ).count()

    completed_predictions = (
        PredictionResult.objects
        .filter(decision__isnull=False)
        .select_related("questionnaire__patient__user", "decision")
    )

    if decision_filter in ("recommend", "normal"):
        completed_predictions = completed_predictions.filter(
            decision__decision=decision_filter
        )

    completed_sort_map = {
        "latest": "-decision__decided_at",
        "oldest": "decision__decided_at",
        "score_high": "-risk_probability",
        "score_low": "risk_probability",
    }
    completed_predictions = completed_predictions.order_by(
        completed_sort_map.get(completed_sort, "-decision__decided_at")
    )

    completed_total_count = PredictionResult.objects.filter(
        decision__isnull=False
    ).count()

    now_local = timezone.localtime()
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_completed_count = PredictionResult.objects.filter(
        decision__isnull=False,
        decision__decided_at__gte=today_start,
        decision__decided_at__lt=today_end,
    ).count()

    pending_paginator = Paginator(pending_predictions, 5)
    completed_paginator = Paginator(completed_predictions, 5)

    pending_page_number = request.GET.get("pending_page")
    completed_page_number = request.GET.get("completed_page")

    pending_page_obj = pending_paginator.get_page(pending_page_number)
    completed_page_obj = completed_paginator.get_page(completed_page_number)

    return render(
        request,
        "screening/doctor_dashboard.html",
        {
            "pending_predictions": pending_page_obj,
            "completed_predictions": completed_page_obj,
            "pending_page_obj": pending_page_obj,
            "completed_page_obj": completed_page_obj,
            "active_menu": "doctor_dashboard",
            "sort": sort,
            "pending_filter": pending_filter,
            "pending_total_count": pending_total_count,
            "completed_sort": completed_sort,
            "decision_filter": decision_filter,
            "completed_total_count": completed_total_count,
            "priority_count": priority_count,
            "today_completed_count": today_completed_count,
        }
    )


@login_required
def doctor_decision(request, prediction_id):
    prediction = get_object_or_404(
        PredictionResult,
        id=prediction_id
    )

    if request.method == "POST":
        form = ClinicalDecisionForm(request.POST)

        if form.is_valid():
            decision = form.save(commit=False)
            decision.prediction = prediction
            decision.doctor = request.user.doctorprofile
            decision.save()

            return redirect("screening:doctor_dashboard")

    else:
        form = ClinicalDecisionForm()

    return render(
        request,
        "screening/doctor_decision.html",
        {
            "form": form,
            "prediction": prediction,
            "active_menu": "doctor_dashboard",
        }
    )


@login_required
def result_list(request):
    predictions = (
        PredictionResult.objects
        .filter(
            questionnaire__patient=request.user.patientprofile
        )
        .select_related("decision")
        .order_by("-created_at")
    )

    return render(
        request,
        "screening/result_list.html",
        {
            "predictions": predictions,
            "active_menu": "result_list",
            "active_group": "screening",
        }
    )


@login_required
def ocr_upload(request, questionnaire_id):
    if request.method == "POST":
        form = OCRUploadForm(request.POST, request.FILES)

        if form.is_valid():
            image = request.FILES["image"]

            ocr_result = extract_health_data(image)

            print(ocr_result["raw_text"])
            print(ocr_result["extracted"])

            request.session["ocr_raw_text"] = ocr_result["raw_text"]
            request.session["ocr_extracted"] = ocr_result["extracted"]

            return redirect(
                "screening:health_record",
                questionnaire_id=questionnaire_id
            )

    else:
        form = OCRUploadForm()

    return render(
        request,
        "screening/ocr_upload.html",
        {
            "form": form,
            "active_group": "screening",
            "active_menu": "questionnaire",
        }
    )


@login_required
def predict_whatif(request):
    """
    환자 대시보드의 What-if 시뮬레이션이 호출하는 엔드포인트.

    환자의 가장 최근 Questionnaire/HealthRecord로 feature_dict를 그대로
    만들고(build_feature_dict 재사용), 그중 smoking_status/smoking_amount만
    요청으로 받은 값으로 덮어써서 동일한 predict_risk_probability()를
    재호출한다. 모델 로딩이나 다른 변수 처리 로직을 새로 만들지 않고,
    health_record_create()가 실제 제출 때 쓰는 것과 완전히 같은 경로를 탄다.

    요청(POST, JSON): {"smoking_status": 0|1|2, "smoking_amount": number}
    응답(JSON): {"risk_probability": float}  (0~1 사이, 권고 점수)

    체중(BMI)은 모델 계수가 단순 선형이라 의학적으로 비직관적이라는 이유로
    시뮬레이션 대상에서 제외됨 - 요청에 weight_delta 없음, HE_BMI는 항상
    환자의 최근 실측값을 그대로 사용한다.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "요청 본문이 올바른 JSON이 아닙니다."}, status=400)

    smoking_status = body.get("smoking_status")
    smoking_amount = body.get("smoking_amount")

    if smoking_status not in (0, 1, 2):
        return JsonResponse({"error": "smoking_status는 0, 1, 2 중 하나여야 합니다."}, status=400)

    try:
        smoking_amount = float(smoking_amount)
    except (TypeError, ValueError):
        return JsonResponse({"error": "smoking_amount가 올바르지 않습니다."}, status=400)

    patient = request.user.patientprofile

    latest_result = (
        PredictionResult.objects
        .filter(questionnaire__patient=patient)
        .select_related("questionnaire", "health_record")
        .order_by("-created_at")
        .first()
    )

    if latest_result is None:
        return JsonResponse(
            {"error": "검진정보가 없어 시뮬레이션을 실행할 수 없습니다."},
            status=404,
        )

    features = build_feature_dict(
        latest_result.questionnaire,
        latest_result.health_record,
    )
    features["smoking_status"] = smoking_status
    features["smoking_amount"] = smoking_amount

    risk_probability, _top_factors = predict_risk_probability(features)

    return JsonResponse({"risk_probability": risk_probability})