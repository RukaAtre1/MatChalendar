from __future__ import annotations

import base64
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_NAME = "MatChalendar Campus Planner Agent"
DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"
DEFAULT_AGENT_SEED = "replace_with_secure_seed"
DEFAULT_AGENT_PORT = 8001
DEMO_PROMPT = (
    "Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency "
    "and took an Uber today. I also have class from 10 to 2 and homework tonight."
)


def load_local_env() -> None:
    for path in (PROJECT_ROOT / ".env", PROJECT_ROOT / ".env.local"):
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip().lstrip("\ufeff")
            value = strip_quotes(value.strip())
            if key and key not in os.environ:
                os.environ[key] = value


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def backend_url() -> str:
    return os.getenv("MATCHALENDAR_BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")


def public_endpoint_base() -> str:
    return os.getenv("AGENT_ENDPOINT", "").strip().rstrip("/")


def call_backend(prompt: str) -> tuple[dict[str, Any], int]:
    url = f"{backend_url()}/api/plan"
    body = json.dumps({"prompt": prompt}).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "MatChalendar-Agentverse/1.0"},
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8")), int(response.status)


def fetch_runtime_status() -> dict[str, Any]:
    req = request.Request(
        f"{backend_url()}/api/runtime/status",
        headers={"User-Agent": "MatChalendar-Agentverse/1.0"},
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            if response.status < 200 or response.status >= 300:
                return {}
            payload = json.loads(response.read().decode("utf-8"))
            return payload if isinstance(payload, dict) else {}
    except (OSError, ValueError, error.URLError):
        return {}


def format_plan_response(plan: dict[str, Any], runtime_status: dict[str, Any] | None = None) -> str:
    summary = str(plan.get("summary") or "MatChalendar generated a weekly campus plan.").strip()
    blocks = plan.get("plan_blocks") or plan.get("calendar_blocks") or []
    carbon_budget = plan.get("carbon_budget") or {}
    skills = plan.get("skills_used") or []
    metadata = plan.get("metadata") or {}

    lines = [
        "MatChalendar Campus Planner Agent",
        "",
        "Summary:",
        clip(summary, 520),
        "",
        "Calendar blocks:",
    ]

    for block in first_blocks(blocks, limit=6):
        title = block.get("title") or "Plan block"
        start = short_time(block.get("start"))
        end = short_time(block.get("end"))
        location = block.get("location") or "UCLA"
        reason = block.get("reason") or ""
        lines.append(f"- {title}: {start}-{end} at {location}. {clip(reason, 150)}".rstrip())

    if isinstance(blocks, list) and len(blocks) > 6:
        lines.append(f"- Plus {len(blocks) - 6} more scheduled blocks in the backend plan.")

    lines.extend(["", "Carbon adjustment:", carbon_note(carbon_budget, plan)])
    lines.extend(["", "Skills used:"])
    lines.append(", ".join(skills) if skills else "calendar, study, dining, health, energy, transportation, sustainability_carbon")
    lines.extend(["", "Runtime note:", runtime_note(metadata, runtime_status or {})])
    return "\n".join(lines).strip()


def deterministic_demo_plan(prompt: str, reason: str = "") -> str:
    return "\n".join(
        [
            "MatChalendar Campus Planner Agent",
            "",
            "Summary:",
            "The backend is unavailable, so I am returning a deterministic demo plan.",
            "",
            "Calendar blocks:",
            "- Class block: Mon 10:00-14:00 at UCLA campus. Protect fixed class time first.",
            "- Recovery walk: Mon 14:15-14:45 at Bruin Walk. Add a zero-emission reset after class.",
            "- Focused homework: Mon 19:45-21:15 at Powell Library. Finish tonight's work after dinner.",
            "- Walk-first commute: Tue 09:20-09:50 at UCLA walking route. Avoid another rideshare when timing allows.",
            "- Low-waste grocery loop: Fri 17:15-18:00 at Westwood Village. Turn the carbon goal into a concrete errand.",
            "",
            "Carbon adjustment:",
            "Treat the emergency Uber as a one-off safety exception, then rebalance the rest of the week with walking, transit, low-waste errands, and plant-forward meals.",
            "",
            "Skills used:",
            "calendar, study, health, energy, transportation, sustainability_carbon, dining, explanation",
            "",
            "Runtime note:",
            f"Backend fallback used because {reason or 'the MatChalendar backend did not respond'}. MATCHALENDAR_BACKEND_URL={backend_url()}",
            "",
            f"Original request: {clip(prompt or DEMO_PROMPT, 220)}",
        ]
    )


def first_blocks(blocks: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(blocks, list):
        return []
    return [block for block in blocks[:limit] if isinstance(block, dict)]


def carbon_note(carbon_budget: dict[str, Any], plan: dict[str, Any]) -> str:
    if not isinstance(carbon_budget, dict):
        carbon_budget = {}
    pieces = []
    current = carbon_budget.get("current_estimated_kg_co2e")
    target = carbon_budget.get("weekly_target_kg_co2e")
    status = carbon_budget.get("status")
    adjustment = carbon_budget.get("adjustment_strategy")
    tradeoffs = plan.get("tradeoffs") or []
    if isinstance(current, (int, float)) and isinstance(target, (int, float)):
        pieces.append(f"{current:.1f} kg CO2e of {target:.1f} kg weekly target")
    if status:
        pieces.append(str(status).replace("_", " "))
    if adjustment:
        pieces.append(str(adjustment).replace("_", " "))
    if tradeoffs:
        pieces.append(clip(str(tradeoffs[0]), 180))
    if not pieces:
        pieces.append("After the emergency Uber, use lower-carbon transportation, low-waste errands, and plant-forward meals for the rest of the week")
    return "; ".join(pieces) + "."


def runtime_note(metadata: dict[str, Any], status: dict[str, Any]) -> str:
    router = metadata.get("runtime_router") if isinstance(metadata, dict) else {}
    selected = router.get("selected_backend") if isinstance(router, dict) else ""
    mode = status.get("runtime_mode") or status.get("mode") or ""
    gx10_enabled = status.get("gx10_enabled")
    if gx10_enabled is None:
        gx10_enabled = status.get("gx10_available")
    fallback_enabled = status.get("fallback_enabled")
    if selected:
        return f"local-first runtime selected {selected}; mode={mode or 'unknown'}; GX10 available/enabled={gx10_enabled}; fallback_enabled={fallback_enabled}."
    if mode or gx10_enabled is not None:
        return f"local-first runtime status: mode={mode or 'unknown'}; GX10 available/enabled={gx10_enabled}; fallback_enabled={fallback_enabled}."
    planner_mode = metadata.get("planner_mode") if isinstance(metadata, dict) else ""
    if planner_mode:
        return f"Backend planner mode: {planner_mode}; MatChalendar remains local-first with deterministic fallback."
    return "MatChalendar is local-first; GX10 routing is used when MATCHALENDAR_BACKEND_URL points to that backend."


def short_time(value: Any) -> str:
    text = str(value or "")
    if "T" in text and len(text) >= 16:
        return text[5:16].replace("T", " ")
    return text or "scheduled"


def clip(text: str, max_chars: int) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3].rstrip() + "..."


def extract_text_from_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return payload.strip()
    if not isinstance(payload, dict):
        return ""

    for key in ("text", "message", "prompt", "query", "input"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    content = payload.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item.strip())
            elif isinstance(item, dict):
                text = item.get("text") or item.get("message") or item.get("content")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        if parts:
            return "\n".join(parts)

    messages = payload.get("messages")
    if isinstance(messages, list):
        parts = []
        for message in messages:
            text = extract_text_from_payload(message)
            if text:
                parts.append(text)
        if parts:
            return "\n".join(parts)

    raw_payload = payload.get("payload")
    if isinstance(raw_payload, str) and raw_payload.strip():
        decoded = decode_possible_payload(raw_payload)
        text = extract_text_from_payload(decoded)
        if text:
            return text

    return ""


def decode_possible_payload(raw_payload: str) -> Any:
    for candidate in (raw_payload, add_base64_padding(raw_payload)):
        try:
            decoded = base64.b64decode(candidate).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            continue
    try:
        return json.loads(raw_payload)
    except Exception:
        return {}


def add_base64_padding(value: str) -> str:
    return value + ("=" * (-len(value) % 4))


def is_uagents_envelope(payload: Any) -> bool:
    return (
        isinstance(payload, dict)
        and "version" in payload
        and "sender" in payload
        and "target" in payload
        and "session" in payload
        and "schema_digest" in payload
    )


async def send_json(send: Any, status: int, body: dict[str, Any]) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [[b"content-type", b"application/json"]],
        }
    )
    await send({"type": "http.response.body", "body": json.dumps(body).encode("utf-8")})


