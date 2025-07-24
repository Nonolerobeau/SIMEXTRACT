
import streamlit as st
import pandas as pd
import numpy as np

# ---------- Physico-chemical models ----------

def co2_density_peng_robinson(P, T):
    return 0.001 * (P / (T + 273.15)) * 44  # g/cm3

def solubility(P, T, compound_coeff=1.0):
    rho = co2_density_peng_robinson(P, T)
    return compound_coeff * rho * 1000  # mg/g

def sovova_extraction_model(t, P, T, dp, flow, Y_max=22, compound_coeff=1.0, shape_factor=1.0):
    D_eff = 1e-6  # m2/s
    A_surf = 1 / dp  # mm^-1
    k_eff = D_eff * A_surf * (flow / 60) * shape_factor
    Y = Y_max * (1 - np.exp(-k_eff * t))
    return min(Y, Y_max)

# ---------- Streamlit Interface ----------

st.set_page_config(page_title="SIMEXTRACT", layout="wide")
st.title("🧪 SIMEXTRACT - CO₂ Extraction Simulator")
st.markdown("Optimisez vos extractions CO₂ avant de passer au laboratoire. Testez vos hypothèses, économisez votre matière première. 🎯")

# Sidebar configuration
st.sidebar.header("🧾 Paramètres d'extraction")

P = st.sidebar.slider("Pression (bar)", 50, 400, 250)
T = st.sidebar.slider("Température (°C)", 30, 100, 55)
dp = st.sidebar.slider("Taille particules (mm)", 0.1, 2.0, 0.3)
flow = st.sidebar.slider("Débit CO₂ (kg/h)", 1, 80, 5)
time = st.sidebar.slider("Temps d'extraction (min)", 5, 300, 60)
compound_coeff = st.sidebar.slider("Coefficient solubilité composé", 0.1, 2.0, 0.8)
shape_factor = st.sidebar.slider("Facteur géométrie du lit (0.6 = mauvais lit / 1.0 = idéal)", 0.6, 1.2, 0.85)

# Prediction
if st.button("▶️ Lancer la simulation"):
    Ymax = solubility(P, T, compound_coeff) / 100  # % max basé sur solubilité
    rendement = sovova_extraction_model(time, P, T, dp, flow, Y_max=Ymax, compound_coeff=compound_coeff, shape_factor=shape_factor)

    df = pd.DataFrame([{
        "Pression (bar)": P,
        "Température (°C)": T,
        "Granulométrie (mm)": dp,
        "Débit CO₂ (kg/h)": flow,
        "Temps (min)": time,
        "Rendement estimé (%)": round(rendement, 2)
    }])

    st.subheader("📊 Résultat de la simulation")
    st.dataframe(df)
    st.success(f"✅ Rendement estimé : {round(rendement, 2)} %")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger les résultats", data=csv, file_name="resultats_simextract.csv", mime="text/csv")
else:
    st.info("Configurez les paramètres à gauche et cliquez sur ▶️ pour lancer la simulation.")
