# CHANGELOG

All notable changes to this reproducibility package will be documented in
this file.

The format is inspired by *Keep a Changelog* and follows semantic
versioning where appropriate.

---

## Version 1.0.0 (Initial Public Release)

### Added
- Complete Python source code for sigma- and beta-convergence
  (cross-sectional, panel fixed-effects, and sub-period), distribution
  dynamics (kernel density estimation, Silverman's multimodality test,
  Markov transition matrix, Shorrocks' mobility index), spatial
  econometrics (global Moran's I under queen contiguity, KNN, and
  distance-band weights; spatial Markov chain), the extensive/intensive
  margin decomposition and its cross-tabulation against productivity
  quartiles, the reintegrated-district sub-period robustness check, the
  Anderson-Hsiao dynamic-panel-bias check, the fodder-crop control
  robustness check, and all seven figures.
- Raw district-year production panel (66 dairy-producing districts,
  2000-2024) and the geoBoundaries administrative boundary data used to
  construct every spatial weight matrix.
- Self-contained district-name reconciliation between the panel and the
  GeoJSON (`spatial_weights.match_district_names()`), requiring no
  external, pre-computed crosswalk file.
- README.md with repository overview and usage instructions.
- CODEBOOK.md describing the analytical workflow, script-to-output
  correspondence, and determinism.
- DATA_DESCRIPTION.md documenting data sources, provenance, and
  variable-level definitions, including why labour, cost, and
  profitability variables are excluded and how the nine reintegrated
  districts are handled.
- REPRODUCIBILITY_CHECKLIST.md, including internal-consistency checks
  across related tables and verified determinism across repeated runs.
- Replication_Guide.md with complete, step-by-step replication
  instructions.
- CITATION.cff and .zenodo.json for software citation and Zenodo
  metadata.
- LICENSE, requirements.txt, environment.yml, .gitignore.

### Reproducibility
- One-command Python workflow via `run_all.py` (13 scripts, under one
  minute).
- All figures rendered at 300 DPI.
- Deterministic bootstrap (Silverman test) and permutation (Moran's I)
  procedures via a fixed random seed (`SEED = 1` in `_paths.py`),
  documented in full in `docs/CODEBOOK.md`, "Determinism."
- Every table checked for internal consistency (e.g. component shares
  summing to 100%; related tables' totals agreeing with one another)
  prior to release.
- Repository organized to remain valid regardless of eventual journal,
  manuscript title, or submission outcome.

### Notes
Zenodo DOI: https://doi.org/10.5281/zenodo.21693849

The manuscript's own DOI (once published) will be added at that time.
