def route_skills(intent):
    skills = ["calendar"]
    constraints = set(intent.get("detected_constraints", []))
    primary_goal = intent.get("primary_goal")

    if "homework_tonight" in constraints or primary_goal == "finish_academic_work":
        skills.append("study")

    if "emergency_uber" in constraints:
        skills.extend(["transportation", "sustainability_carbon"])

    if primary_goal == "reduce_weekly_carbon":
        skills.extend(["dining", "health", "energy", "sustainability_carbon"])

    for skill in ["dining", "health", "energy", "transportation", "sustainability_carbon", "study", "explanation"]:
        if skill not in skills:
            skills.append(skill)

    return skills
