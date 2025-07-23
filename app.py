import streamlit as st
import pandas as pd
from models import model_rsm, model_sovova

st.set_page_config(page_title="SIMEXTRACT", layout="wide")
st.title("🧪 Supercritical CO₂ Extraction Simulator")

# Sidebar – Simulation Settings
st.sidebar.header("🎯 Simulation Settings")
target_yield = st.sidebar.number_input("Target Yield (%)", min_value=0.0, max_value=100.0, value=18.5, step=0.1)
show_advanced = st.sidebar.checkbox("Show advanced factors")

# Main – Input Parameters
col1, col2 = st.columns(2)

with col1:
    T = st.number_input("Temperature (°C)", min_value=10, max_value=100, value=60)
    dp = st.number_input("Particle Size (mm)", min_value=0.1, max_value=5.0, value=0.2, step=0.1)
with col2:
    time = st.number_input("Extraction Time (min)", min_value=10, max_value=300, value=60)
    material = st.selectbox("Material", ["Date Seed", "Lavender", "Rosemary"])

if show_advanced:
    with st.expander("Advanced Parameters"):
        P = st.slider("Pressure (bar)", min_value=50, max_value=400, value=150)
        flow = st.slider("CO₂ Flow Rate (kg/h)", min_value=1, max_value=80, value=10)
else:
    P = 150
    flow = 10

# Run models and display predictions
st.subheader("📊 Model Predictions")

results = []

try:
    rsm_output = model_rsm.predict(target_yield, P, T, dp, flow, time)
    results.append(rsm_output)
except Exception as e:
    st.error(f"Error running RSM model: {e}")

try:
    sovova_output = model_sovova.predict(target_yield, P, T, dp, flow, time)
    results.append(sovova_output)
except Exception as e:
    st.error(f"Error running Sovová model: {e}")

if results:
    df = pd.DataFrame(results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📅 Download Results", data=csv, file_name="simextract_results.csv", mime="text/csv")
else:
    st.info("No results to show yet.")

