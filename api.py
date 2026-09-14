"""
api.py — FastAPI backend for FloodLens.

Wraps the existing risk/advisory/shelter/route/alert logic as REST
endpoints. No business logic lives here — this is a thin HTTP layer over
combine.py, risk_engine.py, advisory.py, shelters.py, routes.py,
alerts.py, database.py and district_grid.py, so the scoring logic used
by the API is byte-for-byte the same as what Streamlit (or a future
React frontend) would call.

Run with:
    uvicorn api:app --reload --port 8000

Docs auto-generated at:
    http://localhost:8000/docs
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from combine import get_location_risk, VILLAGES
from database import (
    init_db, save_risk_score, get_recent_scores,
    get_all_subscribers, register_subscriber,
)
import os
from advisory import generate_advisory
from shelters import find_nearest_shelter, SHELTERS
from routes import fetch_nearby_roads, score_road_risk, risk_to_color, fetch_route_to_point, score_route_segments
from alerts import send_flood_alert, ALERT_TIERS, should_alert
from district_grid import compute_district_grid, TIER_COLORS
from check_subscribers_alerts import check_all_subscribers
from risk_engine import tier_from_score, calculate_risk_breakdown
from data_sources import fetch_current_weather
from otp import send_otp, check_otp, OTP_ENABLED
from database import mark_phone_verified, is_phone_recently_verified, get_status, get_recent_alerts
from push import send_push
from database import save_push_subscription

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")

app = FastAPI(
    title="FloodLens API",
    description="Flood risk intelligence & evacuation decision-support for Gorakhpur district.",
    version="0.1.0",
)
_demo_alerted_points = set()

# Wide-open CORS for the prototype (Streamlit / React dev servers run on
# different ports than the API). Tighten this to specific origins before
# any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------

class OtpSendRequest(BaseModel):
    phone_number: str

class OtpVerifyRequest(BaseModel):
    phone_number: str
    code: str


class RiskResponse(BaseModel):
    latitude: float
    longitude: float
    score: float
    tier: str
    rainfall_mm: float
    water_level_m: float
    low_elevation: int
    flood_history: int
    breakdown: dict
    alert_sent: bool


class RoadSegment(BaseModel):
    coordinates: List[List[float]]
    risk: float
    color: str


class ShelterRoute(BaseModel):
    shelter_name: str
    coordinates: List[List[float]]
    distance_km: float
    duration_min: float
    segments: List[RoadSegment]


class WeatherResponse(BaseModel):
    temperature_c: float
    condition: str


class AdvisoryRequest(BaseModel):
    risk_score: float
    tier: str
    profile: Optional[List[str]] = None
    language: str = "English"
    rainfall_mm: Optional[float] = None
    water_level_m: Optional[float] = None
    breakdown: Optional[dict] = None


class SubscriberRequest(BaseModel):
    phone_number: str
    latitude: float
    longitude: float
    location_label: str
    language: str = "English"
    profile: Optional[List[str]] = None

class PushSubscribeRequest(BaseModel):
    endpoint: str
    keys: dict
    latitude: float
    longitude: float
    location_label: str    

@app.get("/push/vapid-public-key")
def get_vapid_public_key():
    return {"key": VAPID_PUBLIC_KEY}

@app.post("/push/subscribe")
def push_subscribe(req: PushSubscribeRequest):
    save_push_subscription(req.endpoint, req.keys["p256dh"], req.keys["auth"], req.latitude, req.longitude, req.location_label)
    return {"status": "subscribed"}

@app.post("/otp/send")
def otp_send(req: OtpSendRequest):
    try:
        status = send_otp(req.phone_number)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not send code: {e}")

@app.post("/otp/verify")
def otp_verify(req: OtpVerifyRequest):
    try:
        approved = check_otp(req.phone_number, req.code)
        if approved:
            mark_phone_verified(req.phone_number)
        return {"verified": approved}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Verification failed: {e}")

# ---------------------------------------------------------------------
# Risk endpoints
# ---------------------------------------------------------------------

@app.get("/risk", response_model=RiskResponse)
def get_risk(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    rainfall_override: Optional[float] = Query(None),
    persist: bool = Query(True),
):
    score, inputs = get_location_risk(lat, lon, rainfall_override=rainfall_override)
    tier = tier_from_score(score)
    breakdown = calculate_risk_breakdown(inputs)

    if persist and rainfall_override is None:
        save_risk_score(lat, lon, score, inputs)

    alert_sent = False
    if rainfall_override is None and should_alert((lat, lon), tier, _demo_alerted_points):
        sids = send_flood_alert(lat, lon, score, tier, language="en")
        alert_sent = bool(sids)

    return RiskResponse(
        latitude=lat, longitude=lon, score=score, tier=tier,
        rainfall_mm=inputs["rainfall_mm"], water_level_m=inputs["water_level_m"],
        low_elevation=inputs["low_elevation"], flood_history=inputs["flood_history"],
        breakdown=breakdown, alert_sent=alert_sent,
    )


@app.get("/risk/grid")
def get_risk_grid():
    """District-wide grid of risk scores, for the heatmap layer."""
    points = compute_district_grid()
    return {"points": points, "tier_colors": TIER_COLORS}


@app.get("/villages")
def get_villages():
    """The small set of named villages shown as static map markers."""
    return [{"name": name, "lat": lat, "lon": lon} for name, (lat, lon) in VILLAGES.items()]


@app.get("/history")
def get_history(limit: int = Query(10, ge=1, le=100)):
    rows = get_recent_scores(limit=limit)
    return [
        {"latitude": r[0], "longitude": r[1], "score": r[2], "timestamp": r[3]}
        for r in rows
    ]


# ---------------------------------------------------------------------
# Advisory
# ---------------------------------------------------------------------

@app.post("/advisory")
def get_advisory(req: AdvisoryRequest):
    try:
        text = generate_advisory(
            req.risk_score, req.tier, profile=req.profile, language=req.language,
            rainfall_mm=req.rainfall_mm, water_level_m=req.water_level_m, breakdown=req.breakdown,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Advisory generation failed: {e}")
    return {"advisory": text}


# ---------------------------------------------------------------------
# Shelters & roads
# ---------------------------------------------------------------------

@app.get("/shelter")
def get_shelter(lat: float, lon: float):
    name, distance_km = find_nearest_shelter(lat, lon)
    return {"name": name, "distance_km": distance_km}


@app.get("/shelters")
def get_all_shelters(lat: float, lon: float):
    """All known shelters with real distance from the given point —
    not just the nearest one. Powers a full shelter list/map, using the
    same real SHELTERS data as find_nearest_shelter."""
    from geopy.distance import geodesic
    result = []
    for name, (s_lat, s_lon) in SHELTERS.items():
        dist = round(geodesic((lat, lon), (s_lat, s_lon)).km, 2)
        result.append({"name": name, "lat": s_lat, "lon": s_lon, "distance_km": dist})
    result.sort(key=lambda s: s["distance_km"])
    return result


@app.get("/roads", response_model=List[RoadSegment])
def get_roads(lat: float, lon: float):
    score, _ = get_location_risk(lat, lon)
    roads = fetch_nearby_roads(lat, lon)
    if not roads:
        raise HTTPException(status_code=503, detail="Road data temporarily unavailable (Overpass/OSRM busy)")

    result = []
    for road in roads:
        risk = score_road_risk(road, lat, lon, score)
        result.append(RoadSegment(
            coordinates=[[p[0], p[1]] for p in road],
            risk=risk,
            color=risk_to_color(risk),
        ))
    return result


@app.get("/route-to-shelter", response_model=ShelterRoute)
def get_route_to_shelter(lat: float, lon: float):
    """Real OSRM driving route from a point to its nearest shelter —
    distinct from /roads, which scores nearby road risk, not a route to
    a destination. Returns 503 (not a fake route) if OSRM is unreachable.
    Segments are colored using the same real risk-decay scoring as /roads,
    keyed off the ORIGIN point's actual current risk score."""
    shelter_name, _ = find_nearest_shelter(lat, lon)
    shelter_lat, shelter_lon = SHELTERS[shelter_name]
    route = fetch_route_to_point(lat, lon, shelter_lat, shelter_lon)
    if not route:
        raise HTTPException(status_code=503, detail="Route to shelter temporarily unavailable (OSRM busy)")

    origin_score, _ = get_location_risk(lat, lon)  # cached — no extra real network cost
    segments = score_route_segments(route["coordinates"], lat, lon, origin_score)

    return ShelterRoute(
        shelter_name=shelter_name,
        coordinates=[[p[0], p[1]] for p in route["coordinates"]],
        distance_km=route["distance_km"],
        duration_min=route["duration_min"],
        segments=[
            RoadSegment(coordinates=[[p[0], p[1]] for p in seg["coordinates"]], risk=seg["risk"], color=seg["color"])
            for seg in segments
        ],
    )



