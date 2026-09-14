import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_scores (
            id SERIAL PRIMARY KEY, latitude REAL, longitude REAL, risk_score REAL,
            rainfall_mm REAL, water_level_m REAL, elevation_rating INTEGER, flood_history INTEGER, timestamp TEXT
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY, phone_number TEXT, latitude REAL, longitude REAL,
            location_label TEXT, language TEXT, profile TEXT, registered_at TEXT
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_log (
            subscriber_id INTEGER PRIMARY KEY, last_alert_tier TEXT, last_alert_at TEXT
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified_phones (
            phone_number TEXT PRIMARY KEY, verified_at TEXT
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_status (
            key TEXT PRIMARY KEY, value TEXT
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            endpoint TEXT PRIMARY KEY, p256dh TEXT, auth TEXT,
            latitude REAL, longitude REAL, location_label TEXT, registered_at TEXT
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_alert_log (
            endpoint TEXT PRIMARY KEY, last_alert_tier TEXT, last_alert_at TEXT
        )""")
    conn.commit(); conn.close()

def save_risk_score(latitude, longitude, score, inputs):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO risk_scores (latitude, longitude, risk_score, rainfall_mm, water_level_m, elevation_rating, flood_history, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (latitude, longitude, score, inputs["rainfall_mm"], inputs["water_level_m"], inputs["low_elevation"], inputs["flood_history"], datetime.now().isoformat()))
    conn.commit(); conn.close()

def get_recent_scores(limit=10):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude, risk_score, timestamp FROM risk_scores ORDER BY id DESC LIMIT %s", (limit,))
    rows = cursor.fetchall(); conn.close(); return rows

def register_subscriber(phone_number, latitude, longitude, location_label, language, profile):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subscribers (phone_number, latitude, longitude, location_label, language, profile, registered_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (phone_number, latitude, longitude, location_label, language, ",".join(profile), datetime.now().isoformat()))
    conn.commit(); conn.close()

def get_all_subscribers():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT id, phone_number, latitude, longitude, location_label, language, profile FROM subscribers")
    rows = cursor.fetchall(); conn.close(); return rows

def get_last_alert_tier(subscriber_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT last_alert_tier FROM alert_log WHERE subscriber_id = %s", (subscriber_id,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else None

def set_last_alert_tier(subscriber_id, tier):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_log (subscriber_id, last_alert_tier, last_alert_at) VALUES (%s, %s, %s)
        ON CONFLICT (subscriber_id) DO UPDATE SET last_alert_tier=excluded.last_alert_tier, last_alert_at=excluded.last_alert_at
    """, (subscriber_id, tier, datetime.now().isoformat()))
    conn.commit(); conn.close()

def mark_phone_verified(phone_number):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO verified_phones (phone_number, verified_at) VALUES (%s, %s)
        ON CONFLICT (phone_number) DO UPDATE SET verified_at=excluded.verified_at
    """, (phone_number, datetime.now().isoformat()))
    conn.commit(); conn.close()

def is_phone_recently_verified(phone_number, minutes=10):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT verified_at FROM verified_phones WHERE phone_number = %s", (phone_number,))
    row = cursor.fetchone(); conn.close()
    if not row: return False
    return (datetime.now() - datetime.fromisoformat(row[0])).total_seconds() < minutes * 60

def set_status(key, value):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_status (key, value) VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value=excluded.value
    """, (key, value))
    conn.commit(); conn.close()

def get_status(key):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_status WHERE key = %s", (key,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else None

def get_recent_alerts(limit=10):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        SELECT s.location_label, s.phone_number, a.last_alert_tier, a.last_alert_at
        FROM alert_log a JOIN subscribers s ON a.subscriber_id = s.id
        ORDER BY a.last_alert_at DESC LIMIT %s
    """, (limit,))
    rows = cursor.fetchall(); conn.close(); return rows

def save_push_subscription(endpoint, p256dh, auth, latitude, longitude, location_label):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO push_subscriptions (endpoint, p256dh, auth, latitude, longitude, location_label, registered_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (endpoint) DO UPDATE SET latitude=excluded.latitude, longitude=excluded.longitude, location_label=excluded.location_label
    """, (endpoint, p256dh, auth, latitude, longitude, location_label, datetime.now().isoformat()))
    conn.commit(); conn.close()

def get_all_push_subscriptions():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT endpoint, p256dh, auth, latitude, longitude, location_label FROM push_subscriptions")
    rows = cursor.fetchall(); conn.close(); return rows

def get_last_push_alert_tier(endpoint):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT last_alert_tier FROM push_alert_log WHERE endpoint = %s", (endpoint,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else None

def set_last_push_alert_tier(endpoint, tier):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO push_alert_log (endpoint, last_alert_tier, last_alert_at) VALUES (%s, %s, %s)
        ON CONFLICT (endpoint) DO UPDATE SET last_alert_tier=excluded.last_alert_tier, last_alert_at=excluded.last_alert_at
    """, (endpoint, tier, datetime.now().isoformat()))
    conn.commit(); conn.close()

if __name__ == "__main__":
    init_db()
    print("Postgres schema ready.")