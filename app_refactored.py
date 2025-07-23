
import streamlit as st
import pandas as pd

st.set_page_config(page_title="SIMEXTRACT", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: #2c3e50;'>🧪 SIMEXTRACT – CO₂ Supercritical Extraction Simulator</h1>",
    unsafe_allow_html=True
)

with st.expander("ℹ️ Instructions"):
    st.markdown("""
        - Sélectionnez une matière première (ex : Lavande, Romarin).
        - Ajustez les paramètres d’extraction selon vos hypothèses ou données expérimentales.
        - Cliquez sur **Run Simulation** pour voir le rendement estimé, le CO₂ utilisé et le coût.
    """)

# Input section
col1, col2 = st.columns(2)

with col1:
    material = st.text_input("🌿 Material", "Lavender")
    pressure = st.slider("🔵 Pressure (bar)", 50, 400, 150, step=10)
    temperature = st.slider("🌡️ Temperature (°C)", 30, 80, 50, step=5)

with col2:
    flow_rate = st.slider("💨 CO₂ Flow Rate (kg/h)", 1, 10, 5)
    time = st.slider("⏱️ Extraction Time (min)", 10, 180, 60, step=10)

if st.button("▶️ Run Simulation"):
    # Simulated calculations
    co2_used = round(flow_rate * (time / 60), 2)
    yield_estimate = round(pressure * flow_rate * time / 18000, 2) * 1000  # g
    cost = round(co2_used * 0.5, 2)  # € estimation

    st.success("✅ Simulation complete.")

    st.markdown("### 📊 Simulation Results")

    col_yield, col_co2, col_cost = st.columns(3)
    col_yield.metric("Estimated Yield", f"{yield_estimate:.2f} g")
    col_co2.metric("Total CO₂ Used", f"{co2_used:.2f} kg")
    col_cost.metric("Estimated Cost", f"{cost:.2f} €")

    # Display results table
    df = pd.DataFrame([{
        "Material": material,
        "Pressure (bar)": pressure,
        "Temperature (°C)": temperature,
        "Flow Rate (kg/h)": flow_rate,
        "Extraction Time (min)": time,
        "CO₂ Used (kg)": co2_used,
        "Yield (g)": yield_estimate,
        "Estimated Cost (€)": cost
    }])

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Results as CSV", csv, "simextract_results.csv", "text/csv")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>© 2025 SIMEXTRACT • Designed for Alba Tunica Lab</p>",
    unsafe_allow_html=True
)
