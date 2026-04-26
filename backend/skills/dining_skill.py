from food.food_store import load_dining_dataset
from planner.schemas import skill_result


MEAL_TARGETS = {
    "breakfast": {"min": 300, "max": 500},
    "lunch": {"min": 500, "max": 800},
    "dinner": {"min": 600, "max": 900},
    "snack": {"min": 100, "max": 300},
}

FULL_MEAL_PERIODS = {"lunch", "dinner"}
FULL_MEAL_HARD_MIN_CALORIES = 400
FULL_MEAL_HARD_MIN_PROTEIN_G = 20

PROTEIN_KEYWORDS = {
    "bean",
    "beans",
    "chickpea",
    "chicken",
    "edamame",
    "egg",
    "eggs",
    "fish",
    "garbanzo",
    "hummus",
    "lentil",
    "lentils",
    "salmon",
    "shrimp",
    "tempeh",
    "tofu",
    "tuna",
    "turkey",
    "yogurt",
}
CARB_KEYWORDS = {
    "barley",
    "bread",
    "brown rice",
    "cereal",
    "couscous",
    "farro",
    "grain",
    "hash brown",
    "noodle",
    "oat",
    "pasta",
    "potato",
    "quinoa",
    "rice",
    "tortilla",
    "wheat berry",
}
VEGETABLE_KEYWORDS = {
    "arugula",
    "broccoli",
    "carrot",
    "cauliflower",
    "corn",
    "cucumber",
    "dandelion",
    "greens",
    "kale",
    "lettuce",
    "pepper",
    "salad",
    "salsa",
    "spinach",
    "squash",
    "tomato",
    "vegetable",
    "vegetables",
    "veggie",
}
FRUIT_KEYWORDS = {"apple", "apricot", "banana", "berry", "citrus", "fruit", "melon", "orange"}
HEALTHY_FAT_KEYWORDS = {"almond", "avocado", "olive", "peanut", "seed", "sesame", "tahini", "walnut"}


def run_dining_skill(intent, context):
    dataset = load_dining_dataset()
    items = dataset["items"]
    lunch_candidates = _rank_meal_bundles(items, intent, "lunch")[:5]
    dinner_candidates = _rank_meal_bundles(items, intent, "dinner")[:5]

    if not dinner_candidates:
        dinner_candidates = [_fallback_complete_meal("dinner")]
    if not lunch_candidates:
        lunch_candidates = [_fallback_complete_meal("lunch")]

    recommended = []
    if dinner_candidates:
        recommended.append(dinner_candidates[0])
    if lunch_candidates:
        recommended.append(lunch_candidates[0])

    rejected = {
        "lunch": _side_or_snack_candidates(items, intent, "lunch")[:5],
        "dinner": _side_or_snack_candidates(items, intent, "dinner")[:5],
    }

    return {
        **skill_result(
            "dining",
            recommendations=recommended,
            constraints=_constraints(intent),
            evidence=[
                {
                    "source": dataset["metadata"].get("source"),
                    "fallback": dataset["metadata"].get("fallback", False),
                    "item_count": dataset["metadata"].get("item_count", len(items)),
                    "meal_adequacy_policy": "health_first_harvard_plate_mvp",
                }
            ],
        ),
        "candidate_meals": {
            "lunch": lunch_candidates,
            "dinner": dinner_candidates,
        },
        "rejected_candidates": rejected,
    }


def _rank_meal_bundles(items, intent, meal_period):
    groups = {}
    for item in items:
        if meal_period and item.get("meal_period") != meal_period:
            continue
        hard_block, _reason = _hard_block_reason(item, intent)
        if hard_block:
            continue
        groups.setdefault(item.get("dining_hall", "UCLA Dining"), []).append(item)

    bundles = []
    for dining_hall, group_items in groups.items():
        bundles.extend(_build_group_bundles(group_items, intent, meal_period, dining_hall))

    if not bundles:
        return []

    ranked = [bundle for bundle in bundles if bundle["adequacy_status"] == "complete_meal"]
    ranked.sort(key=lambda bundle: bundle["planner_score"], reverse=True)
    return ranked


