"""Unit tests for T6: Food classes (lhf.classify)."""
import math
import unittest

from lhf import composition
from lhf.classify import class_totals, classes_for


class TestT6Classify(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = composition.load_table()

    def test_classes_for_known(self):
        self.assertIn("ADDED_SUGAR", classes_for("I001"))
        self.assertIn("REFINED_GRAIN", classes_for("A018"))
        self.assertIn("COOKING_OIL", classes_for("T508"))
        self.assertIn("HYDROGENATED_FAT", classes_for("T014"))
        self.assertIn("DAIRY_FAT", classes_for("T013"))

    def test_classes_for_multiple(self):
        g528 = classes_for("G528")
        self.assertIn("SALT", g528)
        self.assertIn("SPICE", g528)

        g540 = classes_for("G540")
        self.assertIn("SALT", g540)
        self.assertIn("SPICE", g540)

    def test_classes_for_unclassified_or_missing(self):
        self.assertEqual(classes_for("A019"), [])
        self.assertEqual(classes_for("NOT_A_CODE"), [])
        self.assertEqual(classes_for(""), [])
        self.assertEqual(classes_for(None), [])

    def test_class_totals_empty(self):
        res = class_totals([])
        self.assertEqual(res["added_sugar_g"], 0.0)
        self.assertEqual(res["refined_carb_g"], 0.0)
        self.assertEqual(res["salt_g"], 0.0)
        self.assertEqual(
            res["fat_by_class_g"],
            {"COOKING_OIL": 0.0, "HYDROGENATED_FAT": 0.0, "DAIRY_FAT": 0.0, "OTHER": 0.0},
        )

    def test_class_totals_added_sugar_capping(self):
        # I502 has freesugar_g = 105.0 g / 100 g in UK table; must cap at item mass
        items = [{"code": "I502", "grams": 25.0, "nutrients": composition.nutrients_for("I502", 25.0)}]
        res = class_totals(items)
        self.assertAlmostEqual(res["added_sugar_g"], 25.0)

    def test_class_totals_refined_carb(self):
        items = [
            {"code": "A018", "grams": 100.0, "nutrients": composition.nutrients_for("A018", 100.0)},
            {"code": "A015", "grams": 50.0, "nutrients": composition.nutrients_for("A015", 50.0)},
        ]
        res = class_totals(items)
        exp = float(self.table.loc["A018", "carb_g"]) + 0.5 * float(self.table.loc["A015", "carb_g"])
        self.assertAlmostEqual(res["refined_carb_g"], exp)

    def test_class_totals_salt(self):
        items = [
            {"code": "G528", "grams": 5.0, "nutrients": composition.nutrients_for("G528", 5.0)},
            {"code": "G540", "grams": 2.5, "nutrients": composition.nutrients_for("G540", 2.5)},
        ]
        res = class_totals(items)
        self.assertAlmostEqual(res["salt_g"], 7.5)

    def test_class_totals_fat_partitioning(self):
        items = [
            {"code": "T508", "grams": 20.0, "nutrients": composition.nutrients_for("T508", 20.0)},  # COOKING_OIL
            {"code": "T506", "grams": 15.0, "nutrients": composition.nutrients_for("T506", 15.0)},  # DAIRY_FAT
            {"code": "T014", "grams": 10.0, "nutrients": composition.nutrients_for("T014", 10.0)},  # HYDROGENATED_FAT
            {"code": "A019", "grams": 100.0, "nutrients": composition.nutrients_for("A019", 100.0)},  # OTHER
        ]
        res = class_totals(items)
        fat = res["fat_by_class_g"]
        self.assertAlmostEqual(fat["COOKING_OIL"], 20.0 * float(self.table.loc["T508", "fat_g"]) / 100.0)
        self.assertAlmostEqual(fat["DAIRY_FAT"], 15.0 * float(self.table.loc["T506", "fat_g"]) / 100.0)
        self.assertAlmostEqual(fat["HYDROGENATED_FAT"], 10.0 * float(self.table.loc["T014", "fat_g"]) / 100.0)
        self.assertAlmostEqual(fat["OTHER"], 100.0 * float(self.table.loc["A019", "fat_g"]) / 100.0)

    def test_class_totals_missing_or_invalid_grams(self):
        items = [
            {"code": "G528", "grams": None},
            {"code": "I502", "grams": -10.0},
            {"code": "T508", "grams": 0.0},
        ]
        res = class_totals(items)
        self.assertEqual(res["added_sugar_g"], 0.0)
        self.assertEqual(res["refined_carb_g"], 0.0)
        self.assertEqual(res["salt_g"], 0.0)
        self.assertEqual(res["fat_by_class_g"]["COOKING_OIL"], 0.0)

    def test_class_totals_nutrients_none(self):
        # Deserialized JSON can have None values in nutrients dict (DEF-C3)
        items = [
            {
                "code": "I502",
                "grams": 20.0,
                "nutrients": {"freesugar_g": None, "carb_g": None, "fat_g": None},
            },
            {
                "code": "A018",
                "grams": 100.0,
                "nutrients": {"freesugar_g": None, "carb_g": None, "fat_g": None},
            },
            {
                "code": "T508",
                "grams": 15.0,
                "nutrients": {"freesugar_g": None, "carb_g": None, "fat_g": None},
            },
            {
                "code": "UNKNOWN_CODE",
                "grams": 10.0,
                "nutrients": {"freesugar_g": None, "carb_g": None, "fat_g": None},
            },
        ]
        res = class_totals(items)
        # I502 falls back to table: 20 * min(105, 100) / 100 = 20.0
        self.assertAlmostEqual(res["added_sugar_g"], 20.0)
        # A018 falls back to table
        exp_carb = float(self.table.loc["A018", "carb_g"])
        self.assertAlmostEqual(res["refined_carb_g"], exp_carb)
        # T508 falls back to table
        exp_oil_fat = 15.0 * float(self.table.loc["T508", "fat_g"]) / 100.0
        self.assertAlmostEqual(res["fat_by_class_g"]["COOKING_OIL"], exp_oil_fat)
        # UNKNOWN_CODE contributes 0.0 without crashing
        self.assertFalse(math.isnan(res["added_sugar_g"]))
        self.assertFalse(math.isnan(res["refined_carb_g"]))

    def test_class_totals_nutrients_nan(self):
        # Guard against NaN poisoning (DEF-D9)
        items = [
            {"code": "I001", "grams": 10.0, "nutrients": {"freesugar_g": float("nan")}},
            {"code": "A018", "grams": 50.0, "nutrients": {"carb_g": float("nan")}},
            {"code": "T508", "grams": 20.0, "nutrients": {"fat_g": float("nan")}},
            {"code": "G528", "grams": float("nan"), "nutrients": {}},
        ]
        res = class_totals(items)
        self.assertEqual(res["added_sugar_g"], 0.0)
        self.assertEqual(res["refined_carb_g"], 0.0)
        self.assertEqual(res["salt_g"], 0.0)
        self.assertEqual(res["fat_by_class_g"]["COOKING_OIL"], 0.0)

    def test_class_totals_multi_class_items(self):
        # G528 and G540 are both SALT and SPICE
        items = [
            {"code": "G528", "grams": 4.0, "nutrients": composition.nutrients_for("G528", 4.0)},
            {"code": "G540", "grams": 6.0, "nutrients": composition.nutrients_for("G540", 6.0)},
        ]
        res = class_totals(items)
        self.assertAlmostEqual(res["salt_g"], 10.0)
        # Neither is COOKING_OIL/DAIRY_FAT/HYDROGENATED_FAT -> fat goes to OTHER
        exp_fat = (
            float(self.table.loc["G528", "fat_g"]) * 4.0 / 100.0
            + float(self.table.loc["G540", "fat_g"]) * 6.0 / 100.0
        )
        self.assertAlmostEqual(res["fat_by_class_g"]["OTHER"], exp_fat)

    def test_class_totals_fat_mass_conservation(self):
        # Verify that total fat across all 4 categories exactly equals total fat of all items
        items = [
            {"code": "T508", "grams": 20.0, "nutrients": composition.nutrients_for("T508", 20.0)},
            {"code": "T506", "grams": 15.0, "nutrients": composition.nutrients_for("T506", 15.0)},
            {"code": "T014", "grams": 10.0, "nutrients": composition.nutrients_for("T014", 10.0)},
            {"code": "A019", "grams": 100.0, "nutrients": composition.nutrients_for("A019", 100.0)},
            {"code": "A018", "grams": 50.0, "nutrients": composition.nutrients_for("A018", 50.0)},
            {"code": "I001", "grams": 10.0, "nutrients": composition.nutrients_for("I001", 10.0)},
        ]
        res = class_totals(items)
        total_input_fat = sum(
            float(i["nutrients"]["fat_g"])
            for i in items
            if i["nutrients"].get("fat_g") is not None and not math.isnan(float(i["nutrients"]["fat_g"]))
        )
        total_partitioned_fat = sum(res["fat_by_class_g"].values())
        self.assertAlmostEqual(total_partitioned_fat, total_input_fat, places=6)
        # Ensure all partitions received their share
        self.assertGreater(res["fat_by_class_g"]["COOKING_OIL"], 0.0)
        self.assertGreater(res["fat_by_class_g"]["DAIRY_FAT"], 0.0)
        self.assertGreater(res["fat_by_class_g"]["HYDROGENATED_FAT"], 0.0)
        self.assertGreater(res["fat_by_class_g"]["OTHER"], 0.0)


if __name__ == "__main__":
    unittest.main()
