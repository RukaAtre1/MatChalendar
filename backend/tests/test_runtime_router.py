import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from runtime_router import RuntimeRouter


class DummyPlannerProvider:
    def __init__(self):
        self.calls = []

    def plan(self, payload):
        self.calls.append(payload)
        return {
            "summary": "Local plan",
            "metadata": {"planner_mode": "deterministic_fallback"},
            "plan_blocks": [],
            "skills_used": ["calendar"],
        }


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(
            {
                "summary": "GX10 plan",
                "metadata": {"planner_mode": "asi_one_hosted_ai"},
                "plan_blocks": [],
                "skills_used": ["calendar"],
            }
        ).encode("utf-8")


class RuntimeRouterTests(unittest.TestCase):
    def test_gx10_disabled_uses_local_in_process_planner(self):
        planner = DummyPlannerProvider()
        with patch.dict(os.environ, {"USE_GX10_RUNTIME": "false"}, clear=False):
            plan = RuntimeRouter(planner_provider=planner).plan({"prompt": "Plan locally."})

        router_metadata = plan["metadata"]["runtime_router"]
        self.assertEqual(router_metadata["selected_backend"], "local")
        self.assertFalse(router_metadata["gx10_attempted"])
        self.assertFalse(router_metadata["failover_used"])
        self.assertEqual(planner.calls, [{"prompt": "Plan locally."}])

    @patch("runtime_router.request.urlopen", side_effect=error.URLError("offline"))
    def test_gx10_failure_falls_back_to_local(self, _urlopen):
        planner = DummyPlannerProvider()
        env = {
            "USE_GX10_RUNTIME": "true",
            "RUNTIME_FAILOVER_ENABLED": "true",
            "GX10_BACKEND_URL": "http://100.121.103.97:8000",
        }
        with patch.dict(os.environ, env, clear=False):
            plan = RuntimeRouter(planner_provider=planner).plan({"prompt": "Plan with fallback."})

        router_metadata = plan["metadata"]["runtime_router"]
        self.assertEqual(router_metadata["selected_backend"], "local")
        self.assertTrue(router_metadata["gx10_attempted"])
        self.assertTrue(router_metadata["failover_used"])
        self.assertIn("URLError", router_metadata["runtime_error"])
        self.assertNotIn("100.121.103.97", router_metadata["runtime_error"])

    @patch("runtime_router.request.urlopen", return_value=FakeResponse())
    def test_gx10_success_returns_remote_plan(self, _urlopen):
        planner = DummyPlannerProvider()
        env = {
            "USE_GX10_RUNTIME": "true",
            "RUNTIME_FAILOVER_ENABLED": "true",
            "GX10_BACKEND_URL": "http://100.121.103.97:8000",
        }
        with patch.dict(os.environ, env, clear=False):
            plan = RuntimeRouter(planner_provider=planner).plan({"prompt": "Plan on GX10."})

        router_metadata = plan["metadata"]["runtime_router"]
        self.assertEqual(plan["summary"], "GX10 plan")
        self.assertEqual(router_metadata["selected_backend"], "gx10")
        self.assertTrue(router_metadata["gx10_attempted"])
        self.assertFalse(router_metadata["failover_used"])
        self.assertEqual(planner.calls, [])


if __name__ == "__main__":
    unittest.main()
