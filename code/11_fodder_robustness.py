"""
11_fodder_robustness.py
=========================
Two checks reported in Section 7.6 of the manuscript:

  1. Coverage rates for the production variables not used in the
     convergence models (labour hours, unit cost, profitability),
     compared with fodder-crop area and the core production variables,
     motivating their exclusion (documented further in Section 8).
  2. A beta-convergence regression re-estimated on the subsample of
     districts with non-missing 2000 fodder-crop area, with log
     fodder-crop area added as an additional control, to confirm the
     convergence result is not confounded by cross-district differences
     in feed-land availability.

Produces:
  output/supporting/variable_coverage_rates.csv
  output/supporting/fodder_control_robustness.csv
"""
import numpy as np
import pandas as pd
from scipy import stats
from _paths import RAW_PANEL_CSV, OUTPUT_DIR, SUPPORTING_DIR
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def main():
    raw = pd.read_csv(RAW_PANEL_CSV)
    n_total = len(raw)

    coverage_vars = [
        ("milk_production_tons", "Milk production"),
        ("cows_dairy_buffaloes_stock_heads", "Dairy cattle stock"),
        ("fodder_sown_area_ha", "Fodder-crop sown area"),
        ("labour_hours_per_centner_milk_enterprises", "Labour hours (enterprises)"),
        ("cost_price_per_centner_milk_enterprises_manat", "Unit cost (enterprises)"),
        ("profitability_milk_enterprises_pct", "Profitability (enterprises)"),
    ]
    rows = []
    for col, label in coverage_vars:
        n_valid = raw[col].notna().sum()
        rows.append({
            "Variable": label,
            "N valid": int(n_valid),
            "N total": n_total,
            "% missing": round(100 * (1 - n_valid / n_total), 1),
        })
    coverage = pd.DataFrame(rows)
    coverage.to_csv(SUPPORTING_DIR / "variable_coverage_rates.csv", index=False)
    print("Coverage rates for production variables (Sections 7.6 and 8)")
    print(coverage.to_string(index=False))

    # --- Fodder-crop area control robustness ---
    df = data_overview.load_panel()
    d0 = df[df["year"] == 2000][["region", "yield_per_cow", "fodder_sown_area_ha"]].rename(columns={"yield_per_cow": "y0"})
    d1 = df[df["year"] == 2024][["region", "yield_per_cow"]].rename(columns={"yield_per_cow": "y1"})
    m = d0.merge(d1, on="region").dropna()
    m = m[(m["y0"] > 0) & (m["y1"] > 0) & (m["fodder_sown_area_ha"] > 0)]

    m["log_y0"] = np.log(m["y0"])
    m["growth"] = (np.log(m["y1"]) - np.log(m["y0"])) / 24
    m["log_fodder0"] = np.log(m["fodder_sown_area_ha"])

    def fit(X, y):
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ b
        n, k = X.shape
        cov = (resid @ resid) / (n - k) * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.diag(cov))
        return b, se, n

    X1 = np.column_stack([np.ones(len(m)), m["log_y0"]])
    y = m["growth"].values
    b1, se1, n1 = fit(X1, y)
    t1 = b1[1] / se1[1]

    X2 = np.column_stack([np.ones(len(m)), m["log_y0"], m["log_fodder0"]])
    b2, se2, n2 = fit(X2, y)
    t2_beta = b2[1] / se2[1]
    t2_fodder = b2[2] / se2[2]

    result = pd.DataFrame([
        {"Specification": "No control", "Beta": round(b1[1], 3), "SE": round(se1[1], 3),
         "t": round(t1, 2), "N": n1, "Fodder-area coefficient": "-", "Fodder t-stat": "-"},
        {"Specification": "With log fodder-crop area control", "Beta": round(b2[1], 3), "SE": round(se2[1], 3),
         "t": round(t2_beta, 2), "N": n2, "Fodder-area coefficient": round(b2[2], 4), "Fodder t-stat": round(t2_fodder, 2)},
    ])
    result.to_csv(SUPPORTING_DIR / "fodder_control_robustness.csv", index=False)
    print("\nBeta-convergence with and without a fodder-crop area control (Section 7.6)")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
