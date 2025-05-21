import streamlit as st
import pandas as pd
from prediction_model import predict_player_value

# 页面设置
st.set_page_config(page_title="Virtual Manager Game", layout="centered")
st.title("🎮 Virtual Football Manager")

# 初始预算
if 'budget' not in st.session_state:
    st.session_state['budget'] = 100_000_000  # €100M
if 'team' not in st.session_state:
    st.session_state['team'] = []

st.sidebar.header("📝 Create Your Player")

# 用户输入球员属性
player_name = st.sidebar.text_input("Player Name")
player_age = st.sidebar.slider("Age", 16, 45, 24)
player_height = st.sidebar.number_input("Height (cm)", 150, 220, 180)
player_weight = st.sidebar.number_input("Weight (kg)", 50, 120, 75)
player_potential = st.sidebar.slider("Potential (0-100)", 40, 100, 80)
player_position = st.sidebar.selectbox("Best Position", ['ST', 'CM', 'CAM', 'CB', 'GK', 'LM', 'RM', 'RB', 'LB'])
player_stamina = st.sidebar.slider("Stamina", 20, 100, 70)
player_dribbling = st.sidebar.slider("Dribbling", 20, 100, 70)
player_short_passing = st.sidebar.slider("Short Passing", 20, 100, 70)

# 点击预测
if st.sidebar.button("Predict Player Value"):
    input_data = {
        'Age': player_age,
        'Height': player_height,
        'Weight': player_weight,
        'Potential': player_potential,
        'Best position': player_position,
        'Stamina': player_stamina,
        'Dribbling': player_dribbling,
        'Short passing': player_short_passing
    }
    predicted_value = predict_player_value(input_data)
    st.session_state['current_player'] = {
        'Name': player_name,
        'Value': predicted_value,
        **input_data
    }
    st.sidebar.success(f"Estimated Value: €{predicted_value:,.0f}")

# 确认招募球员
if 'current_player' in st.session_state:
    player = st.session_state['current_player']
    st.subheader("🧍‍♂️ Player to Recruit:")
    st.write(pd.DataFrame([player]).drop(columns=['Height', 'Weight']))

    if st.button("Recruit Player"):
        if player['Value'] > st.session_state['budget']:
            st.error("❌ Not enough budget!")
        else:
            st.session_state['team'].append(player)
            st.session_state['budget'] -= player['Value']
            st.success(f"✅ Successfully recruited {player['Name']}!")
            del st.session_state['current_player']

# 显示当前球队
st.subheader("⚽️ Your Team")
if st.session_state['team']:
    team_df = pd.DataFrame(st.session_state['team'])
    st.write(team_df[['Name', 'Age', 'Best position', 'Potential', 'Value']])

    total_value = team_df['Value'].sum()
    st.markdown(f"**Total Team Value:** €{total_value:,.0f}")

else:
    st.info("You have not recruited any players yet.")

# 显示预算余额
st.sidebar.subheader("💰 Budget Left")
st.sidebar.write(f"€{st.session_state['budget']:,.0f}")
