"""Unit tests for T2: nutrient summing and per-100g computation."""
import math
import unittest
from lhf import compute


class TestT2(unittest.TestCase):
    def test_nutrients_tuple(self):
        self.assertIsInstance(compute.NUTRIENTS, tuple)
        for col in ("energy_kj", "energy_kcal", "fat_g", "sfa_g", "carb_g", "protein_g", "sodium_mg"):
            self.assertIn(col, compute.NUTRIENTS)

    def test_empty_items(self):
        out = compute.sum_nutrients([])
        self.assertEqual(out["total_g"], 0.0)
        self.assertEqual(out["skipped"], [])
        self.assertEqual(out["unknown_tfa_items"], [])
        self.assertEqual(out["unknown_water_items"], [])
        for k in compute.NUTRIENTS:
            self.assertEqual(out["totals"][k], 0.0)
            self.assertEqual(out["per_100g"][k], 0.0)

    def test_skipped_items(self):
        items = [
            {"code": "A019", "grams": 100.0},
            {"code": "NON_EXISTENT_CODE", "grams": 50.0},
            {"code": "A019", "grams": None},
        ]
        out = compute.sum_nutrients(items)
        self.assertEqual(out["skipped"], [1, 2])
        self.assertAlmostEqual(out["total_g"], 100.0)

    def test_nan_handling_and_per_100g(self):
        # A019 has water, T508 (UK sunflower oil) has NaN water and NaN tfa
        items = [
            {"code": "A019", "grams": 100.0},
            {"code": "T508", "grams": 10.0},
        ]
        out = compute.sum_nutrients(items)
        self.assertAlmostEqual(out["total_g"], 110.0)
        self.assertEqual(out["skipped"], [])
        self.assertIn(1, out["unknown_water_items"])
        self.assertIn(1, out["unknown_tfa_items"])
        self.assertTrue(math.isnan(out["totals"]["water_g"]))
        self.assertTrue(math.isnan(out["totals"]["tfa_g"]))
        self.assertTrue(math.isnan(out["per_100g"]["water_g"]))
        self.assertTrue(math.isnan(out["per_100g"]["tfa_g"]))

        # Non-NaN nutrients should scale properly
        self.assertGreater(out["totals"]["fat_g"], 0)
        expected_fat_per_100g = out["totals"]["fat_g"] / out["total_g"] * 100
        self.assertAlmostEqual(out["per_100g"]["fat_g"], expected_fat_per_100g)


if __name__ == "__main__":
    unittest.main()
