from geopy.distance import geodesic

# Real, known Gorakhpur institutions (major hospitals used as flood-relief-capable landmarks).
# Coordinates are approximate (city-area accurate, not survey-precise) — honestly labeled.
SHELTERS = {
    "BRD Medical College": (26.7550, 83.3800),
    "AIIMS Gorakhpur": (26.7815, 83.4267),
    "Railway Hospital, Gorakhpur": (26.7590, 83.3660),
    "Gorakhpur Collectorate (relief coordination)": (26.7580, 83.3700),

    # Additional approximate area reference points for prototype coverage.
    # NOT verified/operational flood shelters; replace with DDMA-approved sites
    # and surveyed coordinates before presenting them as evacuation destinations.
    "Potential evacuation point - Gorakhnath area": (26.7800, 83.3450),
    "Potential evacuation point - Mohaddipur area": (26.7580, 83.3990),
    "Potential evacuation point - Kunraghat area": (26.7460, 83.4190),
    "Potential evacuation point - Khorabar area": (26.7140, 83.4330),
    "Potential evacuation point - Pipraich area": (26.8270, 83.5250),
    "Potential evacuation point - Bhathat area": (26.8540, 83.4100),
    "Potential evacuation point - Jungle Kaudia area": (26.8410, 83.3180),
    "Potential evacuation point - Campierganj area": (27.0290, 83.2680),
    "Potential evacuation point - Sahjanwa area": (26.7470, 83.2140),
    "Potential evacuation point - Piprauli area": (26.6900, 83.2900),
    "Potential evacuation point - Khajni area": (26.6250, 83.3400),
    "Potential evacuation point - Bansgaon area": (26.5500, 83.3500),
    "Potential evacuation point - Kauriram area": (26.5700, 83.4400),
    "Potential evacuation point - Gagaha area": (26.4700, 83.4600),
    "Potential evacuation point - Gola Bazar area": (26.3440, 83.3600),
    "Potential evacuation point - Barhalganj area": (26.2800, 83.5100),
    "Potential evacuation point - Belghat area": (26.4400, 83.2300),
    "Potential evacuation point - Chauri Chaura area": (26.6500, 83.5900),
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