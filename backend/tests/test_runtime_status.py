import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from runtime_status import runtime_status


class FakeHealthResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({"status": "ok"}).encode("utf-8")


class RuntimeStatusTests(unittest.TestCase):
    def test_local_status_is_public_safe(self):
        env = {
            "USE_GX10_RUNTIME": "false",
            "RUNTIME_FAILOVER_ENABLED": "true",
            "AGENTVERSE_AGENT_ENABLED": "false",
            "USE_ASI_ONE": "true",
            "ASI_ONE_API_KEY": "secret-value",
            "LOCAL_BACKEND_URL": "http://127.0.0.1:8000",
        }
        with patch.dict(os.environ, env, clear=False):
            status = runtime_status()

        self.assertEqual(status["runtime_mode"], "LOCAL_BACKEND")
        self.assertEqual(status["mode"], "local_only")
        self.assertFalse(status["gx10_enabled"])
        self.assertFalse(status["gx10_available"])
        self.assertTrue(status["local_first"])
        self.assertEqual(status["backend_url"], "http://127.0.0.1:8000")
        self.assertEqual(status["backend_label"], "Local Backend")
        self.assertNotIn("secret-value", json.dumps(status))

    @patch("runtime_status.request.urlopen", return_value=FakeHealthResponse())
    def test_gx10_status_probes_availability(self, _urlopen):
        env = {
            "USE_GX10_RUNTIME": "true",
            "RUNTIME_FAILOVER_ENABLED": "true",
            "AGENTVERSE_AGENT_ENABLED": "true",
            "GX10_BACKEND_URL": "http://100.121.103.97:8000",
        }
        with patch.dict(os.environ, env, clear=False):
            status = runtime_status()

        self.assertEqual(status["runtime_mode"], "GX10_BACKEND")
        self.assertEqual(status["mode"], "gx10_first")
        self.assertTrue(status["gx10_enabled"])
        self.assertTrue(status["gx10_available"])
        self.assertTrue(status["fallback_enabled"])
        self.assertTrue(status["agentverse_enabled"])
        self.assertEqual(status["backend_url"], "http://100.121.103.97:8000")
        self.assertEqual(status["backend_label"], "ASUS GX10 Backend")

    @patch("runtime_status.request.urlopen", side_effect=OSError("offline"))
    def test_gx10_unavailable_reports_fallback_mode(self, _urlopen):
        env = {
            "USE_GX10_RUNTIME": "true",
            "RUNTIME_FAILOVER_ENABLED": "true",
            "GX10_BACKEND_URL": "http://100.121.103.97:8000",
            "LOCAL_BACKEND_URL": "http://127.0.0.1:8000",
        }
        with patch.dict(os.environ, env, clear=False):
            status = runtime_status()

        self.assertEqual(status["runtime_mode"], "gx10_first_fallback")
        self.assertFalse(status["gx10_available"])
        self.assertEqual(status["backend_url"], "http://127.0.0.1:8000")
        self.assertEqual(status["backend_label"], "Local Backend fallback from GX10")


if __name__ == "__main__":
    unittest.main()
