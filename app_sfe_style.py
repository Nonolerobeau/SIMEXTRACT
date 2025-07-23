
import streamlit as st
import pandas as pd

st.set_page_config(page_title="SIMEXTRACT – CO₂ Extraction", layout="wide")

# Header style
st.markdown("""
<style>
    .title-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .logo-placeholder {
        width: 100px;
        height: 60px;
        background-color: #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #777;
    }
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #2c3e50;
        border-bottom: 2px solid #ccc;
        margin-top: 20px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-header'>"
            "<div class='logo-placeholder'>LOGO</div>"
            "<h2>SIMEXTRACT – Supercritical CO₂ Extraction Tool</h2>"
            "</div>", unsafe_allow_html=True)

# Section: Raw Material (Plant)
st.markdown("<div class='section-title'>🌿 Raw Material (Plant)</div>", unsafe_allow_html=True)
plant = st.selectbox("Select plant material", ["Lavender", "Rosemary", "Chamomile", "Date Seed", "Prickly Pear Seed"])
st.text_input("Optional description", placeholder="Batch, origin, granulometry...")

# Section: Extraction Parameters
st.markdown("<div class='section-title'>⚙️ Extraction Parameters</div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    pressure = st.slider("Pressure (bar)", 50, 400, 150, step=10)
with col2:
    temperature = st.slider("Temperature (°C)", 30, 80, 50, step=5)
with col3:
    flow_rate = st.slider("CO₂ Flow Rate (kg/h)", 1, 10, 5)
with col4:
    time = st.slider("Extraction Time (min)", 10, 180, 60, step=10)

# Section: Target Extract
st.markdown("<div class='section-title'>💧 Target Compound</div>", unsafe_allow_html=True)
compound = st.text_input("Compound of interest (optional)", "Essential oil")
polarity = st.select_slider("Polarity", options=["Non-polar", "Low", "Medium", "High"], value="Low")
molar_mass = st.number_input("Estimated molar mass (g/mol)", min_value=100, max_value=1000, value=250)

# Run Simulation
st.markdown("<div class='section-title'>🔍 Simulation & Results</div>", unsafe_allow_html=True)

if st.button("▶️ Run Simulation"):
    co2_used = round(flow_rate * (time / 60), 2)
    yield_estimate = round(pressure * flow_rate * time / 18000, 2) * 1000  # fake model
    cost = round(co2_used * 0.5, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Estimated Yield", f"{yield_estimate:.2f} g")
    col2.metric("CO₂ Used", f"{co2_used:.2f} kg")
    col3.metric("Estimated Cost", f"{cost:.2f} €")

    df = pd.DataFrame([{
        "Plant": plant,
        "Compound": compound,
        "Pressure (bar)": pressure,
        "Temp (°C)": temperature,
        "Flow (kg/h)": flow_rate,
        "Time (min)": time,
        "Polarity": polarity,
        "Molar Mass": molar_mass,
        "CO₂ Used (kg)": co2_used,
        "Yield (g)": yield_estimate,
        "Cost (€)": cost
    }])

    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "simextract_results.csv", "text/csv")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>© 2025 SIMEXTRACT • Engineered by Alba Tunica Lab</p>",
            unsafe_allow_html=True)
