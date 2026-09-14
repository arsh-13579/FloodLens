import requests
from bs4 import BeautifulSoup
from cache_utils import ttl_cache
from datetime import datetime
from database import set_status

FMISC_URL = "https://raptiffm.fmisc.up.gov.in/rapti/Dashboard.aspx"

@ttl_cache(ttl=1800)
def fetch_live_rapti_water_level(station_name="Birdghat", retries=2):
    headers = {"User-Agent": "Mozilla/5.0 (FloodLens-SIH2026-Prototype)"}

    for attempt in range(retries + 1):
        try:
            response = requests.get(FMISC_URL, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")

            rows = soup.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                texts = [c.get_text(strip=True) for c in cells]

                # Only accept rows with enough columns to be the water-level table
                if len(texts) >= 11 and station_name in texts[0]:
                    set_status("last_water_level_scrape", datetime.now().isoformat())
                    print("Matched row cells:", texts)
                    return {
                        "station": texts[0],
                        "hfl": float(texts[1]),
                        "danger_level": float(texts[2]),
                        "warning_level": float(texts[3]),
                        "cwc_wl": float(texts[4]),
                        "rwl": float(texts[5]),
                    }

            print("Station not found with enough columns — table structure may differ.")
            return None

        except (requests.exceptions.RequestException, ValueError, IndexError) as e:
            print(f"Fetch failed (attempt {attempt+1}): {e}")
            if attempt == retries:
                return None

if __name__ == "__main__":
    data = fetch_live_rapti_water_level()
    print(data)