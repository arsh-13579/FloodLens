from river_distance import water_level_influence, distance_to_river_km
from live_water_level import fetch_live_rapti_water_level

RAPTI_TYPICAL_LEVEL = 60

def get_water_level(latitude, longitude):
    data = fetch_live_rapti_water_level()
    actual_level = data["rwl"] if data else RAPTI_TYPICAL_LEVEL

    influence = water_level_influence(latitude, longitude)
    # Blend: far from river, pull toward a neutral/safe baseline instead of the live reading
    blended = (actual_level * influence) + (RAPTI_TYPICAL_LEVEL * (1 - influence))
    return round(blended, 2)

def get_flood_history(latitude, longitude):
    dist = distance_to_river_km(latitude, longitude)
    if dist < 3:
        return 6      # right on the river, matches documented crossing events
    elif dist < 8:
        return 4
    else:
        return 2      # far from river, lower historical relevance