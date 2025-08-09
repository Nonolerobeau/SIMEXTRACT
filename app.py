import math
import numpy as np
import pandas as pd
import streamlit as st

# =========================
# Helpers num & physique
# =========================

def clamp(x, xmin, xmax):
    return max(xmin, min(xmax, x))

def celsius_to_kelvin(Tc):
    return Tc + 273.15

# ----------------------------------------------------
# Peng–Robinson EOS (pure CO2) -> density [kg/m3]
# ----------------------------------------------------
# PR parameters for CO2:
# Critical properties:
# Tc = 304.1282 K; Pc = 7.3773 MPa; ω = 0.22394; M = 44.0095 g/mol
# Source values are standard; good enough for engineering calcs.
PR_CO2 = {
    "Tc": 304.1282,        # K
    "Pc": 7.3773e6,        # Pa
    "omega": 0.22394,
    "R": 8.314462618,      # J/mol/K
    "M": 44.0095e-3        # kg/mol
}

def peng_robinson_density_CO2(P_bar, T_C):
    """
    Compute CO2 density via Peng–Robinson EOS:
    Inputs:
      P_bar [bar], T_C [°C]
    Output:
      density [kg/m3]
    """
    P = P_bar * 1e5            # Pa
    T = celsius_to_kelvin(T_C) # K
    R = PR_CO2["R"]
    Tc = PR_CO2["Tc"]
    Pc = PR_CO2["Pc"]
    omega = PR_CO2["omega"]
    M = PR_CO2["M"]

    # PR EOS params
    kappa = 0.37464 + 1.54226*omega - 0.26992*(omega**2)
    Tr = T / Tc
    alpha = (1 + kappa*(1 - math.sqrt(Tr)))**2
    a = 0.45724 * (R**2) * (Tc**2) / Pc * alpha
    b = 0.07780 * R * Tc / Pc

    # PR cubic for compressibility factor Z:
    # Z^3 + c2 Z^2 + c1 Z + c0 = 0, with:
    A = a * P / ((R**2) * (T**2))
    B = b * P / (R * T)
    c2 = -(1 - B)
    c1 = A - 3*(B**2) - 2*B
    c0 = -(A*B - B*B - B**3)

    coeffs = [1.0, c2, c1, c0]
    roots = np.roots(coeffs)

    # Keep real roots
    real_roots = [r.real for r in roots if abs(r.imag) < 1e-10]
    if len(real_roots) == 0:
        # fallback: ideal gas density (very rare to hit here)
        rho_ig = P * M / (R * T)
        return float(rho_ig)

    # In supercritical (T > Tc or P > Pc), we typically have one relevant real root.
    # Choose the largest real root > B (gas-like). This is a common robust choice for PR in scCO2 region.
    z_candidates = [z for z in real_roots if z > B + 1e-9]
    if len(z_candidates) == 0:
        z = max(real_roots)
    else:
        z = max(z_candidates)

    # Molar volume Vm = ZRT/P
    Vm = z * R * T / P  # m3/mol
    rho = M / Vm       # kg/m3
    return float(rho)

# ----------------------------------------------------
# Chrastil solubility model: ln S = k ln rho + a/T + b
# Returns S in kg/m3 of CO2 (solubility limit in bulk)
# ----------------------------------------------------
def chrastil_solubility(rho_CO2, T_K, k, a, b, cosolvent_frac=0.0):
    """
    rho_CO2 [kg/m3], T_K [K]
    cosolvent_frac: ethanol mass fraction in solvent stream (0..0.2 typical lab)
    We include a mild multiplicative factor for EtOH polarity boost.
    """
    # Base Chrastil
    S = math.exp(k * math.log(max(rho_CO2, 1e-6)) + a / T_K + b)  # kg/m3
    # Co-solvent boost (small-signal, conservative):
    # Literature shows strong effects, but we keep a gentle factor to avoid overclaims.
    # Up to +50% at 10% EtOH is conservative in many lipid systems.
    boost = 1.0 + 5.0 * cosolvent_frac   # e.g., 0.1 -> +50%
    return S * boost

# ----------------------------------------------------
# Aire spécifique & facteurs géométrie
# ----------------------------------------------------
def specific_area_sphere(d_p_m):
    # area/volume = 6/d for spheres; per bed volume with (1-ε): ap = 6*(1-ε)/d_p
    # Here return particle specific area (m2 particle / m3 particle) = 6 / d_p
    return 6.0 / max(d_p_m, 1e-9)

