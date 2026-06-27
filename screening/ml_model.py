import json
from pathlib import Path

import joblib


ML_DIR = Path(__file__).resolve().parent / "ml"

_model = joblib.load(ML_DIR / "copd_screening_model.pkl")

with open(ML_DIR / "model_config.json", encoding="utf-8") as f:
    _config = json.load(f)

THRESHOLD = _config["threshold"]
FEATURE_ORDER = _config["feature_order"]
IMPUTATION_VALUES = _config["imputation_values"]


def predict_risk_probability(feature_dict):
    """
    feature_dict: {변수명: 값} 형태의 딕셔너리
    반환: (risk_probability, top_factors)
    """
    import numpy as np

    row = []

    for feature in FEATURE_ORDER:
        value = feature_dict.get(feature)

        if value is None:
            value = IMPUTATION_VALUES.get(feature, 0)

        row.append(value)

    X = np.array([row])

    risk_probability = float(_model.predict_proba(X)[0][1])

    pipeline_scaler = _model.named_steps["scaler"]
    pipeline_clf = _model.named_steps["clf"]

    X_scaled = pipeline_scaler.transform(X)
    contributions = X_scaled[0] * pipeline_clf.coef_[0]

    factor_pairs = list(zip(FEATURE_ORDER, contributions))
    factor_pairs.sort(key=lambda x: abs(x[1]), reverse=True)

    top_factors = [
        {
            "feature": feature,
            "contribution": float(contribution),
        }
        for feature, contribution in factor_pairs[:5]
    ]

    return risk_probability, top_factors