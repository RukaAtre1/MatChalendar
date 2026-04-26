LOW_CARBON_KEYWORDS = {
    "bean",
    "beans",
    "lentil",
    "tofu",
    "tempeh",
    "vegetable",
    "vegetables",
    "veggie",
    "greens",
    "salad",
    "grain",
    "quinoa",
    "oatmeal",
    "fruit",
    "rice",
}

MEDIUM_CARBON_KEYWORDS = {
    "chicken",
    "turkey",
    "egg",
    "eggs",
    "cheese",
    "yogurt",
    "fish",
    "shrimp",
}

HIGH_CARBON_KEYWORDS = {
    "beef",
    "steak",
    "burger",
    "pork",
    "bacon",
    "sausage",
    "ribs",
    "lamb",
}


def estimate_food_carbon(item):
    existing = item.get("carbon", {}).get("estimated_co2e_kg")
    if isinstance(existing, (int, float)):
        return round(float(existing), 2)
    return estimate_food_carbon_profile(item)["estimated_co2e_kg"]


def estimate_food_carbon_profile(item):
    tags = _lower_set(item.get("tags", []))
    name = str(item.get("name", "")).lower()
    nutrition = item.get("nutrition") or item.get("estimated_nutrition") or {}
    calories = _number(nutrition.get("calories"), 500)

    if "low carbon" in tags or "low_carbon" in tags:
        value = 0.55
        category = "low"
        method = "ucla_low_carbon_tag"
    elif "high carbon" in tags or "high_carbon" in tags:
        value = 2.8
        category = "high"
        method = "ucla_high_carbon_tag"
    elif _contains_any(name, HIGH_CARBON_KEYWORDS):
        value = 2.4
        category = "high"
        method = "name_based_protein_estimator"
    elif _contains_any(name, MEDIUM_CARBON_KEYWORDS):
        value = 1.25
        category = "medium"
        method = "name_based_protein_estimator"
    elif _contains_any(name, LOW_CARBON_KEYWORDS) or tags.intersection({"vegan", "vegetarian"}):
        value = 0.65
        category = "low"
        method = "plant_forward_estimator"
    else:
        value = 1.1
        category = "medium"
        method = "default_menu_item_estimator"

    if calories > 750:
        value += 0.25
    elif calories < 250:
        value -= 0.15

    value = max(0.15, round(value, 2))
    return {
        "estimated_co2e_kg": value,
        "carbon_category": category,
        "method": method,
        "source": "ucla_tag_plus_estimator",
    }


def _lower_set(values):
    return {str(value).strip().lower().replace("_", " ") for value in values if str(value).strip()}


def _contains_any(text, needles):
    return any(needle in text for needle in needles)


def _number(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
