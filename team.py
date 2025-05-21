# components/team.py

import streamlit as st
import pandas as pd

def render_team_section():
    st.subheader("⚽ Your Team")

    if st.session_state['team']:
        df_team = pd.DataFrame(st.session_state['team'])
        st.write("### Your Current Squad")

        st.dataframe(df_team.style.format({
            "Value": lambda x: f"€{float(str(x).replace('€','').replace(',','')):,.2f}"
        }))

        # 管理区块：删除球员
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

        # 总价值 + 确认按钮
        total_value = sum([
            float(str(p['Value']).replace('€','').replace(',','')) for p in st.session_state['team']
        ])
        st.markdown(f"**Total Team Value:** €{total_value:,.0f}")

        if 'confirm_final' not in st.session_state:
            if st.button("✅ Confirm Final Team"):
                st.session_state['confirm_final'] = True
                st.success("Team confirmed! You can no longer make changes.")
    else:
        st.info("No players recruited yet.")

    # 显示当前预算
    st.sidebar.subheader("💰 Budget Left")
    st.sidebar.write(f"€{st.session_state['budget']:,.0f}")
