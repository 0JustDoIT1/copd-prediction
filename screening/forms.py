from django import forms
from .models import Questionnaire, HealthRecord, ClinicalDecision


class QuestionnaireForm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            "smoking_status",
            "smoking_amount",
            "cough",
            "sputum",
        ]


class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = [
            "height",
            "weight",
            "sbp",
            "dbp",
            "hp_stage",
            "glucose",
            "hba1c",
            "cholesterol",
            "hdl",
            "triglyceride",
            "ast",
            "alt",
            "hemoglobin",
            "wbc",
            "rbc",
        ]


class ClinicalDecisionForm(forms.ModelForm):
    class Meta:
        model = ClinicalDecision
        fields = [
            "decision",
            "memo",
        ]


class OCRUploadForm(forms.Form):
    image = forms.ImageField(
        label="검진결과지 이미지",
        required=True
    )