"""
alerts.py — SMS alert delivery for FloodLens (Phase 2 feature, now built).

Sends an SMS via Twilio when a location's risk tier crosses into
High or Severe. Designed to slot into the existing pipeline right
after get_location_risk() is called in app.py.
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")  # your Twilio number, e.g. "+1415..."

# Demo-only: hardcoded recipient(s). Replace with a DB lookup in Phase 3.
TEST_RECIPIENTS = [
    os.getenv("ALERT_TEST_NUMBER_1"),  # e.g. "+9198XXXXXXXX"
    # os.getenv("ALERT_TEST_NUMBER_2"),  # uncomment to add a second test number
]

ALERT_TIERS = {"High", "Severe"}

def _get_client():
    """Lazily build the Twilio client so import doesn't fail without creds."""
    if not (TWILIO_SID and TWILIO_AUTH_TOKEN):
        raise RuntimeError(
            "Twilio credentials missing. Check TWILIO_ACCOUNT_SID and "
            "TWILIO_AUTH_TOKEN in your .env file."
        )
    return Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def _build_message_body(lat, lon, score, tier, language, trial_mode=True):
    if trial_mode:
        return "sms_event_notifications"
    if language == "hi":
        return (
            f"⚠️ बाढ़ चेतावनी: आपके क्षेत्र ({lat:.4f}, {lon:.4f}) में जोखिम स्तर "
            f"'{tier}' है (स्कोर: {score:.0f}/100). कृपया सुरक्षित मार्ग देखें और "
            f"तैयार रहें। — FloodLens"
        )
    return (
        f"⚠️ Flood Alert: Risk level '{tier}' (score {score:.0f}/100) "
        f"detected near ({lat:.4f}, {lon:.4f}). Check FloodLens for a "
        f"safe route and shelter info. — FloodLens"
    )

def send_sms_to(phone_number, lat, lon, score, tier, language="en", trial_mode=True):
    """Send one alert SMS to a specific phone number. Returns the message SID or None."""
    if not phone_number:
        return None
    body = _build_message_body(lat, lon, score, tier, language, trial_mode)
    client = _get_client()
    message = client.messages.create(body=body, from_=TWILIO_FROM_NUMBER, to=phone_number)
    return message.sid

def send_flood_alert(lat, lon, score, tier, language="en"):
    """Existing demo function — alerts TEST_RECIPIENTS only. Unchanged behavior."""
    if tier not in ALERT_TIERS:
        return []
    sent_sids = []
    for number in TEST_RECIPIENTS:
        sid = send_sms_to(number, lat, lon, score, tier, language, trial_mode=True)
        if sid:
            sent_sids.append(sid)
    return sent_sids

def should_alert(selected_point: tuple, tier: str, already_alerted: set) -> bool:
    """
    Guard against duplicate/spam alerts on Streamlit reruns.

    `already_alerted` should be a st.session_state set, e.g.
    st.session_state["alerted_points"], persisted across reruns.
    Returns True only the first time this exact (point, tier)
    combination crosses into an alertable tier.
    """
    key = (round(selected_point[0], 4), round(selected_point[1], 4), tier)
    if tier in ALERT_TIERS and key not in already_alerted:
        already_alerted.add(key)
        return True
    return False
