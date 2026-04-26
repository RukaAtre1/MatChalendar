MONDAY = "2026-04-27"


def replan_calendar(intent, skill_outputs):
    dining_output = skill_outputs["dining"]
    dinner = _first_meal(dining_output, "dinner")
    lunch = _first_meal(dining_output, "lunch") or dinner
    transport_options = skill_outputs.get("transportation", {}).get("recommendations", [])
    best_transport = transport_options[0] if transport_options else {"mode": "walk", "estimated_minutes": 30, "estimated_co2e_kg": 0.0}
    health_recommendations = skill_outputs.get("health", {}).get("recommendations", [])
    recovery_activity = _activity(health_recommendations, "recovery_walk")
    workout_activity = _activity(health_recommendations, "light_workout")
    planner_text = _planner_text(intent)
    goal_text = _goal_text(intent)
    raw_text = _raw_planner_text(intent)
    low_energy = _mentions(raw_text, ["low energy", "tired", "exhausted", "stress", "recovery-focused", "burnout"])
    sustainability = _mentions(raw_text, ["carbon", "sustain", "emission", "vegetarian", "plant", "walk", "transit", "low waste"])
    study_heavy = _mentions(planner_text, ["homework", "assignment", "schoolwork", "study", "cs", "exam", "midterm", "final", "quiz", "review", "focused"])
    has_meeting = _mentions(raw_text, ["meeting", "group project", "project meeting"])
    exam_prep = _mentions(goal_text, ["exam", "midterm", "final", "quiz", "office hours", "practice problems", "review session"])
    fitness = _mentions(goal_text, ["fitness", "workout", "gym", "training", "exercise", "yoga", "mobility", "wooden center", "post-workout"])
    errands = _mentions(goal_text, ["errand", "laundry", "grocer", "shopping", "pharmacy", "buy groceries"])
    social = _mentions(goal_text, ["friend", "social", "club", "event"])
    car_free = _mentions(goal_text, ["no rideshare", "without rideshare", "avoid rideshare", "walk", "bike", "biking", "transit", "bus"])

    blocks = [
        {
            "id": "block_class_mon",
            "title": "Class block",
            "type": "class",
            "start": f"{MONDAY}T10:00:00",
            "end": f"{MONDAY}T14:00:00",
            "location": "UCLA campus",
            "reason": "This fixed class block is protected before meals, recovery, and study work are placed around it.",
            "scores": {"time": 0.98, "health": 0.66, "energy": 0.70, "sustainability": 0.72, "carbon": 0.84},
            "carbon": {"estimated_co2e_kg": 0.1, "baseline_co2e_kg": 0.1, "delta_co2e_kg": 0.0, "category": "calendar"},
            "skills_used": ["calendar"],
            "data_sources": ["user_schedule"],
        },
        {
            "id": "block_walk_mon",
            "title": "Recovery walk",
            "type": "recovery",
            "start": f"{MONDAY}T14:15:00",
            "end": f"{MONDAY}T14:45:00",
            "location": "Bruin Walk",
            "reason": "A short walk after class creates an energy reset without adding more transportation emissions after the emergency Uber.",
            "scores": {"time": 0.88, "health": 0.84, "energy": 0.80, "sustainability": 0.90, "carbon": 0.96},
            "carbon": {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.4, "delta_co2e_kg": -0.4, "category": "transportation"},
            "activity": _activity_payload(recovery_activity),
            "transportation": {"mode": "walk", "estimated_minutes": 30, "estimated_co2e_kg": 0.0},
            "skills_used": ["calendar", "transportation", "energy", "health", "sustainability_carbon"],
            "data_sources": ["carbon_factors", "user_schedule"],
        },
        {
            "id": "block_dinner_mon",
            "title": dinner.get("meal_name") or f"Balanced dinner at {dinner['dining_hall']}",
            "type": "meal",
            "start": f"{MONDAY}T18:30:00",
            "end": f"{MONDAY}T19:15:00",
            "location": dinner["dining_hall"],
            "meal_name": dinner.get("meal_name", dinner.get("name", "Balanced dinner")),
            "meal_type": dinner.get("meal_type", "dinner"),
            "reason": dinner.get("reason", "Dinner is selected after health adequacy is validated, then ranked for lower carbon impact."),
            "scores": {"time": 0.86, "health": dinner["scores"]["health"], "energy": dinner["scores"]["energy"], "sustainability": dinner["scores"]["sustainability"], "carbon": dinner["scores"]["carbon"]},
            "carbon": _carbon_payload(dinner, 1.8),
            "items": dinner.get("items", []),
            "estimated_nutrition": dinner.get("estimated_nutrition", dinner.get("nutrition", {})),
            "nutrition": dinner.get("estimated_nutrition", dinner.get("nutrition", {})),
            "plate_balance": dinner.get("plate_balance", {}),
            "adequacy_status": dinner.get("adequacy_status", "complete_meal"),
            "adequacy_warnings": dinner.get("adequacy_warnings", []),
            "menu_sections": _menu_sections(dinner),
            "dining_choices": _dining_choices(dining_output, "dinner", dinner),
            "source_url": dinner.get("source_url", ""),
            "skills_used": ["dining", "sustainability_carbon", "health", "energy", "calendar"],
            "data_sources": ["ucla_dining_cache", "carbon_factors", "local_planner"],
        },
        _study_block(low_energy, study_heavy),
        _winddown_block(low_energy),
        {
            "id": "block_transit_tue",
            "title": _transport_title(best_transport),
            "type": "commute",
            "start": "2026-04-28T09:20:00",
            "end": "2026-04-28T09:50:00",
            "location": _transport_location(best_transport),
            "reason": _transport_reason(best_transport),
            "scores": {"time": 0.78, "health": 0.70, "energy": 0.74, "sustainability": 0.91, "carbon": best_transport.get("planner_score", 0.93)},
            "carbon": {"estimated_co2e_kg": best_transport["estimated_co2e_kg"], "baseline_co2e_kg": 1.2, "delta_co2e_kg": round(best_transport["estimated_co2e_kg"] - 1.2, 2), "category": "transportation", "method": "carbon_factors"},
            "transportation": best_transport,
            "skills_used": ["transportation", "sustainability_carbon", "calendar"],
            "data_sources": ["carbon_factors", "user_schedule"],
        },
        {
            "id": "block_lunch_tue",
            "title": lunch.get("meal_name") or "Balanced plant-forward lunch",
            "type": "meal",
            "start": "2026-04-28T12:00:00",
            "end": "2026-04-28T12:45:00",
            "location": lunch["dining_hall"],
            "meal_name": lunch.get("meal_name", lunch.get("name", "Balanced lunch")),
            "meal_type": lunch.get("meal_type", "lunch"),
            "reason": lunch.get("reason", "Lunch is selected after health adequacy is validated, then ranked for lower carbon impact."),
            "scores": {"time": 0.84, "health": lunch["scores"]["health"], "energy": lunch["scores"]["energy"], "sustainability": lunch["scores"]["sustainability"], "carbon": lunch["scores"]["carbon"]},
            "carbon": _carbon_payload(lunch, 1.5),
            "items": lunch.get("items", []),
            "estimated_nutrition": lunch.get("estimated_nutrition", lunch.get("nutrition", {})),
            "nutrition": lunch.get("estimated_nutrition", lunch.get("nutrition", {})),
            "plate_balance": lunch.get("plate_balance", {}),
            "adequacy_status": lunch.get("adequacy_status", "complete_meal"),
            "adequacy_warnings": lunch.get("adequacy_warnings", []),
            "menu_sections": _menu_sections(lunch),
            "dining_choices": _dining_choices(dining_output, "lunch", lunch),
            "source_url": lunch.get("source_url", ""),
            "skills_used": ["dining", "health", "energy", "sustainability_carbon"],
            "data_sources": ["ucla_dining_cache", "carbon_factors"],
        },
        {
            "id": "block_review_wed",
            "title": "Review sprint",
            "type": "study",
            "start": "2026-04-29T15:00:00",
            "end": "2026-04-29T16:15:00",
            "location": "Study commons",
            "reason": "A midweek review prevents Monday night from becoming the only academic catch-up slot.",
            "scores": {"time": 0.84, "health": 0.70, "energy": 0.79, "sustainability": 0.76, "carbon": 0.86},
            "carbon": {"estimated_co2e_kg": 0.05, "baseline_co2e_kg": 0.05, "delta_co2e_kg": 0.0, "category": "study"},
            "skills_used": ["study", "calendar", "energy"],
            "data_sources": ["user_schedule"],
        },
        {
            "id": "block_workout_thu",
            "title": "Light workout",
            "type": "recovery",
            "start": "2026-04-30T16:00:00",
            "end": "2026-04-30T17:00:00",
            "location": "John Wooden Center",
            "reason": "A light workout lands in a low-conflict window and supports health without making the week feel overpacked.",
            "scores": {"time": 0.80, "health": 0.92, "energy": 0.75, "sustainability": 0.78, "carbon": 0.88},
            "carbon": {"estimated_co2e_kg": 0.02, "baseline_co2e_kg": 0.02, "delta_co2e_kg": 0.0, "category": "health"},
            "activity": _activity_payload(workout_activity),
            "skills_used": ["health", "energy", "calendar"],
            "data_sources": ["local_planner"],
        },
    ]

    if has_meeting:
        blocks.append(
            _block(
                "block_project_meeting_mon",
                "Group project meeting",
                "study",
                f"{MONDAY}T17:00:00",
                f"{MONDAY}T18:00:00",
                "Campus collaboration room",
                "The meeting is treated as a fixed collaboration commitment and placed before dinner and homework.",
                {"time": 0.92, "health": 0.70, "energy": 0.72, "sustainability": 0.76, "carbon": 0.86},
                {"estimated_co2e_kg": 0.02, "baseline_co2e_kg": 0.10, "delta_co2e_kg": -0.08, "category": "study"},
                ["calendar", "study", "energy"],
                ["prompt_constraint", "local_planner"],
            )
        )

    if low_energy:
        blocks.extend(_low_energy_blocks())

    if study_heavy and not low_energy:
        blocks.extend(_study_heavy_blocks())

    if exam_prep:
        blocks.extend(_exam_prep_blocks())

    if fitness:
        blocks.extend(_fitness_blocks())

    if errands:
        blocks.extend(_errand_blocks(car_free))

    if social:
        blocks.extend(_social_blocks())

    if sustainability:
        blocks.extend(_sustainability_blocks(dinner))

    return _dedupe_blocks(blocks)


