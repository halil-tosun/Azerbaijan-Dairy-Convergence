"""
07_spatial_markov.py
======================
Spatial Markov chain (Rey, 2001): re-estimates the pooled quartile
transition matrix from 05_markov_chain.py separately for districts
whose queen-contiguity neighbours were, on average, in each quartile
the prior year, and reports the mean diagonal (persistence)
probability for each conditioning quartile.

Produces:
  output/Table8_spatial_markov_diagonal.csv
  output/supporting/spatial_markov_matrices.csv   (full 4x4x4 conditional matrices, used by Figure 6)
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR
from spatial_weights import load_geometries, build_queen_contiguity
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def main():
    df = data_overview.load_panel()
    df["national_mean"] = df.groupby("year")["yield_per_cow"].transform("mean")
    df["relative_yield"] = df["yield_per_cow"] / df["national_mean"]
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
    wide_q = df.pivot(index="region", columns="year", values="quartile")

    names, boundary_points, _ = load_geometries()
    W_full = build_queen_contiguity(names, boundary_points)
    common = [nm for nm in names if nm in wide_q.index]
    idx = [names.index(nm) for nm in common]
    W = W_full[np.ix_(idx, idx)]
    W = W / W.sum(axis=1, keepdims=True)
    wide_q = wide_q.loc[common]

    years = sorted(wide_q.columns)

    # unconditional matrix
    counts_uncond = np.zeros((4, 4))
    for y0, y1 in zip(years[:-1], years[1:]):
        pairs = wide_q[[y0, y1]].dropna()
        for q0, q1 in zip(pairs[y0], pairs[y1]):
            counts_uncond[int(q0) - 1, int(q1) - 1] += 1
    P_uncond = counts_uncond / counts_uncond.sum(axis=1, keepdims=True)

    # conditional matrices: for each district-year with a valid t and t+1
    # quartile, compute the (weight-averaged) modal quartile of its
    # queen-contiguity neighbours at t, and accumulate the t -> t+1
    # transition into that neighbour-quartile's conditional matrix.
    counts_cond = {q: np.zeros((4, 4)) for q in [1, 2, 3, 4]}
    quartile_matrix = wide_q[years].values  # districts x years
    n_districts = quartile_matrix.shape[0]

    for t_idx, (y0, y1) in enumerate(zip(years[:-1], years[1:])):
        q_t = wide_q[y0].values
        q_t1 = wide_q[y1].values
        for i in range(n_districts):
            if np.isnan(q_t[i]) or np.isnan(q_t1[i]):
                continue
            neighbour_weights = W[i]
            valid_neighbours = ~np.isnan(q_t) & (neighbour_weights > 0)
            if valid_neighbours.sum() == 0:
                continue
            w = neighbour_weights[valid_neighbours]
            w = w / w.sum()
            mean_neighbour_q = np.round((w * q_t[valid_neighbours]).sum()).astype(int)
            mean_neighbour_q = min(max(mean_neighbour_q, 1), 4)
            counts_cond[mean_neighbour_q][int(q_t[i]) - 1, int(q_t1[i]) - 1] += 1

    labels = ["Q1(low)", "Q2", "Q3", "Q4(high)"]
    rows = []
    all_matrices = []
    for q in [1, 2, 3, 4]:
        c = counts_cond[q]
        row_sums = c.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        P = c / row_sums
        diag_mean = np.mean(np.diag(P))
        rows.append({"Neighbour quartile": f"Q{q}" + (" (low)" if q == 1 else " (high)" if q == 4 else ""),
                     "Mean diagonal persistence": round(diag_mean, 3)})
        for a in range(4):
            for b in range(4):
                all_matrices.append({"neighbour_quartile": q, "from": labels[a], "to": labels[b],
                                      "probability": round(P[a, b], 4)})

    rows.append({"Neighbour quartile": "Unconditional",
                 "Mean diagonal persistence": round(np.mean(np.diag(P_uncond)), 3)})

    table9 = pd.DataFrame(rows)
    table9.to_csv(OUTPUT_DIR / "Table8_spatial_markov_diagonal.csv", index=False)
    print("Table 8. Diagonal persistence probabilities, by neighbour quartile")
    print(table9.to_string(index=False))

    pd.DataFrame(all_matrices).to_csv(SUPPORTING_DIR / "spatial_markov_matrices.csv", index=False)


if __name__ == "__main__":
    main()
