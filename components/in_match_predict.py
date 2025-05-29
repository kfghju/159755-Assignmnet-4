# components/in_match_predict.py

import os
import pandas as pd
import numpy as np
import streamlit as st
import joblib

# 模型输入特征
FEATURE_COLUMNS = [
    'HTHG', 'HTAG',
    'B365H', 'B365D', 'B365A',
    'BWH', 'BWD', 'BWA',
    'PSH', 'PSD', 'PSA',
    'WHH', 'WHD', 'WHA',
    'AvgH', 'AvgD', 'AvgA',
    'MaxH', 'MaxD', 'MaxA',
    'HPos', 'HPlayed', 'HWon', 'HDrawn', 'HLost',
    'APos', 'APlayed', 'AWon', 'ADrawn', 'ALost',
    'HWinRate', 'AWinRate',
    'HDrawRate', 'ADrawRate',
    'HLossRate', 'ALossRate',
    'PosDiff', 'PosRatio',
    'HDRatio', 'HARatio', 'DARatio'
]

# 加载训练好的模型和 scaler
def load_model_and_scaler():
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, '..', 'models', 'in_match_result_model.pkl')
    scaler_path = os.path.join(base_path, '..', 'models', 'in_match_result_scaler.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        st.error(" 模型文件或标准化器文件缺失，请检查 models 文件夹。")
        st.stop()

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler

# 主函数：调用时传入比赛数据集（包含所有特征）
def render_in_match_predict_section(df_all_teams):
    st.header("🌟 In-Match Result Predictor")

    # 球队选择
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Select Home Team", sorted(df_all_teams['HomeTeam'].unique()))
    with col2:
        away_team = st.selectbox("Select Away Team", sorted(df_all_teams['AwayTeam'].unique()))

    # 查找最新的这场比赛数据
    match_row = df_all_teams[(df_all_teams['HomeTeam'] == home_team) & 
                             (df_all_teams['AwayTeam'] == away_team)].sort_values("Date", ascending=False).head(1)

    if match_row.empty:
        st.warning("⚠️ No data available for this match.")
        return

    # 加载模型 & scaler
    model, scaler = load_model_and_scaler()

    # 提取输入特征
    try:
        X_input = match_row[FEATURE_COLUMNS].astype('float64')
    except KeyError as e:
        st.error(f" 缺少所需字段：{e}")
        st.stop()

    # 标准化 + 预测
    X_scaled = scaler.transform(X_input)
    pred_result = model.predict(X_scaled)[0]
    pred_proba = model.predict_proba(X_scaled)[0]

    # 显示结果
    label_map = {0: "🏠 Home Win", 1: "⚖️ Draw", 2: "🏟️ Away Win"}
    st.subheader(f"Prediction: {label_map.get(pred_result, 'Unknown')}")

    st.markdown("### 📊 Probability Breakdown")
    for i, label in enumerate(["Home Win", "Draw", "Away Win"]):
        st.progress(pred_proba[i])
        st.markdown(f"**{label}:** {pred_proba[i]*100:.1f}%")

    st.caption("Model is based on real-time match state and pre-match betting odds.")
