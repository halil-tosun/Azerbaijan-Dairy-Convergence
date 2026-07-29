"""
04_distribution_dynamics.py
============================
Kernel density estimation of relative milk yield in 2000, 2012, and
2024, and Silverman's (1981) critical-bandwidth bootstrap test for
multimodality in each of those three years.

Note on determinism: the bootstrap test uses numpy's legacy global
RandomState API (np.random.seed / np.random.default_rng with a fixed
seed re-applied before each year's test; see SEED in _paths.py) so that
results are identical across runs and machines.

Produces:
  output/Table5_silverman_test.csv
  output/supporting/kernel_density_grid.csv   (relative-yield density grid used by Figure 3)
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR, SEED, N_BOOTSTRAP_SILVERMAN
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)

GRID = np.linspace(0.1, 3.0, 400)
BW_RANGE = np.linspace(0.01, 1.0, 300)


def kde(x, grid, bw):
    diffs = (grid[:, None] - x[None, :]) / bw
    kernel = np.exp(-0.5 * diffs ** 2) / np.sqrt(2 * np.pi)
    return kernel.sum(axis=1) / (len(x) * bw)


def n_modes(density):
    d = np.diff(density)
    return int(np.sum((d[:-1] > 0) & (d[1:] < 0)))


def critical_bandwidth(x, grid=GRID, bw_range=BW_RANGE):
    for bw in bw_range:
        if n_modes(kde(x, grid, bw)) <= 1:
            return bw
    return bw_range[-1]


def silverman_test(x, grid=GRID, bw_range=BW_RANGE, n_boot=N_BOOTSTRAP_SILVERMAN, seed=SEED):
    """Silverman's (1981) critical-bandwidth bootstrap test for unimodality.

    H0: the density is unimodal. A low bootstrap p rejects H0 (evidence
    of genuine multimodality).
    """
    h_crit = critical_bandwidth(x, grid, bw_range)
    rng = np.random.default_rng(seed)
    n = len(x)
    count_more_modal = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        noise = rng.normal(0, h_crit, n)
        xb = x[idx] + noise
        xb = x.mean() + (xb - xb.mean()) / np.sqrt(1 + h_crit ** 2 / np.var(x))
        h_crit_b = critical_bandwidth(xb, grid, bw_range)
        if h_crit_b >= h_crit:
            count_more_modal += 1
    return h_crit, count_more_modal / n_boot


def relative_yield_panel(df):
    df = df.copy()
    df["national_mean"] = df.groupby("year")["yield_per_cow"].transform("mean")
    df["relative_yield"] = df["yield_per_cow"] / df["national_mean"]
    return df


def main():
    df = relative_yield_panel(data_overview.load_panel())

    years = [2000, 2012, 2024]
    rows = []
    density_records = []
    for year in years:
        x = df[df["year"] == year]["relative_yield"].dropna().values
        x = x[x > 0]
        h_crit, p_boot = silverman_test(x)
        silverman_bw = 0.9 * min(np.std(x, ddof=1), (np.percentile(x, 75) - np.percentile(x, 25)) / 1.34) * len(x) ** (-1 / 5)
        # "Modes" reports the number of modes AT the critical bandwidth
        # h_crit, which is by construction the smallest bandwidth for
        # which the density is unimodal (see critical_bandwidth() above).
        # This is a sanity-check column confirming h_crit was found
        # correctly, not the (generally larger, sometimes >1-modal)
        # number of modes at the raw Silverman rule-of-thumb bandwidth.
        modes_at_hcrit = n_modes(kde(x, GRID, h_crit))
        rows.append({
            "Year": year,
            "Silverman bandwidth": round(silverman_bw, 3),
            "Critical bandwidth": round(h_crit, 3),
            "Modes": modes_at_hcrit,
            "Bootstrap p": round(p_boot, 3),
        })
        density = kde(x, GRID, h_crit)
        for g, d in zip(GRID, density):
            density_records.append({"year": year, "relative_yield": g, "density": d})

    table6 = pd.DataFrame(rows)
    table6.to_csv(OUTPUT_DIR / "Table5_silverman_test.csv", index=False)
    print("Table 5. Silverman (1981) bimodality test results")
    print(table6.to_string(index=False))

    pd.DataFrame(density_records).to_csv(SUPPORTING_DIR / "kernel_density_grid.csv", index=False)
    print("\nKernel density grid (2000, 2012, 2024) written for Figure 3.")


if __name__ == "__main__":
    main()
