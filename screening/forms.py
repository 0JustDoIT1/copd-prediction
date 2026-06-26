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
            "height", "weight",
            "sbp", "dbp", "hp_stage",
            "glucose", "hba1c", "cholesterol", "hdl", "triglyceride",
            "ast", "alt", "hemoglobin", "wbc", "rbc",
        ]
        labels = {
            "height": "Height (키, cm)",
            "weight": "Weight (몸무게, kg)",
            "sbp": "SBP (수축기 혈압, mmHg)",
            "dbp": "DBP (이완기 혈압, mmHg)",
            "hp_stage": "Hypertension Stage (고혈압 단계)",
            "glucose": "Glucose (혈당, mg/dL)",
            "hba1c": "HbA1c (당화혈색소, %)",
            "cholesterol": "Total Cholesterol (총 콜레스테롤, mg/dL)",
            "hdl": "HDL Cholesterol (HDL 콜레스테롤, mg/dL)",
            "triglyceride": "Triglyceride (중성지방, mg/dL)",
            "ast": "AST (간기능, U/L)",
            "alt": "ALT (간기능, U/L)",
            "hemoglobin": "Hemoglobin (헤모글로빈, g/dL)",
            "wbc": "WBC (백혈구, ×10³/μL)",
            "rbc": "RBC (적혈구, ×10⁶/μL)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
            })

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