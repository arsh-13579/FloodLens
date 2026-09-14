"""
district_grid.py — computes risk across a grid covering the whole
Gorakhpur district, so the map shows risk everywhere by default
instead of only after a click.

Deliberately reuses the SAME data sources and formula as combine.py
(risk_engine.calculate_risk_score, reference_data, elevation_to_rating)
so a grid cell's score is directly comparable to a click-point score —
no second scoring system to keep in sync.
"""

import time
import requests
from cache_utils import ttl_cache

from combine import elevation_to_rating
from reference_data import get_water_level, get_flood_history
from risk_engine import calculate_risk_score, tier_from_score

# Roughly covers Gorakhpur district + a small margin, so it also picks up
# nearby villages (Sahjanwa, Barhalganj, Campierganj) without needing a
# hand-maintained village list.
LAT_MIN, LAT_MAX = 26.35, 27.05
LON_MIN, LON_MAX = 83.05, 83.85
GRID_STEP = 0.04  # ~4-5 km spacing -> ~360 real points, denser so the heatmap blends smoothly instead of showing isolated blobs

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPENTOPODATA_URL = "https://api.opentopodata.org/v1/srtm30m"
OPENTOPODATA_CHUNK = 90  # stay under the public API's 100-location cap


def build_grid(step=GRID_STEP):
    points = []
    lat = LAT_MIN
    while lat <= LAT_MAX:
        lon = LON_MIN
        while lon <= LON_MAX:
            points.append((round(lat, 4), round(lon, 4)))
            lon += step
        lat += step
    return points


def batch_fetch_rainfall(points, retries=2):
    lats = ",".join(str(p[0]) for p in points)
    lons = ",".join(str(p[1]) for p in points)
    params = {
        "latitude": lats, "longitude": lons,
        "daily": "precipitation_sum",
        "past_days": 2, "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }
    for attempt in range(retries + 1):
        try:
            resp = requests.get(OPEN_METEO_URL, params=params, timeout=30)
            data = resp.json()
            if isinstance(data, list):
                return [round(sum(v for v in d["daily"]["precipitation_sum"] if v is not None), 1) for d in data]
            return [round(sum(v for v in data["daily"]["precipitation_sum"] if v is not None), 1)]
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            print(f"  Grid rainfall fetch failed (attempt {attempt + 1}): {e}")
            if attempt == retries:
                print("  Using fallback 20mm for all grid points")
                return [20] * len(points)


def batch_fetch_elevation(points, retries=2):
    """OpenTopoData batch call(s), chunked to respect the public API's
    per-request location cap. Same dataset as data_sources.fetch_elevation."""
    elevations = []
    for i in range(0, len(points), OPENTOPODATA_CHUNK):
        chunk = points[i:i + OPENTOPODATA_CHUNK]
        locations = "|".join(f"{lat},{lon}" for lat, lon in chunk)
        for attempt in range(retries + 1):
            try:
                resp = requests.get(OPENTOPODATA_URL, params={"locations": locations}, timeout=30)
                data = resp.json()
                elevations.extend(r["elevation"] for r in data["results"])
                break
            except (requests.exceptions.RequestException, KeyError, IndexError) as e:
                print(f"  Grid elevation fetch failed (attempt {attempt + 1}): {e}")
                if attempt == retries:
                    print(f"  Using fallback 80m for {len(chunk)} points")
                    elevations.extend([80] * len(chunk))
        time.sleep(1)  # be polite to the free public API between chunks
    return elevations


TIER_COLORS = {
    "Low": "#2ecc71",
    "Moderate": "#f1c40f",
    "High": "#e67e22",
    "Severe": "#e74c3c",
}


@ttl_cache(ttl=600)
def compute_district_grid(step=GRID_STEP):
    """Returns a list of dicts: lat, lon, score, tier, color.
    Cached for 10 minutes so panning/rerunning the map doesn't re-fetch."""
    points = build_grid(step)

    rainfall_vals = batch_fetch_rainfall(points)
    elevation_vals = batch_fetch_elevation(points)

    # FIXED: water level and flood history now depend on distance-to-river
    # (see river_distance.py), so they must be computed per grid point using
    # real coordinates — calling get_water_level(None, None) here previously
    # crashed inside geodesic(), which can't accept None. Live water level is
    # still fetched once internally (live_water_level.py is itself cached at
    # the network-call level), so this loop doesn't add extra HTTP calls —
    # it just re-blends that one cached reading per point's river distance.
    results = []
    for i, (lat, lon) in enumerate(points):
        rainfall = rainfall_vals[i] if i < len(rainfall_vals) else 20
        elevation_m = elevation_vals[i] if i < len(elevation_vals) else 80
        elev_rating = elevation_to_rating(elevation_m)

        water_level = get_water_level(lat, lon)
        flood_history = get_flood_history(lat, lon)

        inputs = {
            "rainfall_mm": rainfall,
            "water_level_m": water_level,
            "drainage_poor": elev_rating,
            "low_elevation": elev_rating,
            "flood_history": flood_history,
        }
        score = calculate_risk_score(inputs)
        tier = tier_from_score(score)

        results.append({
            "lat": lat, "lon": lon,
            "score": score, "tier": tier,
            "color": TIER_COLORS[tier],
        })

    return results


if __name__ == "__main__":
    grid = compute_district_grid()
    print(f"Grid points: {len(grid)}")
    for r in grid[:10]:
        print(r)