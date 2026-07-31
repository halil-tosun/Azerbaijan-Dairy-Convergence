# Catching Up Without Closing the Gap: Convergence and Distribution Dynamics of Regional Dairy Productivity in Azerbaijan

## Reproducibility Package

This repository contains the complete reproducibility package accompanying
a manuscript that examines regional productivity convergence in
Azerbaijan's dairy sector, using an unbalanced panel of 66
dairy-producing districts, 2000-2024. The manuscript documents that
robust panel beta-convergence in milk yield per cow coexists with rising
cross-sectional dispersion, shows via distribution-dynamics and spatial
methods that this reflects persistent district-level immobility rather
than spatial spillovers or convergence-club formation, and relates the
persistence to heterogeneity in the extensive and intensive margins of
production growth.

This package is intentionally organized around the *study* rather than
any single journal submission. If the manuscript title, framing, or
target journal changes during peer review, this repository and its
contents remain valid without modification.

---

## Repository Overview

This repository follows open science and computational reproducibility
principles and includes:

- Complete Python source code (data loading, sigma- and beta-convergence,
  distribution dynamics, spatial econometrics, extensive/intensive
  margin decomposition, robustness checks, and figure generation)
- The raw district-year production panel (2000-2024) and the
  geoBoundaries administrative boundary data used to construct every
  spatial weight matrix
- Comprehensive documentation of data provenance and processing
- Software environment specifications

---

## Repository Structure

```text
Azerbaijan-Dairy-Convergence/
├── code/
│   ├── _paths.py                        # shared path/configuration
│   ├── spatial_weights.py               # shared spatial-weights module (not run directly)
│   ├── 01_data_overview.py              # Table 1; Table 2
│   ├── 02_sigma_convergence.py          # Table 3
│   ├── 03_beta_convergence.py           # Table 4a, 4b, 4c
│   ├── 04_distribution_dynamics.py      # Table 5 (Silverman test)
│   ├── 05_markov_chain.py               # Table 6; Shorrocks M
│   ├── 06_moran_analysis.py             # Table 7
│   ├── 07_spatial_markov.py             # Table 8
│   ├── 08_extensive_intensive.py        # Table 9a, 9b, 9c
│   ├── 09_reintegrated_robustness.py    # Table 10
│   ├── 10_dynamic_panel_bias.py         # Anderson-Hsiao IV check (Section 7.4 text)
│   ├── 11_fodder_robustness.py          # Fodder-crop control + coverage rates (Section 7.6 text)
│   ├── 12_study_area_map.py             # Figure 1
│   ├── 13_make_figures.py               # Figures 2-7
│   └── run_all.py
├── data/
│   └── raw/
│       ├── azerbaijan_dairy_panel_WIDE_districts.csv
│       └── geoBoundaries-AZE-ADM2.geojson
├── output/                              # Table 1-10 (.csv), matching the manuscript's own numbering exactly
│   └── supporting/                      # intermediate/robustness data not itself a numbered manuscript table
├── figures/                             # generated figures (.png, 300 DPI)
├── docs/
│   ├── CODEBOOK.md
│   ├── DATA_DESCRIPTION.md
│   ├── REPRODUCIBILITY_CHECKLIST.md
│   └── Replication_Guide.md
├── README.md
├── CHANGELOG.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE
├── requirements.txt
├── environment.yml
└── .gitignore
```

## Documentation

- **docs/CODEBOOK.md** — analytical workflow and script-by-script description
- **docs/DATA_DESCRIPTION.md** — data sources, provenance, and variable definitions
- **docs/REPRODUCIBILITY_CHECKLIST.md** — reproducibility checklist and internal consistency checks
- **docs/Replication_Guide.md** — complete, step-by-step replication guide

## Installation

```bash
conda env create -f environment.yml
conda activate azerbaijan-dairy-convergence-repro
```

or

```bash
pip install -r requirements.txt
```

## Run

```bash
cd code
python run_all.py
```