def _first_meal(dining_output, meal_period):
    candidates = dining_output.get("candidate_meals", {}).get(meal_period, [])
    if candidates:
        return candidates[0]
    for item in dining_output.get("recommendations", []):
        if item.get("meal_period") == meal_period:
            return item
    recommendations = dining_output.get("recommendations", [])
    if recommendations:
        return recommendations[0]
    return {
        "name": "Plant-forward campus meal",
        "meal_name": "Balanced plant-forward campus meal",
        "meal_type": meal_period,
        "dining_hall": "UCLA Dining",
        "meal_period": meal_period,
        "station": "Recommended",
        "items": [
            {"name": "Lentil tofu protein", "station": "Protein", "quantity": 1, "calories": 260, "protein_g": 24, "carbs_g": 24, "fat_g": 8, "fiber_g": 9, "sodium_mg": 420},
            {"name": "Brown rice or quinoa", "station": "Whole grains", "quantity": 1, "calories": 220, "protein_g": 6, "carbs_g": 44, "fat_g": 4, "fiber_g": 5, "sodium_mg": 120},
            {"name": "Seasonal vegetables", "station": "Vegetables", "quantity": 1, "calories": 120, "protein_g": 5, "carbs_g": 22, "fat_g": 3, "fiber_g": 7, "sodium_mg": 180},
        ],
        "estimated_nutrition": {"calories": 600, "protein_g": 35, "carbs_g": 90, "fat_g": 15, "fiber_g": 21, "sodium_mg": 720, "added_sugar_g": 0},
        "nutrition": {"calories": 600, "protein_g": 35, "carbs_g": 90, "fat_g": 15, "fiber_g": 21, "sodium_mg": 720, "added_sugar_g": 0},
        "plate_balance": {
            "heuristic": "Harvard Healthy Eating Plate",
            "vegetables_and_fruits": ["Seasonal vegetables"],
            "whole_grains_or_quality_carbs": ["Brown rice or quinoa"],
            "healthy_protein": ["Lentil tofu protein"],
            "healthy_fat": [],
            "hydration": "Water or unsweetened drink",
            "has_protein": True,
            "has_grain_or_starch": True,
            "has_vegetables": True,
            "has_fruit_or_fiber": True,
            "has_healthy_fat": False,
        },
        "adequacy_status": "complete_meal",
        "adequacy_warnings": [],
        "carbon": {"estimated_co2e_kg": 0.95, "method": "fallback_balanced_meal", "source": "local_planner"},
        "scores": {"health": 0.88, "energy": 0.86, "sustainability": 0.88, "carbon": 0.76},
        "reason": "This fallback meal protects energy adequacy first, then keeps the protein bundle plant-forward.",
        "source_url": "",
    }


