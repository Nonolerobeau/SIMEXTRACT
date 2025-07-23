def predict(target_yield, P, T, dp, flow, time, **kwargs):
    # Exemple de modèle simplifié type RSM (Response Surface Methodology)
    yield_est = 0.2 * P + 0.1 * T - 5 * dp + 2 * flow + 0.5 * time
    return {
        "Model": "RSM",
        "Yield Est.": round(yield_est, 2),
        "Pressure": P,
        "Temp": T,
    }
  add model_rsm.py
