# screening/admin.py
from django.contrib import admin
from .models import Questionnaire, HealthRecord, PredictionResult, ClinicalDecision


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "smoking_status", "cough", "sputum", "submitted_at")
    list_filter = ("smoking_status", "cough", "sputum")


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "bmi", "sbp", "dbp", "hp_stage", "submitted_at")


@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    # risk_probability = "폐활량검사 권고 점수" (COPD 위험확률 아님, 원칙 유지)
    list_display = ("id", "risk_probability", "year", "created_at")
    list_filter = ("year",)


@admin.register(ClinicalDecision)
class ClinicalDecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "prediction", "doctor", "decision", "decided_at")
    list_filter = ("decision",)