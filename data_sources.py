import requests

def fetch_rainfall(latitude, longitude, retries=2):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "precipitation_sum",
        "past_days": 2,      # + today (forecast_days=1) = 3-day cumulative window
        "forecast_days": 1,
        "timezone": "Asia/Kolkata"
    }
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            daily_values = data["daily"]["precipitation_sum"]
            cumulative = sum(v for v in daily_values if v is not None)
            return round(cumulative, 1)
        except requests.exceptions.RequestException as e:
            print(f"  Rainfall fetch failed (attempt {attempt+1}): {e}")
            if attempt == retries:
                print("  Using fallback value: 20mm (typical monsoon estimate)")
                return 20
            
def fetch_elevation(latitude, longitude, retries=2):
    url = "https://api.opentopodata.org/v1/srtm30m"
    params = {"locations": f"{latitude},{longitude}"}
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            return data["results"][0]["elevation"]
        except requests.exceptions.RequestException as e:
            print(f"  Elevation fetch failed (attempt {attempt+1}): {e}")
            if attempt == retries:
                print("  Using fallback value: 80m (typical Gorakhpur elevation)")
                return 80

# WMO weather codes, as returned by Open-Meteo's current_weather field.
# Subset covering conditions realistic for Gorakhpur's climate.
WEATHER_CODE_TEXT = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Light rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}

def weather_code_to_text(code):
    return WEATHER_CODE_TEXT.get(code, "Unknown conditions")

def fetch_current_weather(latitude, longitude, retries=2):
    """Real current temperature + condition, same Open-Meteo source as
    fetch_rainfall above — no new API dependency, just a different field."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "timezone": "Asia/Kolkata",
    }
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            current = data["current_weather"]
            return {
                "temperature_c": current["temperature"],
                "condition": weather_code_to_text(current["weathercode"]),
            }
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"  Weather fetch failed (attempt {attempt+1}): {e}")
            if attempt == retries:
                print("  Using fallback: 28°C, typical monsoon conditions")
                return {"temperature_c": 28, "condition": "Typical monsoon conditions (fallback)"}

VILLAGES = {
    "Gorakhpur City": (26.7606, 83.3732),
    "Barhalganj": (26.5833, 83.2333),
    "Sahjanwa": (26.7333, 83.1500),
}

if __name__ == "__main__":
    for name, (lat, lon) in VILLAGES.items():
        print(f"Fetching {name}...")
        rain = fetch_rainfall(lat, lon)
        print(f"  Rainfall: {rain}mm")
        elev = fetch_elevation(lat, lon)
        print(f"  Elevation: {elev}m")