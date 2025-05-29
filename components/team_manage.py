# components/team_manage.py

import streamlit as st
import pandas as pd

def render_team_section(mode):
    if (mode not in ['Match Predict (Pre-match)', 'Match Predict (In-match)']):
        st.subheader("⚽ Your Team")

        if st.session_state['team']:
            df_team = pd.DataFrame(st.session_state['team'])
            st.write("### Your Current Squad")

            st.dataframe(df_team.style.format({
                "Value": lambda x: f"€{float(str(x).replace('€','').replace(',','')):,.2f}"
            }))

            # Deleting Players
            with st.expander("🧹 Manage Squad (Remove Players)", expanded=True):
                cols = st.columns(len(df_team))
                for i, row in df_team.iterrows():
                    with cols[i]:
                        st.markdown(f"**{row['Name']}**")
                        if 'confirm_final' not in st.session_state:
                            if st.button("❌ Remove", key=f"remove_{i}"):
                                st.session_state['budget'] += float(str(row['Value']).replace('€', '').replace(',', ''))
                                st.session_state['team'].pop(i)
                                st.rerun()

            total_value = sum([
                float(str(p['Value']).replace('€', '').replace(',', '')) for p in st.session_state['team']
            ])
            st.markdown(f"**Total Team Value:** €{total_value:,.0f}")

            if 'confirm_final' not in st.session_state:
                if st.button("✅ Confirm Final Team"):
                    if len(df_team) < 11:
                        st.info("Team player less than 11, cannot play the game")
                    else:
                        st.session_state['confirm_final'] = True
                        st.success("Team confirmed! You can no longer make changes.")
        else:
            st.info("No players recruited yet.")

        # st.sidebar.subheader("💰 Budget Left")
        # st.sidebar.write(f"€{st.session_state['budget']:,.0f}")
