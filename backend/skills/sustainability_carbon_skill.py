import json
from pathlib import Path

from planner.schemas import skill_result


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def run_sustainability_carbon_skill(intent, context):
    factors = json.loads((DATA_DIR / "carbon_factors.json").read_text(encoding="utf-8"))
    emergency_uber = "emergency_uber" in intent.get("detected_constraints", [])
    dining_total = _recommended_dining_total(context.get("dining", {}))
    transport_total = _selected_transport_total(context.get("transportation", {}))
    emergency_total = factors["transportation"]["rideshare_kg_co2e"] if emergency_uber else 0
    base_week = 10.5
    current = round(base_week + dining_total + transport_total + emergency_total, 1)

    carbon_budget = {
        "weekly_target_kg_co2e": factors["weekly_target_kg_co2e"],
        "current_estimated_kg_co2e": current,
        "status": "slightly_above_expected_today" if emergency_uber else "on_track",
        "adjustment_strategy": "lower_carbon_dining_and_walkable_routes",
        "components": {
            "base_week_kg_co2e": base_week,
            "recommended_dining_kg_co2e": round(dining_total, 2),
            "planned_transport_kg_co2e": round(transport_total, 2),
            "logged_emergency_transport_kg_co2e": round(emergency_total, 2),
        },
    }

    return {
        **skill_result(
            "sustainability_carbon",
            recommendations=["choose_low_carbon_dinner", "prefer_walk_bike_or_transit", "keep_recovery_walk"],
            constraints=["stay_under_weekly_carbon_target", "do_not_penalize_emergency_travel"],
            evidence=["carbon_factors.json", {"emergency_uber": emergency_uber}],
        ),
        "carbon_budget": carbon_budget,
    }


def _recommended_dining_total(dining_output):
    total = 0
    for item in dining_output.get("recommendations", []):
        total += float(item.get("carbon", {}).get("estimated_co2e_kg", 0))
    return total


def _selected_transport_total(transportation_output):
    recommendations = transportation_output.get("recommendations", [])
    if not recommendations:
        return 0.0
    best = recommendations[0]
    return float(best.get("estimated_co2e_kg", 0))
