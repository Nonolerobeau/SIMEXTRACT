
import streamlit as st
import pandas as pd
import math

# Import des modules de modèles
from models import model_rsm, model_sovova

st.set_page_config(page_title="SIMEXTRACT", layout="wide")
st.title("SIMEXTRACT – Estimation de rendement d'extraction au CO₂")

st.markdown(
    "Entrez les paramètres d'extraction et le **rendement cible** souhaité.\n"
    "L'application calcule le rendement estimé selon deux modèles : **RSM** et **Sovová**,\n"
    "et vous propose les ajustements nécessaires pour l'atteindre."
)

# Entrées utilisateur
target_yield = st.number_input("🎯 Rendement cible (%)", 0.0, 100.0, 10.0, 1.0)
P = st.number_input("🧪 Pression (bar)", 1.0, 1000.0, 200.0)
T_celsius = st.number_input("🌡️ Température (°C)", 0.0, 300.0, 50.0)
dp = st.number_input("🔹 Taille des particules (mm)", 0.1, 10.0, 0.6)
t = st.number_input("⏱️ Durée d'extraction (min)", 0.0, 300.0, 60.0)

T_kelvin = T_celsius + 273.15

# Calculs modèles
rsm_yield = model_rsm.predict_yield(P, T_kelvin, dp)
sov_yield = model_sovova.predict_yield(P, T_celsius, dp, t)

# Suggestions
Y_MAX = model_sovova.Y_MAX
suggestion_rsm = "✅ Rendement cible atteint." if rsm_yield >= target_yield else "🔧 Augmenter pression / réduire granulométrie."
if target_yield > Y_MAX:
    suggestion_sov = f"⚠️ Cible irréaliste (> {Y_MAX}%)."
else:
    if sov_yield >= target_yield:
        suggestion_sov = "✅ Cible atteinte dans le temps imparti."
    else:
        k = 0.005 * (P / 200.0) * ((0.6 / dp) ** 2)
        time_needed = -math.log(1 - (target_yield / Y_MAX)) / k if k > 0 and (target_yield / Y_MAX) < 1 else float("inf")
        suggestion_sov = f"⏱️ Allonger le temps à ~{int(time_needed)} min." if time_needed < float("inf") else "⚠️ Objectif inatteignable dans ce contexte."

# Affichage résultats
st.subheader("📊 Résultats")

results = [
    {"Modèle": "RSM", "Rendement estimé (%)": round(rsm_yield, 2), "Suggestion": suggestion_rsm},
    {"Modèle": "Sovová", "Rendement estimé (%)": round(sov_yield, 2), "Suggestion": suggestion_sov}
]

df = pd.DataFrame(results).set_index("Modèle")
st.table(df)
