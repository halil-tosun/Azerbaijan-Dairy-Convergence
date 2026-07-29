"""
02_sigma_convergence.py
========================
Computes cross-sectional dispersion of relative milk yield per cow for
each year, 2000-2024 (coefficient of variation and Gini coefficient),
and tests the trend in dispersion for statistical significance using
the non-parametric Mann-Kendall test (Mann, 1945; Kendall, 1975).

Produces:
  output/supporting/sigma_convergence_full_series.csv   (all 25 years)
  output/Table3_sigma_convergence.csv        (selected years, as shown in the manuscript)
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT_DIR, SUPPORTING_DIR
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def gini(x):
    """Standard Gini coefficient for a non-negative array."""
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    cum = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cum) / cum[-1]) / n


def mann_kendall(x):
    """Mann-Kendall trend test (Mann, 1945; Kendall, 1975).

    Returns the standardised test statistic Z and a two-sided p-value.
    """
    from scipy.stats import norm
    n = len(x)
    s = 0
    for k in range(n - 1):
        s += np.sum(np.sign(np.array(x[k + 1:]) - x[k]))
    var_s = n * (n - 1) * (2 * n + 5) / 18
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    p = 2 * (1 - norm.cdf(abs(z)))
    return z, p


def main():
    df = data_overview.load_panel()
    df["national_mean"] = df.groupby("year")["yield_per_cow"].transform("mean")
    df["relative_yield"] = df["yield_per_cow"] / df["national_mean"]

    rows = []
    for year, g in df.groupby("year"):
        rows.append({
            "Year": int(year),
            "N": int(len(g)),
            "Mean": round(g["yield_per_cow"].mean(), 1),
            "CV": round(g["relative_yield"].std() / g["relative_yield"].mean(), 3),
            "Gini": round(gini(g["relative_yield"].values), 3),
        })
    table_full = pd.DataFrame(rows).sort_values("Year")
    table_full.to_csv(SUPPORTING_DIR / "sigma_convergence_full_series.csv", index=False)

    selected_years = [2000, 2005, 2010, 2015, 2020, 2024]
    table_sel = table_full[table_full["Year"].isin(selected_years)]
    table_sel.to_csv(OUTPUT_DIR / "Table3_sigma_convergence.csv", index=False)

    print("Table 3. Sigma-convergence statistics by year (selected years; full 25-year series in output/supporting/sigma_convergence_full_series.csv)")
    print(table_sel.to_string(index=False))

    z, p = mann_kendall(table_full.sort_values("Year")["CV"].values)
    print(f"\nMann-Kendall test for trend in CV, 2000-2024: Z = {z:.2f}, p = {p:.3g}")


if __name__ == "__main__":
    main()
