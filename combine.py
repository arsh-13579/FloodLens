from cache_utils import ttl_cache
from data_sources import fetch_rainfall, fetch_elevation
from reference_data import get_water_level, get_flood_history
from risk_engine import calculate_risk_score

VILLAGES = {
    "Gorakhpur City": (26.7606, 83.3732),
    "Taramandal": (26.7321, 83.3844),   # low-lying, near lake/river bend
    "Sahjanwa": (26.7500, 83.2170),
    "Campierganj": (27.0290, 83.2668),  # corrected real coords, ~34km north
}

def elevation_to_rating(elevation_m):
    # Lower elevation = higher risk rating (1-5 scale, matches risk_engine's MAX_VALUES)
    if elevation_m < 70:
        return 5
    elif elevation_m < 80:
        return 4
    elif elevation_m < 90:
        return 3
    elif elevation_m < 100:
        return 2
    else:
        return 1

@ttl_cache(ttl=600)
def get_location_risk(latitude, longitude, rainfall_override=None):
    rainfall = rainfall_override if rainfall_override is not None else fetch_rainfall(latitude, longitude)
    elevation_m = fetch_elevation(latitude, longitude)
    water_level = get_water_level(latitude, longitude)
    flood_history = get_flood_history(latitude, longitude)

    inputs = {
        "rainfall_mm": rainfall,
        "water_level_m": water_level,
        "drainage_poor": elevation_to_rating(elevation_m),
        "low_elevation": elevation_to_rating(elevation_m),
        "flood_history": flood_history,
    }

    score = calculate_risk_score(inputs)
    return score, inputs

if __name__ == "__main__":
    # VILLAGES here is just our demo/test list — the function itself
    # accepts ANY coordinate, proving location-specific scoring works generally
    for name, (lat, lon) in VILLAGES.items():
        score, inputs = get_location_risk(lat, lon)
        print(f"{name}: Risk Score = {score}")