"""
12_study_area_map.py
======================
Figure 1: choropleth map of average milk yield per cow by district,
2000-2024, using district boundaries from geoBoundaries (Runfola et
al., 2020).

Produces:
  figures/Figure1_study_area_map.png (300 DPI)
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
from _paths import FIG_DIR, FIGURE_DPI
from spatial_weights import match_district_names
import importlib.util
import os

spec = importlib.util.spec_from_file_location("data_overview", os.path.join(os.path.dirname(__file__), "01_data_overview.py"))
data_overview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_overview)

from _paths import GEOBOUNDARIES_GEOJSON, RAW_PANEL_CSV


def main():
    df = data_overview.load_panel()
    mean_yield = df.groupby("region")["yield_per_cow"].mean()

    with open(GEOBOUNDARIES_GEOJSON) as f:
        geo = json.load(f)
    panel_names = sorted(pd.read_csv(RAW_PANEL_CSV)["region"].unique())
    matched = match_district_names(geo, panel_names)

    fig, ax = plt.subplots(figsize=(9, 7))
    patches = []
    values = []
    for feat in geo["features"]:
        gname = feat["properties"]["shapeName"]
        pname = matched.get(gname)
        val = mean_yield.get(pname, np.nan) if pname else np.nan
        geomobj = feat["geometry"]
        parts = geomobj["coordinates"] if geomobj["type"] == "MultiPolygon" else [geomobj["coordinates"]]
        for part in parts:
            ring = np.array(part[0])
            patches.append(MplPolygon(ring, closed=True))
            values.append(val)

    values = np.array(values, dtype=float)
    coll = PatchCollection(patches, cmap="YlGnBu", edgecolor="white", linewidths=0.4)
    coll.set_array(np.nan_to_num(values, nan=np.nanmean(values)))
    ax.add_collection(coll)
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.axis("off")
    cbar = fig.colorbar(coll, ax=ax, shrink=0.75)
    cbar.set_label("Average milk yield per cow (kg), 2000-2024")
    ax.set_title("Study Area: Average Milk Yield per Cow by District, 2000-2024", fontsize=12, fontweight="bold")
    n_districts = int((~np.isnan(values)).sum())
    fig.text(0.5, 0.02,
              "Notes: District boundaries from geoBoundaries (Runfola et al., 2020). "
              f"Sample: 66 dairy-producing districts of Azerbaijan with complete production data, 2000-2024 (unbalanced panel, N=1,522 district-years).",
              ha="center", fontsize=7)
    fig.savefig(FIG_DIR / "Figure1_study_area_map.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    print("Figure 1 written to figures/Figure1_study_area_map.png")


if __name__ == "__main__":
    main()
