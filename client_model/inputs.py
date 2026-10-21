CONTRIB = {0: 300_000, 1: 150_000}
YEARS = 6
YIELD = 0.05375
RESERVE = sum(50_000 / (1 + YIELD)**t for t in range(10))

LTCMA = {"stocks": 0.075, "bonds": 0.046}        # compound returns, not arithmetic
LTCMA_VOL = {"stocks": 0.1796, "bonds": 0.0344}
CORR = 0.00
N_PATHS = 10_000
SAFE_ASSET = "matched"