import streamlit as st

st.set_page_config(page_title="CO₂ Supercritical Extraction Sim")
st.title("Supercritical CO₂ Extraction Simulation")

st.markdown("Simulate your extraction process by choosing parameters below.")

material = st.text_input("Material (e.g. Lavender, Rosemary)", "Lavender")
pressure = st.slider("Pressure (bar)", 50, 400, 150)
temperature = st.slider("Temperature (°C)", 30, 80, 50)
flow_rate = st.slider("CO₂ Flow Rate (kg/h)", 1, 10, 5)
time = st.slider("Extraction Time (min)", 10, 180, 60)

if st.button("Run Simulation"):
    yield_estimate = round((pressure * flow_rate * time) / (temperature * 100), 2)
    st.success(f"Estimated yield for {material}: {yield_estimate} g")
