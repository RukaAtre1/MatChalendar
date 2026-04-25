PLAN_RESPONSE_VERSION = "mvp-0.1"

PLAN_RESPONSE_KEYS = [
    "summary",
    "generated_by",
    "intent",
    "carbon_budget",
    "plan_blocks",
]


def skill_result(name, recommendations=None, constraints=None, evidence=None):
    return {
        "skill": name,
        "recommendations": recommendations or [],
        "constraints": constraints or [],
        "evidence": evidence or [],
    }
