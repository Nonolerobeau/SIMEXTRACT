
import streamlit as st
import pandas as pd

# Seuils critiques par composé (exemple simplifié)
compound_criteria = {
    "Tocophérol (Vitamine E)": {
        "Température_max": 60,
        "Pression_min": 150,
        "Granulométrie_min": 0.3,
        "Granulométrie_max": 0.5
    },
    "Bêta-Carotène": {
        "Température_max": 70,
        "Pression_min": 200,
        "Granulométrie_min": 0.2,
        "Granulométrie_max": 0.4
    }
}

def check_parameters(compound, T, P, dp):
    messages = []
    seuils = compound_criteria.get(compound)
    if not seuils:
        return []

    if T > seuils["Température_max"]:
        messages.append(f"⚠️ La température dépasse le seuil recommandé pour {compound} ({seuils['Température_max']} °C).")
    if P < seuils["Pression_min"]:
        messages.append(f"⚠️ La pression est trop faible pour {compound} (minimum recommandé : {seuils['Pression_min']} bar).")
    if not (seuils["Granulométrie_min"] <= dp <= seuils["Granulométrie_max"]):
        messages.append(f"⚠️ La taille de particule {dp} mm est hors de la plage recommandée ({seuils['Granulométrie_min']}–{seuils['Granulométrie_max']} mm).")

    return messages

# UI
st.set_page_config(page_title="SIMEXTRACT", layout="centered")

st.title("🧪 SIMEXTRACT - CO₂ Extraction Simulator")

compound = st.selectbox("🧬 Composé à extraire", list(compound_criteria.keys()))
extractor = st.selectbox("🏭 Configuration d'extracteur", ["SFE Process 2L – optimisé (80%)"])
P = st.number_input("💥 Pression (bar)", 100, 400, 200)
T = st.number_input("🌡️ Température (°C)", 20, 80, 60)
dp = st.number_input("🔘 Taille particules (mm)", 0.1, 2.0, 0.5)
flow = st.number_input("💨 Débit CO₂ (kg/h)", 1, 20, 10)
time = st.number_input("⏱️ Temps d'extraction (min)", 10, 240, 60)

if st.button("▶️ Lancer la simulation"):
    st.subheader("📋 Résultat de la simulation")

    # Appel au modèle fictif
    est_yield = 18.5  # valeur fixe pour test

    st.success(f"✅ Rendement estimé : {est_yield} %")

    # Affichage des paramètres
    df = pd.DataFrame([{
        "Composé": compound,
        "Extracteur": extractor,
        "Pression (bar)": P,
        "Température (°C)": T,
        "Granulométrie (mm)": dp,
        "Débit CO₂ (kg/h)": flow,
        "Temps (min)": time,
        "Rendement estimé (%)": est_yield
    }])
    st.dataframe(df)

    # Warnings intelligents
    st.subheader("⚠️ Avertissements potentiels")
    warnings = check_parameters(compound, T, P, dp)
    if warnings:
        for msg in warnings:
            st.warning(msg)
    else:
        st.info("✅ Tous les paramètres sont dans les plages recommandées.")

