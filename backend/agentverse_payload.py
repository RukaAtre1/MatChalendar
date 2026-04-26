PROMPT_KEYS = ("prompt", "user_prompt", "message", "input", "query")


def normalize_agentverse_payload(payload):
    if not isinstance(payload, dict):
        return {"prompt": str(payload or "").strip()}

    for key in PROMPT_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return {"prompt": value.strip()}

    prompt = _prompt_from_messages(payload.get("messages"))
    return {"prompt": prompt}


def compact_agentverse_response(plan):
    blocks = plan.get("plan_blocks", []) if isinstance(plan, dict) else []
    metadata = plan.get("metadata", {}) if isinstance(plan, dict) else {}
    carbon_budget = plan.get("carbon_budget", {}) if isinstance(plan, dict) else {}

    return {
        "summary": plan.get("summary", "") if isinstance(plan, dict) else "",
        "calendar_blocks": [
            {
                "title": block.get("title"),
                "type": block.get("type"),
                "start": block.get("start"),
                "end": block.get("end"),
                "location": block.get("location"),
                "reason": block.get("reason"),
            }
            for block in blocks
            if isinstance(block, dict)
        ],
        "skills_used": plan.get("skills_used", []) if isinstance(plan, dict) else [],
        "carbon_note": _carbon_note(carbon_budget),
        "explanation": plan.get("explanation_draft") or plan.get("calendar_strategy") or "",
        "metadata": {"runtime_router": metadata.get("runtime_router", {})},
    }


def _prompt_from_messages(messages):
    if not isinstance(messages, list):
        return ""

    parts = []
    for message in messages:
        if isinstance(message, str):
            clean = message.strip()
        elif isinstance(message, dict):
            clean = str(message.get("content") or message.get("text") or "").strip()
        else:
            clean = ""
        if clean:
            parts.append(clean)
    return "\n".join(parts).strip()


def _carbon_note(carbon_budget):
    if not isinstance(carbon_budget, dict) or not carbon_budget:
        return ""

    current = carbon_budget.get("current_estimated_kg_co2e")
    target = carbon_budget.get("weekly_target_kg_co2e")
    status = carbon_budget.get("status", "")
    if isinstance(current, (int, float)) and isinstance(target, (int, float)):
        return f"{current:.1f} kg CO2e of {target:.1f} kg weekly target; {status}".strip(" ;")
    return str(status or "")
