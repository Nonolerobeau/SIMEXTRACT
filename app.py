
import math
import streamlit as st

# --- Données composés ---
COMPOUNDS = {
    "Tocopherol": {"Y_max": 20.0, "T_seuil": 65, "note": "thermolabile modéré"},
    "Beta-Carotene": {"Y_max": 12.0, "T_seuil": 55, "note": "très thermolabile"},
    "Lycopene": {"Y_max": 10.0, "T_seuil": 55, "note": "thermolabile"},
    "Caffeine": {"Y_max": 18.0, "T_seuil": 80, "note": "stable"},
    "Curcumin": {"Y_max": 15.0, "T_seuil": 65, "note": "sensible oxydation"}
}

# --- Constantes ---
P_REF, T_REF_K, F_REF, DP_REF = 200.0, 313.15, 50.0, 0.6
ALPHA, A_EXP, B_EXP, C_EXP, D_EXP = 0.02, 1.1, 0.6, 0.35, 1.0
BETA_THERM = 0.04

# --- Facteur thermique ---
def thermal_penalty(T_c, T_seuil):
    return 1.0 if T_c <= T_seuil else math.exp(-BETA_THERM * (T_c - T_seuil))

# --- Facteur humidité ---
def moisture_penalty(moist_pct):
    return 1.0 - (moist_pct / 100.0) * 0.3  # pénalité simple

# --- Facteur granulométrie ---
def particle_penalty(dp_mm):
    if dp_mm < 0.1:
        return 0.7  # compactage
    return 1.0

# --- Peng–Robinson simplifié pour densité CO₂ ---
def co2_density_peng_robinson(P_bar, T_c):
    # Approximation rapide (valeurs typiques pour CO₂)
    T_k = T_c + 273.15
    rho_ref = 900  # kg/m3 approx à 300 bar, 40°C
    adj_p = (P_bar / 300.0)
    adj_t = 1 - (T_c - 40) * 0.002
    return max(rho_ref * adj_p * adj_t, 200)

# --- Coefficient cinétique ---
def k_effective(P_bar, T_c, F_g_min, dp_mm, moist_pct, cosolv_frac):
    dens = co2_density_peng_robinson(P_bar, T_c) / 900
    k = (
        ALPHA
        * (P_bar / P_REF) ** A_EXP
        * ((T_c + 273.15) / T_REF_K) ** B_EXP
        * (F_g_min / F_REF) ** C_EXP
        * (DP_REF / dp_mm) ** D_EXP
        * dens
        * moisture_penalty(moist_pct)
        * particle_penalty(dp_mm)
        * (1 + cosolv_frac * 0.5)
    )
    return max(k, 0.0)

# --- Rendement ---
def yield_percent(compound, P_bar, T_c, F_g_min, dp_mm, t_min, moist_pct, cosolv_frac):
    spec = COMPOUNDS[compound]
    Y_max = spec["Y_max"]
    fT = thermal_penalty(T_c, spec["T_seuil"])
    k = k_effective(P_bar, T_c, F_g_min, dp_mm, moist_pct, cosolv_frac)
    t_h = t_min / 60.0
    Y = Y_max * (1 - math.exp(-k * t_h)) * fT
    return max(0.0, min(Y, Y_max)), k, fT

# --- UI Streamlit ---
st.title("SIMEXTRACT – Modèle scientifique CO₂")

compound = st.selectbox("Composé", COMPOUNDS.keys())
P_bar = st.slider("Pression (bar)", 50, 400, 200)
T_c = st.slider("Température (°C)", 20, 100, 50)
F_g_min = st.slider("Débit CO₂ (g/min)", 5, 200, 50)
dp_mm = st.slider("Taille particule (mm)", 0.05, 1.5, 0.6)
moist_pct = st.slider("Humidité matière (%)", 0, 30, 10)
cosolv_frac = st.slider("Fraction EtOH co-solvant (%)", 0, 20, 0) / 100.0
t_min = st.slider("Temps extraction (min)", 5, 360, 90)

if st.button("Calculer rendement"):
    Y, k_val, fT = yield_percent(compound, P_bar, T_c, F_g_min, dp_mm, t_min, moist_pct, cosolv_frac)
    st.success(f"Rendement estimé : {Y:.2f} %")
    st.write(f"Coefficient k : {k_val:.4f} min⁻¹")
    st.write(f"Facteur thermique f_T : {fT:.3f}")
    st.write(f"Densité CO₂ estimée : {co2_density_peng_robinson(P_bar, T_c):.1f} kg/m³")
