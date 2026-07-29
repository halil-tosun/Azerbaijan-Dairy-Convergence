"""
08_extensive_intensive.py
===========================
Decomposes the 2000-2024 change in each district's total milk
production into an extensive margin (herd-size growth), an intensive
margin (yield growth), and an interaction term, using the exact
multiplicative identity:

    Delta(Milk) = Yield_0 * Delta(Cows) + Cows_0 * Delta(Yield)
                  + Delta(Cows) * Delta(Yield)

and cross-tabulates each district's dominant margin against its 2024
relative-yield quartile (Table 9c), and, identically, against its 2000
quartile (reported in Section 6 text, not as a separate table).

Produces:
  output/Table9a_ext_int_national_aggregate.csv
  output/Table9b_ext_int_dominant_margin_counts.csv
  output/Table9c_quartile_by_dominant_margin.csv
  output/supporting/ext_int_by_district.csv   (used by Figure 7)
  output/supporting/quartile2000_by_dominant_margin.csv
"""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from _paths import OUTPUT_DIR, SUPPORTING_DIR
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)


def main():
    df = data_overview.load_panel()

    d0 = df[df["year"] == 2000][["region", "yield_per_cow", "cows_dairy_buffaloes_stock_heads", "milk_production_tons"]]
    d0 = d0.rename(columns={"yield_per_cow": "yield0", "cows_dairy_buffaloes_stock_heads": "cows0", "milk_production_tons": "milk0"})
    d1 = df[df["year"] == 2024][["region", "yield_per_cow", "cows_dairy_buffaloes_stock_heads", "milk_production_tons"]]
    d1 = d1.rename(columns={"yield_per_cow": "yield1", "cows_dairy_buffaloes_stock_heads": "cows1", "milk_production_tons": "milk1"})
    m = d0.merge(d1, on="region").dropna()

    m["delta_cows"] = m["cows1"] - m["cows0"]
    m["delta_yield"] = m["yield1"] - m["yield0"]
    m["extensive"] = m["yield0"] * m["delta_cows"]
    m["intensive"] = m["cows0"] * m["delta_yield"]
    m["interaction"] = m["delta_cows"] * m["delta_yield"]
    m["delta_milk"] = m["milk1"] * 1000 - m["milk0"] * 1000  # kg, matching yield units

    m["ext_share"] = m["extensive"] / (m["extensive"] + m["intensive"] + m["interaction"])
    m["int_share"] = m["intensive"] / (m["extensive"] + m["intensive"] + m["interaction"])
    m["inter_share"] = m["interaction"] / (m["extensive"] + m["intensive"] + m["interaction"])

    m.to_csv(SUPPORTING_DIR / "ext_int_by_district.csv", index=False)

    # --- Table 10: national aggregate ---
    total_ext = m["extensive"].sum()
    total_int = m["intensive"].sum()
    total_inter = m["interaction"].sum()
    total = total_ext + total_int + total_inter
    table9a = pd.DataFrame([
        {"Component": "Extensive margin (herd growth)", "Share of total growth (%)": round(100 * total_ext / total, 1)},
        {"Component": "Intensive margin (yield growth)", "Share of total growth (%)": round(100 * total_int / total, 1)},
        {"Component": "Interaction term", "Share of total growth (%)": round(100 * total_inter / total, 1)},
    ])
    table9a.to_csv(OUTPUT_DIR / "Table9a_ext_int_national_aggregate.csv", index=False)
    print("Table 9a. Extensive/intensive margin decomposition: national aggregate")
    print(table9a.to_string(index=False))

    # --- Table 11: dominant margin counts ---
    m["dominant"] = np.where(m["ext_share"] > m["int_share"], "Extensive", "Intensive")
    counts = m["dominant"].value_counts()
    table9b = pd.DataFrame([
        {"Dominant margin": "Intensive", "Districts": int(counts.get("Intensive", 0))},
        {"Dominant margin": "Extensive", "Districts": int(counts.get("Extensive", 0))},
    ])
    table9b.to_csv(OUTPUT_DIR / "Table9b_ext_int_dominant_margin_counts.csv", index=False)
    print("\nTable 9b. Districts by dominant growth margin")
    print(table9b.to_string(index=False))

    # --- Table 12: 2024 quartile x dominant margin cross-tab ---
    df2 = df.copy()
    df2["national_mean"] = df2.groupby("year")["yield_per_cow"].transform("mean")
    df2["relative_yield"] = df2["yield_per_cow"] / df2["national_mean"]
    cuts = df2["relative_yield"].quantile([0.25, 0.5, 0.75]).values

    def quartile(x):
        if x <= cuts[0]:
            return 1
        elif x <= cuts[1]:
            return 2
        elif x <= cuts[2]:
            return 3
        return 4

    q2024 = df2[df2["year"] == 2024][["region", "relative_yield"]].copy()
    q2024["quartile"] = q2024["relative_yield"].apply(quartile)
    merged = m[["region", "dominant"]].merge(q2024[["region", "quartile"]], on="region")

    ct = pd.crosstab(merged["quartile"], merged["dominant"])
    ct = ct.reindex(columns=["Extensive", "Intensive"], fill_value=0)
    chi2, p, dof, _ = chi2_contingency(ct)

    table9c = ct.reset_index()
    table9c["quartile"] = table9c["quartile"].map({1: "Q1 (low)", 2: "Q2", 3: "Q3", 4: "Q4 (high)"})
    table9c = table9c.rename(columns={"quartile": "2024 quartile", "Extensive": "Extensive-dominated", "Intensive": "Intensive-dominated"})
    table9c.to_csv(OUTPUT_DIR / "Table9c_quartile_by_dominant_margin.csv", index=False)
    print("\nTable 9c. Dominant growth margin by 2024 productivity quartile")
    print(table9c.to_string(index=False))
    print(f"\nChi-square = {chi2:.2f}, df = {dof}, p = {p:.3g}, N = {ct.values.sum()}")

    # --- Reported in Section 6 text (not a separate table): the equivalent
    # cross-tabulation against each district's 2000 quartile, testing
    # whether the margin/quartile association strengthens over the
    # sample period rather than simply reflecting initial conditions. ---
    q2000 = df2[df2["year"] == 2000][["region", "relative_yield"]].copy()
    q2000["quartile"] = q2000["relative_yield"].apply(quartile)
    merged_2000 = m[["region", "dominant"]].merge(q2000[["region", "quartile"]], on="region")

    ct_2000 = pd.crosstab(merged_2000["quartile"], merged_2000["dominant"])
    ct_2000 = ct_2000.reindex(columns=["Extensive", "Intensive"], fill_value=0)
    chi2_2000, p_2000, dof_2000, _ = chi2_contingency(ct_2000)

    table_2000 = ct_2000.reset_index()
    table_2000["quartile"] = table_2000["quartile"].map({1: "Q1 (low)", 2: "Q2", 3: "Q3", 4: "Q4 (high)"})
    table_2000 = table_2000.rename(columns={"quartile": "2000 quartile", "Extensive": "Extensive-dominated", "Intensive": "Intensive-dominated"})
    table_2000.to_csv(SUPPORTING_DIR / "quartile2000_by_dominant_margin.csv", index=False)
    print("\n2000 quartile x dominant growth margin (reported in Section 6 text, not a numbered table)")
    print(table_2000.to_string(index=False))
    print(f"\nChi-square = {chi2_2000:.2f}, df = {dof_2000}, p = {p_2000:.3g}, N = {ct_2000.values.sum()}")


if __name__ == "__main__":
    main()
