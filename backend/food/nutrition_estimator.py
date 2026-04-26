def estimate_nutrition(item):
    nutrition = item.get("nutrition") or item.get("estimated_nutrition") or {}
    return {
        "calories": _number(nutrition.get("calories"), 500),
        "protein_g": _number(nutrition.get("protein_g"), 16),
        "carbs_g": _number(nutrition.get("carbs_g"), 55),
        "fat_g": _number(nutrition.get("fat_g"), 18),
        "fiber_g": _number(nutrition.get("fiber_g"), 4),
        "sugar_g": _number(nutrition.get("sugar_g"), 8),
        "sodium_mg": _number(nutrition.get("sodium_mg"), 650),
    }


def _number(value, default):
    try:
        if value in ("", None):
            return default
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return default
