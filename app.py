import streamlit as st
import math

# --- FONCTION PRINCIPALE ---
def calculate_advanced_yield(P, T, dp, F, t, compound='Tocopherol'):
    Y_max_dict = {
        'Tocopherol': 20.0,
        'Beta-Carotene': 12.0,
        'Lycopene': 10.0,
        'Caffeine': 18.0,
        'Curcumin': 15.0
    }

    Y_max = Y_max_dict.get(compound, 15.0)

    alpha = 0.0005
    beta = 1.2
    gamma = 0.6
    delta = 0.4
    epsilon = 0.8

    try:
        k = alpha * (P ** beta) * (T ** gamma) * (F ** delta) / (dp ** epsilon)
        rendement = Y_max * (1 - math.exp(-k * t))
        return round(max(0.0, min(rendement, Y_max)), 4)
    except Exception as e:
        return f"Erreur de calcul : {str(e)}"

# --- INTERFACE UTILISATEUR ---
st.set_page_config(page_title="SIMEXTRACT - Rendement CO₂", layout="centered")
st.title("🧪 SIMEXTRACT – Estimation du rendement d'extraction CO₂")

with st.form("formulaire_rendement"):
    compound = st.selectbox("Molécule à extraire :", [
        "Tocopherol", "Beta-Carotene", "Lycopene", "Caffeine", "Curcumin"
    ])
    P = st.slider("Pression (bar)", min_value=100, max_value=500, value=250)
    T = st.slider("Température (°C)", min_value=30, max_value=80, value=50)
    dp = st.number_input("Taille des particules (mm)", min_value=0.01, max_value=1.0, value=0.5)
    F = st.slider("Débit de CO₂ (kg/h)", min_value=1, max_value=60, value=10)
    t = st.slider("Temps d'extraction (min)", min_value=1, max_value=240, value=60)
    bouton_calcul = st.form_submit_button("Calculer le rendement")

if bouton_calcul:
    resultat = calculate_advanced_yield(P, T, dp, F, t, compound)
    if isinstance(resultat, float):
        st.success(f"🎯 Rendement estimé : {resultat:.2f} %")
    else:
        st.error(resultat)
