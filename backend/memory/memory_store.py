from pathlib import Path


MEMORY_DIR = Path(__file__).resolve().parent
SOUL_PATH = MEMORY_DIR / "SOUL.md"
MEMORY_PATH = MEMORY_DIR / "MEMORY.md"


def read_soul():
    return _read_markdown(SOUL_PATH)


def read_memory():
    return _read_markdown(MEMORY_PATH)


def write_memory(markdown):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = (markdown or "").strip()
    updated = f"{content}\n" if content else ""
    MEMORY_PATH.write_text(updated, encoding="utf-8")
    return updated


def append_memory_update(markdown_patch):
    patch = (markdown_patch or "").strip()
    if not patch:
        return read_memory()

    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = read_memory().rstrip()
    updated = f"{existing}\n\n## Approved Update\n\n{patch}\n" if existing else f"{patch}\n"
    return write_memory(updated)


def _read_markdown(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
