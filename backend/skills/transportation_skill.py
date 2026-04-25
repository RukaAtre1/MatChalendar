import json
from pathlib import Path

from planner.schemas import skill_result


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def run_transportation_skill(intent, context):
    factors = json.loads((DATA_DIR / "carbon_factors.json").read_text(encoding="utf-8"))
    emergency_uber = "emergency_uber" in intent.get("detected_constraints", [])
    uber_kg = factors["transportation"]["rideshare_kg_co2e"] if emergency_uber else 0

    return skill_result(
        "transportation",
        recommendations=[
            {"mode": "walk", "estimated_minutes": 30, "estimated_co2e_kg": factors["transportation"]["walk_kg_co2e"]},
            {"mode": "bus", "estimated_minutes": 30, "estimated_co2e_kg": factors["transportation"]["bus_kg_co2e"]},
        ],
        constraints=["emergency_rideshare_logged" if emergency_uber else "prefer_walk_or_transit"],
        evidence=[{"emergency_uber_estimated_co2e_kg": uber_kg}, "carbon_factors.json"],
    )
