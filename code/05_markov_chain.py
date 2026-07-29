"""
05_markov_chain.py
===================
First-order Markov transition matrix for relative milk yield quartiles
(pooled, fixed cut-points across the full 2000-2024 sample), and the
Shorrocks (1978) immobility index M.

Produces:
  output/Table6_markov_transition_matrix.csv
  output/supporting/shorrocks_mobility_index.txt
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def shorrocks_m(P):
    """Shorrocks (1978) immobility/mobility index: M = (k - trace(P)) / (k - 1)."""
    k = P.shape[0]
    return (k - np.trace(P)) / (k - 1)


def main():
    df = data_overview.load_panel()
    df["national_mean"] = df.groupby("year")["yield_per_cow"].transform("mean")
    df["relative_yield"] = df["yield_per_cow"] / df["national_mean"]

    # Fixed, pooled quartile cut-points computed over the full sample
    cuts = df["relative_yield"].quantile([0.25, 0.5, 0.75]).values

    def quartile(x):
        if x <= cuts[0]:
            return 1
        elif x <= cuts[1]:
            return 2
        elif x <= cuts[2]:
            return 3
        return 4

    df["quartile"] = df["relative_yield"].apply(quartile)

    wide = df.pivot(index="region", columns="year", values="quartile")
    years = sorted(wide.columns)

    counts = np.zeros((4, 4))
    for y0, y1 in zip(years[:-1], years[1:]):
        pairs = wide[[y0, y1]].dropna()
        for q0, q1 in zip(pairs[y0], pairs[y1]):
            counts[int(q0) - 1, int(q1) - 1] += 1
    P = counts / counts.sum(axis=1, keepdims=True)

    labels = ["Q1 (low)", "Q2", "Q3", "Q4 (high)"]
    table7 = pd.DataFrame(np.round(P, 4), index=labels, columns=labels)
    table7.index.name = "Quartile at t"
    table7.to_csv(OUTPUT_DIR / "Table6_markov_transition_matrix.csv")
    print("Table 6. Markov transition matrix (1-year horizon, pooled 2000-2024)")
    print(table7.to_string())

    m = shorrocks_m(P)
    with open(SUPPORTING_DIR / "shorrocks_mobility_index.txt", "w") as f:
        f.write(f"Shorrocks (1978) mobility index M = {m:.3f}\n")
    print(f"\nShorrocks (1978) mobility index M = {m:.3f}")


if __name__ == "__main__":
    main()
