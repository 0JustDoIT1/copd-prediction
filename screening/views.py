from django.shortcuts import render
from django.http import HttpResponse


def questionnaire_create(request):
    return HttpResponse("문진 입력 페이지")


def health_record_create(request, questionnaire_id):
    return HttpResponse("건강검진 입력")


def predict_screening(request, questionnaire_id, health_record_id):
    return HttpResponse("예측 실행")


def result_detail(request, prediction_id):
    return HttpResponse("결과 페이지")


def doctor_dashboard(request):
    return HttpResponse("의사 대시보드")


def doctor_decision(request, prediction_id):
    return HttpResponse("의사 판정")
