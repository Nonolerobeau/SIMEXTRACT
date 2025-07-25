import streamlit as st
import math

# --- FONCTION PRINCIPALE : Modèle Avancé ---
def calculate_advanced_yield(P, T, dp, F, t, compound='Tocopherol'):
    """
    Modèle avancé pour estimer le rendement d'extraction supercritique CO2.
    """
    Y_max_dict = {
        'Tocopherol': 20.0,
        'Beta-Carotene': 12.0,
        'Lycopene': 10.0,
        'Caffeine': 18.0,
        'Curcumin': 15.0
    }

    Y_max = Y_max_dict.get(compound, 15.0)  # par défaut

    alpha = 0.0005
    beta = 1.2
    gamma = 0.6
    delta = 0.4
    epsilon = 0.8

    try:
        k = alpha * (P ** beta) * (T ** gamma) * (F ** delta) / (dp ** epsilon)
        yield_percent = Y_max * (1 - math.exp(-k * t))
        return max(0.0, min(yield_percent, Y_max))

    except Exception as e:
        return f"Erreur de calcul : {str(e)}"


# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="SIMEXTRACT - Advanced Yield Model", layout="centered")
st.title("🧪 SIMEXTRACT – Estimation de rendement (modèle avancé)")

with st.form("param_form"):
    compound = st.selectbox("Composé à extraire :", [
        "Tocopherol", "Beta-Carotene", "Lycopene", "Caffeine", "Curcumin"
    ])
    P = st.slider("Pression (bar)", 100, 500, 250)
    T = st.slider("Température (°C)", 30, 80, 50)
    dp = st.number_input("Taille des particules (mm)", min_value=0.01, max_value=1.0, value=0.5)
    F = st.slider("Débit de CO₂ (kg/h)", 1, 60, 10)
    t = st.slider("Temps d'extraction (min)", 1, 240, 60)
    submitted = st.form_submit_button("Calculer le rendement")

if submitted:
    result = calculate_advanced_yield(P, T, dp, F, t, compound)
    if isinstance(result, float):
        st.success(f"🎯 Rendement estimé : {result:.2f} %")
    else:
        st.error(result)