def _build_group_bundles(items, intent, meal_period, dining_hall):
    proteins = _top_component_items(items, "protein", intent)
    carbs = _top_component_items(items, "carb", intent)
    vegetables = _top_component_items(items, "vegetable", intent)
    fruits = _top_component_items(items, "fruit", intent)
    fats = _top_component_items(items, "healthy_fat", intent)

    bundles = []
    if not proteins or not carbs or not vegetables:
        return bundles

    for protein in proteins[:8]:
        for carb in carbs[:8]:
            for vegetable in vegetables[:8]:
                selected = _unique_items([protein, carb, vegetable])
                selected = _complete_low_energy_bundle(selected, items, fruits, fats, meal_period, intent)
                bundle = _meal_bundle(selected, meal_period, dining_hall, intent)
                if bundle["adequacy_status"] == "complete_meal":
                    bundles.append(bundle)

    return _dedupe_bundles(bundles)


def _complete_low_energy_bundle(selected, all_items, fruits, fats, meal_period, intent):
    selected = selected[:]
    adequacy = validate_meal_adequacy(selected, meal_period)
    target_min = MEAL_TARGETS.get(meal_period, {}).get("min", 0)
    pool = _component_completion_pool(all_items, fruits, fats, intent)
    while (
        meal_period in FULL_MEAL_PERIODS
        and (adequacy["adequacy_status"] != "complete_meal" or adequacy["estimated_nutrition"]["calories"] < target_min)
        and len(selected) < 5
    ):
        next_item = _best_completion_item(selected, pool)
        if not next_item:
            break
        selected.append(next_item)
        adequacy = validate_meal_adequacy(selected, meal_period)
    return selected


def _component_completion_pool(all_items, fruits, fats, intent):
    pool = _unique_items(
        fruits[:4]
        + fats[:3]
        + _top_component_items(all_items, "protein", intent)[:5]
        + _top_component_items(all_items, "carb", intent)[:5]
        + _top_component_items(all_items, "vegetable", intent)[:5]
    )
    return pool


def _best_completion_item(selected, pool):
    selected_ids = {item.get("id") for item in selected}
    current = _sum_nutrition(selected)

    def score(item):
        if item.get("id") in selected_ids:
            return -1
        nutrition = _nutrition(item)
        need_protein = max(0, FULL_MEAL_HARD_MIN_PROTEIN_G - current["protein_g"])
        need_calories = max(0, FULL_MEAL_HARD_MIN_CALORIES - current["calories"])
        return (
            min(nutrition["protein_g"], need_protein + 10) * 0.9
            + min(nutrition["calories"], need_calories + 250) / 100
            + nutrition.get("fiber_g", 0) * 0.2
            + item.get("scores", {}).get("carbon", 0.6) * 0.4
        )

    candidates = sorted(pool, key=score, reverse=True)
    return candidates[0] if candidates and score(candidates[0]) > 0 else None


def _top_component_items(items, component, intent):
    matches = [item for item in items if _has_component(item, component)]
    matches.sort(key=lambda item: _component_score(item, component, intent), reverse=True)
    return matches


def _component_score(item, component, intent):
    nutrition = _nutrition(item)
    scores = item.get("scores", {})
    base = scores.get("health", 0.6) * 0.45 + scores.get("energy", 0.6) * 0.25 + scores.get("carbon", 0.6) * 0.15
    if component == "protein":
        base += min(nutrition["protein_g"], 30) / 100
    elif component == "carb":
        base += min(nutrition["carbs_g"], 70) / 200
    elif component in ("vegetable", "fruit"):
        base += min(nutrition.get("fiber_g", 0), 10) / 50
    base += _preference_score(item, intent) * 0.05
    return base


