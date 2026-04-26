import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from skills.dining_skill import _rank_meal_bundles, validate_meal_adequacy


def item(name, calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, carbon, hall="Bruin Plate", tags=None):
    return {
        "id": f"{hall}_{name}".lower().replace(" ", "_"),
        "name": name,
        "dining_hall": hall,
        "meal_period": "lunch",
        "station": "Test station",
        "tags": tags or [],
        "nutrition": {
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "fiber_g": fiber_g,
            "sodium_mg": sodium_mg,
            "added_sugar_g": 0,
        },
        "carbon": {"estimated_co2e_kg": carbon},
        "features": {"vegetarian": True, "vegan": True, "high_protein": protein_g >= 20, "low_sodium": sodium_mg <= 650},
        "scores": {"health": 0.84, "energy": 0.80, "sustainability": 0.86, "carbon": max(0.35, 1 - carbon / 4)},
    }


class DiningSkillAdequacyTests(unittest.TestCase):
    def test_single_edamame_item_is_not_lunch(self):
        edamame = item("Edamame Beans", 94, 9.5, 8, 3, 4, 160, 0.1, tags=["low-carbon", "vegan"])

        adequacy = validate_meal_adequacy([edamame], "lunch")

        self.assertEqual(adequacy["adequacy_status"], "incomplete_meal")
        self.assertIn("single_side_or_snack_item", adequacy["adequacy_warnings"])
        self.assertIn("below_400_kcal_full_meal_minimum", adequacy["adequacy_warnings"])
        self.assertIn("below_20g_protein_full_meal_minimum", adequacy["adequacy_warnings"])

    def test_balanced_plant_forward_bundle_is_lunch(self):
        bundle = [
            item("Edamame Beans", 94, 9.5, 8, 3, 4, 160, 0.1, tags=["low-carbon", "vegan"]),
            item("Brown Rice", 220, 5, 45, 2, 4, 120, 0.25, tags=["low-carbon", "vegan"]),
            item("Kale Vegetable Salad", 110, 4, 18, 4, 6, 180, 0.2, tags=["low-carbon", "vegan"]),
            item("Grilled Tofu", 210, 18, 8, 11, 3, 360, 0.45, tags=["low-carbon", "vegan"]),
        ]

        adequacy = validate_meal_adequacy(bundle, "lunch")

        self.assertEqual(adequacy["adequacy_status"], "complete_meal")
        self.assertTrue(adequacy["plate_balance"]["has_protein"])
        self.assertTrue(adequacy["plate_balance"]["has_grain_or_starch"])
        self.assertTrue(adequacy["plate_balance"]["has_vegetables"])

    def test_carbon_ranking_ignores_lowest_carbon_side_item(self):
        side = item("Edamame Beans", 94, 9.5, 8, 3, 4, 160, 0.05, hall="Bruin Plate", tags=["low-carbon", "vegan"])
        low_carbon_complete = [
            side,
            item("Brown Rice", 220, 5, 45, 2, 4, 120, 0.25, hall="Bruin Plate", tags=["low-carbon", "vegan"]),
            item("Kale Vegetable Salad", 110, 4, 18, 4, 6, 180, 0.2, hall="Bruin Plate", tags=["low-carbon", "vegan"]),
            item("Grilled Tofu", 210, 18, 8, 11, 3, 360, 0.45, hall="Bruin Plate", tags=["low-carbon", "vegan"]),
        ]
        higher_carbon_complete = [
            item("Chicken Breast", 310, 35, 0, 12, 0, 420, 2.2, hall="De Neve"),
            item("Garlic Rice", 230, 5, 48, 3, 2, 200, 0.35, hall="De Neve"),
            item("Roasted Vegetables", 120, 4, 18, 4, 6, 220, 0.2, hall="De Neve"),
        ]

        ranked = _rank_meal_bundles(low_carbon_complete + higher_carbon_complete, {"dietary_preferences": []}, "lunch")

        self.assertGreater(len(ranked), 0)
        self.assertEqual(ranked[0]["adequacy_status"], "complete_meal")
        self.assertEqual(ranked[0]["dining_hall"], "Bruin Plate")
        self.assertGreater(ranked[0]["estimated_nutrition"]["calories"], 400)
        self.assertNotEqual(ranked[0]["items"], [side])


if __name__ == "__main__":
    unittest.main()