def _dining_choices(dining_output, meal_period, selected):
    selected_id = selected.get("id")
    choices = []
    for item in dining_output.get("candidate_meals", {}).get(meal_period, []):
        if item.get("id") == selected_id:
            continue
        choices.append(
            {
                "dining_hall": item.get("dining_hall", "UCLA Dining"),
                "name": item.get("meal_name", item.get("name", "Menu item")),
                "meal_name": item.get("meal_name", item.get("name", "Menu item")),
                "meal_type": item.get("meal_type", meal_period),
                "estimated_co2e_kg": item.get("carbon", {}).get("estimated_co2e_kg", 0),
                "items": item.get("items", []),
                "estimated_nutrition": item.get("estimated_nutrition", item.get("nutrition", {})),
                "nutrition": item.get("estimated_nutrition", item.get("nutrition", {})),
                "plate_balance": item.get("plate_balance", {}),
                "adequacy_status": item.get("adequacy_status", "complete_meal"),
                "adequacy_warnings": item.get("adequacy_warnings", []),
                "source_url": item.get("source_url", ""),
                "menu_sections": _menu_sections(item),
            }
        )
    return choices[:4]


def _menu_sections(item):
    if item.get("menu_sections"):
        return item["menu_sections"]
    if item.get("items"):
        sections = {}
        for menu_item in item["items"]:
            station = menu_item.get("station") or "Recommended"
            sections.setdefault(station, []).append(menu_item)
        return [{"station": station, "items": items} for station, items in sections.items()]
    return [
        {
            "station": item.get("station") or "Recommended",
            "items": [
                {
                    "name": item.get("name", "Menu item"),
                    "quantity": 1,
                    "calories": item.get("nutrition", {}).get("calories"),
                    "protein_g": item.get("nutrition", {}).get("protein_g"),
                }
            ],
        }
    ]


