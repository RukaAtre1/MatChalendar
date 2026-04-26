import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from agentverse_payload import compact_agentverse_response, normalize_agentverse_payload


class AgentversePayloadTests(unittest.TestCase):
    def test_accepts_common_prompt_keys(self):
        for key in ("prompt", "user_prompt", "message", "input", "query"):
            with self.subTest(key=key):
                self.assertEqual(normalize_agentverse_payload({key: " Plan my week. "}), {"prompt": "Plan my week."})

    def test_accepts_messages_array(self):
        payload = {
            "messages": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Plan a low-carbon UCLA week."},
            ]
        }

        normalized = normalize_agentverse_payload(payload)

        self.assertIn("You are helpful.", normalized["prompt"])
        self.assertIn("Plan a low-carbon UCLA week.", normalized["prompt"])

    def test_compact_response_only_returns_agent_fields(self):
        response = compact_agentverse_response(
            {
                "summary": "Plan ready.",
                "skills_used": ["calendar", "dining"],
                "carbon_budget": {
                    "current_estimated_kg_co2e": 12.5,
                    "weekly_target_kg_co2e": 35.0,
                    "status": "on_track",
                },
                "metadata": {
                    "planner_mode": "asi_one_hosted_ai",
                    "runtime_router": {"selected_backend": "local"},
                },
                "plan_blocks": [
                    {
                        "title": "Study",
                        "type": "study",
                        "start": "2026-04-27T10:00:00",
                        "end": "2026-04-27T11:00:00",
                        "location": "Powell",
                        "reason": "Protect focus time.",
                    }
                ],
            }
        )

        self.assertEqual(response["summary"], "Plan ready.")
        self.assertEqual(response["calendar_blocks"][0]["title"], "Study")
        self.assertEqual(response["metadata"], {"runtime_router": {"selected_backend": "local"}})
        self.assertIn("12.5 kg CO2e", response["carbon_note"])


if __name__ == "__main__":
    unittest.main()
