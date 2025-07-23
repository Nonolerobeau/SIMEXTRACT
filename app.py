
import streamlit as st
import pandas as pd

# 🎯 Simulation Settings
st.sidebar.header("🎯 Simulation Settings")
target_yield = st.sidebar.number_input("Target Yield (%)", min_value=0.0, max_value=100.0, value=18.5)

# 🧪 Main Input Parameters
st.title("CO₂ Yield Simulation App")
st.subheader("Input Parameters")
col1, col2 = st.columns(2)
with col1:
    temperature = st.number_input("Temperature (°C)", value=60)
    particle_size = st.number_input("Particle Size (mm)", value=0.2)
with col2:
    time = st.number_input("Extraction Time (min)", value=60)
    material = st.selectbox("Material", ["Date Seed", "Lavender", "Rosemary"])

# 📊 Modèle RSM intégré
def model_rsm(target_yield, P, T, dp, flow, time, **kwargs):
    a, b, c = 0.02, 0.03, 5
    yield_est = round(a * P + b * T + c, 2)
    return {
        "Model": "RSM",
        "Estimated Yield (%)": min(yield_est, 100),
        "Recommended P (bar)": P,
        "Recommended T (°C)": T
    }

# 📊 Modèle Sovova corrigé
def model_sovova(target_yield, P, T, dp, flow, time, **kwargs):
    k = 0.0001  # Facteur corrigé réaliste
    yield_est = k * P * T * time / (dp + 1)
    yield_est = min(yield_est, 100)
    return {
        "Model": "Sovova",
        "Estimated Yield (%)": round(yield_est, 2),
        "Recommended P (bar)": P,
        "Recommended T (°C)": T
    }

# ▶️ Run Simulation
if st.button("Run Simulation"):
    models = [model_rsm, model_sovova]
    results = []
    for model in models:
        try:
            result = model(target_yield, 150, temperature, particle_size, 5, time)
            if result["Estimated Yield (%)"] > 100:
                st.warning(f"⚠️ Warning: {result['Model']} predicts unrealistic yield >100%. Check your parameters.")
            results.append(result)
        except Exception as e:
            st.error(f"Error running {model.__name__}: {e}")

    if results:
        df = pd.DataFrame(results)
        st.subheader("📈 Model Predictions")
        st.dataframe(df)
        st.download_button("📥 Download Results (CSV)", data=df.to_csv(index=False), file_name="predictions.csv", mime="text/csv")
