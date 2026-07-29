"""
run_all.py
==========
Runs the full analytical pipeline in order and writes every table
(.csv) reported in the manuscript to ../output/, and every figure
(.png, 300 DPI) to ../figures/.

Expected runtime: under two minutes on a standard laptop. The slowest
steps are the Silverman bootstrap (1,000 resamples x 3 years) and the
Moran's I permutation tests (999 permutations x 5 specifications).

Run individual numbered scripts directly to regenerate only one table
or figure, e.g.: python 06_moran_analysis.py
"""
import importlib.util
import os
import time

HERE = os.path.dirname(__file__)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "main"):
        mod.main()
    return mod


if __name__ == "__main__":
    t0 = time.time()

    print("=== 01: Data overview -- Table 1, Table 2 ===")
    _load("01_data_overview")

    print("\n=== 02: Sigma-convergence -- Table 3 ===")
    _load("02_sigma_convergence")

    print("\n=== 03: Beta-convergence -- Table 4a, 4b, 4c ===")
    _load("03_beta_convergence")

    print("\n=== 04: Distribution dynamics -- Table 6 (Silverman test) ===")
    _load("04_distribution_dynamics")

    print("\n=== 05: Markov chain -- Table 7, Shorrocks M ===")
    _load("05_markov_chain")

    print("\n=== 06: Moran's I -- Table 8 ===")
    _load("06_moran_analysis")

    print("\n=== 07: Spatial Markov chain -- Table 9 ===")
    _load("07_spatial_markov")

    print("\n=== 08: Extensive/intensive margins -- Table 10, 11, 12 ===")
    _load("08_extensive_intensive")

    print("\n=== 09: Reintegrated-district robustness -- Table 13 ===")
    _load("09_reintegrated_robustness")

    print("\n=== 10: Dynamic panel bias check (Anderson-Hsiao IV) ===")
    _load("10_dynamic_panel_bias")

    print("\n=== 11: Fodder-crop robustness and variable coverage ===")
    _load("11_fodder_robustness")

    print("\n=== 12: Figure 1 (study area map) ===")
    _load("12_study_area_map")

    print("\n=== 13: Figures 2-7 ===")
    _load("13_make_figures")

    print(f"\nAll done in {time.time() - t0:.0f} seconds.")
    print("See ../output/ for all tables and ../figures/ for all figures.")
