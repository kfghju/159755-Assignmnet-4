# app.py (主程序入口)

import streamlit as st
st.set_page_config(page_title="Football Manager Simulator", layout="centered")
from player_input import handle_player_input
from recruit import render_recruit_section
from team import render_team_section
from match import run_season_simulation


st.title("💰 Football Player Value Estimator")

# 初始化状态
if 'budget' not in st.session_state:
    st.session_state['budget'] = 1_000_000_000
if 'team' not in st.session_state:
    st.session_state['team'] = []

# 模式选择
mode = st.radio("Player Input Mode", ["Create New Player", "Choose Preset Player"])
st.session_state['mode'] = mode

# 处理球员输入逻辑（侧边栏 + 模型预测）
handle_player_input(mode)

# 招募模块（展示 Player to Recruit + 按钮）
render_recruit_section(mode)

# 球队展示 + 管理
render_team_section()

# 比赛阶段（需已确认）
run_season_simulation()

# 重置按钮（放在最后）
if st.sidebar.button("🔁 Reset Game"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()