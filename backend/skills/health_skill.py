from planner.schemas import skill_result


DEFAULT_WEIGHT_KG = 70
ACTIVITIES = {
    "walk": {"activity": "recovery_walk", "duration_minutes": 30, "met": 3.3, "intensity": "light"},
    "bike": {"activity": "bike_study_trip", "duration_minutes": 30, "met": 5.8, "intensity": "moderate"},
    "workout": {"activity": "light_workout", "duration_minutes": 60, "met": 4.5, "intensity": "moderate"},
    "strength": {"activity": "strength_session", "duration_minutes": 45, "met": 5.0, "intensity": "moderate"},
    "mobility": {"activity": "mobility_reset", "duration_minutes": 45, "met": 2.5, "intensity": "light"},
}


def run_health_skill(intent, context):
    weight_kg = intent.get("user_weight_kg") or DEFAULT_WEIGHT_KG
    requested = intent.get("activity_goals") or ["walk", "workout"]
    recommendations = []

    for key in requested:
        template = ACTIVITIES.get(key)
        if not template:
            continue
        recommendations.append(_activity_recommendation(template, weight_kg))

    if not any(item["activity"] == "recovery_walk" for item in recommendations):
        recommendations.insert(0, _activity_recommendation(ACTIVITIES["walk"], weight_kg))

    return skill_result(
        "health",
        recommendations=recommendations,
        constraints=["avoid_overtraining", "preserve_sleep_winddown", "favor_sufficient_protein"],
        evidence=[{"weight_kg": weight_kg, "weight_source": "prompt_or_default"}, "met_estimate_defaults"],
    )


def estimate_activity_calories(activity_key, duration_minutes, weight_kg=DEFAULT_WEIGHT_KG):
    met = ACTIVITIES.get(activity_key, ACTIVITIES["walk"])["met"]
    return round(met * 3.5 * weight_kg / 200 * duration_minutes)


def _activity_recommendation(template, weight_kg):
    calories = estimate_activity_calories(template["activity"].replace("_session", "").replace("_trip", ""), template["duration_minutes"], weight_kg)
    if template["activity"] == "light_workout":
        calories = estimate_activity_calories("workout", template["duration_minutes"], weight_kg)
    elif template["activity"] == "strength_session":
        calories = estimate_activity_calories("strength", template["duration_minutes"], weight_kg)
    elif template["activity"] == "mobility_reset":
        calories = estimate_activity_calories("mobility", template["duration_minutes"], weight_kg)
    elif template["activity"] == "bike_study_trip":
        calories = estimate_activity_calories("bike", template["duration_minutes"], weight_kg)
    return {
        **template,
        "calories_burned": calories,
        "weight_kg": weight_kg,
        "score": 0.92 if template["intensity"] == "light" else 0.88,
    }
