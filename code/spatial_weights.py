"""
spatial_weights.py
===================
Shared module (not run directly) that builds the spatial weight
matrices used by 07_moran_analysis.py and 08_spatial_markov.py:

  - Queen contiguity (primary specification): districts are neighbours
    if their polygon boundaries touch or overlap.
  - K-nearest-neighbour (KNN) matrices, k = 3-10 (robustness).
  - Fixed distance-band matrix, threshold 100 km (robustness).

District names in the raw panel and in the geoBoundaries GeoJSON use
different transliteration conventions (e.g. "Qazakh" vs "Gazakh"); these
are reconciled here by `match_district_names()` so that no external,
pre-computed name-matching file is required -- this module is fully
self-contained given only the two files in data/raw/.
"""
import json
import re
import numpy as np
import pandas as pd
from _paths import RAW_PANEL_CSV, GEOBOUNDARIES_GEOJSON

EARTH_RADIUS_KM = 6371.0


def match_district_names(geo, panel_names):
    """Reconcile geoBoundaries shapeName strings with panel region names."""
    def normalize(name):
        name = name.lower()
        name = re.sub(r"\bdistrict\b|\bcity\b", "", name).strip()
        repl = {
            "qazakh": "gazakh", "qabala": "gabala", "qakh": "gakh", "qusar": "gusar",
            "qobustan": "gobustan", "quba": "guba", "qubadli": "gubadli",
            "agstafa": "aghstafa", "agsu": "aghsu", "agdam": "aghdam", "agdash": "agdash",
            "agdara": "aghdara", "ismailli": "ismayilli", "masally": "masalli",
            "saatly": "saatli", "zaqatala": "zagatala", "khojavend": "khojavand",
            "siazan": "siyazan", "yardymli": "yardimli", "sumqayit": "sumgayit", "babek": "babak",
        }
        return repl.get(name, name)

    panel_norm = {normalize(n): n for n in panel_names}
    matched = {}
    for feat in geo["features"]:
        gname = feat["properties"]["shapeName"]
        norm = normalize(gname)
        if norm in panel_norm and panel_norm[norm] not in matched.values():
            matched[gname] = panel_norm[norm]
    return matched


def polygon_centroid(ring):
    x, y = ring[:, 0], ring[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y2 - x2 * y
    a = cross.sum() / 2.0
    if abs(a) < 1e-9:
        return x.mean(), y.mean()
    cx = ((x + x2) * cross).sum() / (6 * a)
    cy = ((y + y2) * cross).sum() / (6 * a)
    return cx, cy


def haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def _simplify_ring(ring, decimals=3):
    out = []
    prev = None
    for pt in ring:
        p = (round(pt[0], decimals), round(pt[1], decimals))
        if p != prev:
            out.append(p)
            prev = p
    return out


def _decimate(ring, keep_every=2):
    if len(ring) <= 30:
        return ring
    out = [ring[0]]
    for i in range(1, len(ring) - 1, keep_every):
        out.append(ring[i])
    out.append(ring[-1])
    return out


def load_geometries():
    """Return (names, boundary_points, centroids) for all matched districts.

    `boundary_points[name]` is a simplified, decimated array of the
    district's largest polygon ring, used for queen-contiguity distance
    checks. `centroids[name]` is (lon, lat).
    """
    with open(GEOBOUNDARIES_GEOJSON) as f:
        geo = json.load(f)
    panel_names = sorted(pd.read_csv(RAW_PANEL_CSV)["region"].unique())
    matched = match_district_names(geo, panel_names)

    boundary_points = {}
    for feat in geo["features"]:
        gname = feat["properties"]["shapeName"]
        if gname not in matched:
            continue
        pname = matched[gname]
        if pname in boundary_points:
            continue
        geomobj = feat["geometry"]
        parts = geomobj["coordinates"] if geomobj["type"] == "MultiPolygon" else [geomobj["coordinates"]]
        largest = max(parts, key=lambda part: len(part[0]))
        ring = _decimate(_simplify_ring(largest[0]), keep_every=2)
        boundary_points[pname] = np.array(ring)

    names = sorted(boundary_points.keys())
    centroids = {nm: polygon_centroid(boundary_points[nm]) for nm in names}
    return names, boundary_points, centroids


def build_queen_contiguity(names, boundary_points, touch_threshold_deg=0.02):
    """Queen contiguity weight matrix (row-standardised).

    Districts are neighbours if the minimum distance between their
    (simplified) boundary point sets is below `touch_threshold_deg`
    (~2 km), which tolerates small gaps introduced by ring
    simplification. Any resulting isolate (no neighbour found) is
    connected to its single nearest district by centroid distance, a
    standard, documented fallback for simplification artefacts.
    """
    n = len(names)
    W = np.zeros((n, n))

    def min_dist(pts1, pts2):
        d = np.sqrt(((pts1[:, None, :] - pts2[None, :, :]) ** 2).sum(axis=2))
        return d.min()

    for i in range(n):
        for j in range(i + 1, n):
            if min_dist(boundary_points[names[i]], boundary_points[names[j]]) < touch_threshold_deg:
                W[i, j] = W[j, i] = 1

    n_neighbors = W.sum(axis=1)
    isolates = np.where(n_neighbors == 0)[0]
    if len(isolates) > 0:
        centroids = {nm: polygon_centroid(boundary_points[nm]) for nm in names}
        cent_arr = np.array([centroids[nm] for nm in names])
        for idx in isolates:
            dists = np.sqrt(((cent_arr - cent_arr[idx]) ** 2).sum(axis=1))
            dists[idx] = np.inf
            nearest = np.argmin(dists)
            W[idx, nearest] = W[nearest, idx] = 1

    return W / W.sum(axis=1, keepdims=True)


def build_knn(names, centroids, k):
    n = len(names)
    cent_arr = np.array([centroids[nm] for nm in names])
    W = np.zeros((n, n))
    for i in range(n):
        d = haversine_km(cent_arr[i, 0], cent_arr[i, 1], cent_arr[:, 0], cent_arr[:, 1])
        d[i] = np.inf
        nearest = np.argsort(d)[:k]
        W[i, nearest] = 1
    return W / W.sum(axis=1, keepdims=True)


def build_distance_band(names, centroids, threshold_km=100):
    n = len(names)
    cent_arr = np.array([centroids[nm] for nm in names])
    W = np.zeros((n, n))
    for i in range(n):
        d = haversine_km(cent_arr[i, 0], cent_arr[i, 1], cent_arr[:, 0], cent_arr[:, 1])
        d[i] = np.inf
        W[i, d < threshold_km] = 1
    row_sums = W.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # avoid division by zero for any isolated district
    return W / row_sums
