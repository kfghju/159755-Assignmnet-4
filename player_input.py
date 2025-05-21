# components/player_input.py

import streamlit as st
import pandas as pd
from prediction_model import predict_player_value

@st.cache_data
def load_players():
    df = pd.read_csv("data/players_stats.csv")
    return df[[
        'Full Name', 'Age', 'Height', 'Weight', 'Potential', 'Best position',
        'Stamina', 'Dribbling', 'Short passing'
    ]].dropna()

preset_df = load_players()
st.session_state['preset_df'] = preset_df


def handle_player_input(mode):
    filtered_df = preset_df.copy()

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

    elif mode == "Choose Preset Player":
        st.sidebar.header("📋 Choose Preset Player")
        search_name = st.sidebar.text_input("🔍 Search by name")

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
        input_data['Value'] = round(value, 2)
        st.session_state['current_player'] = input_data
        st.sidebar.success(f"Estimated Value: €{value:,.0f}")
