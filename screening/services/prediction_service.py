"""
COPD 폐활량검사 권고 예측 서비스
"""

from datetime import date

from screening.models import PredictionResult
from screening.ml_model import predict_risk_probability


def calculate_age(birth_date):
    today = date.today()

    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def convert_sex_to_model_value(sex):
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

        # 증상
        "HE_cough1": int(questionnaire.cough),
        "HE_sput1": int(questionnaire.sputum),

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
        "HE_hsCRP": health_record.hscrp,

        # 기왕력
        "DJ4_dg": int(health_record.asthma_history or False),
        "DJ8_dg": int(health_record.rhinitis_history or False),

        # 흡연
        "smoking_status": questionnaire.smoking_status,
        "smoking_amount": questionnaire.smoking_amount,

        # hsCRP 결측 여부
        "hsCRP_missing": 1 if health_record.hscrp is None else 0,
    }

    return features


def create_prediction_result(questionnaire, health_record):
    features = build_feature_dict(questionnaire, health_record)

    risk_probability, top_factors = predict_risk_probability(features)

    prediction = PredictionResult.objects.create(
        questionnaire=questionnaire,
        health_record=health_record,
        risk_probability=risk_probability,
        top_factors=top_factors,
        year=date.today().year,
    )

    return prediction