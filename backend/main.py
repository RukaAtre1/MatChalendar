from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from food.food_store import load_dining_data
from memory.memory_store import append_memory_update, read_memory
from planner.planner_provider import PlannerProvider


HOST = "127.0.0.1"
PORT = 8000
PLANNER_PROVIDER = PlannerProvider()


class MatChalendarHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json({"status": "ok", "planner": "planner_provider"})
            return
        if path == "/api/dining":
            self._send_json({"items": load_dining_data()})
            return
        if path == "/api/memory":
            self._send_json({"memory": read_memory()})
            return
        if path == "/api/demo-schedule":
            schedule_path = BACKEND_DIR / "data" / "sample_schedule.json"
            self._send_json(json.loads(schedule_path.read_text(encoding="utf-8")))
            return

        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/plan", "/api/memory/update"):
            self._send_json({"error": "not_found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid_json"}, status=400)
            return

        if path == "/api/plan":
            self._send_json(PLANNER_PROVIDER.plan(payload))
            return

        markdown_patch = payload.get("markdown_patch", "")
        self._send_json({"memory": append_memory_update(markdown_patch), "saved": bool(markdown_patch.strip())})

    def _serve_static(self, path):
        if path in ("", "/"):
            target = ROOT_DIR / "index.html"
        else:
            target = (ROOT_DIR / path.lstrip("/")).resolve()

        if not str(target).startswith(str(ROOT_DIR)) or not target.is_file():
            self._send_json({"error": "not_found"}, status=404)
            return

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".md": "text/markdown; charset=utf-8",
        }.get(target.suffix, "application/octet-stream")

        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), MatChalendarHandler)
    print(f"MatChalendar API running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000 to use the one-screen demo.")
    server.serve_forever()
