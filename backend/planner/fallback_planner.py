from planner.calendar_replanner import replan_calendar
from planner.intent_parser import parse_intent
from planner.schemas import PLAN_RESPONSE_VERSION
from planner.skill_router import route_skills
from skills.calendar_skill import run_calendar_skill
from skills.dining_skill import run_dining_skill
from skills.energy_skill import run_energy_skill
from skills.explanation_skill import run_explanation_skill
from skills.health_skill import run_health_skill
from skills.study_skill import run_study_skill
from skills.sustainability_carbon_skill import run_sustainability_carbon_skill
from skills.transportation_skill import run_transportation_skill


SKILL_RUNNERS = {
    "calendar": run_calendar_skill,
    "dining": run_dining_skill,
    "study": run_study_skill,
    "health": run_health_skill,
    "energy": run_energy_skill,
    "transportation": run_transportation_skill,
    "sustainability_carbon": run_sustainability_carbon_skill,
}


def build_fallback_plan(prompt, planner_context=None):
    planner_context = planner_context or {}
    ai_contract = planner_context.get("ai_contract") or {}
    intent = parse_intent(prompt)

    if ai_contract.get("understanding"):
        intent["understanding"] = ai_contract["understanding"]

    selected_skills = _select_skills(intent, ai_contract)
    skill_outputs = _run_skills(intent, selected_skills)

    blocks = replan_calendar(intent, skill_outputs)
    blocks = run_explanation_skill(intent, blocks)

    intent["skills_used"] = selected_skills

    return {
        "summary": _summary(ai_contract),
        "generated_by": "deterministic_fallback_planner",
        "response_version": PLAN_RESPONSE_VERSION,
        "intent": intent,
        "understanding": intent.get("understanding", _fallback_understanding(intent)),
        "carbon_budget": skill_outputs["sustainability_carbon"]["carbon_budget"],
        "plan_blocks": blocks,
        "skills_used": selected_skills,
        "skill_trace": _skill_trace(selected_skills, skill_outputs, ai_contract),
        "tradeoffs": ai_contract.get("tradeoffs", []),
        "calendar_strategy": ai_contract.get(
            "calendar_strategy",
            "Protect fixed events, place recovery and meals around them, then add study and low-carbon choices.",
        ),
        "memory_update_suggestion": ai_contract.get("memory_update_suggestion") or _default_memory_suggestion(),
        "integration_points": {
            "asus_gx10": "planner_provider_adapter",
            "asi_one": "planner_provider_adapter",
            "agentverse": "CampusLifePlannerAgent",
            "omegaclaw": "CampusLifePlannerSkill",
        },
    }


def _select_skills(intent, ai_contract):
    skill_names = [
        call.get("skill")
        for call in ai_contract.get("skill_calls", [])
        if isinstance(call, dict) and call.get("skill") in SKILL_RUNNERS
    ]
    selected = skill_names or route_skills(intent)
    if "sustainability_carbon" not in selected:
        selected.append("sustainability_carbon")
    if "dining" not in selected:
        selected.append("dining")
    if "explanation" not in selected:
        selected.append("explanation")
    return _dedupe(selected)


def _run_skills(intent, selected_skills):
    skill_outputs = {}
    for skill in selected_skills:
        if skill == "explanation":
            continue
        runner = SKILL_RUNNERS.get(skill)
        if runner:
            skill_outputs[skill] = runner(intent, skill_outputs)

    for required in ("calendar", "dining", "sustainability_carbon"):
        if required not in skill_outputs:
            skill_outputs[required] = SKILL_RUNNERS[required](intent, skill_outputs)

    return skill_outputs


def _skill_trace(selected_skills, skill_outputs, ai_contract):
    calls_by_skill = {
        call.get("skill"): call
        for call in ai_contract.get("skill_calls", [])
        if isinstance(call, dict) and call.get("skill")
    }
    trace = []
    for skill in selected_skills:
        output = skill_outputs.get(skill, {})
        call = calls_by_skill.get(skill, {})
        trace.append(
            {
                "skill": skill,
                "reason": call.get("reason", "Selected by fallback routing."),
                "query": call.get("query", ""),
                "constraints": output.get("constraints", []),
                "evidence": output.get("evidence", []),
            }
        )
    return trace


def _summary(ai_contract):
    strategy = ai_contract.get("calendar_strategy")
    if strategy:
        return f"Your week was replanned with this strategy: {strategy}"
    return "Your week was replanned to balance class, homework, energy, meals, and your carbon reduction goal."


def _fallback_understanding(intent):
    return {
        "goals": [intent.get("primary_goal", "balanced_week")],
        "constraints": intent.get("detected_constraints", []),
        "priority_order": ["fixed_events", "health_energy", "academic_work", "carbon_reduction"],
        "planning_scope": intent.get("planning_scope", "today"),
    }


def _default_memory_suggestion():
    return {
        "should_update": False,
        "reason": "",
        "markdown_patch": "",
    }


def _dedupe(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result

