"""
01_data_overview.py
====================
Loads the raw district-year panel and produces:

  Table 1 -- variable definitions and data sources (static metadata)
  Table 2 -- descriptive statistics for the full unbalanced panel

Milk yield per cow (kg/head) is computed as milk production (tons,
converted to kg) divided by dairy cattle stock (head). Rows with
non-positive or missing yield are dropped before descriptive statistics
are computed, consistent with every subsequent script in this package.

Produces:
  output/Table1_variable_definitions.csv
  output/Table2_descriptive_statistics.csv
"""
import pandas as pd
from _paths import RAW_PANEL_CSV, OUTPUT_DIR


def load_panel(drop_invalid_yield=True):
    """Load the raw panel and compute milk yield per cow (kg/head).

    This helper is imported by every other script in this package so
    that the same 66-district, 2000-2024 analytical panel is used
    throughout.

    If `drop_invalid_yield` is True (the default, used by every
    convergence/distribution/spatial script), rows with non-positive or
    undefined yield are dropped. Table 2 below intentionally calls this
    with `drop_invalid_yield=False` because each raw variable's own N
    differs slightly (milk production has one fewer valid observation
    than cattle stock, for example), and Table 2 reports each variable's
    own valid-observation count rather than the count after the
    yield-based row filter used everywhere else.
    """
    df = pd.read_csv(RAW_PANEL_CSV)
    df["yield_per_cow"] = (
        df["milk_production_tons"] * 1000 / df["cows_dairy_buffaloes_stock_heads"]
    )
    if drop_invalid_yield:
        df = df[df["yield_per_cow"] > 0].copy()
    return df


def main():
    table1 = pd.DataFrame([
        {"Variable": "Milk yield per cow",
         "Definition": "Milk production divided by dairy cattle stock (kg/head)",
         "Role": "Primary convergence/distribution-dynamics outcome"},
        {"Variable": "Relative yield",
         "Definition": "Milk yield per cow divided by contemporaneous national mean",
         "Role": "Distribution dynamics (Sec. 4)"},
        {"Variable": "Dairy cattle stock",
         "Definition": "Number of dairy cattle (head)",
         "Role": "Extensive-margin input (Sec. 6)"},
        {"Variable": "Fodder-crop sown area",
         "Definition": "Area allocated to fodder-crop cultivation (ha)",
         "Role": "Production input (not used in convergence models)"},
        {"Variable": "Milk production",
         "Definition": "Total annual milk production (tons)",
         "Role": "Extensive/intensive decomposition (Sec. 6)"},
    ])
    table1.to_csv(OUTPUT_DIR / "Table1_variable_definitions.csv", index=False)
    print("Table 1. Variable definitions and data sources")
    print(table1.to_string(index=False))

    df = load_panel(drop_invalid_yield=False)

    def describe(col, label):
        s = df[col].dropna()
        s = s[s > 0]
        return {
            "Variable": label,
            "N": int(s.count()),
            "Mean": round(s.mean(), 1),
            "SD": round(s.std(), 1),
            "Min": round(s.min(), 1),
            "Max": round(s.max(), 1),
        }

    table2 = pd.DataFrame([
        describe("milk_production_tons", "Milk production (tons)"),
        describe("cows_dairy_buffaloes_stock_heads", "Dairy cattle stock (head)"),
        describe("fodder_sown_area_ha", "Fodder-crop sown area (ha)"),
        describe("yield_per_cow", "Milk yield per cow (kg)"),
    ])
    table2.to_csv(OUTPUT_DIR / "Table2_descriptive_statistics.csv", index=False)
    print("\nTable 2. Descriptive statistics (full district panel)")
    print(table2.to_string(index=False))


if __name__ == "__main__":
    main()
