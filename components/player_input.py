# components/player_input.py
import os

import streamlit as st
import pandas as pd
import sqlite3
from components.predict_player_value_model import predict_player_value


@st.cache_data
def load_players():
    base_path = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(base_path, '..', 'data', 'allData.sl3')
    conn = sqlite3.connect(database_path)
    df = pd.read_sql_query("select * from player_stats", conn)
    conn.close()
    df.rename(columns={
        'full_name': 'Full Name',
        'age': 'Age',
        'potential': 'Potential',
        'best_position': 'Best position',
        'short_passing': 'Short passing',
        'dribbling': 'Dribbling',
        'stamina': 'Stamina',
        'height_cm': 'Height',
        'weight_kg': 'Weight'
    }, inplace=True)

    return df[[
        'Full Name', 'Age', 'Height', 'Weight', 'Potential', 'Best position',
        'Stamina', 'Dribbling', 'Short passing', 'year'
    ]].dropna()


preset_df = load_players()


def handle_player_input(mode):
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
        filtered_df = preset_df.copy()
        filtered_df = filtered_df[filtered_df['year'] == '2025']
        if position_filter:
            filtered_df = filtered_df[filtered_df['Best position'].isin(position_filter)]
        if search_name:
            filtered_df = filtered_df[filtered_df['Full Name'].str.contains(search_name, case=False)]
        st.sidebar.markdown(f"Available Preset Players: **{len(filtered_df['Full Name'].unique())}**")

        # Recommended top 10 players (sorted by potential)
        filtered_df['Potential'] = pd.to_numeric(filtered_df['Potential'], errors='coerce')
        recommended_df = filtered_df.sort_values(by='Potential', ascending=False).head(10)
        st.markdown("Top 10 Recommended Players")
        st.dataframe(recommended_df[['Full Name', 'Age', 'Potential', 'Stamina', 'Dribbling', 'Short passing']])
        selected = st.radio("Choose Recommended Players", recommended_df['Full Name'].tolist(), index=0)
        player_row = recommended_df[recommended_df['Full Name'] == selected].iloc[0]
        input_data = {
            'Name': player_row['Full Name'],
            'Age': player_row['Age'],
            'Height': int(float(str(player_row['Height']).strip())),
            'Weight': int(float(str(player_row['Weight']).strip())),
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
