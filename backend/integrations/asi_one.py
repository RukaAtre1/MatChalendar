import json
import os
from urllib import error, request


class ASIOneClient:
    def __init__(self):
        self.use_asi_one = _env_bool("USE_ASI_ONE", False)
        self.api_key = os.getenv("ASI_ONE_API_KEY", "")
        self.base_url = os.getenv("ASI_ONE_BASE_URL", "").rstrip("/")
        self.model = os.getenv("ASI_ONE_MODEL", "")

    def is_available(self):
        return bool(self.use_asi_one and self.api_key and self.base_url and self.model)

    def build_planner_contract(self, prompt, soul="", memory=""):
        if not self.is_available():
            return {
                "available": False,
                "contract": None,
                "error": "USE_ASI_ONE is disabled or ASI_ONE_API_KEY/ASI_ONE_BASE_URL/ASI_ONE_MODEL is missing.",
            }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _system_prompt(soul, memory)},
                {"role": "user", "content": prompt or ""},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        try:
            response = _post_json(f"{self.base_url}/v1/chat/completions", payload, self.api_key)
            content = response["choices"][0]["message"]["content"]
            return {"available": True, "contract": json.loads(content), "error": ""}
        except (KeyError, TypeError, json.JSONDecodeError, OSError, error.URLError) as exc:
            return {"available": False, "contract": None, "error": f"ASI:One request failed: {exc}"}


def _post_json(url, payload, api_key):
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _system_prompt(soul, memory):
    return f"""You are MatChalendar's hosted AI Master Planner fallback.
Return only JSON matching this contract:
{{
  "understanding": {{"goals": [], "constraints": [], "priority_order": [], "planning_scope": ""}},
  "skill_calls": [{{"skill": "", "reason": "", "query": ""}}],
  "tradeoffs": [],
  "calendar_strategy": "",
  "memory_update_suggestion": {{"should_update": false, "reason": "", "markdown_patch": ""}}
}}

Internal skills provide options and evidence. The backend validates and renders the final PlanResponse.

SOUL.md:
{soul}

MEMORY.md:
{memory}
"""


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")

