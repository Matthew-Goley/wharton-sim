CONTRIB = {0: 300_000, 1: 150_000}
YEARS = 6
YIELD = 0.04
RESERVE = sum(50_000 / (1 + YIELD)**t for t in range(10))

LTCMA = {"stocks": 0.067, "bonds": 0.046}
LTCMA_VOL = {"stocks": 0.16, "bonds": 0.06}
CORR = 0.1
N_PATHS = 10_000
SAFE_ASSET = "matched"