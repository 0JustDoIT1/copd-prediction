from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import Questionnaire, HealthRecord, PredictionResult, ClinicalDecision
from .forms import QuestionnaireForm, HealthRecordForm, ClinicalDecisionForm
from .services.prediction_service import create_prediction_result, calculate_age


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
        form = HealthRecordForm()

    patient = request.user.patientprofile

    return render(
        request,
        "screening/health_record_form.html",
        {
            "form": form,
            "questionnaire": questionnaire,
            "patient": patient,
            "age": calculate_age(patient.birth_date),
        }
    )

# 결과페이지 📋
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
        }
    )

# 의사 대시보드 💻
'''
아직 의사가 판정하지 않은 PredictionResult만 가져옴
권고 점수 높은 순으로 정렬
의사 대시보드 템플릿으로 전달
'''

@login_required
def doctor_dashboard(request):
    pending_predictions = PredictionResult.objects.filter(
        decision__isnull=True
    ).select_related(
        "questionnaire__patient__user",
        "health_record__patient__user",
    ).order_by("-risk_probability")

    return render(
        request,
        "screening/doctor_dashboard.html",
        {
            "pending_predictions": pending_predictions,
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