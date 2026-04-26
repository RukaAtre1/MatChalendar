import argparse
import json
import re
import sys
import time
from datetime import UTC, date, datetime, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib import error, request
from urllib.parse import parse_qs, urljoin, urlparse

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from food.carbon_estimator import estimate_food_carbon_profile
from food.nutrition_estimator import estimate_nutrition


BASE_URL = "https://dining.ucla.edu"
MENUS_URL = f"{BASE_URL}/menus-at-a-glance/"
USER_AGENT = "MatChalendar/1.0"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CACHE_DIR = DATA_DIR / "dining_cache"
RAW_DIR = CACHE_DIR / "raw"
NORMALIZED_FILE = CACHE_DIR / "normalized" / "ucla_dining_normalized.json"
FEATURES_FILE = CACHE_DIR / "features" / "ucla_dining_features.json"


def refresh_ucla_dining_cache(days=7, start=None, include_details=True, delay_seconds=0.15):
    start_date = _parse_date(start) if start else date.today()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    NORMALIZED_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEATURES_FILE.parent.mkdir(parents=True, exist_ok=True)

    detail_cache = {}
    normalized = []
    for offset in range(days):
        menu_date = start_date + timedelta(days=offset)
        url = f"{MENUS_URL}?date={menu_date.isoformat()}"
        html = _fetch(url)
        _write_text(RAW_DIR / f"menus-at-a-glance-{menu_date.isoformat()}.html", html)
        day_items = parse_menu_page(html, menu_date.isoformat())

        for item in day_items:
            recipe_id = item.get("recipe_id")
            if include_details and recipe_id:
                if recipe_id not in detail_cache:
                    detail_url = item["source_url"]
                    detail_html = _fetch(detail_url)
                    _write_text(RAW_DIR / "items" / f"{recipe_id}.html", detail_html)
                    detail_cache[recipe_id] = parse_menu_item_page(detail_html)
                    time.sleep(delay_seconds)
                item.update(detail_cache[recipe_id])
            normalized.append(_normalize_item(item))
        time.sleep(delay_seconds)

    features = [enrich_item(item) for item in normalized]
    payload_meta = {
        "source": "ucla_dining",
        "base_url": BASE_URL,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "days": days,
        "start_date": start_date.isoformat(),
        "item_count": len(features),
    }
    _write_json(NORMALIZED_FILE, {"metadata": payload_meta, "items": normalized})
    _write_json(FEATURES_FILE, {"metadata": payload_meta, "items": features})
    return {"metadata": payload_meta, "items": features}


def load_food_knowledge_base():
    if not FEATURES_FILE.exists():
        return {"metadata": {"source": "missing_cache"}, "items": []}
    return json.loads(FEATURES_FILE.read_text(encoding="utf-8"))


def parse_menu_page(html, menu_date):
    parser = UCLAMenuParser(menu_date)
    parser.feed(html)
    return parser.items


def parse_menu_item_page(html):
    text = _page_text(html)
    nutrition = {
        "calories": _extract_number(text, r"Calories\s+([\d.]+)"),
        "protein_g": _extract_number(text, r"Protein\s+([\d.]+)\s*g"),
        "carbs_g": _extract_number(text, r"Total Carbohydrate\s+([\d.]+)\s*g"),
        "fat_g": _extract_number(text, r"Total Fat\s+([\d.]+)\s*g"),
        "fiber_g": _extract_number(text, r"Dietary Fiber\s+([\d.]+)\s*g"),
        "sugar_g": _extract_number(text, r"Total Sugars?\s+([\d.]+)\s*g"),
        "sodium_mg": _extract_number(text, r"Sodium\s+([\d.]+)\s*mg"),
    }
    return {
        "serving_size": _extract_text(text, r"Serving Size\s+(.+?)(?:\s+Calories|\s+Amount Per Serving|$)"),
        "nutrition": {key: value for key, value in nutrition.items() if value is not None},
        "ingredients": _clean_detail_text(_extract_text(text, r"Ingredients\s+(.+?)(?:\s+Allergen|\s+Allergens|\s+Nutrition|$)")),
    }