def _meal_bundle(items, meal_period, dining_hall, intent):
    nutrition = _sum_nutrition(items)
    carbon = _sum_carbon(items)
    plate_balance = _plate_balance(items)
    adequacy = validate_meal_adequacy(items, meal_period)
    health_score = _bundle_health_score(items, nutrition, plate_balance, adequacy)
    satiety_score = _satiety_score(nutrition, meal_period)
    carbon_score = max(0.35, 1.0 - (carbon["estimated_co2e_kg"] / 4.0))
    schedule_score = 0.86
    preference_score = _bundle_preference_score(items, intent)
    planner_score = (
        health_score * 0.45
        + satiety_score * 0.25
        + carbon_score * 0.15
        + schedule_score * 0.10
        + preference_score * 0.05
    )
    first_url = next((item.get("source_url", "") for item in items if item.get("source_url")), "")
    item_names = [item.get("name", "Menu item") for item in items]
    meal_name = _meal_name(meal_period, item_names)

    return {
        "id": f"meal_{meal_period}_{_slug(dining_hall)}_{_slug('_'.join(item_names))[:32]}",
        "name": meal_name,
        "meal_name": meal_name,
        "meal_type": meal_period,
        "meal_period": meal_period,
        "dining_hall": dining_hall,
        "items": [_meal_item_payload(item) for item in items],
        "estimated_nutrition": nutrition,
        "nutrition": nutrition,
        "plate_balance": plate_balance,
        "adequacy_status": adequacy["adequacy_status"],
        "adequacy_warnings": adequacy["adequacy_warnings"],
        "carbon": carbon,
        "reason": _meal_reason(adequacy["adequacy_status"], meal_period, item_names),
        "skills_used": ["dining", "health", "energy", "sustainability_carbon"],
        "scores": {
            "health": round(health_score, 2),
            "energy": round(satiety_score, 2),
            "sustainability": round((carbon_score * 0.55) + (health_score * 0.30) + (preference_score * 0.15), 2),
            "carbon": round(carbon_score, 2),
        },
        "planner_score": round(planner_score, 3),
        "menu_sections": _bundle_menu_sections(items),
        "hydration_note": "Choose water or an unsweetened drink.",
        "source_url": first_url,
    }


def validate_meal_adequacy(items, meal_period):
    nutrition = _sum_nutrition(items)
    plate_balance = _plate_balance(items)
    warnings = []

    if meal_period in FULL_MEAL_PERIODS:
        if len(items) < 2:
            warnings.append("single_side_or_snack_item")
        if not plate_balance["has_protein"]:
            warnings.append("missing_protein_source")
        if not plate_balance["has_grain_or_starch"]:
            warnings.append("missing_grain_or_substantial_carb")
        if not plate_balance["has_vegetables"]:
            warnings.append("missing_vegetables")
        if nutrition["calories"] < FULL_MEAL_HARD_MIN_CALORIES:
            warnings.append("below_400_kcal_full_meal_minimum")
        if nutrition["protein_g"] < FULL_MEAL_HARD_MIN_PROTEIN_G:
            warnings.append("below_20g_protein_full_meal_minimum")
        target = MEAL_TARGETS[meal_period]
        if nutrition["calories"] < target["min"]:
            warnings.append(f"below_{meal_period}_target_calories")
        if nutrition["calories"] > target["max"]:
            warnings.append(f"above_{meal_period}_target_calories")
        status = "complete_meal" if not any(
            warning in warnings
            for warning in (
                "single_side_or_snack_item",
                "missing_protein_source",
                "missing_grain_or_substantial_carb",
                "missing_vegetables",
                "below_400_kcal_full_meal_minimum",
                "below_20g_protein_full_meal_minimum",
            )
        ) else "incomplete_meal"
    elif meal_period == "snack":
        status = "snack"
        target = MEAL_TARGETS["snack"]
        if not target["min"] <= nutrition["calories"] <= target["max"]:
            warnings.append("outside_snack_calorie_target")
    else:
        target = MEAL_TARGETS.get(meal_period)
        status = "complete_meal"
        if target and not target["min"] <= nutrition["calories"] <= target["max"]:
            warnings.append(f"outside_{meal_period}_calorie_target")

    if nutrition["sodium_mg"] > 1100:
        warnings.append("high_sodium")
    if nutrition.get("added_sugar_g", 0) > 20:
        warnings.append("high_added_sugar")

    return {
        "adequacy_status": status,
        "adequacy_warnings": warnings,
        "estimated_nutrition": nutrition,
        "plate_balance": plate_balance,
    }


