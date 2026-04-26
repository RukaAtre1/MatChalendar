import json
from pathlib import Path

from food.food_data_pipeline import FEATURES_FILE, enrich_item


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
MOCK_FILE = DATA_DIR / "dining_mock.json"


def load_dining_dataset():
    try:
        payload = json.loads(FEATURES_FILE.read_text(encoding="utf-8"))
        items = payload.get("items", [])
        if isinstance(items, list) and items:
            return {
                "metadata": {
                    **payload.get("metadata", {}),
                    "source": payload.get("metadata", {}).get("source", "ucla_dining_cache"),
                    "fallback": False,
                },
                "items": items,
            }
    except (OSError, json.JSONDecodeError, TypeError):
        pass

    mock_items = json.loads(MOCK_FILE.read_text(encoding="utf-8"))
    return {
        "metadata": {
            "source": "ucla_dining_mock",
            "fallback": True,
            "item_count": len(mock_items),
        },
        "items": [enrich_item(_normalize_mock_item(item)) for item in mock_items],
    }


def load_dining_data():
    return load_dining_dataset()["items"]


def _normalize_mock_item(item):
    nutrition = item.get("nutrition") or item.get("estimated_nutrition") or {}
    carbon = item.get("carbon", {})
    return {
        **item,
        "date": item.get("date", "2026-04-27"),
        "station": item.get("station", "Local planner"),
        "recipe_id": item.get("recipe_id", item.get("id", "")),
        "source_url": item.get("source_url", ""),
        "nutrition": nutrition,
        "estimated_nutrition": nutrition,
        "carbon": carbon,
    }