# Humidity effect on effective diffusivity (very simplified penalty)
def humidity_diffusivity_factor(moisture_frac):
    # moisture_frac in [0..0.5]
    # penalize D_eff roughly linearly; 0% -> 1.0 ; 30% -> ~0.7 ; 50% -> 0.5
    m = clamp(moisture_frac, 0.0, 0.5)
    return 1.0 - 0.9*m**0.8

# ----------------------------------------------------
# Sovová-like BIC numerical model (plug-flow 1D)
# ----------------------------------------------------
def simulate_bic_sovova(
    P_bar, T_C, d_p_mm, eps_bed, bed_height_m, bed_diam_m,
    m_solid_kg, x_oil0, f_free,
    kf, ks,  # [m/s]
    G_CO2_kg_min, t_total_min,
    chr_k, chr_a, chr_b, cosolvent_frac, moisture_frac
):
    """
    Numerical PFR & two-pool oil model.
    - Discretize bed into Nz cells. Plug flow forward; no axial dispersion modeled.
    - Time stepping Nt.
    - Two oil pools per cell: free (fast) and locked (slow).
    - Transfer limited by mass-transfer + solubility S (Chrastil) + PR density.
    Returns:
      times[min], yields[%], details dict
    """
    # Geometry
    A_bed = math.pi * (bed_diam_m**2) / 4.0
    V_bed = A_bed * bed_height_m
    eps = clamp(eps_bed, 0.2, 0.6)  # typical packed beds
    solid_vol = (1 - eps) * V_bed

    # Particle metrics
    d_p = d_p_mm / 1000.0  # m
    a_p = specific_area_sphere(d_p)  # 6/d_p (particle)
    a_bed = a_p * (1 - eps)  # m2 particle surface per m3 of bed

    # Initial oil per total solid
    m_oil0 = x_oil0 * m_solid_kg
    m_free0 = f_free * m_oil0
    m_lock0 = (1 - f_free) * m_oil0

    # Discretization
    Nz = 30
    Nt = 180
    H = bed_height_m / Nz
    dt = (t_total_min * 60.0) / Nt  # seconds
    Q_CO2 = G_CO2_kg_min / 60.0     # kg/s

    # Fluid properties per step (assume uniform P,T along bed)
    rho = peng_robinson_density_CO2(P_bar, T_C)   # kg/m3
    T_K = celsius_to_kelvin(T_C)
    S = chrastil_solubility(rho, T_K, chr_k, chr_a, chr_b, cosolvent_frac)  # kg/m3 of CO2

    # Optional safety caps
    S = clamp(S, 1e-6, 200.0)  # keep reasonable solubility cap

    # Effective mass-transfer adjustments
    hum_fac = humidity_diffusivity_factor(moisture_frac)
    kf_eff = kf * hum_fac
    ks_eff = ks * hum_fac

    # State arrays per cell
    # Oil (kg) in each cell: split by free/locked
    m_free = np.full(Nz, m_free0 / Nz)
    m_lock = np.full(Nz, m_lock0 / Nz)

    # Fluid concentration at cell inlets (kg oil / m3 CO2)
    C_in = np.zeros(Nz)  # initially pure CO2
    # Cross-section bed area for flux calculations
    # Film area per cell volume: a_bed [m2/m3]; cell volume: V_cell = A_bed*H
    V_cell = A_bed * H
    A_mass = a_bed * V_cell  # total interfacial area in the cell

    # mass balance accumulators
    cum_extracted = 0.0
    times = []
    yields = []

    # velocity of interstitial fluid (superficial / eps)
    # Superficial volumetric flow of CO2:
    # Q_vol = (mass flow) / rho [m3/s]
    Q_vol = Q_CO2 / max(rho, 1e-9)
    u_sup = Q_vol / A_bed        # superficial velocity m/s
    u_int = u_sup / max(eps, 1e-9)  # interstitial if needed (not used directly)

    # Time loop
    for it in range(Nt):
        t_sec = (it+1)*dt
        # PASS 1: compute transfer in each cell given inlet concentration
        C_out = np.zeros(Nz)

        for j in range(Nz):
            # Local outlet concentration limited by solubility S
            # Mass-transfer expression (film-controlled):
            # flux ~ k * A * (C* - C_bulk) * dt
            # C* (equilibrium) can't exceed S
            C_star = S

            # Available oil in this cell:
            oil_here = m_free[j] + m_lock[j]
            if oil_here <= 1e-12:
                # no oil to transfer
                C_out[j] = C_in[j]
                continue

            # Mass-transfer coefficients:
            # Two-stage: first free oil with kf_eff, then locked with ks_eff
            # We compute potential mass transferred for free pool:
            # dM_free = kf_eff * A_mass * (C_star - C_bulk_avg) * dt
            # But we must keep fluid concentration evolution along residence time in cell.
            # For stability, use a single mixing step approximation:

            # Volume of CO2 crossing the cell over dt:
            V_CO2_dt = Q_vol * dt  # m3

            # Start from C_in -> attempt to approach C_star by transfer, limited by pools
            C_bulk = C_in[j]

            # 1) Free pool
            if m_free[j] > 1e-12 and C_bulk < C_star - 1e-12:
                dM_free_potential = kf_eff * A_mass * max(C_star - C_bulk, 0.0) * dt
                dM_free = min(dM_free_potential, m_free[j])
                # This increases outlet concentration by dM_free / V_CO2_dt
                dC = dM_free / max(V_CO2_dt, 1e-12)
                C_bulk = min(C_star, C_bulk + dC)
                m_free[j] -= dM_free

            # 2) Locked pool
            if m_lock[j] > 1e-12 and C_bulk < C_star - 1e-12:
                dM_lock_potential = ks_eff * A_mass * max(C_star - C_bulk, 0.0) * dt
                dM_lock = min(dM_lock_potential, m_lock[j])
                dC = dM_lock / max(V_CO2_dt, 1e-12)
                C_bulk = min(C_star, C_bulk + dC)
                m_lock[j] -= dM_lock

            # Outlet concentration for this cell:
            C_out[j] = clamp(C_bulk, 0.0, C_star)

        # PASS 2: convection shift (plug flow) to next cells
        # Assume one cell length residence time tau_cell = H / u_sup
        # But we enumerated dt; we do a simple upwind: shift concentrations downstream
        C_in_new = np.zeros(Nz)
        # The number of cells advanced by this dt:
        # fraction of cell traversed:
        if u_sup > 1e-12:
            frac = dt * u_sup / H
        else:
            frac = 0.0
        frac = clamp(frac, 0.0, 1.0)

        # Upwind linear mixing between current cell out and upstream out
        # Compute new inlet for cell j from a convex comb of previous t step out of j-1 and j
        C_in_new[0] = (1.0 - frac) * C_out[0]  # inlet fresh CO2 at column entry (C≈0), but keep continuity
        for j in range(1, Nz):
            C_in_new[j] = frac * C_out[j-1] + (1.0 - frac) * C_out[j]

        # Mass recovered at column outlet during this dt:
        C_outlet = C_out[-1]
        m_extracted_dt = C_outlet * Q_vol * dt  # kg

        cum_extracted += m_extracted_dt
        C_in = C_in_new

        Y_pct = 100.0 * cum_extracted / max(m_oil0, 1e-12)
        Y_pct = clamp(Y_pct, 0.0, 100.0)
        times.append(t_sec/60.0)  # minutes
        yields.append(Y_pct)

    details = {
        "rho_CO2_kg_m3": rho,
        "S_kg_per_m3": S,
        "Qvol_m3_s": Q_vol,
        "kf_eff_m_s": kf_eff,
        "ks_eff_m_s": ks_eff,
        "m_extracted_kg": cum_extracted,
        "m_oil0_kg": m_oil0
    }
    return np.array(times), np.array(yields), details


