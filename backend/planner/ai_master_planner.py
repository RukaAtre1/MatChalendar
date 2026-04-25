from planner.intent_parser import parse_intent
from planner.skill_router import route_skills


PLANNER_CONTRACT_KEYS = {
    "understanding",
    "skill_calls",
    "tradeoffs",
    "calendar_strategy",
    "memory_update_suggestion",
}


def build_master_planner_contract(prompt, soul="", memory="", ai_response=None):
    if isinstance(ai_response, dict):
        return normalize_planner_contract(ai_response, prompt)
    return heuristic_planner_contract(prompt, soul=soul, memory=memory)


def heuristic_planner_contract(prompt, soul="", memory=""):
    intent = parse_intent(prompt)
    selected_skills = route_skills(intent)
    constraints = intent.get("detected_constraints", [])
    goals = [intent.get("primary_goal", "balanced_week")]

    skill_calls = [
        {
            "skill": skill,
            "reason": _skill_reason(skill, goals, constraints),
            "query": prompt or "Plan campus life week.",
        }
        for skill in selected_skills
    ]

    return {
        "understanding": {
            "goals": goals,
            "constraints": constraints,
            "priority_order": ["fixed_events", "user_energy", "academic_work", "dining", "transportation", "carbon"],
            "planning_scope": intent.get("planning_scope", "today"),
        },
        "skill_calls": skill_calls,
        "tradeoffs": _tradeoffs(constraints, goals),
        "calendar_strategy": _calendar_strategy(constraints, goals, bool(soul), bool(memory)),
        "memory_update_suggestion": _memory_suggestion(prompt),
    }


def normalize_planner_contract(contract, prompt=""):
    normalized = {key: contract.get(key) for key in PLANNER_CONTRACT_KEYS}
    fallback = heuristic_planner_contract(prompt)

    if not isinstance(normalized.get("understanding"), dict):
        normalized["understanding"] = fallback["understanding"]
    if not isinstance(normalized.get("skill_calls"), list):
        normalized["skill_calls"] = fallback["skill_calls"]
    if not isinstance(normalized.get("tradeoffs"), list):
        normalized["tradeoffs"] = fallback["tradeoffs"]
    if not isinstance(normalized.get("calendar_strategy"), str):
        normalized["calendar_strategy"] = fallback["calendar_strategy"]
    if not isinstance(normalized.get("memory_update_suggestion"), dict):
        normalized["memory_update_suggestion"] = fallback["memory_update_suggestion"]

    normalized["skill_calls"] = [
        {
            "skill": str(call.get("skill", "")).strip(),
            "reason": str(call.get("reason", "")).strip(),
            "query": str(call.get("query", prompt or "")).strip(),
        }
        for call in normalized["skill_calls"]
        if isinstance(call, dict) and call.get("skill")
    ]
    if not normalized["skill_calls"]:
        normalized["skill_calls"] = fallback["skill_calls"]

    return normalized


def _skill_reason(skill, goals, constraints):
    if skill == "calendar":
        return "Protect fixed events and avoid time conflicts."
    if skill == "dining":
        return "Find meals that support health, energy, and lower-carbon choices."
    if skill == "study":
        return "Place homework and review blocks without overloading the evening."
    if skill == "health":
        return "Add recovery and avoid plans that burn out the user."
    if skill == "energy":
        return "Sequence demanding tasks with buffers and rest."
    if skill == "transportation":
        return "Compare walk, transit, and rideshare implications."
    if skill == "sustainability_carbon":
        return "Translate sustainability into measurable calendar decisions."
    if skill == "explanation":
        return "Explain why each block was placed."
    return f"Support {', '.join(goals + constraints)}."


def _tradeoffs(constraints, goals):
    tradeoffs = ["Fixed commitments are protected before optimization."]
    if "emergency_uber" in constraints:
        tradeoffs.append("The plan compensates for rideshare carbon with future choices instead of penalizing the emergency.")
    if "homework_tonight" in constraints:
        tradeoffs.append("Homework remains tonight, but recovery and dining buffers prevent an overloaded evening.")
    if "reduce_weekly_carbon" in goals:
        tradeoffs.append("Lower-carbon dining and transportation are prioritized when timing and energy allow.")
    return tradeoffs


def _calendar_strategy(constraints, goals, soul_used, memory_used):
    parts = ["Respect fixed events first"]
    if "homework_tonight" in constraints:
        parts.append("place homework after dinner with a transition buffer")
    if "reduce_weekly_carbon" in goals or "emergency_uber" in constraints:
        parts.append("use dining and transportation choices to reduce weekly carbon")
    parts.append("keep recovery visible on the calendar")
    if memory_used:
        parts.append("apply stored user preferences where relevant")
    if soul_used:
        parts.append("keep explanations concrete and non-judgmental")
    return "; ".join(parts) + "."


def _memory_suggestion(prompt):
    text = (prompt or "").lower()
    if "prefer" in text or "i like" in text or "i hate" in text or "avoid" in text:
        return {
            "should_update": True,
            "reason": "The prompt appears to contain a stable preference.",
            "markdown_patch": f"- User preference from latest planning request: {prompt.strip()}",
        }
    return {
        "should_update": False,
        "reason": "",
        "markdown_patch": "",
    }