def enrich_item(item):
    tags = _normalized_labels(item.get("tags", []))
    allergens = _normalized_labels(item.get("allergens", []))
    nutrition = estimate_nutrition(item)
    carbon = estimate_food_carbon_profile({**item, "nutrition": nutrition})
    name = str(item.get("name", "")).lower()

    vegetarian = "vegetarian" in tags or "vegan" in tags
    vegan = "vegan" in tags
    high_protein = nutrition["protein_g"] >= 22 or any(word in name for word in ("chicken", "turkey", "tofu", "lentil", "beans"))
    low_sodium = nutrition["sodium_mg"] <= 650
    high_sugar = nutrition["sugar_g"] >= 22

    health_score = 0.72
    health_score += 0.08 if high_protein else 0
    health_score += 0.07 if vegetarian or vegan else 0
    health_score += 0.05 if nutrition["fiber_g"] >= 5 else 0
    health_score -= 0.08 if nutrition["sodium_mg"] > 950 else 0
    health_score -= 0.06 if high_sugar else 0

    energy_score = 0.76
    energy_score += 0.06 if 350 <= nutrition["calories"] <= 750 else -0.04
    energy_score += 0.05 if high_protein else 0
    energy_score += 0.04 if nutrition["fiber_g"] >= 4 else 0

    carbon_score = max(0.35, 1.0 - (carbon["estimated_co2e_kg"] / 3.2))
    sustainability_score = (carbon_score * 0.75) + (0.15 if vegetarian else 0) + (0.10 if vegan else 0)

    avoid_reasons = []
    if allergens:
        avoid_reasons.append("contains_allergens")
    if nutrition["sodium_mg"] > 1100:
        avoid_reasons.append("high_sodium")
    if high_sugar:
        avoid_reasons.append("high_sugar")

    return {
        **item,
        "tags": sorted(tags),
        "allergens": sorted(allergens),
        "nutrition": nutrition,
        "estimated_nutrition": nutrition,
        "carbon": carbon,
        "features": {
            "vegetarian": vegetarian,
            "vegan": vegan,
            "high_protein": high_protein,
            "low_sodium": low_sodium,
            "high_sugar": high_sugar,
            "protein_density": round(nutrition["protein_g"] / max(nutrition["calories"], 1) * 100, 2),
            "avoid_reasons": avoid_reasons,
        },
        "scores": {
            "health": _clamp_score(health_score),
            "energy": _clamp_score(energy_score),
            "sustainability": _clamp_score(sustainability_score),
            "carbon": _clamp_score(carbon_score),
        },
    }


class UCLAMenuParser(HTMLParser):
    def __init__(self, menu_date):
        super().__init__()
        self.menu_date = menu_date
        self.items = []
        self.meal_period = ""
        self.dining_hall = ""
        self.station = ""
        self.in_h2 = False
        self.in_h3 = False
        self.in_h4 = False
        self.current_item = None
        self.current_link = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2":
            self.in_h2 = True
            self.current_text = []
        elif tag == "h3":
            self.in_h3 = True
            self.current_text = []
        elif tag == "h4":
            self.in_h4 = True
            self.current_text = []
        elif tag == "li" and self.meal_period and self.dining_hall and self.station:
            self.current_item = {"tags": [], "allergens": []}
        elif tag == "a" and self.current_item is not None:
            href = attrs.get("href", "")
            if "/menu-item/" in href:
                self.current_link = href
                self.current_text = []
        elif tag == "img" and self.current_item is not None:
            label = attrs.get("title") or attrs.get("alt")
            if label:
                self.current_item["tags"].append(label)
                self.current_item["allergens"].append(label)

    def handle_data(self, data):
        if self.in_h2 or self.in_h3 or self.in_h4 or self.current_link:
            clean = data.strip()
            if clean:
                self.current_text.append(clean)

    def handle_endtag(self, tag):
        if tag == "h2" and self.in_h2:
            heading = " ".join(self.current_text).lower()
            for meal in ("breakfast", "brunch", "lunch", "dinner"):
                if meal in heading:
                    self.meal_period = "lunch" if meal == "brunch" else meal
                    break
            self.in_h2 = False
        elif tag == "h3" and self.in_h3:
            self.dining_hall = " ".join(self.current_text).strip()
            self.in_h3 = False
        elif tag == "h4" and self.in_h4:
            self.station = " ".join(self.current_text).strip()
            self.in_h4 = False
        elif tag == "a" and self.current_link and self.current_item is not None:
            href = urljoin(BASE_URL, self.current_link)
            recipe_id = parse_qs(urlparse(href).query).get("recipe", [""])[0]
            self.current_item.update(
                {
                    "date": self.menu_date,
                    "dining_hall": self.dining_hall,
                    "meal_period": self.meal_period,
                    "station": self.station,
                    "name": " ".join(self.current_text).strip(),
                    "recipe_id": recipe_id,
                    "source_url": href,
                }
            )
            self.current_link = None
        elif tag == "li" and self.current_item is not None:
            if self.current_item.get("name"):
                self.items.append(self.current_item)
            self.current_item = None


