import json
import os
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import main as backend_main


class FakeRuntimeRouter:
    def plan(self, payload):
        return {
            "summary": f"Planned: {payload['prompt']}",
            "skills_used": ["calendar"],
            "carbon_budget": {"status": "on_track"},
            "metadata": {"runtime_router": {"selected_backend": "local"}},
            "plan_blocks": [
                {
                    "title": "Study",
                    "type": "study",
                    "start": "2026-04-27T10:00:00",
                    "end": "2026-04-27T11:00:00",
                    "location": "Powell",
                    "reason": "Focus block.",
                }
            ],
        }


class AgentverseEndpointTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), backend_main.MatChalendarHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_agentverse_disabled_returns_403(self):
        with patch.dict(os.environ, {"AGENTVERSE_AGENT_ENABLED": "false"}, clear=False):
            with self.assertRaises(error.HTTPError) as raised:
                _post_json(f"{self.base_url}/api/agentverse/plan", {"prompt": "Plan my week."})

        self.assertEqual(raised.exception.code, 403)
        payload = json.loads(raised.exception.read().decode("utf-8"))
        self.assertEqual(payload, {"error": "MatChalendar Agentverse demo is disabled."})

    def test_agentverse_enabled_returns_compact_plan(self):
        with patch.dict(os.environ, {"AGENTVERSE_AGENT_ENABLED": "true"}, clear=False):
            with patch.object(backend_main, "RUNTIME_ROUTER", FakeRuntimeRouter()):
                payload = _post_json(f"{self.base_url}/api/agentverse/plan", {"message": "Plan my week."})

        self.assertEqual(payload["summary"], "Planned: Plan my week.")
        self.assertEqual(payload["calendar_blocks"][0]["title"], "Study")
        self.assertEqual(payload["metadata"], {"runtime_router": {"selected_backend": "local"}})
        self.assertNotIn("plan_blocks", payload)


def _post_json(url, payload):
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
