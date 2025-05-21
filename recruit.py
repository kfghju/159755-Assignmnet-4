# components/recruit.py

import streamlit as st
import pandas as pd

def render_recruit_section(mode):
    if 'current_player' in st.session_state and (
        mode == 'Choose Preset Player' or
        (mode == 'Create New Player' and st.session_state['current_player'].get('Name', '').strip())
    ):
        st.subheader("🧍‍♂️ Player to Recruit")
        display_df = pd.DataFrame([st.session_state['current_player']])
        display_df['Value'] = display_df['Value'].apply(
            lambda x: f"€{float(x):,.2f}" if isinstance(x, (int, float)) else x)
        st.write(display_df)

        if 'confirm_final' not in st.session_state:
            if st.button("Recruit Player", key="recruit_button"):
                player = st.session_state['current_player']
                numeric_value = float(str(player['Value']).replace('€', '').replace(',', ''))
                if numeric_value > st.session_state['budget']:
                    st.error("❌ Not enough budget!")
                elif any(p['Name'] == player['Name'] for p in st.session_state['team']):
                    st.warning("⚠️ This player is already in your team.")
                else:
                    player['Value'] = f"€{numeric_value:,.2f}"
                    st.session_state['team'].append(player)
                    st.session_state['budget'] -= numeric_value
                    st.success(f"✅ Successfully recruited {player['Name']}!")
                    st.session_state['recruited_this_round'] = True
                    st.rerun()

    # 清除 current_player 防止重复显示
    if st.session_state.get('recruited_this_round'):
        del st.session_state['current_player']
        del st.session_state['recruited_this_round']
