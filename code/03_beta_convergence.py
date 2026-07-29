"""
03_beta_convergence.py
=======================
Cross-sectional and panel beta-convergence regressions of milk yield
per cow, following Barro and Sala-i-Martin (1992) and, for the panel
fixed-effects specification, Islam (1995).

Produces:
  output/Table4a_beta_convergence_cross_sectional.csv
  output/Table4b_pooled_vs_panel_fe.csv
  output/Table4c_beta_convergence_by_subperiod.csv
"""
import numpy as np
import pandas as pd
from scipy import stats
from _paths import OUTPUT_DIR
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def ols_beta(log_y0, growth):
    """Simple OLS of growth on log(initial level); returns beta, SE, t, p, N."""
    X = np.column_stack([np.ones(len(log_y0)), log_y0])
    y = np.asarray(growth)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    n, k = X.shape
    se = np.sqrt((resid @ resid) / (n - k) * np.linalg.inv(X.T @ X)[1, 1])
    t = b[1] / se
    p = 2 * (1 - stats.t.cdf(abs(t), n - k))
    half_life = np.log(2) / (-b[1]) if b[1] < 0 else np.nan
    return b[1], se, t, p, n, half_life


def cross_section(df, y0=2000, y1=2024, min_herd=None, weight_col=None):
    d0 = df[df["year"] == y0][["region", "yield_per_cow", "cows_dairy_buffaloes_stock_heads"]].rename(
        columns={"yield_per_cow": "y0", "cows_dairy_buffaloes_stock_heads": "herd0"})
    d1 = df[df["year"] == y1][["region", "yield_per_cow"]].rename(columns={"yield_per_cow": "y1"})
    m = d0.merge(d1, on="region").dropna()
    m = m[(m["y0"] > 0) & (m["y1"] > 0)]
    if min_herd is not None:
        m = m[m["herd0"] >= min_herd]
    span = y1 - y0
    m["log_y0"] = np.log(m["y0"])
    m["growth"] = (np.log(m["y1"]) - np.log(m["y0"])) / span
    if weight_col is None:
        return ols_beta(m["log_y0"], m["growth"])
    else:
        # weighted least squares by initial herd size
        w = np.sqrt(m[weight_col].values)
        X = np.column_stack([np.ones(len(m)), m["log_y0"]]) * w[:, None]
        y = m["growth"].values * w
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ b
        n, k = X.shape
        se = np.sqrt((resid @ resid) / (n - k) * np.linalg.inv(X.T @ X)[1, 1])
        t = b[1] / se
        p = 2 * (1 - stats.t.cdf(abs(t), n - k))
        half_life = np.log(2) / (-b[1]) if b[1] < 0 else np.nan
        return b[1], se, t, p, n, half_life


def panel_fe(df, breakpoints):
    """Islam (1995) panel fixed-effects (LSDV) beta-convergence."""
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

    # pooled OLS
    beta_pool, se_pool, t_pool, p_pool, n_pool, _ = ols_beta(panel["log_y0"], panel["growth"])

    # LSDV: demean by region and by period, then OLS (equivalent to two-way FE)
    panel["log_y0_dm"] = (
        panel["log_y0"]
        - panel.groupby("region")["log_y0"].transform("mean")
        - panel.groupby("t")["log_y0"].transform("mean")
        + panel["log_y0"].mean()
    )
    panel["growth_dm"] = (
        panel["growth"]
        - panel.groupby("region")["growth"].transform("mean")
        - panel.groupby("t")["growth"].transform("mean")
        + panel["growth"].mean()
    )
    X = panel["log_y0_dm"].values.reshape(-1, 1)
    y = panel["growth_dm"].values
    b = np.linalg.lstsq(X, y, rcond=None)[0][0]
    resid = y - X.flatten() * b
    n = len(panel)
    n_regions = panel["region"].nunique()
    n_periods = panel["t"].nunique()
    dof = n - n_regions - n_periods - 1  # approx dof for two-way FE
    dof = max(dof, 1)
    se = np.sqrt((resid @ resid) / dof / (X.flatten() @ X.flatten()))
    return (beta_pool, se_pool, n_pool), (b, se, n)


