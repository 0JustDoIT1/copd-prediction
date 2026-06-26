from django.db import models
from accounts.models import PatientProfile, DoctorProfile


class Questionnaire(models.Model):
    SMOKING_CHOICES = [(0, '비흡연'), (1, '과거흡연'), (2, '현재흡연')]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='questionnaires')
    smoking_status = models.IntegerField(choices=SMOKING_CHOICES)
    smoking_amount = models.FloatField(default=0)
    cough = models.BooleanField(default=False)
    sputum = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)


class HealthRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='health_records')
    height = models.FloatField()
    weight = models.FloatField()
    bmi = models.FloatField(null=True, blank=True)
    sbp = models.FloatField(null=True, blank=True)
    dbp = models.FloatField(null=True, blank=True)
    hp_stage = models.IntegerField(null=True, blank=True)
    glucose = models.FloatField(null=True, blank=True)
    hba1c = models.FloatField(null=True, blank=True)
    cholesterol = models.FloatField(null=True, blank=True)
    hdl = models.FloatField(null=True, blank=True)
    triglyceride = models.FloatField(null=True, blank=True)
    ast = models.FloatField(null=True, blank=True)
    alt = models.FloatField(null=True, blank=True)
    hemoglobin = models.FloatField(null=True, blank=True)
    wbc = models.FloatField(null=True, blank=True)
    rbc = models.FloatField(null=True, blank=True)
    hscrp = models.FloatField(null=True, blank=True)
    asthma_history = models.BooleanField(null=True, blank=True)
    rhinitis_history = models.BooleanField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


class PredictionResult(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    health_record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE)
    risk_probability = models.FloatField()  # 의미: 폐활량검사 권고 점수



    top_factors = models.JSONField(default=dict)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ClinicalDecision(models.Model):
    DECISION_CHOICES = [
    ('recommend', '폐활량검사 권고'),
    ('normal', '정상'), # ❗❗❗
]
    prediction = models.OneToOneField(PredictionResult, on_delete=models.CASCADE, related_name='decision')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    memo = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

