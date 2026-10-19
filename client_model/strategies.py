def floor(t, inp):
    f = inp.RESERVE / (1 + inp.YIELD)**(inp.YEARS - t)
    for k, c in inp.CONTRIB.items():
        if k > t:
            f -= c / (1 + inp.YIELD)**(k - t)
    return f

def cppi(m, cap, min_w=0.0):
    def rule(t, value, inp):
        cushion = np.maximum(value - floor(t, inp), 0)
        return np.clip(m * cushion / value, min_w, cap)
    return rule

def glide(weights):                    # fixed benchmark, e.g. [.75,.75,.7,.65,.45,.35]
    def rule(t, value, inp):
        return np.full_like(value, weights[t])
    return rule