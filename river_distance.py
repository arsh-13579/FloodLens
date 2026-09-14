from geopy.distance import geodesic

# Approximate Rapti river path through Gorakhpur district,
# traced from verified points (Sahjanwa -> city center -> Taramandal bend -> south).
# Not survey-precise, but real and reasonably representative.
RAPTI_PATH = [
    (26.7500, 83.2170),  # near Sahjanwa
    (26.7550, 83.2900),
    (26.7606, 83.3732),  # Gorakhpur city center (river passes near here)
    (26.7450, 83.3800),
    (26.7321, 83.3844),  # Taramandal bend
    (26.7100, 83.3950),  # continuing south
]

def distance_to_river_km(latitude, longitude):
    point = (latitude, longitude)
    return min(geodesic(point, river_point).km for river_point in RAPTI_PATH)

def water_level_influence(latitude, longitude, decay_km=10):
    """Returns 0-1: how much the river's water level should matter here."""
    dist = distance_to_river_km(latitude, longitude)
    return max(0, 1 - (dist / decay_km))