@app.get("/weather", response_model=WeatherResponse)
def get_weather(lat: float, lon: float):
    """Real current temperature + condition from Open-Meteo — same
    source as rainfall, just a different field of the same API."""
    data = fetch_current_weather(lat, lon)
    return WeatherResponse(temperature_c=data["temperature_c"], condition=data["condition"])


# ---------------------------------------------------------------------
# Subscribers & alerts
# ---------------------------------------------------------------------

@app.post("/subscribers")
def create_subscriber(req: SubscriberRequest):
    if OTP_ENABLED and not is_phone_recently_verified(req.phone_number):
        raise HTTPException(status_code=403, detail="Phone number not verified — send and confirm an OTP first")
    register_subscriber(req.phone_number, req.latitude, req.longitude, req.location_label, req.language, req.profile or [])
    return {"status": "registered"}


@app.post("/subscribers")
def create_subscriber(req: SubscriberRequest):
    register_subscriber(
        req.phone_number, req.latitude, req.longitude,
        req.location_label, req.language, req.profile or [],
    )
    return {"status": "registered"}


@app.get("/subscribers")
def list_subscribers():
    rows = get_all_subscribers()
    return [
        {
            "id": r[0], "phone_number": r[1], "latitude": r[2], "longitude": r[3],
            "location_label": r[4], "language": r[5], "profile": r[6],
        }
        for r in rows
    ]


@app.post("/alerts/check")
def trigger_alert_check():
    """Manually trigger the subscriber alert sweep (normally run on a
    schedule/cron). Exposed here so it can be tested/demoed on demand."""
    check_all_subscribers()
    return {"status": "checked"}


@app.post("/alerts/test")
def test_alert(lat: float, lon: float, language: str = "en"):
    score, _ = get_location_risk(lat, lon)
    tier = tier_from_score(score)
    sids = send_flood_alert(lat, lon, score, tier, language=language)
    return {"tier": tier, "score": score, "sent": len(sids), "alertable": tier in ALERT_TIERS}


# Admin

@app.get("/admin/status")
def admin_status():
    subs = get_all_subscribers()
    recent = get_recent_alerts(10)
    return {
        "subscriber_count": len(subs),
        "recent_alerts": [
            {"label": r[0], "phone": r[1], "tier": r[2], "alert_at": r[3]} for r in recent
        ],
        "last_water_level_scrape": get_status("last_water_level_scrape"),
    }


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/otp/enabled")
def otp_enabled():
    return {"enabled": OTP_ENABLED}