import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prediction_model import predict_match_result  # 你需要实现这个函数
from utils import load_team_stats, plot_team_form  # 可选的辅助函数模块

# --------------------- 页面配置 ---------------------
st.set_page_config(page_title="Football Match Predictor", layout="wide")
st.title("⚽ Football Match Outcome Predictor")

# --------------------- 侧边栏输入 ---------------------
st.sidebar.header("🔧 Match Settings")
team_list = ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea', 'Tottenham']  # 示例
team_home = st.sidebar.selectbox("🏠 Home Team", team_list)
team_away = st.sidebar.selectbox("🚩 Away Team", [team for team in team_list if team != team_home])

match_date = st.sidebar.date_input("📅 Match Date")

# --------------------- 主界面 ---------------------
st.markdown(f"## {team_home} vs {team_away} - {match_date}")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{team_home} Recent Form")
    home_stats = load_team_stats(team_home)  # 自定义函数从缓存加载数据
    plot_team_form(home_stats, team_home)   # 可画出折线图或雷达图

with col2:
    st.subheader(f"{team_away} Recent Form")
    away_stats = load_team_stats(team_away)
    plot_team_form(away_stats, team_away)

# --------------------- 模型预测结果展示 ---------------------
st.markdown("## 🧠 Match Result Prediction")

if st.button("Run Prediction"):
    prediction, probas = predict_match_result(team_home, team_away, match_date)
    st.success(f"Predicted Outcome: **{prediction}**")
    st.write("Probability Breakdown:")
    st.bar_chart(pd.DataFrame(probas, index=["Probability"]).T)

# --------------------- 更多展示区块（可选） ---------------------
st.markdown("---")
st.markdown("### 📊 Additional Insights")
# 如：进球期望、控球率趋势图、两队对战历史胜率饼图等
