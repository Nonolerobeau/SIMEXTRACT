
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
st.markdown("Visualisez votre rendement estimé en extraction supercritique CO₂ en fonction des paramètres machine, de la géométrie de lit et du composé extrait.")

# Menu déroulant : composé extrait
compound_options = {
    "Acide oléique (lipide classique)": 1.0,
    "Limonène (terpène volatil)": 1.2,
    "Tocophérol (Vitamine E)": 0.6,
    "Caféine (soluble partiellement)": 0.5,
    "Polyphénols (très peu solubles)": 0.35
}
compound_choice = st.selectbox("🔬 Composé à extraire", list(compound_options.keys()))
compound_coeff = compound_options[compound_choice]

# Menu déroulant : extracteur
extractor_options = {
    "SFE Lab Mini – 0.5 L (remplissage 60%)": 0.65,
    "Skrlj 1L GMP – standard (70%)": 0.85,
    "SFE Process 2L – optimisé (80%)": 1.0,
    "Pilote 5L – surrempli (90%)": 1.1,
    "Extracteur artisanal – irrégulier (100%)": 0.5
}
extractor_choice = st.selectbox("🏗️ Configuration d'extracteur", list(extractor_options.keys()))
shape_factor = extractor_options[extractor_choice]

# Paramètres opératoires (menus simplifiés)
P = st.selectbox("🧭 Pression (bar)", [100, 150, 200, 250, 300])
T = st.selectbox("🌡️ Température (°C)", [40, 50, 60, 70, 80])
dp = st.selectbox("🔘 Taille particules (mm)", [0.1, 0.3, 0.5, 1.0])
flow = st.selectbox("💨 Débit CO₂ (kg/h)", [2, 5, 10, 20, 50])
time = st.selectbox("⏱️ Temps d'extraction (min)", [15, 30, 60, 120, 180])

# Prediction
if st.button("▶️ Lancer la simulation"):
    Ymax = solubility(P, T, compound_coeff) / 100  # % max basé sur solubilité
    rendement = sovova_extraction_model(time, P, T, dp, flow, Y_max=Ymax, compound_coeff=compound_coeff, shape_factor=shape_factor)

    df = pd.DataFrame([{
        "Composé": compound_choice,
        "Extracteur": extractor_choice,
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
    st.info("Sélectionnez les paramètres ci-dessus et cliquez sur ▶️ pour estimer le rendement.")
