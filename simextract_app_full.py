
import streamlit as st
import pandas as pd

st.set_page_config(page_title="SIMEXTRACT - CO₂ Extraction Simulator", layout="centered")

st.title("🧪 SIMEXTRACT - CO₂ Extraction Simulator")
st.markdown("Visualisez votre rendement estimé en extraction supercritique CO₂ en fonction des paramètres machine, de la géométrie de lit et du composé extrait.")

# 🔽 Composé à extraire
compound = st.selectbox("🧬 Composé à extraire", [
    "Tocophérol (Vitamine E)",
    "Bêta-Carotène",
    "Acide linoléique",
    "Acide palmitique",
    "Caféine",
    "Huile essentielle de Lavande",
    "Squalène",
    "Polyphénols",
    "Curcumine",
    "Lycopène",
    "Flavonoïdes",
    "Phytostérols",
    "Anthocyanes"
])

# 🏗️ Configuration extracteur
extractor = st.selectbox("🏗️ Configuration d'extracteur", [
    "SFE Process 2L – optimisé (80%)",
    "SFE Eden Labs – standard (60%)",
    "SFE Custom – haute pression (90%)"
])

# Paramètres opératoires
pressure = st.number_input("☀️ Pression (bar)", min_value=50, max_value=400, value=200)
temperature = st.number_input("🌡️ Température (°C)", min_value=35, max_value=80, value=60)
particle_size = st.number_input("⚪ Taille particules (mm)", min_value=0.1, max_value=1.5, step=0.1, value=0.5)
flow_rate = st.number_input("💨 Débit CO₂ (kg/h)", min_value=1.0, max_value=80.0, value=10.0)
extraction_time = st.number_input("⏱️ Temps d'extraction (min)", min_value=10, max_value=180, value=60)

# ⚠️ Alerte si les conditions dépassent certaines limites connues
warnings = []
if compound == "Bêta-Carotène" and temperature > 65:
    warnings.append("⚠️ La Bêta-Carotène est sensible à l'oxydation à haute température (> 65°C).")
if compound == "Polyphénols" and pressure < 120:
    warnings.append("⚠️ Une pression plus élevée (> 120 bar) est recommandée pour extraire les polyphénols.")
if compound == "Caféine" and temperature < 45:
    warnings.append("⚠️ Température basse : extraction de la caféine moins efficace en-dessous de 45°C.")

if warnings:
    st.warning("\n".join(warnings))

# 🔘 Lancer simulation
if st.button("▶️ Lancer la simulation"):
    estimated_yield = 0.0  # valeur temporaire
    if compound == "Tocophérol (Vitamine E)":
        estimated_yield = 8 + 0.05 * (pressure - 100) + 0.1 * (temperature - 40)
    elif compound == "Bêta-Carotène":
        estimated_yield = 5 + 0.04 * (pressure - 100) + 0.08 * (temperature - 40)
    elif compound == "Caféine":
        estimated_yield = 4 + 0.03 * (pressure - 90) + 0.07 * (temperature - 45)
    elif compound == "Huile essentielle de Lavande":
        estimated_yield = 3 + 0.06 * (pressure - 90) + 0.1 * (temperature - 40)
    else:
        estimated_yield = 2 + 0.02 * (pressure - 100) + 0.05 * (temperature - 40)

    estimated_yield = max(0.0, round(estimated_yield, 2))  # Pas de rendement négatif

    df = pd.DataFrame([{
        "Composé": compound,
        "Extracteur": extractor,
        "Pression (bar)": pressure,
        "Température (°C)": temperature,
        "Granulométrie (mm)": particle_size,
        "Débit CO₂ (kg/h)": flow_rate,
        "Temps (min)": extraction_time,
        "Rendement estimé (%)": estimated_yield
    }])

    st.subheader("📊 Résultat de la simulation")
    st.dataframe(df, use_container_width=True)
    st.success(f"✅ Rendement estimé : {estimated_yield} %")
    st.download_button("📥 Télécharger les résultats", data=df.to_csv(index=False), file_name="simulation_result.csv", mime="text/csv")
