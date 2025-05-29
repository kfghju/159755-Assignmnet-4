# app.py (Minimal test version for in_match_predict import)
import streamlit as st
import pandas as pd

from components.in_match_predict import render_in_match_predict_section

# Sample DataFrame with required structure
sample_data = pd.DataFrame({
    'HomeTeam': ['Chelsea', 'Man United'],
    'AwayTeam': ['Arsenal', 'Liverpool'],
    'Date': pd.to_datetime(['2024-04-01', '2024-04-02']),
    'home_team_enc': [1, 2],
    'away_team_enc': [3, 4],
    'weekday': [0, 1],
    'avg_home_odds': [1.8, 2.0],
    'avg_draw_odds': [3.2, 3.0],
    'avg_away_odds': [4.5, 3.8],
    'odds_gap': [2.7, 1.8],
    'draw_prob_ratio': [0.2, 0.25],
    'min_odd_type': [0, 2],
    'league_enc': [0, 1],
    'season': [2024, 2024],
    'HomeWinRate': [0.65, 0.45],
    'AwayWinRate': [0.35, 0.55],
    'FTR': ['H', 'A']
})

st.title("Minimal Test for In-Match Prediction Import")

render_in_match_predict_section(sample_data)
