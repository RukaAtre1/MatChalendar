import re


def parse_intent(prompt):
    text = (prompt or "").lower()
    constraints = []
    dietary_preferences = []
    avoid_terms = []
    nutrition_goals = []
    activity_goals = []
    transportation_preferences = []

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

    if "vegetarian" in text:
        dietary_preferences.append("vegetarian")
    if "vegan" in text:
        dietary_preferences.append("vegan")
    if "halal" in text:
        dietary_preferences.append("halal")
    if "low carbon" in text or "low-carbon" in text or "plant" in text:
        dietary_preferences.append("low_carbon")
    if "high protein" in text or "protein" in text or "post-workout" in text:
        nutrition_goals.append("high_protein")
    if "low sodium" in text:
        nutrition_goals.append("low_sodium")

    for avoid_match in re.finditer(r"(?:avoid|without|no)\s+([a-z][a-z\s-]{1,28})", text):
        avoid_terms.append(avoid_match.group(1).strip(" .,!"))

    if any(term in text for term in ("workout", "gym", "exercise", "fitness", "strength", "training")):
        activity_goals.append("workout")
    if any(term in text for term in ("walk", "walking", "recovery walk")):
        activity_goals.append("walk")
    if any(term in text for term in ("bike", "biking", "cycle")):
        activity_goals.append("bike")
    if any(term in text for term in ("yoga", "mobility", "stretch")):
        activity_goals.append("mobility")

    if any(term in text for term in ("walk", "walking")):
        transportation_preferences.append("walk")
    if any(term in text for term in ("bike", "biking", "cycle")):
        transportation_preferences.append("bike")
    if any(term in text for term in ("transit", "bus", "big blue bus")):
        transportation_preferences.append("bus")
    if any(term in text for term in ("avoid uber", "avoid rideshare", "no uber", "no rideshare", "without rideshare")):
        transportation_preferences.append("avoid_rideshare")

    weight_kg = _extract_weight_kg(text)

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
        "dietary_preferences": _dedupe(dietary_preferences),
        "avoid_terms": _dedupe(avoid_terms),
        "nutrition_goals": _dedupe(nutrition_goals),
        "activity_goals": _dedupe(activity_goals),
        "transportation_preferences": _dedupe(transportation_preferences),
        "user_weight_kg": weight_kg,
    }


def _extract_weight_kg(text):
    kg_match = re.search(r"(\d{2,3})\s*kg", text)
    if kg_match:
        return int(kg_match.group(1))
    lb_match = re.search(r"(\d{2,3})\s*(?:lb|lbs|pounds)", text)
    if lb_match:
        return round(int(lb_match.group(1)) * 0.453592)
    return None


def _dedupe(values):
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result