# =========================
# UI Streamlit
# =========================
st.set_page_config(page_title="SimExtract — scCO₂ Model (PR + Chrastil + BIC)",
                   page_icon="🧪", layout="wide")

st.title("🧪 SimExtract — Supercritical CO₂ Extraction (Peng–Robinson + Chrastil + BIC/Sovová)")

st.markdown("""
Ce MVP intègre :
- **Peng–Robinson** (densité CO₂),
- **Chrastil** (solubilité du composé),
- **Modèle BIC (Sovová) numérique** (huile libre + intra-cellule, transfert + solubilité).
Les résultats sont bornés physiquement (0–100%).
""")

# -------------------------
# Sidebar — Input
# -------------------------
st.sidebar.header("⚙️ Paramètres d'entrée")

# Compound presets (Chrastil)
compound_presets = {
    "Tocopherol": {"Ymax": 20.0, "k": 3.0, "a": -1200.0, "b": -5.5},
    "Beta-Carotene": {"Ymax": 12.0, "k": 3.2, "a": -1400.0, "b": -6.0},
    "Lycopene": {"Ymax": 10.0, "k": 3.1, "a": -1350.0, "b": -5.8},
    "Caffeine": {"Ymax": 18.0, "k": 2.6, "a": -900.0,  "b": -5.0},
    "Curcumin": {"Ymax": 15.0, "k": 2.8, "a": -1000.0, "b": -5.3},
    "Generic Lipid": {"Ymax": 25.0, "k": 3.0, "a": -1100.0, "b": -5.4}
}
compound = st.sidebar.selectbox("Composé cible", list(compound_presets.keys()), index=0)
Ymax_default = compound_presets[compound]["Ymax"]
chr_k_default = compound_presets[compound]["k"]
chr_a_default = compound_presets[compound]["a"]
chr_b_default = compound_presets[compound]["b"]