def _carbon_payload(item, baseline):
    estimated = float(item.get("carbon", {}).get("estimated_co2e_kg", 0))
    return {
        "estimated_co2e_kg": estimated,
        "baseline_co2e_kg": baseline,
        "delta_co2e_kg": round(estimated - baseline, 2),
        "category": "dining",
        "method": item.get("carbon", {}).get("method", "ucla_tag_plus_estimator"),
        "source": item.get("carbon", {}).get("source", "ucla_dining_cache"),
    }


def _meal_extra(meal, meal_type):
    return {
        "meal_name": meal.get("meal_name", meal.get("name", "Balanced meal")),
        "meal_type": meal.get("meal_type", meal_type),
        "items": meal.get("items", []),
        "estimated_nutrition": meal.get("estimated_nutrition", meal.get("nutrition", {})),
        "nutrition": meal.get("estimated_nutrition", meal.get("nutrition", {})),
        "plate_balance": meal.get("plate_balance", {}),
        "adequacy_status": meal.get("adequacy_status", "complete_meal"),
        "adequacy_warnings": meal.get("adequacy_warnings", []),
        "menu_sections": _menu_sections(meal),
        "source_url": meal.get("source_url", ""),
    }


def _static_balanced_meal_extra(meal_name, meal_type, reason):
    items = [
        {"name": "Bean or tofu protein", "station": "Protein", "quantity": 1, "calories": 260, "protein_g": 24, "carbs_g": 24, "fat_g": 8, "fiber_g": 9, "sodium_mg": 420},
        {"name": "Brown rice or whole grain", "station": "Whole grains", "quantity": 1, "calories": 220, "protein_g": 6, "carbs_g": 44, "fat_g": 4, "fiber_g": 5, "sodium_mg": 120},
        {"name": "Seasonal vegetables", "station": "Vegetables", "quantity": 1, "calories": 140, "protein_g": 5, "carbs_g": 24, "fat_g": 4, "fiber_g": 7, "sodium_mg": 190},
        {"name": "Fruit or extra greens", "station": "Fruit and fiber", "quantity": 1, "calories": 80, "protein_g": 1, "carbs_g": 20, "fat_g": 0, "fiber_g": 4, "sodium_mg": 20},
    ]
    nutrition = {"calories": 700, "protein_g": 36, "carbs_g": 112, "fat_g": 16, "fiber_g": 25, "sodium_mg": 750, "added_sugar_g": 0}
    return {
        "meal_name": meal_name,
        "meal_type": meal_type,
        "items": items,
        "estimated_nutrition": nutrition,
        "nutrition": nutrition,
        "plate_balance": {
            "heuristic": "Harvard Healthy Eating Plate",
            "vegetables_and_fruits": ["Seasonal vegetables", "Fruit or extra greens"],
            "whole_grains_or_quality_carbs": ["Brown rice or whole grain"],
            "healthy_protein": ["Bean or tofu protein"],
            "healthy_fat": [],
            "hydration": "Water or unsweetened drink",
            "has_protein": True,
            "has_grain_or_starch": True,
            "has_vegetables": True,
            "has_fruit_or_fiber": True,
            "has_healthy_fat": False,
        },
        "adequacy_status": "complete_meal",
        "adequacy_warnings": [],
        "menu_sections": [
            {"station": "Protein", "items": [items[0]]},
            {"station": "Whole grains", "items": [items[1]]},
            {"station": "Vegetables and fruit", "items": items[2:]},
        ],
        "reason": reason,
    }


def _activity(recommendations, activity_name):
    for item in recommendations:
        if item.get("activity") == activity_name:
            return item
    return {}


def _activity_payload(activity):
    if not activity:
        return {}
    return {
        "name": activity.get("activity"),
        "duration_minutes": activity.get("duration_minutes"),
        "calories_burned": activity.get("calories_burned"),
        "intensity": activity.get("intensity"),
        "weight_kg": activity.get("weight_kg"),
        "method": "met_estimate_defaults",
    }


