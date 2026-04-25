from food.food_store import load_dining_data
from planner.schemas import skill_result


def run_dining_skill(intent, context):
    items = sorted(load_dining_data(), key=lambda item: item["scores"]["carbon"], reverse=True)
    recommended = [
        next(item for item in items if item["meal_period"] == "dinner"),
        next(item for item in items if item["meal_period"] == "lunch"),
    ]
    return skill_result(
        "dining",
        recommendations=recommended,
        constraints=["prefer_open_dining_halls", "preserve_protein", "prefer_low_carbon_options"],
        evidence=["dining_mock.json"],
    )
