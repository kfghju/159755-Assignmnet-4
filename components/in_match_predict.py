import os
import numpy as np
import pandas as pd
import streamlit as st
import joblib

# ===== Data and model loading =====
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    club_stats = pd.read_csv(os.path.join(base, "data", "club_stats.csv"))
    winrates = pd.read_csv(os.path.join(base, "data", "team_winrates.csv"))
    return club_stats, winrates

def load_model_and_scaler():
    base = os.path.dirname(os.path.abspath(__file__))
    model = joblib.load(os.path.join(base, "models", "in_match_result_model.pkl"))
    scaler = joblib.load(os.path.join(base, "models", "in_match_result_scaler.pkl"))
    return model, scaler

# ===== Betting suggestion function =====
def betting_recommendation(pred_result, home_winrate, away_winrate, draw_gap=0.05):
    if pred_result == 'H':
        return 'Bet' if home_winrate > away_winrate else '❌ No Bet'
    elif pred_result == 'A':
        return 'Bet' if away_winrate > home_winrate else '❌ No Bet'
    elif pred_result == 'D':
        return 'Bet' if abs(home_winrate - away_winrate) <= draw_gap else '❌ No Bet'
    return 'Unknown'

# ===== Streamlit Main Function =====
def main():
    st.set_page_config(page_title="⚡ In-Match Football Predictor", layout="centered")
    st.title("🏟️ In-Match Result Prediction")

    club_stats, winrates = load_data()
    team_names = sorted(winrates["HomeTeam"].unique())

    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 Home Team", team_names)
        hthg = st.number_input("⚽ Half-time Goals (Home)", min_value=0, max_value=10, value=1)
        odd_h = st.number_input("💰 Odds - Home Win", min_value=1.0, value=2.1)
    with col2:
        away_team = st.selectbox("🛫 Away Team", [t for t in team_names if t != home_team])
        htag = st.number_input("⚽ Half-time Goals (Away)", min_value=0, max_value=10, value=1)
        odd_a = st.number_input("💰 Odds - Away Win", min_value=1.0, value=3.1)

    odd_d = st.number_input("💰 Odds - Draw", min_value=1.0, value=3.0)

    if st.button("🔮 Predict"):
        # Get data rows
        home_row = club_stats[(club_stats["Club"] == home_team) & (club_stats["Season"] == "2024/25")].iloc[0]
        away_row = club_stats[(club_stats["Club"] == away_team) & (club_stats["Season"] == "2024/25")].iloc[0]
        win_row = winrates[winrates["HomeTeam"] == home_team].iloc[0]
        away_win_row = winrates[winrates["HomeTeam"] == away_team].iloc[0]

        home_winrate, away_winrate = win_row["HomeWinRate"], away_win_row["AwayWinRate"]
        eps = 1e-6

        # All odds features
        df_input = pd.DataFrame([{
            'HTHG': hthg, 'HTAG': htag,
            'B365H': odd_h, 'B365D': odd_d, 'B365A': odd_a,
            'BWH': odd_h, 'BWD': odd_d, 'BWA': odd_a,
            'PSH': odd_h, 'PSD': odd_d, 'PSA': odd_a,
            'WHH': odd_h, 'WHD': odd_d, 'WHA': odd_a,
            'AvgH': odd_h, 'AvgD': odd_d, 'AvgA': odd_a,
            'MaxH': odd_h, 'MaxD': odd_d, 'MaxA': odd_a,
            'HPos': home_row["Position"], 'HPlayed': home_row["Played"],
            'HWon': home_row["Won"], 'HDrawn': home_row["Drawn"], 'HLost': home_row["Lost"],
            'APos': away_row["Position"], 'APlayed': away_row["Played"],
            'AWon': away_row["Won"], 'ADrawn': away_row["Drawn"], 'ALost': away_row["Lost"],
            'HWinRate': home_winrate, 'AWinRate': away_winrate,
            'HDrawRate': home_row["Drawn"] / (home_row["Played"] + eps),
            'ADrawRate': away_row["Drawn"] / (away_row["Played"] + eps),
            'HLossRate': home_row["Lost"] / (home_row["Played"] + eps),
            'ALossRate': away_row["Lost"] / (away_row["Played"] + eps),
            'PosDiff': away_row["Position"] - home_row["Position"],
            'PosRatio': home_row["Position"] / (away_row["Position"] + eps),
            'HDRatio': odd_h / (odd_d + eps),
            'HARatio': odd_h / (odd_a + eps),
            'DARatio': odd_d / (odd_a + eps)
        }])

        # Model loading & prediction
        model, scaler = load_model_and_scaler()
        X_scaled = scaler.transform(df_input)
        pred_index = model.predict(X_scaled)[0]
        pred_proba = model.predict_proba(X_scaled)[0]

        label_map = {0: 'H', 1: 'D', 2: 'A'}
        label_text = {'H': '🏠 Home Win', 'D': '⚖️ Draw', 'A': '🏟️ Away Win'}
        pred_label = label_map[pred_index]
        readable = label_text[pred_label]
        bet_suggestion = betting_recommendation(pred_label, home_winrate, away_winrate)

        # Display results
        st.success(f"🎯 Prediction: **{readable}**")
        st.markdown("### 📊 Probability")
        st.markdown(f"- Home Win: **{pred_proba[0]*100:.1f}%**")
        st.markdown(f"- Draw: **{pred_proba[1]*100:.1f}%**")
        st.markdown(f"- Away Win: **{pred_proba[2]*100:.1f}%**")
        st.markdown("---")
        st.markdown(f"### 💡 Betting Suggestion: **{bet_suggestion}**")
        st.markdown(f"🏠 Home Win Rate: **{home_winrate:.2f}**  🛫 Away Win Rate: **{away_winrate:.2f}**")

if __name__ == "__main__":
    main()
