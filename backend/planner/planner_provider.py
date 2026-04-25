from config import load_local_env
from integrations.asi_one import ASIOneClient
from integrations.local_ai import LocalAIClient
from memory.memory_store import read_memory, read_soul
from planner.ai_master_planner import build_master_planner_contract
from planner.fallback_planner import build_fallback_plan
from planner.schemas import validate_plan_response


class PlannerProvider:
    def __init__(self, local_ai=None, asi_one=None):
        load_local_env()
        self.local_ai = local_ai or LocalAIClient()
        self.asi_one = asi_one or ASIOneClient()

    def plan(self, request_or_prompt):
        prompt = _extract_prompt(request_or_prompt)
        soul = read_soul()
        memory = read_memory()

        source = self._choose_planner_source(prompt, soul, memory)
        ai_contract = source.get("contract")
        if ai_contract is None:
            ai_contract = build_master_planner_contract(prompt, soul=soul, memory=memory)

        plan = build_fallback_plan(prompt, planner_context={"ai_contract": ai_contract, "soul": soul, "memory": memory})
        plan["generated_by"] = source["generated_by"]
        plan["metadata"] = self._metadata(source, soul, memory)

        valid, errors = validate_plan_response(plan)
        if valid:
            return plan

        fallback = build_fallback_plan(prompt)
        fallback["generated_by"] = "deterministic_fallback_planner"
        fallback["metadata"] = self._metadata(
            {
                **source,
                "planner_mode": "deterministic_fallback",
                "generated_by": "deterministic_fallback_planner",
                "fallback_reason": "AI-assisted plan failed validation: " + "; ".join(errors),
            },
            soul,
            memory,
        )
        valid_fallback, fallback_errors = validate_plan_response(fallback)
        if not valid_fallback:
            fallback["metadata"]["validation_errors"] = fallback_errors
        return fallback

    def _choose_planner_source(self, prompt, soul, memory):
        asi_configured = self.asi_one.is_available()
        asi_available = False
        local_configured = self.local_ai.is_available()

        if asi_configured:
            result = self.asi_one.build_planner_contract(prompt, soul=soul, memory=memory)
            if result.get("available") and result.get("contract"):
                asi_available = True
                return {
                    "generated_by": "asi_one_ai_assisted_planner",
                    "planner_mode": "asi_one_hosted_ai",
                    "integrations_used": ["asi_one"],
                    "fallback_reason": "",
                    "local_ai_available": False,
                    "asi_one_available": True,
                    "contract": build_master_planner_contract(prompt, soul=soul, memory=memory, ai_response=result["contract"]),
                }
            asi_error = result.get("error", "ASI:One unavailable.")
        else:
            asi_error = "ASI:One disabled or unconfigured."

        return {
            "generated_by": "deterministic_fallback_planner",
            "planner_mode": "deterministic_fallback",
            "integrations_used": ["deterministic_fallback"],
            "fallback_reason": f"{asi_error} GX10 local AI kept optional and disabled for this ASI:One-first flow.",
            "local_ai_available": False,
            "local_ai_configured": local_configured,
            "asi_one_available": asi_available,
            "contract": None,
        }

    def _metadata(self, source, soul, memory):
        return {
            "generated_by": source.get("generated_by", "deterministic_fallback_planner"),
            "planner_mode": source.get("planner_mode", "deterministic_fallback"),
            "integrations_used": source.get("integrations_used", []),
            "fallback_reason": source.get("fallback_reason", ""),
            "local_ai_available": bool(source.get("local_ai_available")),
            "local_ai_configured": bool(source.get("local_ai_configured")),
            "asi_one_available": bool(source.get("asi_one_available")),
            "memory_used": bool(memory),
            "soul_used": bool(soul),
        }


def _extract_prompt(request_or_prompt):
    if isinstance(request_or_prompt, dict):
        return request_or_prompt.get("prompt", "")
    return request_or_prompt or ""


def plan(request_or_prompt):
    return PlannerProvider().plan(request_or_prompt)
