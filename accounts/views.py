from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def home(request):
    """
    GET /
    지금은 로그인 구분 없이 그냥 환자 대시보드로 보냄.
    TODO: 로그인 로직 붙으면 role 보고 patient/doctor 대시보드로 분기.
    """
    return redirect("accounts:patient_dashboard")


def patient_dashboard(request):
    """
    GET /dashboard
    환자 홈. 지금은 화면 틀만 보여줌.
    TODO: HealthRecord/PredictionResult 연동 (screening.models 사용)
    """
    return render(request, "accounts/patient_dashboard.html")


def doctor_dashboard(request):
    """
    GET /doctor/dashboard
    의사 대시보드. 지금은 화면 틀만 보여줌.
    TODO: screening.models.PredictionResult를 risk_probability 내림차순으로 조회
    """
    return render(request, "accounts/doctor_dashboard.html")


@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    return JsonResponse({"detail": "TODO: signup not implemented"}, status=501)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    return JsonResponse({"detail": "TODO: login not implemented"}, status=501)


@require_http_methods(["POST"])
def logout_view(request):
    return JsonResponse({"detail": "TODO: logout not implemented"}, status=501)