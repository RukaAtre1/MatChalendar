import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_dining_data():
    return json.loads((DATA_DIR / "dining_mock.json").read_text(encoding="utf-8"))