load_local_env()

try:
    from uagents import Agent, Context, Protocol
    from uagents.asgi import ASGIServer
    from uagents_core.contrib.protocols.chat import (
        ChatAcknowledgement,
        ChatMessage,
        EndSessionContent,
        TextContent,
        chat_protocol_spec,
    )
    from uagents_core.models import Model
except ImportError as exc:
    raise SystemExit(
        "Missing Fetch.ai uAgents dependencies. Install them with:\n"
        "  python -m pip install uagents\n"
        f"Original import error: {exc}"
    ) from exc


CHAT_MESSAGE_DIGEST = Model.build_schema_digest(ChatMessage)
CHAT_PROTOCOL_DIGEST = chat_protocol_spec.digest


def create_text_chat(text: str, end_session: bool = True) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=text),
            *([EndSessionContent(type="end-session")] if end_session else []),
        ],
    )


def extract_text(msg: Any) -> str:
    text_method = getattr(msg, "text", None)
    if callable(text_method):
        text = text_method()
        if text:
            return str(text).strip()
    return extract_text_from_payload({"content": getattr(msg, "content", [])})


def resolve_seed() -> str:
    return (
        os.getenv("AGENT_SEED_PHRASE")
        or os.getenv("AGENT_SEED")
        or DEFAULT_AGENT_SEED
    )


