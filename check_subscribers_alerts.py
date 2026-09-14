from database import get_all_subscribers, get_last_alert_tier, set_last_alert_tier, init_db
from combine import get_location_risk
from alerts import send_sms_to, ALERT_TIERS
from risk_engine import tier_from_score
from database import get_all_push_subscriptions, get_last_push_alert_tier, set_last_push_alert_tier
from push import send_push

def check_all_subscribers():
    init_db()
    subscribers = get_all_subscribers()
    print(f"Checking {len(subscribers)} subscribers...")

    for sub_id, phone, lat, lon, label, language, profile in subscribers:
        score, inputs = get_location_risk(lat, lon)
        tier = tier_from_score(score)

        last_tier = get_last_alert_tier(sub_id)

        # Alert only if now in an alertable tier AND (no prior alert OR tier changed)
        if tier in ALERT_TIERS and tier != last_tier:
            lang_code = "hi" if language == "Hindi" else "en"
            sid = send_sms_to(phone, lat, lon, score, tier, lang_code, trial_mode=True)
            set_last_alert_tier(sub_id, tier)
            print(f"  ALERTED {label} ({phone}): {tier} (score {score}) — SID {sid}")
        elif tier not in ALERT_TIERS and last_tier in ALERT_TIERS:
            set_last_alert_tier(sub_id, tier)  # reset once risk drops back down
            print(f"  Risk dropped for {label}: now {tier}")
        else:
            print(f"  No change for {label}: {tier} (score {score})")

def check_push_subscribers():
    subs = get_all_push_subscriptions()
    print(f"Checking {len(subs)} push subscribers...")
    for endpoint, p256dh, auth, lat, lon, label in subs:
        score, inputs = get_location_risk(lat, lon)
        tier = tier_from_score(score)
        last_tier = get_last_push_alert_tier(endpoint)
        if tier in ALERT_TIERS and tier != last_tier:
            info = {"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}}
            ok = send_push(info, "FloodLens Alert", f"{tier} flood risk near {label} (score {score})")
            set_last_push_alert_tier(endpoint, tier)
            print(f"  PUSHED {label}: {tier} — sent={ok}")
        elif tier not in ALERT_TIERS and last_tier in ALERT_TIERS:
            set_last_push_alert_tier(endpoint, tier)
        else:
            print(f"  No change for {label}: {tier}")            

if __name__ == "__main__":
    check_all_subscribers()
    check_push_subscribers()