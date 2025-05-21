# components/match.py

import streamlit as st
import random

def run_season_simulation():
    if 'confirm_final' in st.session_state:
        st.markdown("---")
        st.header("🏟️ Premier League Season Simulator (38 Games)")

        if 'current_match' not in st.session_state:
            st.session_state['current_match'] = 0
            st.session_state['match_results'] = []

        if st.session_state['current_match'] < 38:
            if st.button(f"▶️ Play Match {st.session_state['current_match'] + 1}"):
                match_number = st.session_state['current_match'] + 1

                # 随机事件模拟（未来可替换为真实预测模型）
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

        # 展示比赛日志
        st.subheader("📋 Match Events Log")
        for match_num, result in st.session_state['match_results']:
            st.markdown(f"**Match {match_num}:** {result}")

        st.markdown("</div>", unsafe_allow_html=True)