def resolve_agentverse_key() -> str:
    return os.getenv("AGENTVERSE_KEY") or os.getenv("AGENTVERSE_API_KEY") or ""


submit_logger = logging.getLogger("submit_debug")
submit_logger.setLevel(logging.INFO)
if not submit_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[submit_debug] %(asctime)s %(levelname)s %(message)s"))
    submit_logger.addHandler(handler)


class SubmitCompatibilityMiddleware:
    def __init__(self, server: ASGIServer, native_call: Any) -> None:
        self.server = server
        self.native_call = native_call

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope.get("type") != "http" or scope.get("path") != "/submit" or scope.get("method") != "POST":
            await self.native_call(self.server, scope, receive, send)
            return

        raw_body = await self.read_body(receive)
        submit_logger.info("POST /submit raw request: %s", clip(raw_body.decode("utf-8", errors="replace"), 1800))

        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError as exc:
            submit_logger.warning("POST /submit invalid JSON: %s", exc)
            await send_json(send, 400, {"error": "invalid_json", "message": str(exc)})
            return

        if is_uagents_envelope(payload):
            submit_logger.info(
                "uAgents envelope received: sender=%s target=%s schema=%s",
                payload.get("sender"),
                payload.get("target"),
                payload.get("schema_digest"),
            )
            if payload.get("target") != agent.address:
                submit_logger.warning(
                    "Envelope target mismatch. received=%s running_agent=%s",
                    payload.get("target"),
                    agent.address,
                )
            await self.forward_to_native(scope, raw_body, send)
            return

        await self.handle_plain_submit(payload, send)

    async def read_body(self, receive: Any) -> bytes:
        chunks = []
        more_body = True
        while more_body:
            message = await receive()
            chunks.append(message.get("body", b""))
            more_body = bool(message.get("more_body", False))
        return b"".join(chunks)

    async def forward_to_native(self, scope: Any, raw_body: bytes, send: Any) -> None:
        consumed = False

        async def replay_receive() -> dict[str, Any]:
            nonlocal consumed
            if consumed:
                return {"type": "http.disconnect"}
            consumed = True
            return {"type": "http.request", "body": raw_body, "more_body": False}

        status_holder: list[int] = []

        async def capture_send(event: dict[str, Any]) -> None:
            if event.get("type") == "http.response.start":
                status_holder.append(int(event.get("status", 0)))
            await send(event)

        await self.native_call(self.server, scope, replay_receive, capture_send)
        submit_logger.info("native /submit returned HTTP %s", status_holder[0] if status_holder else "unknown")

    async def handle_plain_submit(self, payload: Any, send: Any) -> None:
        user_text = extract_text_from_payload(payload) or DEMO_PROMPT
        submit_logger.info("received message: %s", clip(user_text, 240))
        submit_logger.info("backend URL called: %s/api/plan", backend_url())

        try:
            plan, status_code = call_backend(user_text)
            submit_logger.info("backend response status: %s", status_code)
            response_text = format_plan_response(plan, fetch_runtime_status())
        except Exception as exc:
            submit_logger.exception("backend request failed")
            response_text = deterministic_demo_plan(user_text, reason=exc.__class__.__name__)

        submit_logger.info("response returned: %s", clip(response_text, 240))
        await send_json(
            send,
            200,
            {
                "text": response_text,
                "response": response_text,
                "agent": agent.address,
                "schema_digest": CHAT_MESSAGE_DIGEST,
            },
        )


