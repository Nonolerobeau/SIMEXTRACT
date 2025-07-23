import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Supercritical CO₂ Extraction Simulator", layout="centered")

st.title("Supercritical CO₂ Extraction Simulation")
st.markdown("Simulate your extraction process by choosing parameters below.")

# Input fields
material = st.text_input("Material (e.g. Lavender, Rosemary)", value="Lavender")

pressure = st.slider("Pressure (bar)", min_value=50, max_value=400, value=150)
temperature = st.slider("Temperature (°C)", min_value=30, max_value=80, value=50)
flow_rate = st.slider("CO₂ Flow Rate (kg/h)", min_value=1, max_value=10, value=5)
extraction_time = st.slider("Extraction Time (min)", min_value=10, max_value=180, value=60)

# Calculations
if st.button("Run Simulation"):
    st.subheader("Simulation Results")

    # Estimations
    total_CO2 = flow_rate * (extraction_time / 60)
    yield_percentage = np.clip((pressure * 0.02 + temperature * 0.1) / 10, 0, 1)
    estimated_yield_g = yield_percentage * 1000  # 1000 g input material assumed
    cost_per_kg_CO2 = 0.5  # €/kg
    estimated_cost = total_CO2 * cost_per_kg_CO2

    # Display results
    st.markdown(f"🧪 **Estimated Yield**: `{estimated_yield_g:.2f} g`")
    st.markdown(f"🌬️ **Total CO₂ Used**: `{total_CO2:.2f} kg`")
    st.markdown(f"💰 **Estimated Cost**: `{estimated_cost:.2f} €`")

    # Table for export
    results = pd.DataFrame({
        "Material": [material],
        "Pressure (bar)": [pressure],
        "Temperature (°C)": [temperature],
        "Flow Rate (kg/h)": [flow_rate],
        "Extraction Time (min)": [extraction_time],
        "CO₂ Used (kg)": [total_CO2],
        "Yield (g)": [estimated_yield_g],
        "Estimated Cost (€)": [estimated_cost]
    })

    st.dataframe(results)

    # Download button
    csv = results.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Download Results (CSV)", data=csv, file_name="extraction_results.csv", mime="text/csv")
    