def _side_or_snack_candidates(items, intent, meal_period):
    candidates = []
    for item in items:
        if item.get("meal_period") != meal_period:
            continue
        hard_block, block_reason = _hard_block_reason(item, intent)
        if hard_block:
            continue
        adequacy = validate_meal_adequacy([item], meal_period)
        if adequacy["adequacy_status"] == "complete_meal":
            continue
        nutrition = _nutrition(item)
        candidates.append(
            {
                **item,
                "meal_type": meal_period,
                "estimated_nutrition": nutrition,
                "nutrition": nutrition,
                "plate_balance": adequacy["plate_balance"],
                "adequacy_status": "snack" if nutrition["calories"] <= MEAL_TARGETS["snack"]["max"] else "incomplete_meal",
                "adequacy_warnings": ([block_reason] if block_reason else []) + adequacy["adequacy_warnings"],
                "side_or_snack": True,
            }
        )
    candidates.sort(key=lambda item: (item.get("scores", {}).get("carbon", 0.6), item["nutrition"]["calories"]), reverse=True)
    return candidates


def _has_component(item, component):
    text = _item_text(item)
    nutrition = _nutrition(item)
    if component == "protein":
        return nutrition["protein_g"] >= 9 or _contains_any(text, PROTEIN_KEYWORDS)
    if component == "carb":
        return nutrition["carbs_g"] >= 15 or _contains_any(text, CARB_KEYWORDS)
    if component == "vegetable":
        return _contains_any(text, VEGETABLE_KEYWORDS) or item.get("station", "").lower() in ("farmstand", "field greens bar")
    if component == "fruit":
        return _contains_any(text, FRUIT_KEYWORDS)
    if component == "healthy_fat":
        return _contains_any(text, HEALTHY_FAT_KEYWORDS)
    return False


def _plate_balance(items):
    fruit_items = [item for item in items if _has_component(item, "fruit")]
    vegetable_items = [item for item in items if _has_component(item, "vegetable")]
    carb_items = [item for item in items if _has_component(item, "carb")]
    protein_items = [item for item in items if _has_component(item, "protein")]
    fat_items = [item for item in items if _has_component(item, "healthy_fat")]
    return {
        "heuristic": "Harvard Healthy Eating Plate",
        "vegetables_and_fruits": _component_names(_unique_items(vegetable_items + fruit_items)),
        "whole_grains_or_quality_carbs": _component_names(carb_items),
        "healthy_protein": _component_names(protein_items),
        "healthy_fat": _component_names(fat_items),
        "hydration": "Water or unsweetened drink",
        "has_protein": bool(protein_items),
        "has_grain_or_starch": bool(carb_items),
        "has_vegetables": bool(vegetable_items),
        "has_fruit_or_fiber": bool(fruit_items) or _sum_nutrition(items).get("fiber_g", 0) >= 5,
        "has_healthy_fat": bool(fat_items),
    }


def _sum_nutrition(items):
    total = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "fiber_g": 0,
        "sodium_mg": 0,
        "added_sugar_g": 0,
    }
    for item in items:
        nutrition = _nutrition(item)
        for key in total:
            total[key] += nutrition.get(key, 0)
    return {key: round(value, 2) for key, value in total.items()}


