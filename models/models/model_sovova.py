def predict(target_yield, P, T, dp, flow, time, **kwargs):
    # Modèle inspiré de Sovová (simplifié)
    yield_est = (P * flow * time) / (1 + dp * 10 + T * 0.1)
    return {
        "Model": "Sovová",
        "Yield Est.": round(yield_est, 2),
        "Pressure": P,
        "Temp": T,
    }
  add model_sovova.py
