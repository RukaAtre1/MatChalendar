"""Test the DebugSubmitMiddleware with various payload shapes."""
import asyncio
import json
import sys
sys.path.insert(0, '.')

import importlib.util
spec = importlib.util.spec_from_file_location(
    'matchalendar_agent', r'agentverse\matchalendar_agent.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Test _extract_text_from_raw with various shapes
test_cases = [
    ({"text": "Plan my week"}, "Plan my week"),
    ({"message": "Plan my week"}, "Plan my week"),
    ({"prompt": "Plan my week"}, "Plan my week"),
    ({"content": [{"type": "text", "text": "Plan my week"}]}, "Plan my week"),
    ({"messages": [{"content": "Plan my week"}]}, "Plan my week"),
    ({}, ""),
]

print("=== _extract_text_from_raw tests ===")
all_pass = True
for payload, expected in test_cases:
    got = mod._extract_text_from_raw(payload)
    ok = got == expected
    all_pass = all_pass and ok
    print(f"  {'PASS' if ok else 'FAIL'} payload_keys={list(payload.keys())} → got={repr(got)}")

print()
print("=== Middleware ASGI test (plain payload) ===")

async def run_middleware_test():
    responses = []

    # Build a fake ASGI scope for POST /submit
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/submit",
        "headers": [(b"content-type", b"application/json")],
    }

    body = json.dumps({"text": "Plan my UCLA week with a sustainability focus."}).encode()

    async def fake_receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def fake_send(event):
        responses.append(event)

    # Use a passthrough app that returns 400 (simulating native handler rejecting)
    async def native_app(scope, receive, send):
        await send({"type": "http.response.start", "status": 400, "headers": []})
        await send({"type": "http.response.body", "body": b'{"error":"test rejection"}'})

    mw = mod.DebugSubmitMiddleware(native_app)
    await mw(scope, fake_receive, fake_send)

    status_events = [e for e in responses if e.get("type") == "http.response.start"]
    body_events = [e for e in responses if e.get("type") == "http.response.body"]

    status = status_events[0]["status"] if status_events else None
    body_bytes = body_events[0]["body"] if body_events else b""

    print(f"  HTTP status: {status}")
    try:
        resp_json = json.loads(body_bytes)
        print(f"  Response keys: {list(resp_json.keys())}")
        if "text" in resp_json:
            print(f"  Response text snippet: {resp_json['text'][:200]}")
    except Exception as e:
        print(f"  Response body: {body_bytes[:200]!r} ({e})")

asyncio.run(run_middleware_test())
print()
print("=== All basic tests done ===")
