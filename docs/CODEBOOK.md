# CODEBOOK

## Analytical Workflow

This package reproduces every table and figure reported in the
accompanying manuscript from a single raw input file
(`data/raw/azerbaijan_dairy_panel_WIDE_districts.csv`) plus one
administrative-boundary file
(`data/raw/geoBoundaries-AZE-ADM2.geojson`) used only for the spatial
analyses (Moran's I, spatial Markov chain, and Figure 1).

| Script | Description | Produces |
|---|---|---|
| `_paths.py` | Shared path/configuration (raw-data locations, reintegrated-district list, random seed, DPI); not run directly | — |
| `spatial_weights.py` | Shared module: district-name reconciliation between the panel and the GeoJSON, polygon centroids, queen-contiguity construction, KNN and distance-band matrices; not run directly | — |
| `01_data_overview.py` | Loads the raw panel and computes milk yield per cow (kg/head); reports variable definitions and full-panel descriptive statistics | Table 1; Table 2 |
| `02_sigma_convergence.py` | Coefficient of variation and Gini coefficient of relative yield by year; Mann-Kendall (1945; 1975) trend test | Table 3 |
| `03_beta_convergence.py` | Cross-sectional beta-convergence (absolute, herd-size-filtered, herd-weighted, two sub-periods); pooled OLS vs. two-way panel fixed-effects (Islam, 1995); beta-convergence for each five-year sub-period | Table 4a; Table 4b; Table 4c |
| `04_distribution_dynamics.py` | Kernel density estimation and Silverman's (1981) critical-bandwidth bootstrap multimodality test for 2000, 2012, and 2024 | Table 5; kernel-density grid for Figure 3 (`output/supporting/`) |
| `05_markov_chain.py` | Pooled, fixed-cutpoint quartile transition matrix; Shorrocks (1978) mobility index | Table 6 (Shorrocks M in `output/supporting/`) |
| `06_moran_analysis.py` | Global Moran's I (Moran, 1950) under queen contiguity (primary; Anselin, 1988), KNN (k=6,10), and a 100 km distance band, with permutation-based significance | Table 7; scatterplot data for Figure 5 (`output/supporting/`) |
| `07_spatial_markov.py` | Spatial Markov chain (Rey, 2001): quartile transition matrix conditioned on the (weight-averaged) quartile of a district's queen-contiguity neighbours in the prior year | Table 8 |
| `08_extensive_intensive.py` | Extensive/intensive/interaction decomposition of 2000-2024 milk-production growth; dominant-margin classification; cross-tabulation against both the 2024 and the 2000 productivity quartile (chi-square tests) | Table 9a; Table 9b; Table 9c (2000-quartile cross-tab reported in Section 6 text, in `output/supporting/`) |
| `09_reintegrated_robustness.py` | Re-estimates full-period and sub-period beta-convergence excluding the nine reintegrated districts | Table 10 |
| `10_dynamic_panel_bias.py` | Anderson and Hsiao (1982) first-differenced IV re-estimate of the panel fixed-effects coefficient, with a Staiger-Stock (1997) first-stage F-statistic | Section 7.4 robustness check (`output/supporting/`) |
| `11_fodder_robustness.py` | Coverage rates for labour, cost, and profitability variables (motivating their exclusion); beta-convergence with and without a fodder-crop-area control | Section 7.6 robustness checks (`output/supporting/`) |
| `12_study_area_map.py` | Choropleth map of average milk yield per cow, 2000-2024 | Figure 1 |
| `13_make_figures.py` | Reads the CSV outputs of scripts 02-08 and renders Figures 2-7 | Figures 2-7 |
| `run_all.py` | Runs scripts 01-13 in order | All tables and figures |

## The Nine Reintegrated Districts

Aghdam, Fuzuli, Jabrayil, Kalbajar, Gubadli, Lachin, Zangilan, Khojavand,
and Shusha districts experienced conflict-related disruption to
production for much of the sample period and have undergone post-2020
reconstruction and reintegration. This list is defined once, in
`_paths.py` (`REINTEGRATED_DISTRICTS`), and used only by
`09_reintegrated_robustness.py` (Section 7.2 of the manuscript). No
other script excludes these districts; they are part of the main
analytical panel throughout Sections 3-6.

## District Name Matching (Panel vs. GeoJSON)

The raw production panel and the geoBoundaries GeoJSON use different
transliteration conventions for several districts (e.g. "Qazakh" in one
source, "Gazakh" in the other). `spatial_weights.match_district_names()`
reconciles these via a normalization function with an explicit
transliteration lookup table, so that this package requires no external,
pre-computed name-crosswalk file. Of the geoBoundaries features, 73 are
successfully matched to panel districts and used in every spatial
analysis; districts without a usable geometry match (or without
sufficient production-variable coverage) are excluded from the
respective spatial computation, consistent with the unbalanced-panel
description in the manuscript.

## Statistical Methods Reference

| Method | Used in | Reference |
|---|---|---|
| Absolute beta-convergence (cross-sectional and panel) | `03`, `09` | Barro and Sala-i-Martin (1992); Islam (1995) |
| Mann-Kendall trend test | `02` | Mann (1945); Kendall (1975) |
| Kernel density estimation / Silverman multimodality bootstrap | `04` | Silverman (1981) |
| Markov transition matrix / Shorrocks mobility index | `05` | Quah (1996, 1997); Shorrocks (1978) |
| Global Moran's I | `06` | Moran (1950); Anselin (1988) |
| Spatial Markov chain | `07` | Rey (2001) |
| Anderson-Hsiao first-differenced IV | `10` | Anderson and Hsiao (1982); Nickell (1981) |
| Weak-instrument diagnostic (first-stage F) | `10` | Staiger and Stock (1997) |

Full bibliographic details, including DOIs, are provided in the
accompanying manuscript's reference list.

## Determinism

All computations in this package are deterministic given the fixed
random seed `SEED = 1` set in `_paths.py`. Two procedures consume random
draws:

- The Silverman (1981) bootstrap in `04_distribution_dynamics.py`, which
  re-seeds `np.random.default_rng(SEED)` independently for each of the
  three years tested (2000, 2012, 2024), using 1,000 resamples per year.
- The Moran's I permutation test in `06_moran_analysis.py`, which
  re-seeds `np.random.default_rng(SEED)` independently for each of the
  five specifications reported in Table 7, using 999 permutations each.

Both use numpy's modern Generator API (`np.random.default_rng`), not the
legacy global `RandomState` API. Changing `SEED`, the number of
resamples/permutations, or the order in which specifications are
evaluated will still produce statistically valid results, but not
necessarily the bit-for-bit p-values reported in the manuscript's Table
5 and Table 7.

## Table and Figure Numbering

Tables in `output/` and figures in `figures/` are numbered to match the
accompanying manuscript exactly: Table 1, Table 2, Table 3, Table 4a/4b/4c,
Table 5, Table 6, Table 7, Table 8, Table 9a/9b/9c, and Table 10 (14
files in total); Figure 1 through Figure 7. Files in `output/supporting/`
are intermediate data used to build figures, or statistics reported in
manuscript text rather than in a numbered table (Sections 7.4, 7.6, and
8); they are not additional manuscript tables.

