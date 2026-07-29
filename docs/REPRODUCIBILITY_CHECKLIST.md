# REPRODUCIBILITY_CHECKLIST

## Study

**Catching Up Without Closing the Gap: Convergence and Distribution
Dynamics of Regional Dairy Productivity in Azerbaijan** (unbalanced
panel of 66 dairy-producing districts, 2000-2024)

---

## Reproducibility Status

| Item | Status |
|------|:------:|
| Source code included (Python) | ✓ |
| Raw data included (production panel and administrative boundaries) | ✓ |
| Data provenance and variable-level documentation included | ✓ |
| README provided | ✓ |
| CODEBOOK provided | ✓ |
| Data documentation provided | ✓ |
| Software dependencies documented | ✓ |
| Conda environment provided | ✓ |
| License provided | ✓ |
| Citation metadata (CITATION.cff, .zenodo.json) | ✓ |
| One-command workflow (`run_all.py`) | ✓ |
| Figures reproducible (300 DPI) | ✓ (Figures 1-7) |
| Tables reproducible | ✓ (Tables 1-13) |
| Deterministic bootstrap/permutation (fixed random seed) | ✓ |
| Open repository planned | ✓ |
| Zenodo DOI | https://doi.org/10.5281/zenodo.21693849 |
| Manuscript DOI | Pending -- will be added once available |

---

## Computational Environment

- Python environment documented in `environment.yml`
- Package list and pinned, independently verified versions documented in `requirements.txt`
- Python version tested: 3.12.3
- Package versions tested: pandas 3.0.2, NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.8
- Expected runtime: under one minute on a standard laptop

---

## Expected Workflow

1. Create the Python environment (`conda env create -f environment.yml`
   or `pip install -r requirements.txt`).
2. Run `python code/run_all.py`.
3. Verify that all 24 output files appear in `output/` and all 7 figures
   appear in `figures/` at 300 DPI.
4. Cross-check reported values against the manuscript's tables and
   figures (see `docs/CODEBOOK.md` for the full script-to-output
   correspondence).

---

## Internal Consistency

Every table produced by this package was checked for internal
consistency prior to release, including cross-checks between related
tables (for example, Table 11's dominant-margin counts sum to the same
totals as Table 12's cross-tabulation columns) and between reported
statistics and the underlying data-generating identities (for example,
the extensive, intensive, and interaction shares in Table 10 sum to
100%). All such checks passed.

Determinism was verified by running the full pipeline (`run_all.py`)
multiple times independently and confirming identical output across
runs, given the fixed random seed documented in `docs/CODEBOOK.md`,
"Determinism."

---

## Transparency Statement

This repository has been prepared to maximize computational
reproducibility and long-term accessibility. It is organized around the
underlying study rather than any specific journal submission, so that it
remains fully valid regardless of the eventual publication venue,
manuscript title, or peer-review outcome.

Once archived, this release will be assigned a permanent Zenodo DOI,
which will be added to this document, to `README.md`, `CITATION.cff`, and
`.zenodo.json`.
