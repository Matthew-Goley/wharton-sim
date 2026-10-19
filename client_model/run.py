import itertools
from types import SimpleNamespace
import numpy as np
import pandas as pd

from client_model import inputs
from client_model.scenarios import make_scenarios, make_normal_scenarios
from client_model.strategies import cppi, glide
from client_model.simulate import run

FACILITY_SHARE = 0.75      # share of surplus that goes to the facility
MIN_FUNDED = 0.99          # objective: must cover the reserve 99% of the time


def make_inputs(**changes):
    """Copy of inputs.py with some values changed. Recomputes the reserve if the yield changes."""
    inp = SimpleNamespace(**{k: getattr(inputs, k) for k in dir(inputs) if k.isupper()})
    for k, v in changes.items():
        setattr(inp, k, v)
    inp.RESERVE = sum(50_000 / (1 + inp.YIELD)**t for t in range(10))
    return inp


def build_strategies():
    """Every candidate strategy, as {name: rule}."""
    strats = {}
    for m, cap, min_w in itertools.product([2, 3, 4, 5], [0.6, 0.7, 0.8, 0.9], [0.0, 0.1, 0.2]):
        strats[f"CPPI m={m} cap={cap:.0%} min={min_w:.0%}"] = cppi(m, cap, min_w)
    strats["Glide 75 to 35"] = glide([0.75, 0.75, 0.70, 0.65, 0.45, 0.35])
    strats["Glide 90 to 40"] = glide([0.90, 0.85, 0.80, 0.70, 0.55, 0.40])
    strats["Fixed 60/40"] = glide([0.60] * 6)
    return strats


def score(V, inp):
    """Turn simulated 2033 values into the numbers we care about."""
    surplus = V - inp.RESERVE
    contrib = FACILITY_SHARE * np.maximum(surplus, 0)
    return {
        "p_funded": (surplus >= 0).mean(),
        "median_contrib": np.median(contrib),
        "p10_contrib": np.percentile(contrib, 10),
        "p90_contrib": np.percentile(contrib, 90),
        "p_zero_contrib": (contrib == 0).mean(),
        "median_V2033": np.median(V),
    }


def grid_search(scen, inp):
    rows = []
    for name, rule in build_strategies().items():
        V, _ = run(rule, scen, inp)     # same scenarios for every strategy
        rows.append({"strategy": name, **score(V, inp)})
    return pd.DataFrame(rows)


def pick_winner(df):
    passed = df[df["p_funded"] >= MIN_FUNDED]
    if passed.empty:
        print(f"Nothing reached {MIN_FUNDED:.0%} funded. Showing the safest instead.")
        return df.sort_values("p_funded", ascending=False).iloc[0]
    return passed.sort_values("median_contrib", ascending=False).iloc[0]


def robustness(scen_kwargs_list):
    """Rerun the whole grid under different assumptions; report each test's winner and top 3."""
    out = []
    for label, inp, scen in scen_kwargs_list:
        df = grid_search(scen, inp)
        top3 = df[df["p_funded"] >= MIN_FUNDED].nlargest(3, "median_contrib")["strategy"].tolist()
        w = pick_winner(df)
        out.append({"test": label, "winner": w["strategy"], "p_funded": w["p_funded"],
                    "median_contrib": w["median_contrib"], "top3": " | ".join(top3)})
    return pd.DataFrame(out)


if __name__ == "__main__":
    pd.set_option("display.width", 200, "display.max_columns", 20)

    # ---- Step 6: base case ----
    base = make_inputs()
    scen = make_scenarios(base.N_PATHS, base.YEARS, base.LTCMA, seed=42)
    results = grid_search(scen, base)
    results.sort_values("median_contrib", ascending=False).to_csv("client_model/results_base.csv", index=False)
    winner = pick_winner(results)
    print("Reserve:", round(base.RESERVE))
    print(results.sort_values("median_contrib", ascending=False).head(10).round(3))
    print("\nWINNER:\n" + winner.to_string())

    # ---- Step 7: robustness ----
    def stocks_shift(d):
        return {**base.LTCMA, "stocks": base.LTCMA["stocks"] + d}

    tests = []
    for y in [0.03, 0.05]:
        inp = make_inputs(YIELD=y)
        tests.append((f"yield {y:.0%}", inp, scen))
    for d in [-0.01, 0.01]:
        inp = make_inputs(LTCMA=stocks_shift(d))
        tests.append((f"stocks {d:+.0%}", inp, make_scenarios(inp.N_PATHS, inp.YEARS, inp.LTCMA, seed=42)))
    tests.append(("normal dist", base,
                  make_normal_scenarios(base.N_PATHS, base.YEARS, base.LTCMA, base.LTCMA_VOL, base.CORR, seed=42)))

    rob = robustness(tests)
    rob.to_csv("client_model/results_robustness.csv", index=False)
    print("\nROBUSTNESS:\n", rob.round(3).to_string(index=False))