import json
import os
from urllib import error, request


class LocalAIClient:
    def __init__(self):
        self.use_local_ai = _env_bool("USE_LOCAL_AI", False)
        self.base_url = os.getenv("LOCAL_AI_BASE_URL", "").rstrip("/")
        self.model = os.getenv("LOCAL_MODEL_NAME", "")
        self.fallback_to_mock = _env_bool("FALLBACK_TO_MOCK", True)

    def is_available(self):
        return bool(self.use_local_ai and self.base_url and self.model)

    def build_planner_contract(self, prompt, soul="", memory=""):
        if not self.is_available():
            return {
                "available": False,
                "contract": None,
                "error": "USE_LOCAL_AI is disabled or LOCAL_AI_BASE_URL/LOCAL_MODEL_NAME is missing.",
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
            response = _post_json(f"{self.base_url}/v1/chat/completions", payload)
            content = response["choices"][0]["message"]["content"]
            return {"available": True, "contract": json.loads(content), "error": ""}
        except (KeyError, TypeError, json.JSONDecodeError, OSError, error.URLError) as exc:
            return {"available": False, "contract": None, "error": f"GX10 local AI request failed: {exc}"}


def _post_json(url, payload):
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def _system_prompt(soul, memory):
    return f"""You are MatChalendar's AI Master Planner.
Return only JSON matching this contract:
{{
  "understanding": {{"goals": [], "constraints": [], "priority_order": [], "planning_scope": ""}},
  "skill_calls": [{{"skill": "", "reason": "", "query": ""}}],
  "tradeoffs": [],
  "calendar_strategy": "",
  "memory_update_suggestion": {{"should_update": false, "reason": "", "markdown_patch": ""}}
}}

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