def _nutrition(item):
    raw = item.get("nutrition") or item.get("estimated_nutrition") or {}
    return {
        "calories": _number(raw.get("calories"), 0),
        "protein_g": _number(raw.get("protein_g"), 0),
        "carbs_g": _number(raw.get("carbs_g"), 0),
        "fat_g": _number(raw.get("fat_g"), 0),
        "fiber_g": _number(raw.get("fiber_g"), 0),
        "sodium_mg": _number(raw.get("sodium_mg"), 0),
        "added_sugar_g": _number(raw.get("added_sugar_g"), 0),
    }


def _sum_carbon(items):
    estimated = round(sum(_number(item.get("carbon", {}).get("estimated_co2e_kg"), 0) for item in items), 2)
    return {
        "estimated_co2e_kg": estimated,
        "carbon_category": "low" if estimated <= 1.5 else "medium" if estimated <= 2.6 else "high",
        "method": "health_gated_bundle_sum",
        "source": "ucla_dining_cache",
    }


def _bundle_health_score(items, nutrition, plate_balance, adequacy):
    item_scores = [item.get("scores", {}).get("health", 0.72) for item in items]
    score = sum(item_scores) / max(len(item_scores), 1)
    score += 0.08 if plate_balance["has_protein"] and plate_balance["has_grain_or_starch"] and plate_balance["has_vegetables"] else -0.18
    score += 0.05 if nutrition.get("fiber_g", 0) >= 5 else 0
    score -= 0.08 if nutrition["sodium_mg"] > 1100 else 0
    score -= 0.12 if adequacy["adequacy_status"] != "complete_meal" else 0
    return _clamp_score(score)


def _satiety_score(nutrition, meal_period):
    target = MEAL_TARGETS.get(meal_period, {"min": 400, "max": 800})
    if target["min"] <= nutrition["calories"] <= target["max"]:
        calorie_score = 0.9
    elif nutrition["calories"] < target["min"]:
        calorie_score = max(0.35, nutrition["calories"] / max(target["min"], 1))
    else:
        calorie_score = max(0.45, 1 - ((nutrition["calories"] - target["max"]) / 600))
    protein_score = min(1.0, nutrition["protein_g"] / 30)
    fiber_score = min(1.0, nutrition.get("fiber_g", 0) / 8)
    return _clamp_score(calorie_score * 0.55 + protein_score * 0.30 + fiber_score * 0.15)


def _preference_score(item, intent):
    preferences = set(intent.get("dietary_preferences", []))
    features = item.get("features", {})
    score = 0.65
    if "vegetarian" in preferences and features.get("vegetarian"):
        score += 0.18
    if "vegan" in preferences and features.get("vegan"):
        score += 0.22
    return _clamp_score(score)


def _bundle_preference_score(items, intent):
    if not items:
        return 0.65
    return _clamp_score(sum(_preference_score(item, intent) for item in items) / len(items))


def _hard_block_reason(item, intent):
    features = item.get("features", {})
    preferences = set(intent.get("dietary_preferences", []))
    name = str(item.get("name", "")).lower()
    if "vegan" in preferences and not features.get("vegan"):
        return True, "not_vegan"
    if "vegetarian" in preferences and not features.get("vegetarian"):
        return True, "not_vegetarian"
    for avoid in intent.get("avoid_terms", []):
        if avoid and avoid in name:
            return True, f"avoid_{avoid.replace(' ', '_')}"
    return False, ""


def _meal_item_payload(item):
    nutrition = _nutrition(item)
    return {
        "name": item.get("name", "Menu item"),
        "station": item.get("station", "Recommended"),
        "quantity": 1,
        "calories": nutrition["calories"],
        "protein_g": nutrition["protein_g"],
        "carbs_g": nutrition["carbs_g"],
        "fat_g": nutrition["fat_g"],
        "fiber_g": nutrition.get("fiber_g"),
        "sodium_mg": nutrition.get("sodium_mg"),
        "carbon": item.get("carbon", {}),
    }


def _bundle_menu_sections(items):
    sections = {}
    for item in items:
        station = item.get("station") or "Recommended"
        sections.setdefault(station, []).append(_meal_item_payload(item))
    return [{"station": station, "items": station_items} for station, station_items in sections.items()]


