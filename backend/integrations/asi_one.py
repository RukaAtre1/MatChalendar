import json
import os
from urllib import error, request


class ASIOneClient:
    def __init__(self):
        self.use_asi_one = _env_bool("USE_ASI_ONE", False)
        self.api_key = os.getenv("ASI_ONE_API_KEY", "")
        self.base_url = (os.getenv("ASI_ONE_BASE_URL") or "https://api.asi1.ai/v1").rstrip("/")
        self.model = os.getenv("ASI_ONE_MODEL") or "asi1"
        self.timeout_seconds = _env_int("ASI_ONE_TIMEOUT_SECONDS", 20)

    def is_available(self):
        return bool(self.use_asi_one and self.api_key and self.base_url and self.model)

    def build_planner_contract(self, prompt, soul="", memory=""):
        if not self.is_available():
            return {
                "available": False,
                "contract": None,
                "error": "USE_ASI_ONE is disabled or ASI_ONE_API_KEY is missing.",
            }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _system_prompt(soul, memory)},
                {"role": "user", "content": prompt or ""},
            ],
            "temperature": 0.2,
            "response_format": _response_format_schema(),
        }
        try:
            response = _post_json(_chat_completion_url(self.base_url), payload, self.api_key, self.timeout_seconds)
            content = response["choices"][0]["message"]["content"]
            context = _normalize_ai_planner_context(json.loads(content))
            return {"available": True, "contract": context, "error": ""}
        except (KeyError, TypeError, json.JSONDecodeError, OSError, error.URLError) as exc:
            return {"available": False, "contract": None, "error": f"ASI:One request failed: {exc}"}
        except ValueError as exc:
            return {"available": False, "contract": None, "error": f"ASI:One returned invalid planner context: {exc}"}


def _post_json(url, payload, api_key, timeout_seconds):
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "MatChalendar/1.0",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _system_prompt(soul, memory):
    return f"""You are MatChalendar's hosted AI Master Planner fallback.
Return only JSON matching this AIPlannerContext contract:
{{
  "goals": [],
  "constraints": [],
  "priority_order": [],
  "selected_skills": [],
  "tradeoffs": [],
  "explanation_draft": "",
  "confidence": 0.0
}}

You do not write final calendar plan_blocks. Internal skills provide options and evidence.
The MatChalendar backend validates and renders the final PlanResponse.
Allowed selected_skills values: calendar, dining, study, health, energy, transportation, sustainability_carbon, explanation.

SOUL.md:
{soul}

MEMORY.md:
{memory}
"""


def _response_format_schema():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "ai_planner_context",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "goals": {"type": "array", "items": {"type": "string"}},
                    "constraints": {"type": "array", "items": {"type": "string"}},
                    "priority_order": {"type": "array", "items": {"type": "string"}},
                    "selected_skills": {"type": "array", "items": {"type": "string"}},
                    "tradeoffs": {"type": "array", "items": {"type": "string"}},
                    "explanation_draft": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "goals",
                    "constraints",
                    "priority_order",
                    "selected_skills",
                    "tradeoffs",
                    "explanation_draft",
                    "confidence",
                ],
            },
        },
    }


def _normalize_ai_planner_context(context):
    if not isinstance(context, dict):
        raise ValueError("context must be an object")

    required_lists = ["goals", "constraints", "priority_order", "selected_skills", "tradeoffs"]
    normalized = {}
    for key in required_lists:
        value = context.get(key)
        if not isinstance(value, list):
            raise ValueError(f"{key} must be a list")
        normalized[key] = [str(item).strip() for item in value if str(item).strip()]

    explanation_draft = context.get("explanation_draft")
    if not isinstance(explanation_draft, str):
        raise ValueError("explanation_draft must be a string")
    normalized["explanation_draft"] = explanation_draft.strip()

    confidence = context.get("confidence")
    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be a number")
    normalized["confidence"] = max(0.0, min(1.0, float(confidence)))

    if not normalized["goals"]:
        raise ValueError("goals must not be empty")
    if not normalized["selected_skills"]:
        raise ValueError("selected_skills must not be empty")

    return normalized


def _chat_completion_url(base_url):
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def _env_int(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")