def _transport_title(option):
    labels = {"walk": "Walk-first commute", "bike": "Bike-first commute", "bus": "Transit-first commute", "rideshare": "Rideshare commute"}
    return labels.get(option.get("mode"), "Low-carbon commute")


def _transport_location(option):
    labels = {"walk": "UCLA walking route", "bike": "Bike route", "bus": "Big Blue Bus", "rideshare": "Rideshare"}
    return labels.get(option.get("mode"), "Campus route")


def _transport_reason(option):
    if option.get("mode") in ("walk", "bike"):
        return "Tomorrow's route uses an active, zero-direct-emission option where timing allows."
    if option.get("mode") == "bus":
        return "Tomorrow's route uses transit where the schedule allows, reducing carbon without creating a rushed morning."
    return "This route keeps the fastest option visible while tracking the higher carbon impact."


def _study_block(low_energy, study_heavy):
    if low_energy:
        return _block(
            "block_study_mon",
            "Gentle homework block",
            "study",
            f"{MONDAY}T20:00:00",
            f"{MONDAY}T20:55:00",
            "Dorm study lounge",
            "Because energy is low, homework is shortened and kept close to home after dinner.",
            {"time": 0.84, "health": 0.82, "energy": 0.86, "sustainability": 0.78, "carbon": 0.90},
            {"estimated_co2e_kg": 0.02, "baseline_co2e_kg": 0.20, "delta_co2e_kg": -0.18, "category": "study"},
            ["study", "calendar", "energy", "health", "explanation"],
            ["user_schedule", "local_planner"],
        )
    title = "Focused homework deep work" if study_heavy else "Homework deep work"
    return _block(
        "block_study_mon",
        title,
        "study",
        f"{MONDAY}T19:45:00",
        f"{MONDAY}T21:15:00",
        "Powell Library",
        "Homework stays tonight, but starts after dinner and a transition buffer so the plan does not stack heavy work immediately after class.",
        {"time": 0.89, "health": 0.72, "energy": 0.78, "sustainability": 0.80, "carbon": 0.88},
        {"estimated_co2e_kg": 0.05, "baseline_co2e_kg": 0.20, "delta_co2e_kg": -0.15, "category": "study"},
        ["study", "calendar", "energy", "explanation"],
        ["user_schedule", "local_planner"],
    )


def _winddown_block(low_energy):
    if low_energy:
        return _block(
            "block_winddown_mon",
            "Early recovery wind-down",
            "rest",
            f"{MONDAY}T21:30:00",
            f"{MONDAY}T22:15:00",
            "Dorm",
            "The evening ends earlier because the prompt signals low energy and recovery needs.",
            {"time": 0.86, "health": 0.94, "energy": 0.92, "sustainability": 0.76, "carbon": 0.90},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.0, "delta_co2e_kg": 0.0, "category": "rest"},
            ["health", "energy", "calendar"],
            ["local_planner"],
        )
    return _block(
        "block_winddown_mon",
        "Sleep wind-down",
        "rest",
        f"{MONDAY}T22:30:00",
        f"{MONDAY}T23:00:00",
        "Dorm",
        "A short wind-down block protects recovery after a day with class, emergency travel, and homework.",
        {"time": 0.82, "health": 0.88, "energy": 0.86, "sustainability": 0.74, "carbon": 0.90},
        {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.0, "delta_co2e_kg": 0.0, "category": "rest"},
        ["health", "energy", "calendar"],
        ["local_planner"],
    )


def _low_energy_blocks():
    return [
        _block(
            "block_recovery_tue",
            "Quiet recovery reset",
            "rest",
            "2026-04-28T15:00:00",
            "2026-04-28T15:35:00",
            "Dorm",
            "A low-effort recovery window protects energy before any optional work.",
            {"time": 0.82, "health": 0.93, "energy": 0.94, "sustainability": 0.72, "carbon": 0.90},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.0, "delta_co2e_kg": 0.0, "category": "rest"},
            ["health", "energy", "calendar"],
            ["local_planner"],
        )
    ]


def _study_heavy_blocks():
    return [
        _block(
            "block_focus_tue",
            "Focused study sprint",
            "study",
            "2026-04-28T15:30:00",
            "2026-04-28T16:45:00",
            "Powell Library",
            "A second study sprint spreads academic work across the week instead of relying on one long night.",
            {"time": 0.86, "health": 0.72, "energy": 0.80, "sustainability": 0.78, "carbon": 0.88},
            {"estimated_co2e_kg": 0.04, "baseline_co2e_kg": 0.10, "delta_co2e_kg": -0.06, "category": "study"},
            ["study", "calendar", "energy"],
            ["user_schedule", "local_planner"],
        ),
        _block(
            "block_review_fri",
            "Assignment review buffer",
            "study",
            "2026-05-01T14:00:00",
            "2026-05-01T15:00:00",
            "Study commons",
            "A Friday review buffer catches loose ends before the weekend.",
            {"time": 0.84, "health": 0.74, "energy": 0.78, "sustainability": 0.76, "carbon": 0.86},
            {"estimated_co2e_kg": 0.03, "baseline_co2e_kg": 0.08, "delta_co2e_kg": -0.05, "category": "study"},
            ["study", "calendar"],
            ["user_schedule"],
        ),
    ]


