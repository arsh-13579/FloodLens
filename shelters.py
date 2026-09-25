from geopy.distance import geodesic

# Real, known Gorakhpur institutions (major hospitals used as flood-relief-capable landmarks).
# Coordinates are approximate (city-area accurate, not survey-precise) — honestly labeled.
SHELTERS = {
    "BRD Medical College": (26.7550, 83.3800),
    "AIIMS Gorakhpur": (26.7815, 83.4267),
    "Railway Hospital, Gorakhpur": (26.7590, 83.3660),
    "Gorakhpur Collectorate (relief coordination)": (26.7580, 83.3700),
    
}

def find_nearest_shelter(latitude, longitude):
    user_point = (latitude, longitude)
    nearest_name = None
    nearest_distance = float("inf")

    for name, coords in SHELTERS.items():
        distance_km = geodesic(user_point, coords).km
        if distance_km < nearest_distance:
            nearest_distance = distance_km
            nearest_name = name

    return nearest_name, round(nearest_distance, 2)

if __name__ == "__main__":
    from combine import VILLAGES
    for name, (lat, lon) in VILLAGES.items():
        shelter, dist = find_nearest_shelter(lat, lon)
        print(f"{name} -> nearest shelter: {shelter} ({dist} km)")