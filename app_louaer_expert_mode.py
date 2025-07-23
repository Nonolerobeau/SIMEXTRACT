
import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="SIMEXTRACT – Expert Mode", layout="wide")

st.title("🔬 SIMEXTRACT – Expert Mode: Mehdi Louaer Model")
st.markdown("Based on the quadratic response surface model described in the PhD thesis of Mehdi Louaer (2016).")

st.markdown("### 📌 Model Equation (decoded variables)")
st.latex(r'''
R(\%) = 8.427 + 0.682P + 0.413T - 3.078dp + 0.653PT - 1.123Pd + 0.533Td
- 0.060P^2 + 0.445T^2 + 0.620dp^2
''')

# Input block
with st.form("louaer_form"):
    st.subheader("Enter your process parameters:")
    col1, col2, col3 = st.columns(3)
    with col1:
        P = st.number_input("Pressure P (coded units)", value=0.0, format="%.3f")
    with col2:
        T = st.number_input("Temperature T (coded units)", value=0.0, format="%.3f")
    with col3:
        dp = st.number_input("Particle diameter dp (coded units)", value=0.0, format="%.3f")

    submitted = st.form_submit_button("▶️ Estimate Yield")

if submitted:
    # Apply the model equation from the thesis
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

    st.success(f"📈 Estimated extraction yield: **{R} %**")

    # Optional: summary
    df = pd.DataFrame([{
        "Pressure (P)": P,
        "Temperature (T)": T,
        "Particle Diameter (dp)": dp,
        "Estimated Yield (%)": R
    }])
    st.markdown("### 🧾 Summary Table")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "louaer_model_results.csv", "text/csv")
