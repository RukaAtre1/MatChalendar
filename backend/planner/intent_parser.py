import re


def parse_intent(prompt):
    text = (prompt or "").lower()
    constraints = []

    if "uber" in text or "rideshare" in text or "ride-share" in text:
        constraints.append("emergency_uber")

    class_match = re.search(r"class\s+from\s+(\d{1,2})(?::\d{2})?\s*(?:am|pm)?\s+to\s+(\d{1,2})(?::\d{2})?\s*(?:am|pm)?", text)
    if class_match:
        constraints.append(f"class_{class_match.group(1)}_to_{class_match.group(2)}")
    elif "class" in text:
        constraints.append("class_time")

    if "homework" in text or "assignment" in text or "study" in text:
        constraints.append("homework_tonight")

    if "low energy" in text or "tired" in text or "exhausted" in text:
        constraints.append("low_energy")

    primary_goal = "balanced_week"
    if "carbon" in text or "sustain" in text or "emission" in text:
        primary_goal = "reduce_weekly_carbon"
    elif "study" in text or "homework" in text:
        primary_goal = "finish_academic_work"

    planning_scope = "this_week" if "week" in text else "today"

    return {
        "primary_goal": primary_goal,
        "planning_scope": planning_scope,
        "detected_constraints": constraints,
    }
