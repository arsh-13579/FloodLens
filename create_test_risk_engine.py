from risk_engine import calculate_risk_score, normalize, normalize_water_level

def test_normalize_caps_at_one():
    assert normalize(500, 300) == 1.0
    assert normalize(150, 300) == 0.5
    assert normalize(0, 300) == 0.0
    print("PASS: normalize caps correctly")

def test_water_level_baseline():
    # Normal level (below safe_min) should score 0, not risky
    assert normalize_water_level(50, 55, 74.98) == 0.0
    # At danger mark should score 1.0
    assert normalize_water_level(74.98, 55, 74.98) == 1.0
    # Above danger mark should still cap at 1.0
    assert normalize_water_level(80, 55, 74.98) == 1.0
    print("PASS: water level baseline logic correct")

def test_high_risk_scores_high():
    high_risk = {
        "rainfall_mm": 220,
        "water_level_m": 76,
        "drainage_poor": 4,
        "low_elevation": 5,
        "flood_history": 8,
    }
    score = calculate_risk_score(high_risk)
    assert score >= 70, f"Expected high-risk score >=70, got {score}"
    print(f"PASS: high-risk scenario scored {score} (expected >=70)")

def test_low_risk_scores_low():
    low_risk = {
        "rainfall_mm": 40,
        "water_level_m": 60,
        "drainage_poor": 1,
        "low_elevation": 1,
        "flood_history": 1,
    }
    score = calculate_risk_score(low_risk)
    assert score <= 30, f"Expected low-risk score <=30, got {score}"
    print(f"PASS: low-risk scenario scored {score} (expected <=30)")

def test_score_never_exceeds_100():
    max_risk = {
        "rainfall_mm": 9999,
        "water_level_m": 9999,
        "drainage_poor": 9999,
        "low_elevation": 9999,
        "flood_history": 9999,
    }
    score = calculate_risk_score(max_risk)
    assert score <= 100, f"Score exceeded 100: {score}"
    print(f"PASS: extreme inputs capped at {score} (expected <=100)")

def test_score_never_negative():
    min_risk = {
        "rainfall_mm": 0,
        "water_level_m": 0,
        "drainage_poor": 0,
        "low_elevation": 0,
        "flood_history": 0,
    }
    score = calculate_risk_score(min_risk)
    assert score >= 0, f"Score went negative: {score}"
    print(f"PASS: zero inputs scored {score} (expected >=0)")

if __name__ == "__main__":
    test_normalize_caps_at_one()
    test_water_level_baseline()
    test_high_risk_scores_high()
    test_low_risk_scores_low()
    test_score_never_exceeds_100()
    test_score_never_negative()
    print("\nALL TESTS PASSED")