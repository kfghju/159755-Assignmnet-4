# components/predict_match_result_model_pre_match.py

import os
import numpy as np
import pandas as pd
from glob import glob
import joblib

def predict_match_result(df_match):
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, '..', 'models', 'pre_match_result_model.pkl')
    scaler_path = os.path.join(base_path, '..', 'models', 'pre_match_result_scaler.pkl')
    _model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Loaded model type:", type(_model))
    print("Is model fitted?", hasattr(_model, "coef_"))
    features = [
        'b365_prob_h', 'b365_prob_d', 'b365_prob_a',
        'overall_diff', 'attack_diff', 'midfield_diff',
        'defence_diff', 'age_diff'
    ]
    X_new = df_match[features]
    X_new_scaled = scaler.transform(X_new)
    pred = _model.predict(X_new_scaled)[0]
    proba = _model.predict_proba(X_new_scaled)[0]
    result_map = {0: 'Home Win', 1: 'Away Win'}
    return {
        "prediction": result_map[pred],
        "probabilities": {
            "Home Win": round(proba[0], 3),
            "Away Win": round(proba[1], 3)
        }
    }

