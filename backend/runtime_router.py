import json
import os
from urllib import error, request

from config import load_local_env
from planner.planner_provider import PlannerProvider


class RuntimeRouter:
    def __init__(self, planner_provider=None):
        load_local_env()
        self.planner_provider = planner_provider or PlannerProvider()
        self.use_gx10_runtime = _env_bool("USE_GX10_RUNTIME", False)
        self.gx10_backend_url = _clean_base_url(os.getenv("GX10_BACKEND_URL", "http://100.121.103.97:8000"))
        self.failover_enabled = _env_bool("RUNTIME_FAILOVER_ENABLED", True)
        self.timeout_seconds = _env_int("RUNTIME_ROUTER_TIMEOUT_SECONDS", 8)

    def plan(self, payload):
        request_payload = payload if isinstance(payload, dict) else {"prompt": str(payload or "")}
        if not self.use_gx10_runtime:
            return self._local_plan(request_payload, gx10_attempted=False, failover_used=False, runtime_error="")

        try:
            plan = self._remote_plan(request_payload)
            return _with_router_metadata(
                plan,
                selected_backend="gx10",
                gx10_attempted=True,
                failover_used=False,
                runtime_error="",
            )
        except Exception as exc:
            runtime_error = _short_error(exc)
            if self.failover_enabled:
                return self._local_plan(
                    request_payload,
                    gx10_attempted=True,
                    failover_used=True,
                    runtime_error=runtime_error,
                )
            raise RuntimeError(f"GX10 runtime unavailable: {runtime_error}") from exc

    def _remote_plan(self, payload):
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.gx10_backend_url}/api/plan",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "MatChalendar/1.0"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def _local_plan(self, payload, gx10_attempted, failover_used, runtime_error):
        plan = self.planner_provider.plan(payload)
        return _with_router_metadata(
            plan,
            selected_backend="local",
            gx10_attempted=gx10_attempted,
            failover_used=failover_used,
            runtime_error=runtime_error,
        )


def _with_router_metadata(plan, selected_backend, gx10_attempted, failover_used, runtime_error):
    result = dict(plan or {})
    metadata = dict(result.get("metadata") or {})
    metadata["runtime_router"] = {
        "selected_backend": selected_backend,
        "gx10_attempted": bool(gx10_attempted),
        "failover_used": bool(failover_used),
        "runtime_error": runtime_error or "",
    }
    result["metadata"] = metadata
    return result


def _clean_base_url(value):
    return str(value or "").rstrip("/")


def _short_error(exc):
    if isinstance(exc, error.HTTPError):
        return f"HTTPError {exc.code}"
    if isinstance(exc, error.URLError):
        reason = getattr(exc, "reason", "")
        if reason:
            return f"URLError {reason.__class__.__name__}"
        return "URLError"
    if isinstance(exc, TimeoutError):
        return "TimeoutError"
    return exc.__class__.__name__


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
