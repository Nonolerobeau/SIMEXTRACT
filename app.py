import streamlit as st
import pandas as pd
import numpy as np


-------------------------

MODELES INTÉGRÉS DIRECTEMENT

-------------------------

def rsm_model(P, T, dp, flow, time): # Coefficients fictifs (à remplacer par calibration réelle) yield_est = 0.01 * P + 0.05 * T - 0.2 * dp + 0.3 * flow + 0.1 * time return { "Model": "RSM", "Estimated Yield (%)": round(yield_est, 2), "Recommended P (bar)": P, "Recommended T (C)": T }

def sovova_model(P, T, dp, flow, time): # Formule simplifiée inspirée de Sovová yield_est = 0.008 * P + 0.04 * T - 0.1 * dp + 0.25 * flow + 0.08 * time return { "Model": "Sovova", "Estimated Yield (%)": round(yield_est, 2), "Recommended P (bar)": P, "Recommended T (C)": T }

-------------------------

INTERFACE STREAMLIT

-------------------------

st.set_page_config(page_title="SIMEXTRACT", layout="wide") st.title("🧪 SIMEXTRACT - CO₂ Supercritical Extraction Simulator")

with st.sidebar: st.header("🎯 Simulation Settings") target_yield = st.number_input("Target Yield (%)", min_value=0.0, value=18.5) show_advanced = st.checkbox("Show advanced factors")

st.divider()
st.markdown("#### 📦 Parameters")
T = st.number_input("Temperature (C)", value=60)
time = st.number_input("Extraction Time (min)", value=60)
dp = st.number_input("Particle Size (mm)", value=0.2)
material = st.selectbox("Material", ["Date Seed", "Lavender", "Custom"])

if show_advanced:
    P = st.slider("Pressure (bar)", 100, 400, 150)
    flow = st.slider("CO₂ Flow Rate (kg/h)", 1, 30, 10)
else:
    P = 150
    flow = 10

if st.button("Run Simulation"): results = []

# Appliquer chaque modèle
for model_func in [rsm_model, sovova_model]:
    res = model_func(P, T, dp, flow, time)
    results.append(res)

df = pd.DataFrame(results)

st.subheader("📊 Model Predictions")
st.dataframe(df, use_container_width=True)

st.download_button("📥 Download Results (CSV)", data=df.to_csv(index=False), file_name="simextract_results.csv")

else: st.info("Click 'Run Simulation' to get model predictions.")
