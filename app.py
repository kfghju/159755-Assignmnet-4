# app.py

import streamlit as st
import pandas as pd
from prediction_model import predict_player_value

st.set_page_config(page_title="Virtual Manager Game", layout="centered")
st.title("🎮 Virtual Football Manager")


# 加载已有球员数据（预设球员）
@st.cache_data
def load_players():
    df = pd.read_csv("players_stats.csv")
    return df[[
        'Full Name', 'Age', 'Height', 'Weight', 'Potential', 'Best position',
        'Stamina', 'Dribbling', 'Short passing'
    ]].dropna()


preset_df = load_players()

# 初始化搜索与筛选前显示全部数量
filtered_df = preset_df.copy()

# 初始预算与团队列表
if 'budget' not in st.session_state:
    st.session_state['budget'] = 1_000_000_000
if 'team' not in st.session_state:
    st.session_state['team'] = []

# 玩家选择方式
mode = st.radio("Player Input Mode", ["Create New Player", "Choose Preset Player"])

if mode == "Create New Player":
    st.sidebar.header("📝 Create Your Player")
    name = st.sidebar.text_input("Player Name")
    age = st.sidebar.slider("Age", 16, 45, 24)
    height = st.sidebar.number_input("Height (cm)", 150, 220, 180)
    weight = st.sidebar.number_input("Weight (kg)", 50, 120, 75)
    potential = st.sidebar.slider("Potential", 40, 100, 80)
    position = st.sidebar.selectbox("Best Position", sorted(preset_df['Best position'].dropna().unique()))
    stamina = st.sidebar.slider("Stamina", 20, 100, 70)
    dribbling = st.sidebar.slider("Dribbling", 20, 100, 70)
    short_passing = st.sidebar.slider("Short Passing", 20, 100, 70)

    if st.sidebar.button("Predict Player Value"):
        input_data = {
            'Name': name,
            'Age': age,
            'Height': height,
            'Weight': weight,
            'Potential': potential,
            'Best position': position,
            'Stamina': stamina,
            'Dribbling': dribbling,
            'Short passing': short_passing
        }
        value = round(predict_player_value(input_data), 2)
        input_data['Value'] = format(value, ',.2f')
        st.session_state['current_player'] = input_data
        st.sidebar.success(f"Estimated Value: €{value:,.0f}")

else:
    st.sidebar.header("📋 Choose Preset Player")
    search_name = st.sidebar.text_input("🔍 Search by name")
    filtered_df = preset_df.copy()

    if 'position_filter' not in st.session_state:
        st.session_state['position_filter'] = []
    st.session_state['position_filter'] = st.sidebar.multiselect(
        "Filter by Position",
        sorted(preset_df['Best position'].dropna().unique()),
        default=st.session_state['position_filter']
    )
    position_filter = st.session_state['position_filter']
    if position_filter:
        filtered_df = filtered_df[filtered_df['Best position'].isin(position_filter)]

    if search_name:
        filtered_df = filtered_df[filtered_df['Full Name'].str.contains(search_name, case=False)]

    st.sidebar.markdown(f"Available Preset Players: **{len(filtered_df['Full Name'].unique())}**")

    selected = st.sidebar.selectbox("Select Player", filtered_df['Full Name'].unique())
    if not filtered_df[filtered_df['Full Name'] == selected].empty:
        player_row = filtered_df[filtered_df['Full Name'] == selected].sample(n=1).iloc[0]
    else:
        st.error("⚠️ No matching players found for the selected name and filters.")
        st.stop()
    input_data = {
        'Name': player_row['Full Name'],
        'Age': player_row['Age'],
        'Height': int(str(player_row['Height'])[:3]),
        'Weight': int(str(player_row['Weight']).replace('kg', '').strip()[:3]),
        'Potential': float(str(player_row['Potential']).split('\n')[0]),
        'Best position': player_row['Best position'],
        'Stamina': float(str(player_row['Stamina']).split('\n')[0]),
        'Dribbling': float(str(player_row['Dribbling']).split('\n')[0]),
        'Short passing': float(str(player_row['Short passing']).split('\n')[0])
    }
    value = predict_player_value(input_data)

    if value > 1_000_000_000:
        value = value / 100  # 修正预测模型输出异常值（如从log值转换时出错）
    input_data['Value'] = round(value, 2)
    st.session_state['current_player'] = input_data
    st.sidebar.success(f"Estimated Value: €{value:,.0f}")

