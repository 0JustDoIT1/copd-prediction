from django import forms
from .models import DailyLog

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = [
            "smoking_count",
            "dyspnea_grade",
            "spo2",
            "has_cough",
            "has_sputum",
            "exercised",
            "memo",
        ]
        widgets = {
            "smoking_count": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 99}
            ),
            "dyspnea_grade": forms.Select(
                attrs={"class": "form-select"}
            ),
            "spo2": forms.NumberInput(
                attrs={"class": "form-control", "min": 80, "max": 100, "step": "0.1", "placeholder": "예: 98.5"}
            ),
            "has_cough": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
            "has_sputum": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
            "exercised": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
            "memo": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "특이사항을 자유롭게 작성해 주세요. (최대 500자)"}
            ),
        }

    def clean_memo(self):
        memo = self.cleaned_data.get("memo", "")
        if len(memo) > 500:
            raise forms.ValidationError("메모는 500자 이하로 입력해 주세요.")
        return memo