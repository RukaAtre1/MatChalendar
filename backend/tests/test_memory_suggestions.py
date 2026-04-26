import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from planner.ai_master_planner import heuristic_planner_contract


class MemorySuggestionTests(unittest.TestCase):
    def test_memory_suggestion_summarizes_preferences_without_raw_prompt(self):
        prompt = (
            "Plan my UCLA week. I have PHYSCI 5 from 10 to 2, a problem set due tonight, "
            "and I want dinner near campus. Keep my meals low-carbon and prefer walking, "
            "transit, and focused study blocks."
        )

        suggestion = heuristic_planner_contract(prompt)["memory_update_suggestion"]

        self.assertTrue(suggestion["should_update"])
        self.assertIn("low-carbon", suggestion["markdown_patch"])
        self.assertIn("near-campus dining", suggestion["markdown_patch"])
        self.assertIn("walking", suggestion["markdown_patch"])
        self.assertIn("public transit", suggestion["markdown_patch"])
        self.assertIn("focused study blocks", suggestion["markdown_patch"])
        self.assertNotIn("PHYSCI 5", suggestion["markdown_patch"])
        self.assertNotIn("problem set due tonight", suggestion["markdown_patch"])
        self.assertNotIn("latest planning request", suggestion["markdown_patch"])

    def test_memory_suggestion_ignores_one_off_schedule(self):
        prompt = "Plan my UCLA week. I have class from 10 to 2 and a problem set due tonight."

        suggestion = heuristic_planner_contract(prompt)["memory_update_suggestion"]

        self.assertFalse(suggestion["should_update"])
        self.assertEqual("", suggestion["markdown_patch"])


if __name__ == "__main__":
    unittest.main()
