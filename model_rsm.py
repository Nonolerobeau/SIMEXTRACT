
def predict(target_yield, P, T, dp, flow, time, **kwargs):
    # Exemple simplifié de prédiction avec le modèle RSM (Response Surface Methodology)
    # Cette formule est illustrative
    yield_est = 0.01 * P + 0.05 * T - 0.1 * dp + 0.2 * flow + 0.3 * time
    return {
        "Model": "RSM",
        "Yield Est.": round(yield_est, 2),
        "Pressure": P,
        "Temp": T,
        "Time": time,
    }
