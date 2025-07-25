import streamlit as st
import math

Y_max_dict = {
    'Tocopherol': 20.0,
    'Beta-Carotene': 12.0,
    'Lycopene': 10.0,
    'Caffeine': 18.0,
    'Curcumin': 15.0,
    'Thymol': 6.0,
    'Squalene': 14.0,
    'Chlorophyll': 8.5,
    'Rosmarinic Acid': 7.0,
    'Capsaicin': 11.0,
    'Linalool': 5.0,
    'Geraniol': 5.5,
    'Eugenol': 9.0,
    'Carvacrol': 6.8,
    'Menthol': 7.2
}

def calculate_balanced_yield(P, T, dp, F, t, compound='Tocopherol'):
    Y_max = Y_max_dict.get(compound, 15.0)

    P_crit = 74.0
    T_crit = 31.1
    F_ref = 10.0
    alpha = 0.015

    T_seuil = 65.0
    beta = 0.08

    try:
        k = alpha * ((P / P_crit) ** 0.8) * ((T / T_crit) ** 0.4) * ((F / F_ref) ** 0.2) * (1 / (dp ** 0.5))
        f_T = 1.0 if T <= T_seuil else math.exp(-beta * (T - T_seuil))
        rendement = Y_max * (1 - math.exp(-k * t)) * f_T
        return round(max(0.0, min(rendement, Y_max)), 4), k, f_T
    except Exception as e:
        return f"Erreur de calcul : {str(e)}", None, None

st.set_page_config(page_title="SIMEXTRACT - Modèle équilibré", layout="centered")
st.title("🧪 SIMEXTRACT – Estimation de rendement CO₂ (modèle avec facteur thermique)")

with st.form("formulaire_rendement"):
    compound = st.selectbox("Molécule à extraire :", list(Y_max_dict.keys()))
    P = st.slider("Pression (bar)", min_value=100, max_value=500, value=250)
    T = st.slider("Température (°C)", min_value=30, max_value=80, value=50)
    dp = st.number_input("Taille des particules (mm)", min_value=0.01, max_value=1.0, value=0.5)
    F = st.slider("Débit de CO₂ (kg/h)", min_value=1, max_value=60, value=10)
    t = st.slider("Temps d'extraction (min)", min_value=1, max_value=240, value=60)
    bouton_calcul = st.form_submit_button("Calculer le rendement")

if bouton_calcul:
    resultat, k_val, f_T_val = calculate_balanced_yield(P, T, dp, F, t, compound)
    if isinstance(resultat, float):
        st.success(f"🎯 Rendement estimé : {resultat:.2f} %")
        st.info(f"🔍 Coefficient cinétique k = {k_val:.4f} min⁻¹")
        if f_T_val < 1.0:
            st.warning(f"⚠️ Rendement pénalisé par la température : facteur thermique f_T = {f_T_val:.3f}")
    else:
        st.error(resultat)
