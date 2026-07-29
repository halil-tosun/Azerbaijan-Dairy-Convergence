# DATA_DESCRIPTION

## Data Sources

This study uses two publicly available data sources.

### 1. District-level dairy production panel

`data/raw/azerbaijan_dairy_panel_WIDE_districts.csv` is an unbalanced
panel of district-year agricultural production statistics for
Azerbaijan, 2000-2024, compiled from the *Agriculture of Azerbaijan*
statistical yearbook and regional statistical database published by the
State Statistical Committee of the Republic of Azerbaijan. The raw file
contains 1,814 district-year rows spanning 74 administrative units; 66
districts have sufficient production-variable coverage to enter the core
convergence, distribution-dynamics, and spatial analyses (Sections 3-7 of
the manuscript).

### 2. Administrative boundary data (geoBoundaries)

`data/raw/geoBoundaries-AZE-ADM2.geojson` provides Azerbaijan's
second-level administrative district boundaries, used to construct the
queen-contiguity spatial weight matrix (the primary specification for
Moran's I and the spatial Markov chain) and district centroids (used for
the KNN and distance-band robustness weight matrices, and for Figure 1).
Source: Runfola, D. et al. (2020), "geoBoundaries: A global database of
political administrative boundaries," *PLOS ONE* 15(4): e0231866. Full
citation details, including the DOI, are provided in the manuscript's
reference list.

---

## Files

### `data/raw/azerbaijan_dairy_panel_WIDE_districts.csv`

| Column | Description |
|---|---|
| `region` | District (or city) name |
| `region_type` | Administrative unit type |
| `year` | Year, 2000-2024 |
| `milk_production_tons` | Total annual milk production (tons) |
| `cows_dairy_buffaloes_stock_heads` | Dairy cattle (and buffalo) stock (head) |
| `cows_heads` | Total cattle stock (head), not used in this package |
| `fodder_sown_area_ha` | Area sown to fodder crops (ha) |
| `labour_hours_per_centner_milk_enterprises` | Labour hours per centner of milk, enterprise farms (52% missing; not used) |
| `cost_price_per_centner_milk_enterprises_manat` | Unit cost per centner of milk, enterprise farms (manat; 52% missing; not used) |
| `cost_price_per_centner_milk_private_manat` | Unit cost per centner of milk, private farms (manat; not used) |
| `profitability_milk_enterprises_pct` | Profitability, enterprise farms (%; 57% missing; not used) |
| `profitability_milk_private_pct` | Profitability, private farms (%; not used) |
| `selling_price_per_centner_milk_enterprises_manat` | Selling price per centner of milk, enterprise farms (manat; not used) |
| `selling_price_per_centner_milk_private_manat` | Selling price per centner of milk, private farms (manat; not used) |

**Milk yield per cow** (kg/head; the primary outcome variable throughout
this package) is not stored as a raw column; it is computed on the fly
in `01_data_overview.py::load_panel()` as
`milk_production_tons * 1000 / cows_dairy_buffaloes_stock_heads`, and
imported by every subsequent script.

**Relative yield** (used for the distribution-dynamics and quartile-based
analyses) is likewise computed on the fly, as each district-year's yield
divided by the contemporaneous national mean yield.

### `data/raw/geoBoundaries-AZE-ADM2.geojson`

Standard GeoJSON `FeatureCollection`; each feature's `properties.shapeName`
gives the district name (in geoBoundaries' own transliteration, which
differs from the panel's for several districts -- see
`docs/CODEBOOK.md`, "District Name Matching") and `geometry` gives its
polygon (or multipolygon) boundary in longitude/latitude coordinates.

---

## Why Labour, Cost, and Profitability Variables Are Not Used

The raw panel includes district-year records on labour input, unit
cost, and enterprise profitability, in addition to the core production
variables (milk production, cattle stock, fodder-crop area). These are
**not** used in any convergence, distribution-dynamics, or spatial
model, because their coverage is far sparser than the core variables:

| Variable | % missing |
|---|---:|
| Milk production | 0.1% |
| Dairy cattle stock | 0.0% |
| Fodder-crop sown area | 10.1% |
| Labour hours (enterprises) | 51.9% |
| Unit cost (enterprises) | 51.8% |
| Profitability (enterprises) | 57.0% |

(`11_fodder_robustness.py` reproduces this table exactly.) This
quantifies and confirms the data-availability constraint noted as a
limitation in Section 8 of the manuscript: the exclusion of labour,
cost, and profitability reflects genuine missingness, not an arbitrary
modelling choice. Fodder-crop area, by contrast, has sufficient coverage
(89.9%) to be tested directly as a robustness control (Section 7.6);
`11_fodder_robustness.py` confirms that adding it as a covariate leaves
the beta-convergence estimate essentially unchanged.

---

## The Nine Reintegrated Districts

Aghdam, Fuzuli, Jabrayil, Kalbajar, Gubadli, Lachin, Zangilan, Khojavand,
and Shusha districts experienced conflict-related disruption to
production for much of the sample period and have undergone post-2020
reconstruction and reintegration. Several show extreme growth rates
mechanically driven by near-zero base-year (2000) values -- for example,
one district's dairy herd grows from 11 head in 2000 to over 4,000 head
by 2024. These districts remain part of the main analytical panel
throughout Sections 3-6 of the manuscript; `09_reintegrated_robustness.py`
re-estimates the headline convergence results excluding them, confirming
the main findings are not an artefact of this subset (Section 7.2).

---

## Data Access and Terms of Use

- The State Statistical Committee of the Republic of Azerbaijan's
  *Agriculture of Azerbaijan* yearbook and regional statistical database
  are publicly available.
- geoBoundaries data are released under a permissive open license; see
  https://www.geoboundaries.org for full terms and to access boundary
  data for other countries or administrative levels.
