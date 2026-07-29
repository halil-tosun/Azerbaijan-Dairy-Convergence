"""
10_dynamic_panel_bias.py
==========================
Checks the panel fixed-effects beta-convergence estimate (Table 4b) for
short-T dynamic panel bias (Nickell, 1981) using an Anderson and Hsiao
(1982) first-differenced instrumental-variables estimator: the
differenced lagged level is instrumented with its second lag. Reports
the estimate together with the first-stage F-statistic (Staiger and
Stock, 1997) as a weak-instrument diagnostic.

This is a reported robustness check (Section 7.4 of the manuscript),
not a table; results are printed and written to a summary CSV.

Produces:
  output/supporting/dynamic_panel_bias_check.csv
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def main():
    df = data_overview.load_panel()
    breakpoints = [2000, 2005, 2010, 2015, 2020, 2024]

    records = []
    for t, (y0, y1) in enumerate(zip(breakpoints[:-1], breakpoints[1:]), start=1):
        d0 = df[df["year"] == y0][["region", "yield_per_cow"]].rename(columns={"yield_per_cow": "y0"})
        d1 = df[df["year"] == y1][["region", "yield_per_cow"]].rename(columns={"yield_per_cow": "y1"})
        m = d0.merge(d1, on="region").dropna()
        m = m[(m["y0"] > 0) & (m["y1"] > 0)]
        span = y1 - y0
        m["log_y0"] = np.log(m["y0"])
        m["growth"] = (np.log(m["y1"]) - np.log(m["y0"])) / span
        m["t"] = t
        records.append(m[["region", "t", "log_y0", "growth"]])
    panel = pd.concat(records).reset_index(drop=True)

    wide_g = panel.pivot(index="region", columns="t", values="growth")
    wide_l = panel.pivot(index="region", columns="t", values="log_y0")

    rows = []
    for region in wide_g.index:
        for t in [3, 4, 5]:  # need t-2, i.e. t >= 3
            try:
                dG = wide_g.loc[region, t] - wide_g.loc[region, t - 1]
                dL = wide_l.loc[region, t] - wide_l.loc[region, t - 1]
                Z = wide_l.loc[region, t - 2]
                if np.isfinite(dG) and np.isfinite(dL) and np.isfinite(Z):
                    rows.append({"region": region, "t": t, "dG": dG, "dL": dL, "Z": Z})
            except KeyError:
                continue
    ah = pd.DataFrame(rows)
    period_dum = pd.get_dummies(ah["t"], prefix="t", drop_first=True).astype(float)

    # First stage: dL ~ Z + period dummies (F-test for instrument relevance)
    X_full = np.column_stack([np.ones(len(ah)), ah["Z"].values, period_dum.values])
    X_restricted = np.column_stack([np.ones(len(ah)), period_dum.values])
    y = ah["dL"].values

    def rss(X, y):
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ b
        return r @ r, X.shape[1]

    rss_full, k_full = rss(X_full, y)
    rss_restr, k_restr = rss(X_restricted, y)
    n = len(y)
    f_stat = ((rss_restr - rss_full) / (k_full - k_restr)) / (rss_full / (n - k_full))

    b1, *_ = np.linalg.lstsq(X_full, y, rcond=None)
    dL_hat = X_full @ b1

    X2 = np.column_stack([np.ones(len(ah)), dL_hat, period_dum.values])
    y2 = ah["dG"].values
    b2, *_ = np.linalg.lstsq(X2, y2, rcond=None)

    X2_actual = np.column_stack([np.ones(len(ah)), ah["dL"].values, period_dum.values])
    resid2_actual = y2 - X2_actual @ b2
    n2, k2 = X2.shape
    sigma2 = (resid2_actual @ resid2_actual) / (n2 - k2)
    cov2 = sigma2 * np.linalg.inv(X2.T @ X2)
    se2 = np.sqrt(np.diag(cov2))

    beta_ah, se_ah = b2[1], se2[1]
    t_ah = beta_ah / se_ah

    summary = pd.DataFrame([{
        "Estimator": "Anderson-Hsiao (1982) first-differenced IV",
        "Beta": round(beta_ah, 3),
        "SE": round(se_ah, 3),
        "t": round(t_ah, 2),
        "N": n2,
        "Districts": ah["region"].nunique(),
        "First-stage F": round(f_stat, 2),
    }])
    summary.to_csv(SUPPORTING_DIR / "dynamic_panel_bias_check.csv", index=False)
    print("Anderson-Hsiao (1982) first-differenced IV check (Section 7.4)")
    print(summary.to_string(index=False))
    print(f"\nFirst-stage F = {f_stat:.2f} (Staiger and Stock, 1997, rule-of-thumb threshold: 10)")


if __name__ == "__main__":
    main()
