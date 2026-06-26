import json
from pathlib import Path

import joblib

ML_DIR = Path(__file__).resolve().parent / 'ml'

# 모듈 로드 시점에 한 번만 읽어서 메모리에 캐시 — 매 요청마다 다시 로드하면 느림
_model = joblib.load(ML_DIR / 'copd_screening_model.pkl')

with open(ML_DIR / 'model_config.json', encoding='utf-8') as f:
    _config = json.load(f)

THRESHOLD = _config['threshold']
FEATURE_ORDER = _config['feature_order']
IMPUTATION_VALUES = _config['imputation_values']


def predict_risk_probability(feature_dict):
    """
    feature_dict: {변수명: 값} 형태의 딕셔너리 (Questionnaire + HealthRecord에서 추출)
    반환: (risk_probability, top_factors)
    """
    import numpy as np

    # 1. feature_order 순서대로 값 정렬, 결측치는 imputation_values로 채움
    row = []
    for feature in FEATURE_ORDER:
        value = feature_dict.get(feature)
        if value is None:
            value = IMPUTATION_VALUES.get(feature, 0)
        row.append(value)

    X = np.array([row])

    # 2. 예측
    risk_probability = _model.predict_proba(X)[0][1]

    # 3. top_factors 계산 (Logistic Regression: scaler.transform(X) * coef_)
    pipeline_scaler = _model.named_steps['standardscaler']  # 파이프라인 단계명은 실제 pkl 구조 확인 필요
    pipeline_clf = _model.named_steps['logisticregression']

    X_scaled = pipeline_scaler.transform(X)
    contributions = X_scaled[0] * pipeline_clf.coef_[0]

    factor_pairs = list(zip(FEATURE_ORDER, contributions))
    factor_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    top_factors = factor_pairs[:5]

    return risk_probability, top_factors