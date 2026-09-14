def normalize(value, max_value):
    score = value / max_value
    return min(score, 1.0)    # cap at 1.0 even if value exceeds max

def normalize_water_level(value, safe_min, danger_max):
    if value <= safe_min:
        return 0.0
    score = (value - safe_min) / (danger_max - safe_min)
    return min(score, 1.0)

WATER_LEVEL_SAFE_MIN = 55   # normal river level, no real risk
WATER_LEVEL_DANGER_MAX = 74.98   # Rapti's actual danger mark

MAX_VALUES = {
    "rainfall_mm": 300,
    "drainage_poor": 5,
    "low_elevation": 5,
    "flood_history": 10
}

WEIGHTS = {
    "rainfall_mm": 0.30,
    "water_level_m": 0.20,
    "drainage_poor": 0.20,
    "low_elevation": 0.15,
    "flood_history": 0.15
}

def calculate_risk_score(inputs):
    total_score = 0
    for factor, raw_value in inputs.items():
        if factor == "water_level_m":
            normalized = normalize_water_level(raw_value, WATER_LEVEL_SAFE_MIN, WATER_LEVEL_DANGER_MAX)
        else:
            normalized = normalize(raw_value, MAX_VALUES[factor])
        weighted = normalized * WEIGHTS[factor]
        total_score += weighted
    return round(total_score * 100, 1)

def calculate_risk_breakdown(inputs):
    """
    Returns {factor: weighted_points}, showing exactly how many of the
    final 0-100 points each factor contributed. Uses the SAME normalize
    functions as calculate_risk_score above, so summing this dict's
    values always equals what calculate_risk_score returns for the same
    inputs — no second formula to drift out of sync with the real one.
    """
    breakdown = {}
    for factor, raw_value in inputs.items():
        if factor == "water_level_m":
            normalized = normalize_water_level(raw_value, WATER_LEVEL_SAFE_MIN, WATER_LEVEL_DANGER_MAX)
        else:
            normalized = normalize(raw_value, MAX_VALUES[factor])
        breakdown[factor] = round(normalized * WEIGHTS[factor] * 100, 1)
    return breakdown

# ---------------------------------------------------------------------
# SINGLE SOURCE OF TRUTH for tier thresholds. Previously duplicated as
# inline if/elif chains in app.py, api.py, district_grid.py, and
# check_subscribers_alerts.py — all four now import this instead, so a
# future threshold change only needs to happen in one place.
# ---------------------------------------------------------------------
TIER_THRESHOLDS = {"Low": 25, "Moderate": 50, "High": 75}

def tier_from_score(score):
    if score < TIER_THRESHOLDS["Low"]:
        return "Low"
    elif score < TIER_THRESHOLDS["Moderate"]:
        return "Moderate"
    elif score < TIER_THRESHOLDS["High"]:
        return "High"
    return "Severe"

if __name__ == "__main__":
    # Test 1: a high-risk, low-lying area near the river during heavy rain
    high_risk_area = {
        "rainfall_mm": 220,
        "water_level_m": 76,
        "drainage_poor": 4,
        "low_elevation": 5,
        "flood_history": 8,
    }

    # Test 2: a well-drained, higher-ground area during light rain
    low_risk_area = {
        "rainfall_mm": 40,
        "water_level_m": 60,
        "drainage_poor": 1,
        "low_elevation": 1,
        "flood_history": 1,
    }

    print("High-risk area score:", calculate_risk_score(high_risk_area))
    print("Low-risk area score:", calculate_risk_score(low_risk_area))