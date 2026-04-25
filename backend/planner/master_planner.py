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


def build_plan(prompt):
    intent = parse_intent(prompt)
    selected_skills = route_skills(intent)

    skill_outputs = {}
    for skill in selected_skills:
        if skill == "explanation":
            continue
        skill_outputs[skill] = SKILL_RUNNERS[skill](intent, skill_outputs)

    blocks = replan_calendar(intent, skill_outputs)
    blocks = run_explanation_skill(intent, blocks)

    intent["skills_used"] = selected_skills

    return {
        "summary": "Your week was replanned to balance class, homework, energy, meals, and your carbon reduction goal.",
        "generated_by": "deterministic_mvp_master_planner",
        "response_version": PLAN_RESPONSE_VERSION,
        "intent": intent,
        "carbon_budget": skill_outputs["sustainability_carbon"]["carbon_budget"],
        "plan_blocks": blocks,
        "integration_points": {
            "asus_gx10": "visible_ui_badge_only",
            "agentverse": "planned_external_skill",
            "omegaclaw": "planned_invoker",
        },
    }