This reproduces the complete analytical workflow: descriptive
statistics, sigma- and beta-convergence (cross-sectional, panel
fixed-effects, and sub-period), distribution dynamics (kernel density
estimation and Silverman's multimodality test), the Markov transition
matrix and Shorrocks' mobility index, global Moran's I under queen
contiguity and robustness weight matrices, the spatial Markov chain, the
extensive/intensive margin decomposition and its cross-tabulation
against productivity quartiles, the reintegrated-district sub-period
robustness check, the Anderson-Hsiao dynamic-panel-bias check, the
fodder-crop control robustness check, and all seven figures.

Expected runtime: under one minute on a standard laptop. The slowest
steps are the Silverman bootstrap (1,000 resamples x 3 years) and the
Moran's I permutation tests (999 permutations x 5 specifications).

## Script-to-Output Correspondence

| Script | Produces |
|---|---|
| `01_data_overview.py` | Table 1 (variable definitions); Table 2 (descriptive statistics) |
| `02_sigma_convergence.py` | Table 3 (sigma-convergence by year) |
| `03_beta_convergence.py` | Table 4a (cross-sectional specifications); Table 4b (pooled OLS vs. panel FE); Table 4c (sub-period beta-convergence) |
| `04_distribution_dynamics.py` | Table 5 (Silverman bimodality test); kernel-density grid for Figure 3 (in `output/supporting/`) |
| `05_markov_chain.py` | Table 6 (Markov transition matrix); Shorrocks (1978) mobility index M (in `output/supporting/`) |
| `06_moran_analysis.py` | Table 7 (global Moran's I: queen contiguity, KNN, distance-band); scatterplot data for Figure 5 (in `output/supporting/`) |
| `07_spatial_markov.py` | Table 8 (spatial Markov diagonal persistence, by neighbour quartile) |
| `08_extensive_intensive.py` | Table 9a (national aggregate decomposition); Table 9b (dominant-margin counts); Table 9c (quartile x dominant-margin cross-tab) |
| `09_reintegrated_robustness.py` | Table 10 (sub-period beta-convergence, excluding reintegrated districts) |
| `10_dynamic_panel_bias.py` | Anderson-Hsiao (1982) IV check reported in Section 7.4 (in `output/supporting/`) |
| `11_fodder_robustness.py` | Variable coverage rates and fodder-crop control check reported in Sections 7.6 and 8 (in `output/supporting/`) |
| `12_study_area_map.py` | Figure 1 (choropleth map of average milk yield per cow by district) |
| `13_make_figures.py` | Figure 2 (sigma/beta convergence panel); Figure 3 (kernel density evolution); Figure 4 (Markov heatmap); Figure 5 (Moran scatterplot); Figure 6 (spatial Markov heatmaps); Figure 7 (extensive/intensive margins by district) |

## A Note on District Name Matching

District names in the raw production panel and in the geoBoundaries
GeoJSON use different transliteration conventions for several districts
(e.g. "Qazakh" vs "Gazakh"). This is reconciled automatically by
`spatial_weights.match_district_names()`, so no external, pre-computed
name-crosswalk file is required; the package is fully self-contained
given only the two files in `data/raw/`.

## Citation

Please cite both the published article (once available) and this
archived repository. Citation metadata are provided in `CITATION.cff`
and `.zenodo.json`.

## License

MIT License (code in this repository). The underlying district-level
agricultural statistics originate from the State Statistical Committee
of the Republic of Azerbaijan; administrative boundary data are from
geoBoundaries (Runfola et al., 2020, PLOS ONE). See
`docs/DATA_DESCRIPTION.md` for full provenance and terms of use.

## Contact

**Halil Tosun, Ph.D.**

Department of Animal Science, School of Agricultural and Food Sciences,
ADA University, Baku, Azerbaijan

ORCID: https://orcid.org/0000-0001-5117-0390

Email: halilibrahimtosun@gmail.com

## DOI

**Zenodo DOI:** https://doi.org/10.5281/zenodo.21693848

The manuscript's own DOI (once published) will be added to this file and
to the citation metadata files at that time.

## Version

**Version:** 1.0.0