def main():
    df = data_overview.load_panel()

    # --- Table 4a: cross-sectional specifications ---
    rows = []
    beta, se, t, p, n, hl = cross_section(df)
    rows.append({"Specification": "Absolute (2000-2024, unweighted)", "N": n, "Beta": round(beta, 3),
                  "SE": round(se, 3), "t": round(t, 2), "p": round(p, 3), "Half-life (yrs)": round(hl, 1)})

    beta, se, t, p, n, hl = cross_section(df, min_herd=50)
    rows.append({"Specification": "Min herd >= 50 in 2000", "N": n, "Beta": round(beta, 3),
                  "SE": round(se, 3), "t": round(t, 2), "p": round(p, 3), "Half-life (yrs)": round(hl, 1)})

    beta, se, t, p, n, hl = cross_section(df, weight_col="herd0")
    rows.append({"Specification": "Weighted by 2000 herd size", "N": n, "Beta": round(beta, 3),
                  "SE": round(se, 3), "t": round(t, 2), "p": round(p, 3), "Half-life (yrs)": round(hl, 1)})

    beta, se, t, p, n, hl = cross_section(df, y0=2000, y1=2019)
    rows.append({"Specification": "Sub-period (2000-2019)", "N": n, "Beta": round(beta, 3),
                  "SE": round(se, 3), "t": round(t, 2), "p": round(p, 3), "Half-life (yrs)": round(hl, 1)})

    beta, se, t, p, n, hl = cross_section(df, y0=2005, y1=2024)
    rows.append({"Specification": "Sub-period (2005-2024)", "N": n, "Beta": round(beta, 3),
                  "SE": round(se, 3), "t": round(t, 2), "p": round(p, 3), "Half-life (yrs)": round(hl, 1)})

    table4a = pd.DataFrame(rows)
    table4a.to_csv(OUTPUT_DIR / "Table4a_beta_convergence_cross_sectional.csv", index=False)
    print("Table 4a. Beta-convergence regressions: cross-sectional specifications")
    print(table4a.to_string(index=False))

    # --- Table 4b: pooled OLS vs. panel FE (Islam, 1995) ---
    breakpoints = [2000, 2005, 2010, 2015, 2020, 2024]
    (beta_pool, se_pool, n_pool), (beta_fe, se_fe, n_fe) = panel_fe(df, breakpoints)
    table4b = pd.DataFrame([
        {"Specification": "Pooled OLS", "Beta": round(beta_pool, 3), "SE": round(se_pool, 3), "N": n_pool},
        {"Specification": "Panel FE (district + period)", "Beta": round(beta_fe, 3), "SE": round(se_fe, 3), "N": n_fe},
    ])
    table4b.to_csv(OUTPUT_DIR / "Table4b_pooled_vs_panel_fe.csv", index=False)
    print("\nTable 4b. Pooled OLS vs. panel fixed effects (Islam, 1995)")
    print(table4b.to_string(index=False))

    # --- Table 4c: beta-convergence by five-year sub-period ---
    rows = []
    for y0, y1 in zip(breakpoints[:-1], breakpoints[1:]):
        beta, se, t, p, n, hl = cross_section(df, y0=y0, y1=y1)
        sign = "+" if beta > 0 else ""
        rows.append({"Period": f"{y0}-{y1}", "Beta": f"{sign}{beta:.3f}", "SE": round(se, 3),
                     "t": round(t, 2), "N": n})
    table4c = pd.DataFrame(rows)
    table4c.to_csv(OUTPUT_DIR / "Table4c_beta_convergence_by_subperiod.csv", index=False)
    print("\nTable 4c. Beta-convergence by five-year sub-period")
    print(table4c.to_string(index=False))


if __name__ == "__main__":
    main()
