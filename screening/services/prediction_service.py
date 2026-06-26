"""
COPD 폐활량검사 권고 예측 서비스
"""

from datetime import date

from screening.models import PredictionResult


def calculate_age(birth_date):
    today = date.today()

    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def convert_sex_to_model_value(sex):
    """
    PatientProfile.sex 값을 ML 모델 입력값으로 변환

    임시 기준:
    M -> 1
    F -> 2

    KNHANES 코드북 기준 확인 후 필요 시 수정
    """
    if sex == "M":
        return 1
    if sex == "F":
        return 2

    return None


def build_feature_dict(questionnaire, health_record):
    patient = questionnaire.patient

    features = {
        # 인구학
        "sex": convert_sex_to_model_value(patient.sex),
        "age": calculate_age(patient.birth_date),
        "HE_ht": health_record.height,
        "HE_wt": health_record.weight,
        "HE_BMI": health_record.bmi,

        # 흡연
        "smoking_status": questionnaire.smoking_status,
        "smoking_amount": questionnaire.smoking_amount,

        # 증상
        "HE_cough1": int(questionnaire.cough),
        "HE_qput1": int(questionnaire.sputum),

        # 혈압
        "HE_sbp": health_record.sbp,
        "HE_dbp": health_record.dbp,
        "HE_HP": health_record.hp_stage,

        # 혈액검사
        "HE_glu": health_record.glucose,
        "HE_HbA1c": health_record.hba1c,
        "HE_chol": health_record.cholesterol,
        "HE_HDL_st2": health_record.hdl,
        "HE_TG": health_record.triglyceride,
        "HE_ast": health_record.ast,
        "HE_alt": health_record.alt,
        "HE_HB": health_record.hemoglobin,
        "HE_WBC": health_record.wbc,
        "HE_RBC": health_record.rbc,
    }

    return features


def create_prediction_result(questionnaire, health_record):
    """
    임시 예측 함수

    실제 ML 모델 연결 전까지는 가짜 점수로 PredictionResult를 생성합니다.
    나중에 copd_screening_model.pkl 연결 시 이 부분을 교체합니다.
    """

    features = build_feature_dict(questionnaire, health_record)

    # TODO: 실제 모델 연결 후 교체
    risk_probability = 0.0

    prediction = PredictionResult.objects.create(
        questionnaire=questionnaire,
        health_record=health_record,
        risk_probability=risk_probability,
        top_factors={},
        year=date.today().year,
    )

    return prediction