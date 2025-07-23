MODELES INTÉGRÉS DIRECTEMENT

import streamlit as st import pandas as pd

------------------ MODELES ------------------

def model_rsm(P, T, dp, flow, time, **kwargs): # Modèle simplifié RSM, exemple yield_rsm = 0.1 * P + 0.05 * T - 2 * dp + 0.3 * flow + 0.2 * time return max(yield_rsm, 0)

def model_sovova(P, T, dp, flow, time, **kwargs): # Modèle simplifié Sovova, exemple yield_sovova = 0.08 * P + 0.04 * T - 1.5 * dp + 0.25 * flow + 0.1 * time return max(yield_sovova, 0)

------------------ APP ------------------

st.set_page_config(page_title="SIMEXTRACT", layout="wide") st.title("🎯 Supercritical CO₂ Extraction Simulator")

st.sidebar.header("Simulation Settings") target_yield = st.sidebar.number_input("Target Yield (%)", value=18.5, step=0.1)

with st.sidebar.expander("⚙️ Show advanced factors"): dp = st.number_input("Particle Size (mm)", value=0.2) flow = st.number_input("CO₂ Flow Rate (kg/h)", value=5.0)

col1, col2, col3 = st.columns(3)

with col1: P = st.number_input("Pressure (bar)", value=150) with col2: T = st.number_input("Temperature (°C)", value=60) with col3: time = st.number_input("Extraction Time (min)", value=60)

------------------ CALCUL ------------------

if st.button("Run Simulation"): results = []

try:
    y_rsm = model_rsm(P, T, dp, flow, time)
    results.append({"Model": "RSM", "Estimated Yield (%)": round(y_rsm, 2), "Recommended P": P, "Recommended T": T})
except Exception as e:
    st.error(f"❌ Error RSM model: {e}")

try:
    y_sovova = model_sovova(P, T, dp, flow, time)
    results.append({"Model": "Sovova", "Estimated Yield (%)": round(y_sovova, 2), "Recommended P": P, "Recommended T": T})
except Exception as e:
    st.error(f"❌ Error Sovova model: {e}")

if results:
    st.subheader("📊 Model Predictions")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    csv = df_results.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results (CSV)", data=csv, file_name="simextract_results.csv", mime="text/csv")

