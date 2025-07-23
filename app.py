
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SIMEXTRACT – CO₂ Extraction Simulator", layout="wide")

st.title("🧪 SIMEXTRACT – CO₂ Extraction Simulator")
st.markdown("Developed by Alba Tunica Lab | Inspired by industrial & academic models")

tab1, tab2 = st.tabs(["📊 Standard Mode", "🧠 Expert Mode – Advanced Yield Estimation"])

# STANDARD MODE
with tab1:
    st.header("📊 Standard Simulation")
    material = st.selectbox("🌿 Raw Material", ["Lavender", "Rosemary", "Chamomile", "Date Seed", "Prickly Pear Seed"])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pressure = st.slider("Pressure (bar)", 50, 400, 150)
    with col2:
        temperature = st.slider("Temperature (°C)", 30, 80, 50)
    with col3:
        flow_rate = st.slider("CO₂ Flow Rate (kg/h)", 1, 10, 5)
    with col4:
        time = st.slider("Extraction Time (min)", 10, 180, 60)

    if st.button("▶️ Run Standard Simulation"):
        co2_used = round(flow_rate * (time / 60), 2)
        yield_estimate = round(pressure * flow_rate * time / 18000, 2) * 1000  # simple model
        cost = round(co2_used * 0.5, 2)

        st.success(f"Estimated Yield: {yield_estimate:.2f} g | CO₂ Used: {co2_used:.2f} kg | Cost: {cost:.2f} €")

        df_std = pd.DataFrame([{
            "Material": material,
            "Pressure (bar)": pressure,
            "Temperature (°C)": temperature,
            "Flow Rate (kg/h)": flow_rate,
            "Time (min)": time,
            "CO₂ Used (kg)": co2_used,
            "Yield (g)": yield_estimate,
            "Cost (€)": cost
        }])
        st.dataframe(df_std)
        csv_std = df_std.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv_std, "standard_mode_results.csv", "text/csv")

# EXPERT MODE
with tab2:
    st.header("🧠 Expert Mode – Advanced Yield Estimation")
    st.markdown("Inspired by Louaer et al. (2016) – Implemented by Alba Tunica Lab")
    st.latex(r'''
        R(\%) = 8.427 + 0.682P + 0.413T - 3.078dp + 0.653PT - 1.123Pd + 0.533Td
        - 0.060P^2 + 0.445T^2 + 0.620dp^2
    ''')

    with st.form("expert_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            P = st.number_input("Coded Pressure (P)", value=0.0, format="%.3f")
        with col2:
            T = st.number_input("Coded Temperature (T)", value=0.0, format="%.3f")
        with col3:
            dp = st.number_input("Coded Particle Diameter (dp)", value=0.0, format="%.3f")

        submitted = st.form_submit_button("▶️ Run Expert Simulation")

    if submitted:
        R = (8.427 +
             0.682 * P +
             0.413 * T -
             3.078 * dp +
             0.653 * P * T -
             1.123 * P * dp +
             0.533 * T * dp -
             0.060 * P ** 2 +
             0.445 * T ** 2 +
             0.620 * dp ** 2)
        R = round(R, 3)

        st.success(f"Estimated Yield (R%): {R} %")

        df_expert = pd.DataFrame([{
            "Coded Pressure (P)": P,
            "Coded Temperature (T)": T,
            "Coded Diameter (dp)": dp,
            "Estimated Yield (%)": R
        }])
        st.dataframe(df_expert)
        csv_exp = df_expert.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv_exp, "expert_mode_results.csv", "text/csv")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2025 SIMEXTRACT • Engineered by Alba Tunica Lab</p>", unsafe_allow_html=True)