def install_submit_compatibility() -> None:
    server = getattr(agent, "_server", None)
    if server is None:
        submit_logger.warning("uAgents server not found; /submit compatibility was not installed")
        return

    server._matchalendar_submit_middleware = SubmitCompatibilityMiddleware(server, _NATIVE_ASGI_CALL)
    server_class = type(server)
    if getattr(server_class, "_matchalendar_patched", False):
        submit_logger.info("/submit compatibility already installed")
        return

    async def patched_call(self: ASGIServer, scope: Any, receive: Any, send: Any) -> None:
        middleware = getattr(self, "_matchalendar_submit_middleware", None)
        if middleware is None:
            await _NATIVE_ASGI_CALL(self, scope, receive, send)
            return
        await middleware(scope, receive, send)

    server_class.__call__ = patched_call
    server_class._matchalendar_patched = True
    submit_logger.info("/submit compatibility installed")


_NATIVE_ASGI_CALL = ASGIServer.__call__

_seed = resolve_seed()
_port = int(os.getenv("AGENT_PORT", str(DEFAULT_AGENT_PORT)))
_endpoint_base = public_endpoint_base()
_endpoints = [f"{_endpoint_base}/submit"] if _endpoint_base else None
_agentverse_key = resolve_agentverse_key()
_use_mailbox = bool(not _endpoints and _agentverse_key)

agent = Agent(
    name=os.getenv("AGENT_NAME", AGENT_NAME),
    seed=_seed,
    port=_port,
    endpoint=_endpoints,
    mailbox=_use_mailbox,
    publish_agent_details=True,
)

protocol = Protocol(spec=chat_protocol_spec)


@protocol.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage) -> None:
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id),
    )
    user_text = extract_text(msg) or DEMO_PROMPT
    ctx.logger.info("received chat message from %s: %s", sender, clip(user_text, 240))
    ctx.logger.info("backend URL called: %s/api/plan", backend_url())

    try:
        plan, status_code = call_backend(user_text)
        ctx.logger.info("backend response status: %s", status_code)
        response_text = format_plan_response(plan, fetch_runtime_status())
    except Exception as exc:
        ctx.logger.exception("backend request failed")
        response_text = deterministic_demo_plan(user_text, reason=exc.__class__.__name__)

    await ctx.send(sender, create_text_chat(response_text, end_session=True))
    ctx.logger.info("response returned: %s", clip(response_text, 240))


@protocol.on_message(ChatAcknowledgement)
async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
    ctx.logger.info("received acknowledgement from %s for %s", sender, msg.acknowledged_msg_id)


agent.include(protocol, publish_manifest=True)


def print_startup_banner() -> None:
    seed_status = "placeholder" if _seed == DEFAULT_AGENT_SEED else f"custom len={len(_seed)}"
    endpoint_url = _endpoints[0] if _endpoints else "<not configured>"
    print()
    print("=" * 72)
    print(f"  {AGENT_NAME}")
    print("=" * 72)
    print(f"  Agent address        : {agent.address}")
    print(f"  Port                 : {_port}")
    print(f"  Seed source          : AGENT_SEED_PHRASE/AGENT_SEED ({seed_status})")
    print(f"  Backend URL          : {backend_url()}/api/plan")
    print(f"  Public endpoint base : {_endpoint_base or '<not configured>'}")
    print(f"  Registered endpoint  : {endpoint_url}")
    print(f"  Chat protocol digest : {CHAT_PROTOCOL_DIGEST}")
    print()
    print("  Agentverse External Integration should register:")
    print(f"    Address : {agent.address}")
    print(f"    Webhook : {endpoint_url}")
    print()
    print("  /submit compatibility is enabled for plain JSON and native uAgents envelopes.")
    print("=" * 72)
    print()


if __name__ == "__main__":
    print_startup_banner()
    install_submit_compatibility()
    agent.run()
