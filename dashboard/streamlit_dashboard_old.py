import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

API_URL = "http://localhost:8000/predict"

# --- Streamlit Config ---
st.set_page_config(
    page_title="Predictive Maintenance Dashboard", layout="wide")
st.title("🔧 Real-Time Predictive Maintenance (Simulated)")

# --- Simulate Sensor Stream ---


def simulate_sensor_data():
    temp = np.random.normal(70, 2)
    vib = np.random.normal(0.3, 0.05)
    pres = np.random.normal(1.2, 0.05)

    if np.random.rand() < 0.1:
        temp += np.random.uniform(10, 20)
        vib += np.random.uniform(0.2, 0.4)
        pres += np.random.uniform(0.2, 0.4)

    return temp, vib, pres


# --- Initialize Session State ---
if "data" not in st.session_state:
    st.session_state.data = []

# --- Display UI ---
placeholder = st.empty()

while True:
    temp, vib, pres = simulate_sensor_data()
    st.session_state.data.append((temp, vib, pres))

    # Keep only the last 10 timesteps
    if len(st.session_state.data) > 10:
        st.session_state.data = st.session_state.data[-10:]

    # Prepare window for prediction
    window = st.session_state.data
    df = pd.DataFrame(window, columns=["Temperature", "Vibration", "Pressure"])

    # Send to prediction API if enough data
    if len(window) == 10:
        payload = {
            "temperature": df["Temperature"].tolist(),
            "vibration": df["Vibration"].tolist(),
            "pressure": df["Pressure"].tolist()
        }
        try:
            response = requests.post(API_URL, json=payload)
            result = response.json()
            prediction = result.get("label", "Unknown")
            score = result.get("prediction", 0.0)
        except Exception as e:
            prediction = "API Error"
            score = str(e)
    else:
        prediction = "Waiting for data..."
        score = "-"

    # --- Display ---
    with placeholder.container():
        st.subheader("📊 Live Sensor Feed")
        st.line_chart(df)

        st.subheader("🔎 Prediction")
        st.metric(label="Status", value=prediction)
        st.metric(label="Anomaly Score", value=round(
            float(score), 3) if score != "-" else "-")

    time.sleep(1)
