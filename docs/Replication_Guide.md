# Replication Guide

This guide walks through reproducing every table and figure in the
accompanying manuscript, step by step.

## 1. Set Up the Environment

**Option A — Conda (recommended)**

```bash
conda env create -f environment.yml
conda activate azerbaijan-dairy-convergence-repro
```

**Option B — pip**

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the Full Pipeline

```bash
cd code
python run_all.py
```

You should see console output for thirteen steps, each printing the
table(s) or figure(s) it produces, followed by a total runtime (under
one minute on a standard laptop).

## 3. Verify the Outputs

After running, check that the following files exist:

```
output/Table1_variable_definitions.csv
output/Table2_descriptive_statistics.csv
output/Table3_sigma_convergence.csv
output/Table4a_beta_convergence_cross_sectional.csv
output/Table4b_pooled_vs_panel_fe.csv
output/Table4c_beta_convergence_by_subperiod.csv
output/Table5_silverman_test.csv
output/Table6_markov_transition_matrix.csv
output/Table7_morans_i.csv
output/Table8_spatial_markov_diagonal.csv
output/Table9a_ext_int_national_aggregate.csv
output/Table9b_ext_int_dominant_margin_counts.csv
output/Table9c_quartile_by_dominant_margin.csv
output/Table10_subperiod_excl_reintegrated.csv

output/supporting/sigma_convergence_full_series.csv
output/supporting/kernel_density_grid.csv
output/supporting/shorrocks_mobility_index.txt
output/supporting/moran_scatterplot_data.csv
output/supporting/spatial_markov_matrices.csv
output/supporting/ext_int_by_district.csv
output/supporting/full_period_excl_reintegrated.csv
output/supporting/dynamic_panel_bias_check.csv
output/supporting/fodder_control_robustness.csv
output/supporting/variable_coverage_rates.csv
output/supporting/quartile2000_by_dominant_margin.csv

figures/Figure1_study_area_map.png
figures/Figure2_sigma_beta_convergence.png
figures/Figure3_kernel_density.png
figures/Figure4_markov_heatmap.png
figures/Figure5_moran_scatterplot.png
figures/Figure6_spatial_markov.png
figures/Figure7_extensive_intensive.png
```

Ten additional files -- intermediate data used only to build figures, or
statistics reported in the manuscript's text (Sections 7.4, 7.6, and 8)
rather than in a numbered table -- are written to `output/supporting/`
and are not themselves numbered manuscript tables.

## 4. Cross-Check Against the Manuscript

Open each CSV in `output/` and compare its values against the
corresponding table in the manuscript. All values should match exactly
(to the rounding shown). If you find a discrepancy, please open an issue
in this repository, including your Python and package versions.

## 5. Regenerate a Single Table or Figure

Each numbered script can be run independently, for example:

```bash
cd code
python 06_moran_analysis.py
```

This is useful if you only want to re-verify one specific result (e.g.
the spatial autocorrelation analysis) without rerunning the full
pipeline. Scripts `03`, `05`, `06`, `07`, `08`, `09`, and `10` all import
`01_data_overview.py`'s `load_panel()` function, so `01` does not need
to be run first for these to work standalone; it is included in
`run_all.py` purely for its own table output (Table 1, Table 2).
`13_make_figures.py` reads the CSV outputs of scripts `02`-`08`, so those
must be run at least once beforehand (as `run_all.py` does automatically)
before `13` can regenerate the figures.

## 6. Understanding the Data

Before reusing or extending this dataset, read
`docs/DATA_DESCRIPTION.md` in full, particularly the sections "Why
Labour, Cost, and Profitability Variables Are Not Used" and "The Nine
Reintegrated Districts."

## 7. Troubleshooting

- **`ModuleNotFoundError`**: confirm the environment from Step 1 is
  activated before running `run_all.py`.
- **Bootstrap/permutation results differ slightly from the manuscript**:
  confirm you have not modified `SEED` in `code/_paths.py`. With the
  default seed (1) and the pinned package versions in
  `requirements.txt`, results should match exactly.
- **Spatial analysis scripts run slowly or raise a district-matching
  warning**: confirm `data/raw/geoBoundaries-AZE-ADM2.geojson` has not
  been modified; `spatial_weights.py` expects 73 successfully matched
  districts.
- **Figures look different from the manuscript**: confirm your
  matplotlib version matches `requirements.txt`; minor rendering
  differences across matplotlib versions do not affect the reported
  statistics, only cosmetic details (marker size, font rendering).
