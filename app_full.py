
import streamlit as st
import pandas as pd
import importlib
import os

st.set_page_config(page_title="SIMEXTRACT – CO₂ Yield Simulator", layout="wide")

st.title("🧪 SIMEXTRACT – CO₂ Supercritical Extraction Simulator")

st.markdown("This platform predicts extraction yield based on scientific or user-defined models, and suggests optimal process parameters.")

st.sidebar.header("🎯 Simulation Settings")
target_yield = st.sidebar.number_input("Target Yield (%)", 0.0, 100.0, 18.5, 0.1)

show_advanced = st.sidebar.checkbox("Show advanced factors", value=False)

st.markdown(f"### 🎯 Target Yield: **{target_yield} %**")

st.markdown("---")
st.subheader("🔬 Basic Process Inputs")

col1, col2 = st.columns(2)
with col1:
    P = st.number_input("Pressure (bar)", 100, 500, 300)
    T = st.number_input("Temperature (°C)", 30, 80, 60)
    dp = st.selectbox("Particle Size (mm)", [0.2, 0.3, 0.4, 0.5, 0.6])
with col2:
    flow = st.number_input("CO₂ Flow Rate (kg/h)", 1.0, 20.0, 5.0)
    time = st.number_input("Extraction Time (min)", 10, 300, 60)
    material = st.selectbox("Material", ["Date Seed", "Lavender", "Rosemary"])

# Advanced parameters
advanced_inputs = {}
if show_advanced:
    st.markdown("### ⚙️ Advanced Parameters")
    col3, col4 = st.columns(2)
    with col3:
        polarity = st.selectbox("Compound Polarity", ["Non-polar", "Slightly polar", "Polar"])
        mol_weight = st.number_input("Molecular Weight (g/mol)", 50, 1000, 282)
    with col4:
        pretreatment = st.checkbox("Pre-treated material (DIC, milling)")
        init_mass = st.number_input("Initial Mass (g)", 10, 500, 50)

    advanced_inputs = {
        "polarity": polarity,
        "mol_weight": mol_weight,
        "pretreatment": pretreatment,
        "init_mass": init_mass
    }

st.markdown("---")
st.subheader("📊 Model Predictions")

def load_models():
    model_dir = "models"
    results = []
    for file in os.listdir(model_dir):
        if file.startswith("model_") and file.endswith(".py"):
            modname = file[:-3]
            mod = importlib.import_module(f"models.{modname}")
            result = mod.predict(target_yield=target_yield, 
                                 P=P, T=T, dp=dp, flow=flow, time=time,
                                 material=material, **advanced_inputs)
            results.append(result)
    return results

try:
    model_results = load_models()
    df_results = pd.DataFrame(model_results)
    st.dataframe(df_results, use_container_width=True)
except Exception as e:
    st.error(f"Error loading models: {e}")

st.markdown("---")
st.subheader("🧪 Dev Mode – Upload Custom Model")
st.info("Developers can add models in the `/models/` directory. Each must implement a `predict()` function.")
st.code("""
def predict(target_yield: float, P, T, dp, flow, time, **kwargs):
    return {"Model": "MyModel", "Yield Est.": 18.4, "Pressure": P, "Temp": T}
""", language="python")
