import json
from pathlib import Path

from planner.schemas import skill_result


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def run_calendar_skill(intent, context):
    schedule = json.loads((DATA_DIR / "sample_schedule.json").read_text(encoding="utf-8"))
    return skill_result(
        "calendar",
        recommendations=schedule["fixed_events"],
        constraints=["protect_fixed_events", "avoid_overlaps", "leave_transition_buffers"],
        evidence=["sample_schedule.json"],
    )