def _fetch(url, retries=2, timeout=20):
    last_error = None
    for attempt in range(retries + 1):
        try:
            req = request.Request(url, headers={"User-Agent": USER_AGENT})
            with request.urlopen(req, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (OSError, error.URLError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def _normalize_item(item):
    labels = _normalized_labels(item.get("tags", []))
    allergen_names = {
        "dairy",
        "eggs",
        "fish",
        "gluten",
        "milk",
        "peanuts",
        "sesame",
        "shellfish",
        "soy",
        "tree nuts",
        "wheat",
    }
    tags = sorted(label for label in labels if label not in allergen_names)
    allergens = sorted(label for label in labels if label in allergen_names)
    return {
        "id": f"ucla_{item.get('date', '').replace('-', '')}_{item.get('recipe_id') or _slug(item.get('name', 'item'))}",
        "date": item.get("date", ""),
        "name": item.get("name", ""),
        "dining_hall": item.get("dining_hall", ""),
        "meal_period": item.get("meal_period", ""),
        "station": item.get("station", ""),
        "recipe_id": item.get("recipe_id", ""),
        "available_start": _meal_start(item.get("meal_period")),
        "available_end": _meal_end(item.get("meal_period")),
        "tags": tags,
        "allergens": allergens,
        "ingredients": item.get("ingredients", ""),
        "serving_size": item.get("serving_size", ""),
        "nutrition": item.get("nutrition", {}),
        "source_url": item.get("source_url", ""),
    }


def _page_text(html):
    cleaned = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return re.sub(r"\s+", " ", unescape(cleaned)).strip()


def _extract_number(text, pattern):
    match = re.search(pattern, text, flags=re.I)
    if not match:
        return None
    try:
        value = float(match.group(1))
        return int(value) if value.is_integer() else value
    except ValueError:
        return None


def _extract_text(text, pattern):
    match = re.search(pattern, text, flags=re.I)
    return match.group(1).strip(" :") if match else ""


def _clean_detail_text(value):
    value = value.strip(" :&")
    return value if len(value) > 8 else ""


def _normalized_labels(values):
    labels = set()
    for value in values:
        clean = str(value).strip().lower().replace("_", " ")
        if clean:
            labels.add(clean)
    return labels


def _meal_start(meal_period):
    return {"breakfast": "07:00", "lunch": "11:00", "dinner": "17:00"}.get(meal_period, "")


def _meal_end(meal_period):
    return {"breakfast": "10:00", "lunch": "14:00", "dinner": "21:00"}.get(meal_period, "")


def _slug(value):
    slug = re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")
    return slug[:48] or "item"


def _clamp_score(value):
    return round(max(0.0, min(1.0, value)), 2)


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Refresh UCLA Dining menu cache for MatChalendar.")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--start-date", default="")
    parser.add_argument("--skip-details", action="store_true")
    args = parser.parse_args()
    payload = refresh_ucla_dining_cache(
        days=args.days,
        start=args.start_date or None,
        include_details=not args.skip_details,
    )
    print(json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()
