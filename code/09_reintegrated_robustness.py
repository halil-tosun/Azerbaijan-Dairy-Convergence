"""
09_reintegrated_robustness.py
===============================
Re-estimates beta-convergence for the full 2000-2024 period and for
each five-year sub-period, excluding the nine districts affected by
conflict-related disruption to production and reintegrated from 2020
onward (Section 7.2 of the manuscript).

Produces:
  output/Table10_subperiod_excl_reintegrated.csv
  output/supporting/full_period_excl_reintegrated.csv
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR, REINTEGRATED_DISTRICTS
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)

spec3 = importlib.util.spec_from_file_location("beta_convergence", os.path.join(os.path.dirname(__file__), "03_beta_convergence.py"))
beta_convergence = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(beta_convergence)

spec2 = importlib.util.spec_from_file_location("sigma_convergence", os.path.join(os.path.dirname(__file__), "02_sigma_convergence.py"))
sigma_convergence = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(sigma_convergence)


def main():
    df = data_overview.load_panel()
    df_excl = df[~df["region"].isin(REINTEGRATED_DISTRICTS)].copy()

    breakpoints = [2000, 2005, 2010, 2015, 2020, 2024]
    rows = []
    for y0, y1 in zip(breakpoints[:-1], breakpoints[1:]):
        beta_full, se_full, t_full, p_full, n_full, _ = beta_convergence.cross_section(df, y0=y0, y1=y1)
        beta_excl, se_excl, t_excl, p_excl, n_excl, _ = beta_convergence.cross_section(df_excl, y0=y0, y1=y1)
        rows.append({
            "Period": f"{y0}-{y1}",
            "Full sample beta (p)": f"{'+' if beta_full > 0 else ''}{beta_full:.3f} ({'p<0.001' if p_full < 0.001 else round(p_full, 3)})",
            "Excluding reintegrated districts beta (p)": f"{'+' if beta_excl > 0 else ''}{beta_excl:.3f} ({'p<0.001' if p_excl < 0.001 else round(p_excl, 3)})",
        })
    table10 = pd.DataFrame(rows)
    table10.to_csv(OUTPUT_DIR / "Table10_subperiod_excl_reintegrated.csv", index=False)
    print("Table 10. Beta-convergence by five-year sub-period, excluding reintegrated districts")
    print(table10.to_string(index=False))

    # Full-period (2000-2024) sigma and beta, with vs. without reintegrated districts
    def cv_by_year(data, year):
        g = data[data["year"] == year]
        rel = g["yield_per_cow"] / g["yield_per_cow"].mean()
        return rel.std() / rel.mean()

    beta_full, se_full, *_ = beta_convergence.cross_section(df)
    beta_excl, se_excl, *_ = beta_convergence.cross_section(df_excl)

    summary = pd.DataFrame([
        {"Sample": "Full sample", "CV 2000": round(cv_by_year(df, 2000), 3), "CV 2024": round(cv_by_year(df, 2024), 3),
         "Beta (2000-2024)": round(beta_full, 3), "SE": round(se_full, 3)},
        {"Sample": "Excluding reintegrated districts", "CV 2000": round(cv_by_year(df_excl, 2000), 3),
         "CV 2024": round(cv_by_year(df_excl, 2024), 3), "Beta (2000-2024)": round(beta_excl, 3), "SE": round(se_excl, 3)},
    ])
    summary.to_csv(SUPPORTING_DIR / "full_period_excl_reintegrated.csv", index=False)
    print("\nFull-period (2000-2024) sigma- and beta-convergence, with vs. without reintegrated districts")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
