
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SIMEXTRACT – Yield Target Dashboard", layout="wide")

st.title("🧪 SIMEXTRACT – Predictive Yield Dashboard")
st.markdown("Test multiple scientific models to estimate process settings required to reach a target extraction yield.")

# Target yield input
target_yield = st.number_input("🎯 Define your target yield (%)", min_value=0.0, max_value=100.0, value=18.5, step=0.1)
st.markdown(f"#### Target Yield: **{target_yield} %**")

st.markdown("---")
st.subheader("🧬 General Process Parameters")

col1, col2 = st.columns(2)
with col1:
    material = st.selectbox("Raw Material", ["Lavender", "Rosemary", "Chamomile", "Date Seed", "Prickly Pear Seed"])
    compound = st.text_input("Compound to Extract", "Essential oil")
with col2:
    max_temp = st.slider("Max Allowed Temperature (°C)", 30, 80, 60)
    max_pressure = st.slider("Max Allowed Pressure (bar)", 100, 400, 300)

st.markdown("---")
st.subheader("🧠 Model Predictions to Reach Target Yield")

def model_standard(target):
    # Naive model estimation
    # Reverse-solving for a rough approximation (no real thermodynamics!)
    try:
        # Simulate required parameters to reach target yield (empirical, placeholder)
        flow = 5  # fixed for now
        time = 60  # minutes
        temp = round((target / 1000) * 360)  # fake inversion
        pressure = round((target * 18000) / (flow * time))
        co2_used = round(flow * (time / 60), 2)
        yield_pred = round(pressure * flow * time / 18000, 2)
        delta = abs(yield_pred - target)
        return {
            "Model": "Standard",
            "Yield Est. (%)": yield_pred,
            "Delta": delta,
            "Pressure (bar)": pressure,
            "Temperature (°C)": temp,
            "Flow (kg/h)": flow,
            "Time (min)": time,
            "dp (mm)": "—"
        }
    except:
        return None

def model_louaer(target):
    # Placeholder: fixed parameters that give ~18.5%
    P, T, dp = 0.5, 0.7, 0.2  # coded values
    R = (8.427 +
         0.682 * P +
         0.413 * T -
         3.078 * dp +
         0.653 * P * T -
         1.123 * P * dp +
         0.533 * T * dp -
         0.060 * P ** 2 +
         0.445 * T ** 2 +
         0.620 * dp ** 2)
    delta = abs(R - target)
    return {
        "Model": "Louaer",
        "Yield Est. (%)": round(R, 2),
        "Delta": round(delta, 2),
        "Pressure (bar)": "coded",
        "Temperature (°C)": "coded",
        "Flow (kg/h)": "—",
        "Time (min)": "—",
        "dp (mm)": dp
    }

def model_peng_robinson(target):
    # Placeholder for future model
    return {
        "Model": "Peng-Robinson (coming soon)",
        "Yield Est. (%)": "—",
        "Delta": "—",
        "Pressure (bar)": "—",
        "Temperature (°C)": "—",
        "Flow (kg/h)": "—",
        "Time (min)": "—",
        "dp (mm)": "—"
    }

results = [model_standard(target_yield),
           model_louaer(target_yield),
           model_peng_robinson(target_yield)]

df_results = pd.DataFrame(results)
st.dataframe(df_results, use_container_width=True)

st.markdown("#### 🧪 Dev Mode (Experimental)")
st.info("Here you will be able to inject custom models and compare their predictions.")
st.code("# def model_custom(target): ...", language="python")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2025 SIMEXTRACT Platform – Engineered by Alba Tunica Lab</p>", unsafe_allow_html=True)
