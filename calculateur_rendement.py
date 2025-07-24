
import numpy as np

def rendement_theorique(t_minutes):
    """
    Calcule le rendement théorique Y(t) en % dans des conditions optimales
    :param t_minutes: temps d'extraction en minutes
    :return: rendement estimé (en %)
    """
    dp = 0.1  # taille particule optimale (mm)
    flow = 30  # débit optimal (kg/h)
    D_eff = 1e-6  # diffusivité effective (m2/s)
    shape_factor = 1.0  # lit homogène

    A_surf = 1 / dp  # surface spécifique
    k_opt = D_eff * A_surf * (flow / 60) * shape_factor

    t = np.array(t_minutes, dtype=float)
    rendement = 100 * (1 - np.exp(-k_opt * t))
    return rendement
