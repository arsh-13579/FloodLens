import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FACTOR_LABELS = {
    "rainfall_mm": "heavy rainfall",
    "water_level_m": "rising river water level",
    "drainage_poor": "poor drainage in the area",
    "low_elevation": "low ground elevation",
    "flood_history": "a history of flooding nearby",
}

def generate_advisory(risk_score, tier, profile=None, language="English",
                       rainfall_mm=None, water_level_m=None, breakdown=None):
    profile_text = ", ".join(profile) if profile else "general public"

    # Identify the single biggest contributor to this score, so the advisory
    # can reference the ACTUAL driving factor instead of generic boilerplate.
    dominant_factor = None
    if breakdown:
        top_key = max(breakdown, key=breakdown.get)
        dominant_factor = FACTOR_LABELS.get(top_key, top_key)

    context_lines = []
    if rainfall_mm is not None:
        context_lines.append(f"3-day cumulative rainfall: {rainfall_mm}mm")
    if water_level_m is not None:
        context_lines.append(f"Current river water level: {water_level_m}m")
    if dominant_factor:
        context_lines.append(f"Primary driver of this risk score: {dominant_factor}")
    context_text = "\n".join(context_lines) if context_lines else "No additional sensor context available."

    prompt = f"""You are a flood safety advisor for Gorakhpur, India.
Risk Score: {risk_score}/100
Risk Tier: {tier}
Vulnerable groups present: {profile_text}
Respond in: {language}

Real current conditions at this location:
{context_text}

Write a short (3-4 sentences), clear, actionable flood safety advisory for a resident at this location.
Reference the specific real conditions above (e.g. the actual rainfall figure or water level) rather than generic advice.
Be concrete about what to do RIGHT NOW given this specific tier — Low means monitor, Moderate means prepare,
High means get ready to move, Severe means evacuate immediately.
If vulnerable groups are listed, tailor advice for them specifically.
Do not use markdown formatting."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    advisory = generate_advisory(
        56.6, "High", profile=["Elderly", "Medical"], language="English",
        rainfall_mm=37.3, water_level_m=75.91,
        breakdown={"rainfall_mm": 3.7, "water_level_m": 20.0, "drainage_poor": 16.0, "low_elevation": 12.0, "flood_history": 9.0},
    )
    print(advisory)