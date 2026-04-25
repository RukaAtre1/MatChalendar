MONDAY = "2026-04-27"


def replan_calendar(intent, skill_outputs):
    dining = skill_outputs["dining"]["recommendations"]
    dinner = next(item for item in dining if item["meal_period"] == "dinner")
    lunch = next(item for item in dining if item["meal_period"] == "lunch")
    planner_text = _planner_text(intent)
    raw_text = _raw_planner_text(intent)
    low_energy = _mentions(raw_text, ["low energy", "tired", "exhausted", "stress", "recover", "burnout"])
    sustainability = _mentions(raw_text, ["carbon", "sustain", "emission", "vegetarian", "plant", "walk", "transit", "low waste"])
    study_heavy = _mentions(raw_text, ["homework", "assignment", "study", "cs", "exam", "review", "focused"])
    has_meeting = _mentions(raw_text, ["meeting", "group project", "project meeting"])

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
            "skills_used": ["calendar", "transportation", "energy", "health", "sustainability_carbon"],
            "data_sources": ["carbon_factors", "user_schedule"],
        },
        {
            "id": "block_dinner_mon",
            "title": f"Low-carbon dinner at {dinner['dining_hall']}",
            "type": "meal",
            "start": f"{MONDAY}T18:30:00",
            "end": f"{MONDAY}T19:15:00",
            "location": dinner["dining_hall"],
            "reason": "The emergency Uber raised today's transportation impact, so dinner shifts toward a plant-forward option while preserving protein and evening energy.",
            "scores": {"time": 0.86, "health": dinner["scores"]["health"], "energy": dinner["scores"]["energy"], "sustainability": dinner["scores"]["sustainability"], "carbon": dinner["scores"]["carbon"]},
            "carbon": {"estimated_co2e_kg": dinner["carbon"]["estimated_co2e_kg"], "baseline_co2e_kg": 1.8, "delta_co2e_kg": -1.1, "category": "dining"},
            "skills_used": ["dining", "sustainability_carbon", "health", "energy", "calendar"],
            "data_sources": ["ucla_dining_mock", "carbon_factors", "local_planner"],
        },
        _study_block(low_energy, study_heavy),
        _winddown_block(low_energy),
        {
            "id": "block_transit_tue",
            "title": "Transit-first commute",
            "type": "commute",
            "start": "2026-04-28T09:20:00",
            "end": "2026-04-28T09:50:00",
            "location": "Big Blue Bus",
            "reason": "Tomorrow's route uses transit where the schedule allows, compensating for today's ride-share without creating a rushed morning.",
            "scores": {"time": 0.78, "health": 0.70, "energy": 0.74, "sustainability": 0.91, "carbon": 0.93},
            "carbon": {"estimated_co2e_kg": 0.3, "baseline_co2e_kg": 1.2, "delta_co2e_kg": -0.9, "category": "transportation"},
            "skills_used": ["transportation", "sustainability_carbon", "calendar"],
            "data_sources": ["carbon_factors", "user_schedule"],
        },
        {
            "id": "block_lunch_tue",
            "title": "Plant-forward lunch",
            "type": "meal",
            "start": "2026-04-28T12:00:00",
            "end": "2026-04-28T12:45:00",
            "location": lunch["dining_hall"],
            "reason": "A lighter lunch keeps afternoon energy steady while continuing the lower-carbon dining pattern.",
            "scores": {"time": 0.84, "health": lunch["scores"]["health"], "energy": lunch["scores"]["energy"], "sustainability": lunch["scores"]["sustainability"], "carbon": lunch["scores"]["carbon"]},
            "carbon": {"estimated_co2e_kg": lunch["carbon"]["estimated_co2e_kg"], "baseline_co2e_kg": 1.5, "delta_co2e_kg": -0.9, "category": "dining"},
            "skills_used": ["dining", "health", "energy", "sustainability_carbon"],
            "data_sources": ["ucla_dining_mock", "carbon_factors"],
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

    if sustainability:
        blocks.extend(_sustainability_blocks(dinner))

    return _dedupe_blocks(blocks)


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
            "Plant-forward dinner",
            "meal",
            "2026-05-01T18:30:00",
            "2026-05-01T19:15:00",
            dinner["dining_hall"],
            "A second plant-forward dinner reinforces the lower-carbon dining pattern requested in the prompt.",
            {"time": 0.82, "health": dinner["scores"]["health"], "energy": dinner["scores"]["energy"], "sustainability": 0.95, "carbon": dinner["scores"]["carbon"]},
            {"estimated_co2e_kg": dinner["carbon"]["estimated_co2e_kg"], "baseline_co2e_kg": 1.8, "delta_co2e_kg": -1.1, "category": "dining"},
            ["dining", "health", "energy", "sustainability_carbon"],
            ["ucla_dining_mock", "carbon_factors"],
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
        ),
    ]


def _block(id, title, type, start, end, location, reason, scores, carbon, skills_used, data_sources):
    return {
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


def _mentions(text, needles):
    return any(needle in text for needle in needles)


def _dedupe_blocks(blocks):
    seen = set()
    result = []
    for block in sorted(blocks, key=lambda item: (item["start"], item["end"], item["id"])):
        if block["id"] in seen:
            continue
        seen.add(block["id"])
        result.append(block)
    return result
