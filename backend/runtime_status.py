import json
import os
from urllib import error, request

from config import load_local_env


def runtime_status():
    load_local_env()
    gx10_enabled = _env_bool("USE_GX10_RUNTIME", False)
    fallback_enabled = _env_bool("RUNTIME_FAILOVER_ENABLED", True)
    gx10_backend_url = _clean_base_url(os.getenv("GX10_BACKEND_URL", "http://100.121.103.97:8000"))
    local_backend_url = _clean_base_url(os.getenv("LOCAL_BACKEND_URL", "http://127.0.0.1:8000"))
    gx10_available = _probe_gx10(gx10_backend_url) if gx10_enabled else False
    runtime_mode = _runtime_mode(gx10_enabled, gx10_available, fallback_enabled)
    using_gx10 = runtime_mode == "GX10_BACKEND"

    return {
        "runtime_mode": runtime_mode,
        "backend_url": gx10_backend_url if using_gx10 else local_backend_url,
        "gx10_enabled": gx10_enabled,
        "gx10_available": gx10_available,
        "local_first": True,
        "fallback_enabled": fallback_enabled,
        "backend_label": _backend_label(runtime_mode),
        "agentverse_enabled": agentverse_enabled(),
        "asi_one_enabled": _asi_one_enabled(),
        "mode": "gx10_first" if gx10_enabled else "local_only",
    }


def agentverse_enabled():
    load_local_env()
    return _env_bool("AGENTVERSE_AGENT_ENABLED", False)


def _probe_gx10(base_url):
    timeout_seconds = _env_int("RUNTIME_ROUTER_TIMEOUT_SECONDS", 8)
    req = request.Request(
        f"{base_url}/api/health",
        headers={"User-Agent": "MatChalendar/1.0"},
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            if response.status < 200 or response.status >= 300:
                return False
            json.loads(response.read().decode("utf-8"))
            return True
    except (OSError, ValueError, error.URLError):
        return False


def _runtime_mode(gx10_enabled, gx10_available, fallback_enabled):
    if not gx10_enabled:
        return "LOCAL_BACKEND"
    if gx10_available:
        return "GX10_BACKEND"
    if fallback_enabled:
        return "gx10_first_fallback"
    return "GX10_BACKEND"


def _backend_label(runtime_mode):
    labels = {
        "LOCAL_BACKEND": "Local Backend",
        "GX10_BACKEND": "ASUS GX10 Backend",
        "gx10_first_fallback": "Local Backend fallback from GX10",
    }
    return labels.get(runtime_mode, "Local Backend")


def _clean_base_url(value):
    return str(value or "").rstrip("/")


def _asi_one_enabled():
    return bool(
        _env_bool("USE_ASI_ONE", False)
        and os.getenv("ASI_ONE_API_KEY", "")
        and os.getenv("ASI_ONE_BASE_URL", "https://api.asi1.ai/v1")
        and os.getenv("ASI_ONE_MODEL", "asi1")
    )


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