with st.sidebar.expander("Paramètres Chrastil (éditables)"):
    chr_k = st.number_input("k (sans unité)", value=float(chr_k_default), step=0.1, format="%.3f")
    chr_a = st.number_input("a [K]", value=float(chr_a_default), step=50.0, format="%.1f")
    chr_b = st.number_input("b (sans unité)", value=float(chr_b_default), step=0.1, format="%.3f")

st.sidebar.markdown("---")

# Machine / procédé
P_bar = st.sidebar.number_input("Pression [bar]", value=250.0, min_value=80.0, max_value=500.0, step=10.0)
T_C = st.sidebar.number_input("Température [°C]", value=50.0, min_value=20.0, max_value=120.0, step=1.0)
G_CO2 = st.sidebar.number_input("Débit CO₂ [kg/min]", value=1.0, min_value=0.1, max_value=10.0, step=0.1)
t_total_min = st.sidebar.number_input("Durée extraction [min]", value=210.0, min_value=10.0, max_value=2000.0, step=10.0)
cosolvent_frac = st.sidebar.slider("EtOH co-solvant (fraction massique)", 0.0, 0.20, 0.00, 0.01)

st.sidebar.markdown("---")
# Lit & solide
bed_height_m = st.sidebar.number_input("Hauteur de lit H [m]", value=0.30, min_value=0.05, max_value=2.0, step=0.01, format="%.2f")
bed_diam_m = st.sidebar.number_input("Diamètre de lit D [m]", value=0.05, min_value=0.01, max_value=1.0, step=0.01, format="%.2f")
eps_bed = st.sidebar.slider("Porosité de lit ε [-]", 0.20, 0.60, 0.40, 0.01)
d_p_mm = st.sidebar.number_input("Diamètre particule [mm]", value=0.60, min_value=0.10, max_value=2.0, step=0.05)
moisture = st.sidebar.slider("Humidité matière (massique)", 0.0, 0.5, 0.10, 0.01)

st.sidebar.markdown("---")
# Matière végétale & cinétique
m_solid_kg = st.sidebar.number_input("Masse de solide [kg]", value=0.08, min_value=0.01, max_value=20.0, step=0.01, format="%.2f")
x_oil0_pct = st.sidebar.number_input("Teneur initiale en huile [% masse solide]", value=15.0, min_value=1.0, max_value=60.0, step=0.5)
f_free = st.sidebar.slider("Fraction d'huile libre f_free", 0.0, 1.0, 0.25, 0.05)

with st.sidebar.expander("Coefficients de transfert (avancés)"):
    kf = st.number_input("k_f (huile libre) [m/s]", value=5e-5, min_value=1e-7, max_value=1e-3, step=1e-5, format="%.1e")
    ks = st.number_input("k_s (huile intra-cell) [m/s]", value=8e-6, min_value=1e-8, max_value=5e-4, step=1e-6, format="%.1e")

st.sidebar.markdown("---")
target = st.sidebar.number_input("🎯 Rendement cible [%]", value=15.0, min_value=1.0, max_value=100.0, step=1.0)

# Warnings utiles
warns = []
if T_C > 80.0:
    warns.append("Température > 80 °C : risque de dégradation de molécules sensibles.")
