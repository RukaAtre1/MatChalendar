from planner.schemas import skill_result


def run_health_skill(intent, context):
    return skill_result(
        "health",
        recommendations=[
            {"activity": "recovery_walk", "duration_minutes": 30, "score": 0.84},
            {"activity": "light_workout", "duration_minutes": 60, "score": 0.92},
        ],
        constraints=["avoid_overtraining", "preserve_sleep_winddown", "favor_sufficient_protein"],
        evidence=["meal_scores", "activity_defaults"],
    )
