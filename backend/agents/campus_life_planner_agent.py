from runtime_router import RuntimeRouter


class CampusLifePlannerAgent:
    name = "CampusLifePlannerAgent"
    description = "MatChalendar campus life planner agent for explainable, carbon-aware weekly planning."

    def __init__(self, planner_provider=None, runtime_router=None):
        self.runtime_router = runtime_router or RuntimeRouter(planner_provider=planner_provider)

    def run(self, prompt, concise=False):
        plan = self.runtime_router.plan({"prompt": prompt})
        if concise:
            return {
                "summary": plan.get("summary", ""),
                "generated_by": plan.get("generated_by", ""),
                "planner_mode": plan.get("metadata", {}).get("planner_mode", ""),
                "blocks": [
                    {
                        "title": block.get("title"),
                        "start": block.get("start"),
                        "end": block.get("end"),
                        "reason": block.get("reason"),
                    }
                    for block in plan.get("plan_blocks", [])
                ],
            }
        return plan


def run(prompt, concise=False):
    return CampusLifePlannerAgent().run(prompt, concise=concise)
