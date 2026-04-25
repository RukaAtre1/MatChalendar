import json
from pathlib import Path

from planner.schemas import skill_result


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def run_sustainability_carbon_skill(intent, context):
    factors = json.loads((DATA_DIR / "carbon_factors.json").read_text(encoding="utf-8"))
    emergency_uber = "emergency_uber" in intent.get("detected_constraints", [])
    current = 19.4 if emergency_uber else 14.2

    carbon_budget = {
        "weekly_target_kg_co2e": factors["weekly_target_kg_co2e"],
        "current_estimated_kg_co2e": current,
        "status": "slightly_above_expected_today" if emergency_uber else "on_track",
        "adjustment_strategy": "lower_carbon_dining_and_walkable_routes",
    }

    return {
        **skill_result(
            "sustainability_carbon",
            recommendations=["choose_low_carbon_dinner", "prefer_transit_tomorrow", "keep_recovery_walk"],
            constraints=["stay_under_weekly_carbon_target", "do_not_penalize_emergency_travel"],
            evidence=["carbon_factors.json", {"emergency_uber": emergency_uber}],
        ),
        "carbon_budget": carbon_budget,
    }
