
def predict(target_yield, P, T, dp, flow, time, **kwargs):
    # Exemple simplifié basé sur un modèle Sovová adapté
    # Cette formule est illustrative
    yield_est = 0.02 * P + 0.03 * T - 0.05 * dp + 0.15 * flow + 0.1 * time
    return {
        "Model": "Sovová",
        "Yield Est.": round(yield_est, 2),
        "Pressure": P,
        "Temp": T,
        "Time": time,
    }
