from planner.planner_provider import PlannerProvider


class CampusLifePlannerSkill:
    name = "CampusLifePlannerSkill"
    description = "High-level MatChalendar skill for OmegaClaw campus life planning."

    def __init__(self, planner_provider=None):
        self.planner_provider = planner_provider or PlannerProvider()

    def run(self, prompt):
        plan = self.planner_provider.plan({"prompt": prompt})
        return {
            "summary": plan.get("summary", ""),
            "generated_by": plan.get("generated_by", ""),
            "metadata": plan.get("metadata", {}),
            "calendar_summary": [
                {
                    "title": block.get("title"),
                    "type": block.get("type"),
                    "start": block.get("start"),
                    "end": block.get("end"),
                    "location": block.get("location"),
                    "reason": block.get("reason"),
                }
                for block in plan.get("plan_blocks", [])
            ],
            "blocks": plan.get("plan_blocks", []),
            "explanations": [
                {
                    "block_id": block.get("id"),
                    "reason": block.get("reason"),
                    "impact": block.get("explanation", {}).get("impact"),
                }
                for block in plan.get("plan_blocks", [])
            ],
            "carbon_impact": plan.get("carbon_budget", {}),
            "skills_used": plan.get("skills_used", []),
        }


def run(prompt):
    return CampusLifePlannerSkill().run(prompt)
