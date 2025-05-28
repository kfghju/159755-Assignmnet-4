# components/match.py
import os

import streamlit as st
import random
import pandas as pd
import sqlite3
from components.predict_match_result_model_pre_match import predict_match_result

def run_season_simulation():
    # base_path = os.path.dirname(os.path.abspath(__file__))
    # database_path = os.path.join(base_path, '..', 'data', 'allData.sl3')
    # scaler_path = os.path.join(base_path, '..', 'models', 'match_result_scaler.pkl')
    # connection = sqlite3.connect(database_path)
    # cursor = connection.cursor()
    # df_team = pd.DataFrame(st.session_state['team'])
    # df_all_team = pd.read_sql_query("select * from team_stats where year == '2025'", connection)
    # cursor.close()
    # connection.close()
    if 'confirm_final' in st.session_state:
        st.markdown("---")
        st.header("Match Simulator")

        if 'current_match' not in st.session_state:
            st.session_state['current_match'] = 0
            st.session_state['match_results'] = []

        if st.session_state['current_match'] < 38:
            if st.button(f"Play Match {st.session_state['current_match'] + 1}"):
                match_number = st.session_state['current_match'] + 1

                # Random event simulation
                events = [
                    "No major events.",
                    "One player injured.",
                    "Key player improved after intense training!",
                    "Market value of one player dropped.",
                    "Fan support surged – morale up!",
                    "Star player underperforms due to pressure."
                ]
                event_result = random.choice(events)
                st.session_state['match_results'].append((match_number, event_result))
                st.session_state['current_match'] += 1
                st.rerun()

        # Show game log
        st.subheader("📋 Match Events Log")
        for match_num, result in st.session_state['match_results']:
            st.markdown(f"**Match {match_num}:** {result}")

        st.markdown("</div>", unsafe_allow_html=True)

