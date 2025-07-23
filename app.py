import streamlit as st
import pandas as pd

# 🎯 Sidebar : Objectif de rendement
st.sidebar.header("🎯 Simulation Settings")
target_yield = st.sidebar.number_input("Target Yield (%)", min_value=0.0, max_value=100.0, value=18.5, step=0.1)

# 📦 Paramètres utilisateur
st.title("🧪 Supercritical CO₂ Extraction - SIMEXTRACT")

col1, col2 = st.columns(2)
with col1:
    T = st.number_input("Temperature (°C)", 30, 100, value=60)
    dp = st.number_input("Particle Size (mm)", 0.1, 5.0, value=0.2, step=0.1)
with col2:
    time = st.number_input("Extraction Time (min)", 10, 180, value=60)
    material = st.selectbox("Material", ["Date Seed", "Lavender", "Chamomile"])

flow = st.slider("CO₂ Flow Rate (kg/h)", 1, 10, value=5)
pressure = st.slider("Pressure (bar)", 50, 400, value=150)

# 📊 Modèle RSM
def model_rsm(P, T, dp, flow, time):
    yield_rsm = 0.02 * P + 0.5 * T - 5 * dp + 2 * flow + 0.1 * time
    return round(yield_rsm, 2)

# 📊 Modèle Sovova simplifié
def model_sovova(P, T, dp, flow, time):
    yield_sovova = 0.01 * P + 0.3 * T - 4 * dp + 1.5 * flow + 0.15 * time
    return round(yield_sovova, 2)

# ▶️ Simulation
if st.button("Run Simulation"):
    results = [
        {"Model": "RSM", "Estimated Yield (%)": model_rsm(pressure, T, dp, flow, time), "Recommended P (bar)": pressure, "Recommended T (°C)": T},
        {"Model": "Sovova", "Estimated Yield (%)": model_sovova(pressure, T, dp, flow, time), "Recommended P (bar)": pressure, "Recommended T (°C)": T},
    ]
    st.subheader("📈 Model Predictions")
    df = pd.DataFrame(results)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results (CSV)", csv, "simulation_results.csv", "text/csv")
    