# 推荐前 10 名综合评分球员
if mode == "Choose Preset Player" and not filtered_df.empty:
    st.subheader("🏆 Top 10 Suggested Players (by Composite Score)")


    def composite_score(row):
        return (
                float(row['Potential']) * 0.4 +
                float(row['Stamina']) * 0.2 +
                float(row['Dribbling']) * 0.2 +
                float(row['Short passing']) * 0.2
        )


    top_players = filtered_df.copy()
    for col in ['Potential', 'Stamina', 'Dribbling', 'Short passing']:
        top_players[col] = top_players[col].astype(str).str.extract(r'(\d+)')[0].astype(float)

    top_players["Score"] = top_players.apply(composite_score, axis=1)
    top_10 = top_players.sort_values("Score", ascending=False).head(10)

    selected_top_player = st.selectbox("Click to Select Player from Suggestions", top_10['Full Name'].tolist(),
                                       key="top_suggested_select")
    st.session_state['selected_top_player'] = selected_top_player
    if 'selected_top_player' in st.session_state and st.session_state['selected_top_player'] and not top_10[
        top_10['Full Name'] == st.session_state['selected_top_player']].empty:
        player_row = top_10[top_10['Full Name'] == st.session_state['selected_top_player']].iloc[0]
        input_data = {
            'Name': player_row['Full Name'],
            'Age': player_row['Age'],
            'Height': int(str(player_row['Height'])[:3]) if 'Height' in player_row else 180,
            'Weight': int(str(player_row['Weight']).replace('kg', '').strip()[:3]) if 'Weight' in player_row else 75,
            'Potential': float(str(player_row['Potential']).split('\n')[0]),
            'Best position': player_row['Best position'],
            'Stamina': float(str(player_row['Stamina']).split('\n')[0]),
            'Dribbling': float(str(player_row['Dribbling']).split('\n')[0]),
            'Short passing': float(str(player_row['Short passing']).split('\n')[0])
        }
        value = predict_player_value(input_data)
        input_data['Value'] = value
        st.session_state['current_player'] = input_data

    st.dataframe(
        top_10[['Full Name', 'Best position', 'Age', 'Potential', 'Stamina', 'Dribbling', 'Short passing', 'Score']])

# 招募功能
if 'current_player' in st.session_state and (mode == 'Choose Preset Player' or (
        mode == 'Create New Player' and 'Name' in st.session_state['current_player'] and
        st.session_state['current_player']['Name'].strip())):
    st.subheader("🧍‍♂️ Player to Recruit")
    display_df = pd.DataFrame([st.session_state['current_player']])
    display_df['Value'] = display_df['Value'].apply(lambda x: f"€{float(x):,.2f}" if isinstance(x, (int, float)) else x)
    st.write(display_df)

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

# 球队展示
st.subheader("⚽ Your Team")
if st.session_state['team']:
    df_team = pd.DataFrame(st.session_state['team'])

    st.write("### Your Current Squad")
    st.dataframe(df_team.style.format({"Value": lambda x: f"€{float(str(x).replace('€', '').replace(',', '')):,.2f}"}))
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

    total_value = sum([float(str(p['Value']).replace('€', '').replace(',', '')) for p in st.session_state['team']])
    st.markdown(f"**Total Team Value:** €{total_value:,.0f}")

    if 'confirm_final' not in st.session_state:
        if st.button("✅ Confirm Final Team"):
            st.session_state['confirm_final'] = True
            st.success("Team confirmed! You can no longer make changes.")
else:
    st.info("No players recruited yet.")

# 安全清理已招募球员记录
if st.session_state.get('recruited_this_round'):
    del st.session_state['current_player']
    del st.session_state['recruited_this_round']

# 重置按钮
if st.sidebar.button("🔁 Reset Game"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# 预算显示
st.sidebar.subheader("💰 Budget Left")
st.sidebar.write(f"€{st.session_state['budget']:,.0f}")
