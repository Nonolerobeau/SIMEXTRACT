
import streamlit as st
import pandas as pd

# ------------------ Simulation UI ------------------
st.set_page_config(page_title="SIMEXTRACT", layout="wide")
st.title("🧪 SIMEXTRACT - CO₂ Supercritical Extraction Simulator")

st.sidebar.header("🎯 Target Yield")
target_yield = st.sidebar.number_input("Target Yield (%)", min_value=0.0, value=18.5)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Extraction Parameters")
P = st.sidebar.slider("Pressure (bar)", 50, 400, 150)
T = st.sidebar.slider("Temperature (°C)", 30, 100, 60)
dp = st.sidebar.slider("Particle Size (mm)", 0.1, 2.0, 0.2)
flow = st.sidebar.slider("CO₂ Flow Rate (kg/h)", 1, 80, 5)
time = st.sidebar.slider("Extraction Time (min)", 10, 300, 60)
material = st.sidebar.selectbox("Material", ["Date Seed", "Lavender", "Rosemary"])

# ------------------ Model Definitions ------------------
def model_rsm(P, T, dp, flow, time):
    # Hypothèse RSM simple : base polynomiale avec poids
    yield_est = (0.015 * P + 0.06 * T - 3.0 * dp + 0.25 * flow + 0.12 * time - 10)
    return min(max(round(yield_est, 2), 0), 100)

def model_sovova(P, T, dp, flow, time):
    # Approche simplifiée Sovová (cinétique de type logistique)
    k = 0.00012
    Y_max = 22.0  # Rendement max réaliste (%)
    try:
        yield_est = Y_max * (1 - (2.718 ** (-k * flow * time / (dp + 0.1))))
    except OverflowError:
        yield_est = Y_max
    return min(max(round(yield_est, 2), 0), Y_max)

# ------------------ Simulation Run ------------------
if st.button("▶️ Run Simulation"):
    rsm_result = model_rsm(P, T, dp, flow, time)
    sovova_result = model_sovova(P, T, dp, flow, time)

    df = pd.DataFrame([
        {"Model": "RSM", "Estimated Yield (%)": rsm_result, "Recommended P": P, "Recommended T": T},
        {"Model": "Sovova", "Estimated Yield (%)": sovova_result, "Recommended P": P, "Recommended T": T}
    ])

    st.subheader("📊 Model Predictions")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results", data=csv, file_name="simextract_results.csv", mime="text/csv")
else:
    st.info("Configure parameters and click ▶️ Run Simulation.")