def _sustainability_blocks(dinner):
    return [
        _block(
            "block_grocery_fri",
            "Low-waste grocery loop",
            "commute",
            "2026-05-01T17:15:00",
            "2026-05-01T18:00:00",
            "Westwood Village",
            "A walkable grocery loop turns the sustainability goal into a concrete low-waste errand.",
            {"time": 0.78, "health": 0.74, "energy": 0.72, "sustainability": 0.94, "carbon": 0.95},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.8, "delta_co2e_kg": -0.8, "category": "transportation"},
            ["transportation", "sustainability_carbon", "calendar"],
            ["carbon_factors", "local_planner"],
        ),
        _block(
            "block_plant_dinner_fri",
            dinner.get("meal_name", "Plant-forward dinner"),
            "meal",
            "2026-05-01T18:30:00",
            "2026-05-01T19:15:00",
            dinner["dining_hall"],
            dinner.get("reason", "A second plant-forward dinner reinforces the lower-carbon dining pattern requested in the prompt."),
            {"time": 0.82, "health": dinner["scores"]["health"], "energy": dinner["scores"]["energy"], "sustainability": 0.95, "carbon": dinner["scores"]["carbon"]},
            _carbon_payload(dinner, 1.8),
            ["dining", "health", "energy", "sustainability_carbon"],
            ["ucla_dining_mock", "carbon_factors"],
            _meal_extra(dinner, "dinner"),
        ),
        _block(
            "block_bike_study_sat",
            "Bike study trip",
            "study",
            "2026-05-02T10:30:00",
            "2026-05-02T12:00:00",
            "Westwood study cafe",
            "A bikeable study trip combines focused work with a low-carbon route.",
            {"time": 0.80, "health": 0.82, "energy": 0.80, "sustainability": 0.93, "carbon": 0.95},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.6, "delta_co2e_kg": -0.6, "category": "transportation"},
            ["study", "transportation", "sustainability_carbon", "calendar"],
            ["carbon_factors", "local_planner"],
        ),
        _block(
            "block_meal_prep_sun",
            "Low-waste meal prep",
            "meal",
            "2026-05-03T17:00:00",
            "2026-05-03T18:15:00",
            "Dorm kitchen",
            "Meal prep converts the sustainability goal into lower-waste choices for the next week.",
            {"time": 0.76, "health": 0.84, "energy": 0.78, "sustainability": 0.96, "carbon": 0.92},
            {"estimated_co2e_kg": 0.4, "baseline_co2e_kg": 1.5, "delta_co2e_kg": -1.1, "category": "dining"},
            ["dining", "health", "sustainability_carbon", "calendar"],
            ["carbon_factors", "local_planner"],
            _static_balanced_meal_extra(
                "Low-waste meal prep",
                "dinner",
                "Meal prep includes protein, grains, vegetables, fruit or fiber, and water so sustainability does not replace adequacy.",
            ),
        ),
    ]


def _exam_prep_blocks():
    return [
        _block(
            "block_office_hours_tue",
            "Chemistry office hours",
            "study",
            "2026-04-28T17:05:00",
            "2026-04-28T17:45:00",
            "Young Hall",
            "Office hours are placed before the exam so confusing topics can be resolved before practice ramps up.",
            {"time": 0.88, "health": 0.72, "energy": 0.78, "sustainability": 0.74, "carbon": 0.86},
            {"estimated_co2e_kg": 0.03, "baseline_co2e_kg": 0.10, "delta_co2e_kg": -0.07, "category": "study"},
            ["study", "calendar", "energy"],
            ["prompt_constraint", "local_planner"],
        ),
        _block(
            "block_practice_wed",
            "Practice problem set",
            "study",
            "2026-04-29T16:30:00",
            "2026-04-29T17:45:00",
            "Study commons",
            "Practice problems follow the midweek review while the material is fresh, with a buffer after the review sprint.",
            {"time": 0.86, "health": 0.70, "energy": 0.76, "sustainability": 0.76, "carbon": 0.87},
            {"estimated_co2e_kg": 0.04, "baseline_co2e_kg": 0.10, "delta_co2e_kg": -0.06, "category": "study"},
            ["study", "calendar", "energy", "explanation"],
            ["prompt_constraint", "local_planner"],
        ),
        _block(
            "block_exam_review_thu",
            "Exam review session",
            "study",
            "2026-04-30T13:00:00",
            "2026-04-30T14:00:00",
            "Powell Library",
            "The last full review lands the day before the exam, leaving the evening for a lighter routine.",
            {"time": 0.84, "health": 0.72, "energy": 0.78, "sustainability": 0.76, "carbon": 0.88},
            {"estimated_co2e_kg": 0.04, "baseline_co2e_kg": 0.10, "delta_co2e_kg": -0.06, "category": "study"},
            ["study", "calendar", "energy"],
            ["prompt_constraint", "local_planner"],
        ),
        _block(
            "block_exam_fri",
            "Chemistry exam",
            "class",
            "2026-05-01T10:00:00",
            "2026-05-01T12:00:00",
            "UCLA campus",
            "The exam is treated as a fixed academic commitment and protected from other optimization.",
            {"time": 0.98, "health": 0.68, "energy": 0.72, "sustainability": 0.70, "carbon": 0.84},
            {"estimated_co2e_kg": 0.1, "baseline_co2e_kg": 0.1, "delta_co2e_kg": 0.0, "category": "calendar"},
            ["calendar", "study"],
            ["prompt_constraint"],
        ),
    ]


