import numpy as np, pandas as pd

def make_scenarios(n_paths, years, ltcma, block=3, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.read_csv("client_model/data/returns.csv")
    logr = np.log1p(df[["stocks", "bonds"]].values)
    for j, k in enumerate(["stocks", "bonds"]):
        logr[:, j] += np.log1p(ltcma[k]) - logr[:, j].mean()
    out = np.empty((n_paths, years, 2))
    for p in range(n_paths):
        idx = []
        while len(idx) < years:
            s = rng.integers(0, len(logr) - block)
            idx.extend(range(s, s + block))
        out[p] = logr[idx[:years]]
    return np.expm1(out)   # shape: paths x years x [stocks, bonds]

def make_normal_scenarios(n_paths, years, ltcma, vol, corr, seed=0):
    rng = np.random.default_rng(seed)
    mu = np.log1p([ltcma["stocks"], ltcma["bonds"]])
    sd = np.array([vol["stocks"], vol["bonds"]])
    cov = np.array([[sd[0]**2, corr*sd[0]*sd[1]], [corr*sd[0]*sd[1], sd[1]**2]])
    return np.expm1(rng.multivariate_normal(mu, cov, size=(n_paths, years)))