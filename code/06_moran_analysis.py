"""
06_moran_analysis.py
=====================
Global Moran's I (Moran, 1950) for district-level milk-yield growth
(2000-2024) and level (2020-2024 average), under the preferred queen-
contiguity spatial weight matrix (Anselin, 1988) and, as robustness
checks, k-nearest-neighbour (k = 6, 10) and fixed distance-band (<100 km)
matrices. Significance is assessed by permutation (999 random
relabellings of the weight matrix), not the analytical normal
approximation.

Produces:
  output/Table7_morans_i.csv
  output/supporting/moran_scatterplot_data.csv   (queen-contiguity growth data used by Figure 5)
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR, SEED, N_PERMUTATION_MORAN
from spatial_weights import load_geometries, build_queen_contiguity, build_knn, build_distance_band
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def morans_i(x, W):
    n = len(x)
    z = x - x.mean()
    num = n * (z[:, None] * W * z[None, :]).sum()
    den = W.sum() * (z ** 2).sum()
    return num / den


def permutation_p(x, W, observed_i, n_perm=N_PERMUTATION_MORAN, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(x)
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(n)
        i_perm = morans_i(x[perm], W)
        if abs(i_perm) >= abs(observed_i):
            count += 1
    return (count + 1) / (n_perm + 1)


def main():
    df = data_overview.load_panel()
    names, boundary_points, centroids = load_geometries()

    d0 = df[df["year"] == 2000][["region", "yield_per_cow"]].rename(columns={"yield_per_cow": "y0"})
    d1 = df[df["year"] == 2024][["region", "yield_per_cow"]].rename(columns={"yield_per_cow": "y1"})
    growth = d0.merge(d1, on="region").dropna()
    growth = growth[(growth["y0"] > 0) & (growth["y1"] > 0)]
    growth["growth"] = np.log(growth["y1"] / growth["y0"])
    growth_map = dict(zip(growth["region"], growth["growth"]))

    level = df[df["year"].between(2020, 2024)].groupby("region")["yield_per_cow"].mean()
    level_map = level.to_dict()

    aligned_names = [nm for nm in names if nm in growth_map]
    growth_vec = np.array([growth_map[nm] for nm in aligned_names])
    level_vec = np.array([level_map.get(nm, np.nan) for nm in aligned_names])
    valid_level = ~np.isnan(level_vec)

    W_queen_full = build_queen_contiguity(names, boundary_points)
    idx = [names.index(nm) for nm in aligned_names]
    W_queen = W_queen_full[np.ix_(idx, idx)]
    W_queen = W_queen / W_queen.sum(axis=1, keepdims=True)

    rows = []
    i_growth = morans_i(growth_vec, W_queen)
    p_growth = permutation_p(growth_vec, W_queen, i_growth)
    rows.append({"Specification": "Queen contiguity (primary)", "Variable": "Growth 2000-2024",
                 "Moran's I": round(i_growth, 3), "p (permutation)": round(p_growth, 3)})

    i_level = morans_i(level_vec[valid_level], W_queen[np.ix_(valid_level, valid_level)] /
                        W_queen[np.ix_(valid_level, valid_level)].sum(axis=1, keepdims=True))
    p_level = permutation_p(level_vec[valid_level],
                             W_queen[np.ix_(valid_level, valid_level)] / W_queen[np.ix_(valid_level, valid_level)].sum(axis=1, keepdims=True),
                             i_level)
    rows.append({"Specification": "Queen contiguity (primary)", "Variable": "Level 2020-2024 avg",
                 "Moran's I": round(i_level, 3), "p (permutation)": round(p_level, 3)})

    for k in [6, 10]:
        W_knn_full = build_knn(names, centroids, k)
        W_knn = W_knn_full[np.ix_(idx, idx)]
        W_knn = W_knn / W_knn.sum(axis=1, keepdims=True)
        i_k = morans_i(growth_vec, W_knn)
        p_k = permutation_p(growth_vec, W_knn, i_k)
        rows.append({"Specification": f"KNN k={k}", "Variable": "Growth 2000-2024",
                      "Moran's I": round(i_k, 3), "p (permutation)": round(p_k, 3)})

    W_db_full = build_distance_band(names, centroids, threshold_km=100)
    W_db = W_db_full[np.ix_(idx, idx)]
    row_sums = W_db.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    W_db = W_db / row_sums
    i_db = morans_i(growth_vec, W_db)
    p_db = permutation_p(growth_vec, W_db, i_db)
    rows.append({"Specification": "Distance-band <100km", "Variable": "Growth 2000-2024",
                 "Moran's I": round(i_db, 3), "p (permutation)": round(p_db, 3)})

    table8 = pd.DataFrame(rows)
    table8.to_csv(OUTPUT_DIR / "Table7_morans_i.csv", index=False)
    print("Table 7. Global Moran's I: queen contiguity (primary) and robustness")
    print(table8.to_string(index=False))

    # data for the Moran scatterplot (Figure 5): growth vs. spatial lag of growth
    spatial_lag = W_queen @ growth_vec
    scatter = pd.DataFrame({
        "region": aligned_names,
        "growth_dev": growth_vec - growth_vec.mean(),
        "spatial_lag_dev": spatial_lag - spatial_lag.mean(),
    })
    scatter.to_csv(SUPPORTING_DIR / "moran_scatterplot_data.csv", index=False)


if __name__ == "__main__":
    main()