def _fitness_blocks():
    return [
        _block(
            "block_strength_tue",
            "Strength session",
            "recovery",
            "2026-04-28T17:50:00",
            "2026-04-28T18:35:00",
            "John Wooden Center",
            "A short strength block gives the fitness goal a visible place without crowding the academic core of the day.",
            {"time": 0.82, "health": 0.94, "energy": 0.80, "sustainability": 0.78, "carbon": 0.88},
            {"estimated_co2e_kg": 0.02, "baseline_co2e_kg": 0.02, "delta_co2e_kg": 0.0, "category": "health"},
            ["health", "energy", "calendar"],
            ["prompt_constraint", "local_planner"],
            {"activity": {"name": "strength_session", "duration_minutes": 45, "calories_burned": 276, "intensity": "moderate", "method": "met_estimate_defaults"}},
        ),
        _block(
            "block_mobility_wed",
            "Morning mobility",
            "recovery",
            "2026-04-29T08:15:00",
            "2026-04-29T09:00:00",
            "Dorm courtyard",
            "Mobility work supports recovery while keeping the afternoon available for study.",
            {"time": 0.84, "health": 0.92, "energy": 0.82, "sustainability": 0.82, "carbon": 0.94},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.02, "delta_co2e_kg": -0.02, "category": "health"},
            ["health", "energy", "calendar"],
            ["prompt_constraint", "local_planner"],
            {"activity": {"name": "mobility_reset", "duration_minutes": 45, "calories_burned": 138, "intensity": "light", "method": "met_estimate_defaults"}},
        ),
        _block(
            "block_recovery_meal_fri",
            "Post-workout recovery meal",
            "meal",
            "2026-05-01T16:15:00",
            "2026-05-01T16:55:00",
            "Bruin Plate",
            "A recovery meal is placed close to training time so fitness support is explicit, not implied.",
            {"time": 0.82, "health": 0.90, "energy": 0.84, "sustainability": 0.88, "carbon": 0.86},
            {"estimated_co2e_kg": 0.7, "baseline_co2e_kg": 1.5, "delta_co2e_kg": -0.8, "category": "dining"},
            ["dining", "health", "energy", "calendar"],
            ["ucla_dining_mock", "local_planner"],
            _static_balanced_meal_extra(
                "Post-workout recovery meal",
                "dinner",
                "This recovery meal protects post-workout protein, carbohydrates, vegetables, and hydration before optimizing for carbon.",
            ),
        ),
        _block(
            "block_active_recovery_sun",
            "Active recovery reset",
            "recovery",
            "2026-05-03T10:00:00",
            "2026-05-03T10:40:00",
            "Bruin Walk",
            "A light Sunday reset prevents the fitness plan from becoming all high-intensity work.",
            {"time": 0.80, "health": 0.92, "energy": 0.86, "sustainability": 0.86, "carbon": 0.94},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.02, "delta_co2e_kg": -0.02, "category": "health"},
            ["health", "energy", "calendar", "transportation"],
            ["prompt_constraint", "local_planner"],
            {"activity": {"name": "active_recovery", "duration_minutes": 40, "calories_burned": 154, "intensity": "light", "method": "met_estimate_defaults"}},
        ),
    ]


