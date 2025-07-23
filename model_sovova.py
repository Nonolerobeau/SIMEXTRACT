
def predict(target_yield, P, T, dp, flow, time, **kwargs):
    # Simplified Sovová-style model with base assumptions
    kf = 0.004
    ks = 0.002
    x0 = 0.12
    t_hrs = time / 60
    yield_est = x0 * (1 - (1 / (1 + kf * t_hrs + ks * t_hrs)))

    suggestion = {
        "Pressure": round(P, 2),
        "Temperature": round(T, 2),
        "Flow Rate": round(flow, 2),
        "Time": round(time, 2)
    }

    return {
        "Model": "Sovová (Kinetic Approx.)",
        "Yield Est.": round(yield_est * 100, 2),
        "Suggested Params": suggestion
    }
