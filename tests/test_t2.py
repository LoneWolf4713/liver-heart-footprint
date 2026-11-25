"""Unit tests for T2: nutrient summing and per-100g computation."""
import math
import unittest
from lhf import compute


class TestT2(unittest.TestCase):
    def test_nutrients_tuple(self):
        self.assertIsInstance(compute.NUTRIENTS, tuple)
        expected_nutrients = (
            "energy_kj",
            "energy_kcal",
            "fat_g",
            "sfa_g",
            "mufa_g",
            "pufa_g",
            "tfa_g",
            "carb_g",
            "freesugar_g",
            "fibre_g",
            "protein_g",
            "sodium_mg",
            "water_g",
        )
        self.assertEqual(len(compute.NUTRIENTS), len(expected_nutrients))
        for col in expected_nutrients:
            self.assertIn(col, compute.NUTRIENTS)

    def test_empty_and_none_items(self):
        for empty_input in ([], None, (), (x for x in [])):
            out = compute.sum_nutrients(empty_input)
            self.assertEqual(out["total_g"], 0.0)
            self.assertEqual(out["skipped"], [])
            self.assertEqual(out["unknown_tfa_items"], [])
            self.assertEqual(out["unknown_water_items"], [])
            for k in compute.NUTRIENTS:
                self.assertEqual(out["totals"][k], 0.0)
                self.assertEqual(out["per_100g"][k], 0.0)

    def test_skipped_items_extended(self):
        items = [
            {"code": "A019", "grams": 100.0},
            {"code": "NON_EXISTENT_CODE", "grams": 10.0},
            {"code": "A019", "grams": None},
            {"code": None, "grams": 10.0},
            None,
            {"code": "A019", "grams": "not_a_number"},
            {"code": "A019", "grams": True},
            {"code": "A019", "grams": float("nan")},
            {"code": "A019", "grams": -5.0},
            {"code": "A019", "grams": 0.0},
        ]
        out = compute.sum_nutrients(items)
        expected_skipped = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.assertEqual(out["skipped"], expected_skipped)
        self.assertAlmostEqual(out["total_g"], 100.0)

    def test_zero_gram_water_nan_isolation(self):
        # A019 has valid water, T508 (UK sunflower oil) has NaN water and NaN tfa
        # Zero-gram items must be skipped and NOT contaminate water_g/tfa_g with NaN (DEF-B9)
        items = [
            {"code": "A019", "grams": 100.0},
            {"code": "T508", "grams": 0.0},
        ]
        out = compute.sum_nutrients(items)
        self.assertEqual(out["skipped"], [1])
        self.assertEqual(out["unknown_water_items"], [])
        self.assertEqual(out["unknown_tfa_items"], [])
        self.assertFalse(math.isnan(out["totals"]["water_g"]))
        self.assertGreater(out["totals"]["water_g"], 0.0)
        self.assertFalse(math.isnan(out["per_100g"]["water_g"]))
        self.assertAlmostEqual(out["total_g"], 100.0)

    def test_all_zero_or_negative_grams(self):
        items = [
            {"code": "A019", "grams": 0.0},
            {"code": "T508", "grams": -5.0},
            {"code": "A019", "grams": None},
        ]
        out = compute.sum_nutrients(items)
        self.assertEqual(out["total_g"], 0.0)
        self.assertEqual(out["skipped"], [0, 1, 2])
        self.assertEqual(out["unknown_water_items"], [])
        self.assertEqual(out["unknown_tfa_items"], [])
        for k in compute.NUTRIENTS:
            self.assertEqual(out["totals"][k], 0.0)
            self.assertEqual(out["per_100g"][k], 0.0)

    def test_nan_handling_and_per_100g(self):
        # A019 has water, T508 (UK sunflower oil) has NaN water and NaN tfa
        items = [
            {"code": "A019", "grams": 100.0},
            {"code": "T508", "grams": 10.0},
        ]
        out = compute.sum_nutrients(items)
        self.assertAlmostEqual(out["total_g"], 100.0 + 10.0)
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

    def test_nan_order_independence(self):
        # T508 first (NaN water), then A019 (valid water)
        items = [
            {"code": "T508", "grams": 10.0},
            {"code": "A019", "grams": 100.0},
        ]
        out = compute.sum_nutrients(items)
        self.assertAlmostEqual(out["total_g"], 100.0 + 10.0)
        self.assertEqual(out["skipped"], [])
        self.assertEqual(out["unknown_water_items"], [0])
        self.assertEqual(out["unknown_tfa_items"], [0])
        self.assertTrue(math.isnan(out["totals"]["water_g"]))
        self.assertTrue(math.isnan(out["totals"]["tfa_g"]))

    def test_generator_input(self):
        items_list = [
            {"code": "A019", "grams": 100.0},
            {"code": "T508", "grams": 10.0},
        ]
        out_list = compute.sum_nutrients(items_list)
        out_gen = compute.sum_nutrients(item for item in items_list)
        self.assertEqual(out_list["total_g"], out_gen["total_g"])
        self.assertEqual(out_list["skipped"], out_gen["skipped"])
        self.assertEqual(out_list["unknown_water_items"], out_gen["unknown_water_items"])


if __name__ == "__main__":
    unittest.main()