def _meal_name(meal_period, item_names):
    prefix = "Balanced lunch" if meal_period == "lunch" else "Balanced dinner"
    if item_names:
        return f"{prefix}: {item_names[0]}"
    return prefix


def _meal_reason(status, meal_period, item_names):
    if status != "complete_meal":
        return "This option is treated as a snack or side because it does not meet full-meal nutrition adequacy."
    return (
        f"This {meal_period} passes health-first adequacy with protein, a grain or substantial carb, "
        "vegetables, and water before carbon is used as a secondary ranking factor."
    )


def _fallback_complete_meal(meal_period):
    base_items = [
        _synthetic_item("Lentil tofu protein", "Protein", 260, 24, 24, 8, 9, 420, 0.55),
        _synthetic_item("Brown rice or quinoa", "Whole grains", 220, 6, 44, 4, 5, 120, 0.35),
        _synthetic_item("Seasonal vegetables", "Vegetables", 120, 5, 22, 3, 7, 180, 0.25),
    ]
    if meal_period == "dinner":
        base_items.append(_synthetic_item("Fruit or extra greens", "Fruit and fiber", 80, 1, 20, 0, 4, 20, 0.15))
    return _meal_bundle(base_items, meal_period, "UCLA Dining", {"dietary_preferences": ["vegetarian"]})


def _synthetic_item(name, station, calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, co2e):
    return {
        "id": f"fallback_{_slug(name)}",
        "name": name,
        "station": station,
        "dining_hall": "UCLA Dining",
        "tags": ["vegetarian", "low-carbon"],
        "nutrition": {
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "fiber_g": fiber_g,
            "sodium_mg": sodium_mg,
            "added_sugar_g": 0,
        },
        "carbon": {"estimated_co2e_kg": co2e, "carbon_category": "low", "method": "fallback_balanced_meal"},
        "features": {"vegetarian": True, "vegan": False, "high_protein": protein_g >= 20, "low_sodium": sodium_mg <= 650},
        "scores": {"health": 0.88, "energy": 0.84, "sustainability": 0.9, "carbon": 0.86},
    }


def _constraints(intent):
    constraints = [
        "health_and_energy_adequacy_are_hard_constraints",
        "lunch_dinner_require_complete_meal_bundle",
        "do_not_schedule_side_or_snack_as_full_meal",
        "rank_carbon_only_after_nutrition_adequacy",
        "prefer_water_or_unsweetened_drinks",
    ]
    for preference in intent.get("dietary_preferences", []):
        constraints.append(f"prefer_{preference}")
    for goal in intent.get("nutrition_goals", []):
        constraints.append(f"target_{goal}")
    return constraints


def _component_names(items):
    return [item.get("name", "Menu item") for item in _unique_items(items)]


def _unique_items(items):
    seen = set()
    result = []
    for item in items:
        key = item.get("id") or item.get("name")
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _dedupe_bundles(bundles):
    seen = set()
    result = []
    for bundle in sorted(bundles, key=lambda item: item["planner_score"], reverse=True):
        key = (bundle["dining_hall"], tuple(item["name"] for item in bundle["items"]))
        if key in seen:
            continue
        seen.add(key)
        result.append(bundle)
    return result


def _item_text(item):
    parts = [
        item.get("name", ""),
        item.get("station", ""),
        item.get("ingredients", ""),
        " ".join(item.get("tags", [])),
    ]
    return " ".join(str(part) for part in parts).lower()


def _contains_any(text, needles):
    return any(needle in text for needle in needles)


def _slug(value):
    text = "".join(char.lower() if char.isalnum() else "_" for char in str(value))
    return "_".join(part for part in text.split("_") if part)[:80] or "item"


def _number(value, default):
    try:
        if value in ("", None):
            return default
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return default


def _clamp_score(value):
    return round(max(0.0, min(1.0, value)), 2)
