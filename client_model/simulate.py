import numpy as np

def run(rule, scen, inp):
    V = np.zeros(scen.shape[0])
    matched = getattr(inp, "SAFE_ASSET", "bootstrap") == "matched"
    for t in range(inp.YEARS):
        V += inp.CONTRIB.get(t, 0)
        w = rule(t, V, inp)
        r_stock = scen[:, t, 0]
        r_bond = inp.YIELD if matched else scen[:, t, 1]
        V *= 1 + w * r_stock + (1 - w) * r_bond
        if t == 3:
            V_2031 = V.copy()
    return V, V_2031