# app.py

import streamlit as st
import pandas as pd
from prediction_model import predict_player_value

st.set_page_config(page_title="Player Value Estimator", layout="centered")
st.title("💰 Football Player Value Estimator")

# 用户输入
st.sidebar.header("📋 Player Info")
name = st.sidebar.text_input("Full Name")
age = st.sidebar.slider("Age", 16, 45, 24)
height = st.sidebar.number_input("Height (cm)", 150, 220, 180)
weight = st.sidebar.number_input("Weight (kg)", 50, 120, 75)
potential = st.sidebar.slider("Potential (0-100)", 40, 100, 80)
position = st.sidebar.selectbox("Best Position", ['ST', 'CM', 'CAM', 'CB', 'GK', 'LM', 'RM', 'RB', 'LB'])
stamina = st.sidebar.slider("Stamina", 20, 100, 70)
dribbling = st.sidebar.slider("Dribbling", 20, 100, 70)
short_passing = st.sidebar.slider("Short Passing", 20, 100, 70)

if st.button("Predict Market Value"):
    input_data = {
        'Age': age,
        'Height': height,
        'Weight': weight,
        'Potential': potential,
        'Best position': position,
        'Stamina': stamina,
        'Dribbling': dribbling,
        'Short passing': short_passing
    }
    value_prediction = predict_player_value(input_data)
    st.success(f"Estimated Market Value (log €): {value_prediction:.2f}")
