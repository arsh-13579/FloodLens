import requests
import math
from geopy.distance import geodesic

def fetch_nearby_roads(latitude, longitude, radius_m=1500):
    directions = [0, 45, 90, 135, 180, 225, 270, 315]
    roads = []
    offset = 0.012  # roughly 1.3km

    for angle in directions:
        end_lat = latitude + offset * math.cos(math.radians(angle))
        end_lon = longitude + offset * math.sin(math.radians(angle))

        url = f"https://router.project-osrm.org/route/v1/driving/{longitude},{latitude};{end_lon},{end_lat}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                coords = data["routes"][0]["legs"][0]  # confirm structure below
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"OSRM fetch failed for angle {angle}: {e}")
            continue

        try:
            geometry = data["routes"][0]["geometry"]
            decoded = decode_polyline(geometry)
            if decoded:
                roads.append(decoded)
        except (KeyError, IndexError) as e:
            print(f"Geometry parse failed for angle {angle}: {e}")

    return roads

def decode_polyline(polyline_str, precision=5):
    # Decodes Google/OSRM-style encoded polylines into (lat, lon) tuples
    index, lat, lon = 0, 0, 0
    coordinates = []
    factor = 10 ** precision

    while index < len(polyline_str):
        for coord in ["lat", "lon"]:
            shift, result = 0, 0
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else (result >> 1)
            if coord == "lat":
                lat += delta
            else:
                lon += delta
        coordinates.append((lat / factor, lon / factor))
    return coordinates

def score_road_risk(road_coords, risk_lat, risk_lon, location_risk_score):
    mid_idx = len(road_coords) // 2
    mid_point = road_coords[mid_idx]
    dist_km = geodesic(mid_point, (risk_lat, risk_lon)).km
    decay_factor = max(0, 1 - (dist_km / 1.5))
    road_risk = location_risk_score * decay_factor
    return round(road_risk, 1)

def risk_to_color(road_risk):
    if road_risk < 15: return "green"
    elif road_risk < 30: return "orange"
    else: return "red"

def fetch_route_to_point(start_lat, start_lon, end_lat, end_lon, retries=2):
    """
    Real OSRM driving route between two specific points (e.g. user's
    selected location -> nearest shelter). Distinct from fetch_nearby_roads
    above, which scans 8 directions for road-risk coloring, not a route
    to a destination. Returns None on failure rather than a fabricated
    route, so callers can show "unavailable" instead of fake data.
    """
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                return {
                    "coordinates": decode_polyline(route["geometry"]),
                    "distance_km": round(route["distance"] / 1000, 2),
                    "duration_min": round(route["duration"] / 60, 1),
                }
            return None
        except (requests.exceptions.RequestException, ValueError, KeyError, IndexError) as e:
            print(f"Route-to-point fetch failed (attempt {attempt+1}): {e}")
            if attempt == retries:
                return None

def score_route_segments(route_coords, origin_lat, origin_lon, origin_risk_score, chunk_size=6):
    """
    Splits a route into colored chunks using the SAME distance-decay risk
    scoring already used for nearby-road risk (score_road_risk / risk_to_color
    above) — segments near the high-risk origin come out red/orange,
    segments closer to the shelter (farther from the risk source) fade
    toward green. Deliberately reuses tested logic rather than inventing
    a second, separate risk-coloring method for routes.
    """
    segments = []
    for i in range(0, len(route_coords) - 1, chunk_size):
        chunk = route_coords[i:i + chunk_size + 1]
        if len(chunk) < 2:
            continue
        risk = score_road_risk(chunk, origin_lat, origin_lon, origin_risk_score)
        segments.append({
            "coordinates": chunk,
            "risk": risk,
            "color": risk_to_color(risk),
        })
    return segments

if __name__ == "__main__":
    roads = fetch_nearby_roads(26.7606, 83.3732)
    print(f"Found {len(roads)} road paths")
    for road in roads:
        risk = score_road_risk(road, 26.7606, 83.3732, 49.6)
        print(f"Road risk: {risk}")