if d_p_mm < 0.15:
    warns.append("d_p < 0.15 mm : risque de colmatage & chemins préférentiels.")
if G_CO2 / max(m_solid_kg, 1e-9) < 0.2:
    warns.append("Débit CO₂ / masse solide très bas : extraction très lente possible.")
if eps_bed < 0.25 or eps_bed > 0.55:
    warns.append("Porosité atypique : vérifie l'empotage (remplissage).")
if moisture > 0.30:
    warns.append("Humidité > 30% : transfert interne fortement pénalisé; sécher davantage si possible.")

if warns:
    st.warning("⚠️ " + " | ".join(warns))

# -------------------------
# Calcul & Affichage
# -------------------------
# Convert oil content
x_oil0 = x_oil0_pct / 100.0

if st.button("🚀 Calculer la simulation"):
    times, yields, details = simulate_bic_sovova(
        P_bar=P_bar, T_C=T_C, d_p_mm=d_p_mm, eps_bed=eps_bed,
        bed_height_m=bed_height_m, bed_diam_m=bed_diam_m,
        m_solid_kg=m_solid_kg, x_oil0=x_oil0, f_free=f_free,
        kf=kf, ks=ks, G_CO2_kg_min=G_CO2, t_total_min=t_total_min,
        chr_k=chr_k, chr_a=chr_a, chr_b=chr_b,
        cosolvent_frac=cosolvent_frac, moisture_frac=moisture
    )

    df = pd.DataFrame({"Time [min]": times, "Yield [%]": yields})
    st.line_chart(df.set_index("Time [min]"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rendement final [%]", f"{yields[-1]:.2f}")
    with col2:
        st.metric("Densité CO₂ [kg/m³]", f"{details['rho_CO2_kg_m3']:.1f}")
    with col3:
        st.metric("Solubilité S [kg/m³ CO₂]", f"{details['S_kg_per_m3']:.2f}")

    st.subheader("📋 Détails calcul")
    st.json({
        "Débit volumique CO₂ [m³/s]": round(details["Qvol_m3_s"], 6),
        "k_f effectif [m/s]": f"{details['kf_eff_m_s']:.3e}",
        "k_s effectif [m/s]": f"{details['ks_eff_m_s']:.3e}",
        "Huile initiale [kg]": round(details["m_oil0_kg"], 6),
        "Huile extraite [kg]": round(details["m_extracted_kg"], 6),
    })

    # Reco simple pour atteindre cible (ajuste G_CO2 ou temps)
    Yf = yields[-1]
    if Yf < target:
        shortfall = target - Yf
        # Heuristique: augmenter G_CO2 ou t_total
        recos = []
        recos.append("Augmenter la **pression** (↑ densité → ↑ solubilité) avant tout.")
        if T_C < 70:
            recos.append("Augmenter **T** (fluidifie l'huile) tout en restant < 80 °C si molécule sensible.")
        recos.append("Réduire **d_p** vers 0.3–0.6 mm si possible (↑ aire spécifique).")
        recos.append("Introduire **5–10% EtOH** (co‑solvant) si la molécule est moyenne à polaire.")
        recos.append("Augmenter **G_CO₂** ou **durée** (débit insuffisant ou temps trop court).")
        st.info("🎯 Recommandations pour viser {:.1f}% :\n- ".format(target) + "\n- ".join(recos))
    else:
        st.success(f"🎉 Objectif {target:.1f}% atteint (ou dépassé). Vous pouvez tenter de réduire le temps ou le débit pour optimiser les coûts.")

# -------------------------
# Footer – Notes scientifiques
# -------------------------
st.markdown("""
---
**Notes**  
- Densité CO₂ via **Peng–Robinson** (Tc, Pc, ω CO₂).  
- Solubilité via **Chrastil** ; paramètres ajustables par composé.  
- **Modèle BIC/Sovová numérique**: 2 réservoirs (huile libre / intra‑cellulaire), transfert filmique, limitation par solubilité, lit 1D plug‑flow.  
- **Humidité** pénalise k_f et k_s (effet sur D_eff). **EtOH** booste la solubilité (facteur conservatif).  
- Rendements bornés **0–100 %**; ceci reste un **MVP scientifique** : pour la calibration, injecter des données réelles et ajuster (k_f, k_s, k,a,b).
""")        return round(max(0.0, min(rendement, Y_max)), 4), k, f_T
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
