import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from food.food_data_pipeline import enrich_item, parse_menu_item_page, parse_menu_page


class DiningPipelineTests(unittest.TestCase):
    def test_parse_menu_page_extracts_menu_items(self):
        html = """
        <h2>LUNCH MENU FOR TODAY</h2>
        <h3>Bruin Plate</h3>
        <h4>Harvest</h4>
        <ul>
          <li><a href="/menu-item/?recipe=1234">Lentil Bowl</a>
            <img title="Vegetarian"><img title="Low Carbon"><img title="Soy">
          </li>
        </ul>
        """
        items = parse_menu_page(html, "2026-04-27")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["meal_period"], "lunch")
        self.assertEqual(items[0]["dining_hall"], "Bruin Plate")
        self.assertEqual(items[0]["recipe_id"], "1234")

    def test_parse_menu_item_page_extracts_nutrition(self):
        html = """
        <main>
          Serving Size 1 bowl Calories 420
          Total Fat 12 g Sodium 640 mg Total Carbohydrate 52 g
          Dietary Fiber 8 g Total Sugars 5 g Protein 21 g
        </main>
        """
        detail = parse_menu_item_page(html)
        self.assertEqual(detail["nutrition"]["calories"], 420)
        self.assertEqual(detail["nutrition"]["protein_g"], 21)
        self.assertEqual(detail["nutrition"]["sodium_mg"], 640)

    def test_enrich_item_sets_features_and_scores(self):
        item = {
            "name": "Lentil vegetable plate",
            "meal_period": "dinner",
            "tags": ["Vegetarian", "Low Carbon"],
            "allergens": [],
            "nutrition": {"calories": 470, "protein_g": 19, "carbs_g": 62, "fat_g": 14, "fiber_g": 9, "sugar_g": 5, "sodium_mg": 540},
        }
        enriched = enrich_item(item)
        self.assertTrue(enriched["features"]["vegetarian"])
        self.assertLessEqual(enriched["carbon"]["estimated_co2e_kg"], 0.7)
        self.assertGreater(enriched["scores"]["health"], 0.8)


if __name__ == "__main__":
    unittest.main()
