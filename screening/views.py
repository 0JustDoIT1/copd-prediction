from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Questionnaire, PredictionResult
from .forms import (
    QuestionnaireForm,
    HealthRecordForm,
    ClinicalDecisionForm,
    OCRUploadForm,
)
from .services.prediction_service import create_prediction_result, calculate_age
from .services.ocr_service import extract_health_data

@login_required
def screening_home(request): # 로그인한 사용자만 문진입력 가능
    return render(
        request,
        "screening/screening_home.html",
        {
            "active_group": "screening",
            "active_menu": "screening_home",
        }
    )


# 문진 입력 ✏️
@login_required 
def questionnaire_create(request): 
    if request.method == "POST":
        form = QuestionnaireForm(request.POST) # 환자가 제출한 문진 데이터 받음

        if form.is_valid():
            questionnaire = form.save(commit=False) # DB에 바로 저장하지 않고 잠깐 멈춤
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
            "form": form
        }
    )


# 건강검진 입력 💉
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

            # BMI 자동 계산
            height_m = health_record.height / 100
            health_record.bmi = round(
                health_record.weight / (height_m ** 2),
                2
            )

            # 고혈압 단계 자동 계산
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
        }
    )

# 결과페이지 📋
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

# 의사 대시보드 💻
'''
아직 의사가 판정하지 않은 PredictionResult 가져옴 + 검토 완료도 추가
권고 점수 높은 순으로 정렬
의사 대시보드 템플릿으로 전달
'''

@login_required
def doctor_dashboard(request):
    pending_predictions = (
        PredictionResult.objects
        .filter(decision__isnull=True)
        .select_related(
            "questionnaire__patient__user"
        )
        .order_by("-risk_probability")
    )

    completed_predictions = (
        PredictionResult.objects
        .filter(decision__isnull=False)
        .select_related(
            "questionnaire__patient__user",
            "decision"
        )
        .order_by("-decision__decided_at")
    )

    return render(
        request,
        "screening/doctor_dashboard.html",
        {
            "pending_predictions": pending_predictions,
            "completed_predictions": completed_predictions,
            "active_menu": "doctor_dashboard",
        }
    )


# 의사 판정 🔨
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




# 환자가 결과 확인페이지
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

# ocr 서비스
@login_required
def ocr_upload(request):
    if request.method == "POST":
        form = OCRUploadForm(request.POST, request.FILES)

        if form.is_valid():
            image = request.FILES["image"]

            ocr_result = extract_health_data(image)

            print(ocr_result["raw_text"])
            print(ocr_result["extracted"])

            # OCR 원문과 추출값을 세션에 저장
            request.session["ocr_raw_text"] = ocr_result["raw_text"]
            request.session["ocr_extracted"] = ocr_result["extracted"]

            return redirect("screening:questionnaire")

    else:
        form = OCRUploadForm()

    return render(
        request,
        "screening/ocr_upload.html",
        {
            "form": form,
            "active_group": "screening",
            "active_menu": "ocr_upload",
        }
    )