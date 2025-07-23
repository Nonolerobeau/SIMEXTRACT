
def predict(target_yield, P, T, dp, flow, time, **kwargs):
    # RSM modèle basé sur Louaer (simplifié)
    k = 0.015
    yield_est = k * P * T / (dp + 0.1) * (flow / 10) * (time / 60)

    suggestion = {
        "Pressure": round(P, 2),
        "Temperature": round(T, 2),
        "Flow Rate": round(flow, 2),
        "Time": round(time, 2)
    }

    return {
        "Model": "RSM (Louaer)",
        "Yield Est.": round(yield_est, 2),
        "Suggested Params": suggestion
    }
