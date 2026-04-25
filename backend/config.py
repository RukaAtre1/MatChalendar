import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def load_local_env():
    for path in (ROOT_DIR / ".env", ROOT_DIR / ".env.local"):
        _load_env_file(path)


def _load_env_file(path):
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = _strip_quotes(value.strip())
        if key and key not in os.environ:
            os.environ[key] = value


def _strip_quotes(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value
