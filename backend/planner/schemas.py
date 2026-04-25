PLAN_RESPONSE_VERSION = "mvp-0.1"

PLAN_RESPONSE_KEYS = [
    "summary",
    "generated_by",
    "metadata",
    "intent",
    "understanding",
    "carbon_budget",
    "plan_blocks",
    "skills_used",
]


def skill_result(name, recommendations=None, constraints=None, evidence=None):
    return {
        "skill": name,
        "recommendations": recommendations or [],
        "constraints": constraints or [],
        "evidence": evidence or [],
    }


REQUIRED_BLOCK_KEYS = [
    "id",
    "title",
    "type",
    "start",
    "end",
    "reason",
    "scores",
    "skills_used",
]


def validate_plan_response(plan):
    errors = []
    if not isinstance(plan, dict):
        return False, ["PlanResponse must be an object."]

    for key in PLAN_RESPONSE_KEYS:
        if key not in plan:
            errors.append(f"Missing PlanResponse field: {key}")

    blocks = plan.get("plan_blocks")
    if not isinstance(blocks, list) or not blocks:
        errors.append("plan_blocks must be a non-empty list.")
        return False, errors

    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            errors.append(f"plan_blocks[{index}] must be an object.")
            continue
        for key in REQUIRED_BLOCK_KEYS:
            if key not in block:
                errors.append(f"plan_blocks[{index}] missing field: {key}")
        if not isinstance(block.get("scores"), dict):
            errors.append(f"plan_blocks[{index}].scores must be an object.")
        if not isinstance(block.get("skills_used"), list) or not block.get("skills_used"):
            errors.append(f"plan_blocks[{index}].skills_used must be a non-empty list.")
        if block.get("start") and block.get("end") and block["start"] >= block["end"]:
            errors.append(f"plan_blocks[{index}] start must be before end.")

    errors.extend(_overlap_errors(blocks))
    return not errors, errors


def _overlap_errors(blocks):
    errors = []
    comparable = [
        (block.get("start"), block.get("end"), block.get("id"))
        for block in blocks
        if isinstance(block, dict) and block.get("start") and block.get("end")
    ]
    comparable.sort()
    for index in range(1, len(comparable)):
        previous_start, previous_end, previous_id = comparable[index - 1]
        current_start, current_end, current_id = comparable[index]
        if previous_start[:10] == current_start[:10] and current_start < previous_end:
            errors.append(f"Time conflict between {previous_id} and {current_id}.")
    return errors
