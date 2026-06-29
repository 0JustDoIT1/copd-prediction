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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ModelChoiceField/TypedChoiceField가 기본으로 만드는 빈 옵션("---------")을
        # 끄고, 대신 원하는 안내 문구 하나만 빈 값으로 넣는다.
        # (둘 다 살려두면 "흡연 상태를 선택해주세요."와 "---------"가 같이
        # 떠서 빈 옵션이 중복으로 보이는 문제가 있었음)
        self.fields["smoking_status"].choices = [
            ("", "흡연 상태를 선택해주세요.")
        ] + [
            choice for choice in self.fields["smoking_status"].choices
            if choice[0] != ""
        ]

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

        # disabled 처리된 input은 폼 제출 시 값 자체가 전송되지 않으므로,
        # smoking_amount를 required=False로 둬서 "이 필드는 필수입니다" 에러가
        # clean() 도달 전에 먼저 발생하지 않게 한다. 실제 값 보정은 clean()에서.
        self.fields["smoking_amount"].required = False

    def clean(self):
        cleaned_data = super().clean()
        smoking_status = cleaned_data.get("smoking_status")
        smoking_amount = cleaned_data.get("smoking_amount")

        # 비흡연(0)·과거흡연(1)인 경우, 클라이언트에서 disabled로 막아도
        # 폼 데이터를 직접 조작해서 보낼 수 있고, disabled된 input은 값 자체가
        # 전송되지 않아 None으로 들어올 수도 있으므로 서버에서 항상 0으로
        # 최종 보정한다 (입력값을 신뢰하지 않고 서버가 마지막에 확정).
        if str(smoking_status) in ("0", "1"):
            cleaned_data["smoking_amount"] = 0
        elif str(smoking_status) == "2":
            # 현재흡연(2)인데 흡연량이 비어있거나 0이면, 논리적으로 맞지 않으므로
            # 명시적인 에러로 막는다. 0을 "값이 없다"는 의미로 그냥 채워버리지 않음.
            if smoking_amount in (None, ""):
                self.add_error("smoking_amount", "현재흡연을 선택한 경우 하루 흡연량을 입력해주세요.")
            elif smoking_amount <= 0:
                self.add_error("smoking_amount", "현재흡연을 선택한 경우 흡연량은 0보다 커야 합니다.")

        return cleaned_data


class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = [
            "height", "weight",
            "sbp", "dbp", "bp_medication",
            "glucose", "hba1c", "cholesterol", "hdl", "triglyceride",
            "ast", "alt", "hemoglobin", "wbc", "rbc",
            "hscrp", "asthma_history", "rhinitis_history",
        ]

        labels = {
            "height": "Height (키, cm)",
            "weight": "Weight (몸무게, kg)",
            "sbp": "SBP (수축기 혈압, mmHg)",
            "dbp": "DBP (이완기 혈압, mmHg)",
            "bp_medication": "현재 혈압약을 복용 중입니까?",
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
            "hscrp": "hsCRP (고감도 C-반응단백, mg/L)",
            "asthma_history": "Asthma History (천식 진단 이력)",
            "rhinitis_history": "Rhinitis History (비염 진단 이력)",
        }

        widgets = {
            "asthma_history": forms.RadioSelect(
                choices=[
                    (True, "예"),
                    (False, "아니오"),
                ]
            ),
            "rhinitis_history": forms.RadioSelect(
                choices=[
                    (True, "예"),
                    (False, "아니오"),
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

        # 예측 모델에 필요한 필수 변수
        required_fields = [
            "height",
            "weight",
            "sbp",
            "dbp",
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
            "asthma_history",
            "rhinitis_history",
        ]

        for field_name in required_fields:
            self.fields[field_name].required = True

        # hsCRP는 결측 허용
        self.fields["hscrp"].required = False


class ClinicalDecisionForm(forms.ModelForm):
    class Meta:
        model = ClinicalDecision
        fields = [
            "decision",
            "memo",
        ]
        labels = {
            "memo": "의사 소견",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # smoking_status와 동일한 이유로, 자동 생성되는 빈 옵션과 중복되지 않게 처리
        self.fields["decision"].choices = [
            ("", "판정을 선택해주세요.")
        ] + [
            choice for choice in self.fields["decision"].choices
            if choice[0] != ""
        ]


class OCRUploadForm(forms.Form):
    image = forms.ImageField(
        label="검진결과지 이미지",
        required=True
    )