import json
from pathlib import Path

from planner.schemas import skill_result


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def run_transportation_skill(intent, context):
    factors = json.loads((DATA_DIR / "carbon_factors.json").read_text(encoding="utf-8"))
    transport = factors["transportation"]
    emergency_uber = "emergency_uber" in intent.get("detected_constraints", [])
    preferences = set(intent.get("transportation_preferences", []))

    options = [
        _option("walk", 30, transport["walk_kg_co2e"], preferences),
        _option("bike", 18, transport.get("bike_kg_co2e", 0.0), preferences),
        _option("bus", 30, transport["bus_kg_co2e"], preferences),
        _option("rideshare", 12, transport["rideshare_kg_co2e"], preferences, penalize="avoid_rideshare" in preferences),
    ]
    options.sort(key=lambda item: item["planner_score"], reverse=True)

    return skill_result(
        "transportation",
        recommendations=options,
        constraints=["emergency_rideshare_logged" if emergency_uber else "prefer_walk_or_transit"],
        evidence=[{"emergency_uber_estimated_co2e_kg": transport["rideshare_kg_co2e"] if emergency_uber else 0}, "carbon_factors.json"],
    )


def _option(mode, minutes, co2e, preferences, penalize=False):
    score = 1.0 - min(0.9, co2e / 6)
    if mode in preferences:
        score += 0.12
    if mode in ("walk", "bike") and "avoid_rideshare" in preferences:
        score += 0.08
    if penalize:
        score -= 0.45
    return {
        "mode": mode,
        "estimated_minutes": minutes,
        "estimated_co2e_kg": round(co2e, 2),
        "planner_score": round(max(0, min(1, score)), 2),
    }
