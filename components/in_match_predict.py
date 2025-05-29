# components/in_match_predict.py
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
import joblib

# Dummy model loading (replace with real model path)
def load_model():
    return joblib.load("models/final_model.pkl")  # Replace with your model path

# Extract feature columns used in training
FEATURE_COLUMNS = [
    'home_team_enc', 'away_team_enc', 'weekday',
    'avg_home_odds', 'avg_draw_odds', 'avg_away_odds',
    'odds_gap', 'draw_prob_ratio', 'min_odd_type',
    'league_enc', 'season', 'HomeWinRate', 'AwayWinRate'
]

# Main function to be called from app.py

def render_in_match_predict_section(df_all_teams):
    st.header("🌟 In-Match Result Predictor")

    # Team selection
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Select Home Team", sorted(df_all_teams['HomeTeam'].unique()))
    with col2:
        away_team = st.selectbox("Select Away Team", sorted(df_all_teams['AwayTeam'].unique()))

    # Filter one row for the selected match
    match_row = df_all_teams[(df_all_teams['HomeTeam'] == home_team) & 
                             (df_all_teams['AwayTeam'] == away_team)].sort_values("Date", ascending=False).head(1)

    if match_row.empty:
        st.warning("No data available for this match.")
        return

    # Load trained model
    model = load_model()

    # Prepare input
    X_input = match_row[FEATURE_COLUMNS].astype('float64')

    # Predict and display
    pred_proba = model.predict_proba(X_input)[0]
    pred_result = model.predict(X_input)[0]

    label_map = {0: "🏠 Home Win", 1: "⚖️ Draw", 2: "🏟️ Away Win"}
    st.subheader(f"Prediction: {label_map[pred_result]}")

    st.markdown("### Probability Breakdown")
    st.progress(pred_proba[0])
    st.markdown(f"**Home Win:** {pred_proba[0]*100:.1f}%")
    st.progress(pred_proba[1])
    st.markdown(f"**Draw:** {pred_proba[1]*100:.1f}%")
    st.progress(pred_proba[2])
    st.markdown(f"**Away Win:** {pred_proba[2]*100:.1f}%")

    st.caption("Model is based on historical win rates and odds-based features.")
