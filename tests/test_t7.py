"""Unit tests for T7: Daily-budget footprint (lhf.footprint)."""
import math
import os
import unittest
import pandas as pd

from lhf import constants
from lhf.footprint import footprint, get_baseline
from lhf.paths import DATA_CURATED


class TestT7Footprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baselines_df = pd.read_csv(os.path.join(DATA_CURATED, "baselines.csv")).set_index("metric_id")["value"].astype(float)
        cls.constants_df = pd.read_csv(os.path.join(DATA_CURATED, "constants.csv")).set_index("id")["value"].astype(float)

    def test_get_baseline(self):
        self.assertAlmostEqual(get_baseline("NSO_CALORIES_URBAN"), 2240.0)
        self.assertAlmostEqual(get_baseline("NSO_CALORIES_RURAL"), 2212.0)
        with self.assertRaises(KeyError):
            get_baseline("NONEXISTENT_KEY")

    def test_footprint_urban_general(self):
        ps = {
            "energy_kcal": 450.0,
            "fat_g": 22.0,
            "sfa_g": 9.0,
            "added_sugar_g": 12.0,
            "sodium_mg": 800.0,
            "refined_carb_g": 40.0,
        }
        res = footprint(ps, setting="urban", risk="general")
        self.assertIn("axes", res)
        self.assertIn("reference", res)
        self.assertIn("context", res)

        axes = res["axes"]
        for k in ps:
            self.assertIn(k, axes)
            self.assertAlmostEqual(axes[k]["amount"], ps[k])
            self.assertIn("unit", axes[k])
            self.assertIn("limit", axes[k])
            self.assertIn("pct_of_limit", axes[k])
            self.assertIn("pct_energy", axes[k])
            self.assertIn("limit_sources", axes[k])

        e_expected = 2240.0
        self.assertAlmostEqual(axes["energy_kcal"]["limit"], e_expected)
        self.assertEqual(axes["energy_kcal"]["limit_sources"], ["NSO_CALORIES_URBAN"])

        fat_limit = 30.0 / 100 * e_expected / 9.0
        self.assertAlmostEqual(axes["fat_g"]["limit"], fat_limit)
        self.assertAlmostEqual(axes["fat_g"]["pct_of_limit"], 22.0 / fat_limit * 100)
        self.assertAlmostEqual(axes["fat_g"]["pct_energy"], 22.0 * 9.0 / e_expected * 100)
        self.assertEqual(axes["fat_g"]["limit_sources"], ["LIMIT_TOTAL_FAT_PCT", "NSO_CALORIES_URBAN", "FAT_KCAL_PER_G"])

        sfa_limit = 10.0 / 100 * e_expected / 9.0
        self.assertAlmostEqual(axes["sfa_g"]["limit"], sfa_limit)
        self.assertAlmostEqual(axes["sfa_g"]["pct_of_limit"], 9.0 / sfa_limit * 100)
        self.assertAlmostEqual(axes["sfa_g"]["pct_energy"], 9.0 * 9.0 / e_expected * 100)
        self.assertEqual(axes["sfa_g"]["limit_sources"], ["LIMIT_SFA_GENERAL", "NSO_CALORIES_URBAN", "FAT_KCAL_PER_G"])

        self.assertAlmostEqual(axes["added_sugar_g"]["limit"], 25.0)
        self.assertAlmostEqual(axes["added_sugar_g"]["pct_of_limit"], 12.0 / 25.0 * 100)
        self.assertIsNone(axes["added_sugar_g"]["pct_energy"])
        self.assertEqual(axes["added_sugar_g"]["limit_sources"], ["LIMIT_ADDED_SUGAR_GRAMS"])

        sodium_limit = 5.0 * 393.4
        self.assertAlmostEqual(axes["sodium_mg"]["limit"], sodium_limit)
        self.assertAlmostEqual(axes["sodium_mg"]["pct_of_limit"], 800.0 / sodium_limit * 100)
        self.assertIsNone(axes["sodium_mg"]["pct_energy"])
        self.assertEqual(axes["sodium_mg"]["limit_sources"], ["LIMIT_SALT_GRAMS", "SODIUM_MG_PER_G_SALT"])

        self.assertIsNone(axes["refined_carb_g"]["limit"])
        self.assertIsNone(axes["refined_carb_g"]["pct_of_limit"])
        self.assertIsNone(axes["refined_carb_g"]["pct_energy"])
        self.assertEqual(axes["refined_carb_g"]["limit_sources"], [])

        self.assertIn("NSO_FAT_URBAN", res["context"])
        self.assertIn("INDIAB_SFA_NATIONAL", res["context"])
        self.assertAlmostEqual(res["context"]["NSO_FAT_URBAN"], 70.0)
        self.assertAlmostEqual(res["context"]["INDIAB_SFA_NATIONAL"], 8.9)

    def test_footprint_rural_cardiometabolic(self):
        ps = {
            "energy_kcal": 500.0,
            "fat_g": 30.0,
            "sfa_g": 10.0,
            "added_sugar_g": 5.0,
            "sodium_mg": 600.0,
            "refined_carb_g": 50.0,
        }
        res = footprint(ps, setting="rural", risk="cardiometabolic")
        axes = res["axes"]
        e_expected = 2212.0

        self.assertAlmostEqual(axes["energy_kcal"]["limit"], e_expected)
        self.assertEqual(axes["energy_kcal"]["limit_sources"], ["NSO_CALORIES_RURAL"])

        sfa_limit = 7.0 / 100 * e_expected / 9.0
        self.assertAlmostEqual(axes["sfa_g"]["limit"], sfa_limit)
        self.assertEqual(axes["sfa_g"]["limit_sources"], ["LIMIT_SFA_CARDIOMETABOLIC", "NSO_CALORIES_RURAL", "FAT_KCAL_PER_G"])

        self.assertIn("NSO_FAT_RURAL", res["context"])
        self.assertAlmostEqual(res["context"]["NSO_FAT_RURAL"], 59.8)

    def test_footprint_zeros(self):
        ps = {k: 0.0 for k in ["energy_kcal", "fat_g", "sfa_g", "added_sugar_g", "sodium_mg", "refined_carb_g"]}
        res = footprint(ps)
        for k, ax in res["axes"].items():
            self.assertEqual(ax["amount"], 0.0)
            if k == "refined_carb_g":
                self.assertIsNone(ax["pct_of_limit"])
            else:
                self.assertEqual(ax["pct_of_limit"], 0.0)

    def test_footprint_none_handling(self):
        self.assertIsNone(footprint(None))

    def test_footprint_missing_keys_or_nan(self):
        ps = {"energy_kcal": float("nan"), "fat_g": None}
        res = footprint(ps)
        self.assertEqual(res["axes"]["energy_kcal"]["amount"], 0.0)
        self.assertEqual(res["axes"]["fat_g"]["amount"], 0.0)
