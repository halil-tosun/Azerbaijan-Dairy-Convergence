"""
Shared path and configuration module. Every script imports this so the
package runs identically regardless of the current working directory it
is launched from.

Tables are written to ../output/ (as .csv). Figures (.png) are written to
../figures/ at 300 DPI.
"""
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CODE_DIR.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "output"
SUPPORTING_DIR = OUTPUT_DIR / "supporting"
FIG_DIR = ROOT_DIR / "figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SUPPORTING_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_PANEL_CSV = RAW_DIR / "azerbaijan_dairy_panel_WIDE_districts.csv"
GEOBOUNDARIES_GEOJSON = RAW_DIR / "geoBoundaries-AZE-ADM2.geojson"

# The nine districts affected by conflict-related disruption to production
# for much of the sample period, reintegrated from 2020 onward. See
# Section 7.2 of the manuscript and docs/DATA_DESCRIPTION.md.
REINTEGRATED_DISTRICTS = [
    "Aghdam district",
    "Fuzuli district",
    "Jabrayil district",
    "Kalbajar district",
    "Gubadli district",
    "Lachin district",
    "Zangilan district",
    "Khojavand district",
    "Shusha district",
]

FIGURE_DPI = 300
# SEED = 1 reproduces the exact bootstrap/permutation statistics reported
# in the manuscript (Table 6 Silverman bootstrap p-values; Table 8 Moran's
# I permutation p-values). See docs/CODEBOOK.md, "Determinism".
SEED = 1
N_BOOTSTRAP_SILVERMAN = 1000
N_PERMUTATION_MORAN = 999
