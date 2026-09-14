# backtest_formula.py
"""
Validates the risk formula against a real, documented historical flood
event. Only water_level_m is manually entered — sourced from an official
CWC Flood Situation Report, cited below. Rainfall is fetched live from
Open-Meteo's real historical archive; elevation and flood_history use the
exact same functions the live app uses.
"""
import requests
from combine import elevation_to_rating
from reference_data import get_flood_history
from data_sources import fetch_elevation
from risk_engine import calculate_risk_score, tier_from_score
from datetime import datetime, timedelta

HISTORICAL_EVENTS = [
    {
        "label": "Birdghat, Gorakhpur — 24 July 2020",
        "date": "2020-07-24",
        "lat": 26.7606, "lon": 83.3732,
        "water_level_m": 75.91,  # CWC Flood Situation Report, 24-Jul-2020, 14:00 hrs
        "official_classification": "SEVERE (0.93m above danger mark)",
        "source": "https://cwc.gov.in/sites/default/files/fsr-n32-24-07.pdf",
    },
]

def fetch_historical_rainfall(lat, lon, date):
    """Real 3-day cumulative rainfall ending on `date`, matching the
    live app's cumulative-rainfall approach (Open-Meteo Archive API)."""
    end = datetime.strptime(date, "%Y-%m-%d")
    start = end - timedelta(days=2)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start.strftime("%Y-%m-%d"), "end_date": date,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
    }
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    values = data["daily"]["precipitation_sum"]
    return round(sum(v for v in values if v is not None), 1)

def run_backtest():
    print(f"{'Event':<40} {'Score':<8} {'Our Tier':<10} {'CWC Classification'}")
    print("-" * 100)
    for e in HISTORICAL_EVENTS:
        rainfall = fetch_historical_rainfall(e["lat"], e["lon"], e["date"])
        elevation_m = fetch_elevation(e["lat"], e["lon"])
        elev_rating = elevation_to_rating(elevation_m)
        flood_history = get_flood_history(e["lat"], e["lon"])

        inputs = {
            "rainfall_mm": rainfall, "water_level_m": e["water_level_m"],
            "drainage_poor": elev_rating, "low_elevation": elev_rating,
            "flood_history": flood_history,
        }
        score = calculate_risk_score(inputs)
        tier = tier_from_score(score)

        print(f"{e['label']:<40} {score:<8} {tier:<10} {e['official_classification']}")
        print(f"  Real historical rainfall (Open-Meteo Archive, {e['date']}): {rainfall}mm")
        print(f"  Source: {e['source']}\n")

if __name__ == "__main__":
    run_backtest()