def _errand_blocks(car_free):
    route_reason = "The route is kept walk/transit-first because the prompt asks to avoid rideshare." if car_free else "Errands are batched so they do not fragment the study week."
    return [
        _block(
            "block_laundry_wed",
            "Laundry reset",
            "errand",
            "2026-04-29T17:55:00",
            "2026-04-29T18:45:00",
            "Dorm laundry",
            "Laundry is batched after academic work so it becomes a contained chore instead of a weeklong distraction.",
            {"time": 0.82, "health": 0.76, "energy": 0.72, "sustainability": 0.78, "carbon": 0.86},
            {"estimated_co2e_kg": 0.15, "baseline_co2e_kg": 0.25, "delta_co2e_kg": -0.10, "category": "errand"},
            ["calendar", "energy"],
            ["prompt_constraint", "local_planner"],
        ),
        _block(
            "block_admin_errands_thu",
            "Campus errand loop",
            "errand",
            "2026-04-30T17:20:00",
            "2026-04-30T18:05:00",
            "UCLA campus",
            route_reason,
            {"time": 0.80, "health": 0.74, "energy": 0.72, "sustainability": 0.88 if car_free else 0.78, "carbon": 0.92 if car_free else 0.84},
            {"estimated_co2e_kg": 0.0 if car_free else 0.1, "baseline_co2e_kg": 0.6, "delta_co2e_kg": -0.6 if car_free else -0.5, "category": "transportation"},
            ["calendar", "transportation", "sustainability_carbon"],
            ["prompt_constraint", "carbon_factors"],
        ),
        _block(
            "block_grocery_fri",
            "Car-free grocery run",
            "commute",
            "2026-05-01T17:15:00",
            "2026-05-01T18:00:00",
            "Westwood Village",
            "Groceries are grouped into a single walkable errand instead of several short trips.",
            {"time": 0.78, "health": 0.74, "energy": 0.72, "sustainability": 0.92, "carbon": 0.94},
            {"estimated_co2e_kg": 0.0, "baseline_co2e_kg": 0.8, "delta_co2e_kg": -0.8, "category": "transportation"},
            ["transportation", "sustainability_carbon", "calendar"],
            ["prompt_constraint", "carbon_factors"],
        ),
    ]


def _social_blocks():
    return [
        _block(
            "block_friend_dinner_tue",
            "Friend dinner",
            "social",
            "2026-04-28T18:45:00",
            "2026-04-28T19:45:00",
            "De Neve",
            "A social meal is placed after the academic day so connection is scheduled without displacing study work.",
            {"time": 0.82, "health": 0.82, "energy": 0.78, "sustainability": 0.78, "carbon": 0.84},
            {"estimated_co2e_kg": 0.8, "baseline_co2e_kg": 1.2, "delta_co2e_kg": -0.4, "category": "dining"},
            ["calendar", "dining", "health"],
            ["prompt_constraint", "ucla_dining_mock"],
        ),
        _block(
            "block_club_event_thu",
            "Club event",
            "social",
            "2026-04-30T18:15:00",
            "2026-04-30T19:15:00",
            "Ackerman Union",
            "The club event is protected as a real campus-life commitment while leaving the afternoon workout intact.",
            {"time": 0.84, "health": 0.80, "energy": 0.76, "sustainability": 0.78, "carbon": 0.86},
            {"estimated_co2e_kg": 0.05, "baseline_co2e_kg": 0.20, "delta_co2e_kg": -0.15, "category": "social"},
            ["calendar", "energy", "transportation"],
            ["prompt_constraint", "local_planner"],
        ),
    ]


def _block(id, title, type, start, end, location, reason, scores, carbon, skills_used, data_sources, extra=None):
    block = {
        "id": id,
        "title": title,
        "type": type,
        "start": start,
        "end": end,
        "location": location,
        "reason": reason,
        "scores": scores,
        "carbon": carbon,
        "skills_used": skills_used,
        "data_sources": data_sources,
    }
    if extra:
        block.update(extra)
    return block


def _planner_text(intent):
    parts = [_raw_planner_text(intent)]
    understanding = intent.get("understanding", {})
    for key in ("goals", "constraints", "priority_order"):
        value = understanding.get(key, [])
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts).lower()


def _raw_planner_text(intent):
    parts = [intent.get("raw_prompt", ""), intent.get("primary_goal", ""), intent.get("planning_scope", "")]
    parts.extend(intent.get("detected_constraints", []))
    return " ".join(parts).lower()


def _goal_text(intent):
    parts = [_raw_planner_text(intent)]
    understanding = intent.get("understanding", {})
    goals = understanding.get("goals", [])
    if isinstance(goals, list):
        parts.extend(str(item) for item in goals)
    return " ".join(parts).lower()


def _mentions(text, needles):
    return any(needle in text for needle in needles)


def _dedupe_blocks(blocks):
    seen = set()
    result = []
    for block in sorted(blocks, key=lambda item: (item["start"], item["end"], item["id"])):
        if block["id"] in seen:
            continue
        if _overlaps_existing(block, result):
            continue
        seen.add(block["id"])
        result.append(block)
    return result


def _overlaps_existing(block, scheduled):
    for existing in scheduled:
        if existing["start"][:10] == block["start"][:10] and block["start"] < existing["end"] and existing["start"] < block["end"]:
            return True
    return False
