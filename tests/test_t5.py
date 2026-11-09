"""Unit tests for T5: household measures to grams (lhf.grams)."""
import unittest
from lhf.grams import grams_for


class TestT5Grams(unittest.TestCase):
    def test_rule1_stated_mass(self):
        res = grams_for(2, "cup", None, 150, None, "A504")
        self.assertEqual(res["basis"], "STATED_MASS")
        self.assertEqual(res["grams"], 150.0)
        self.assertEqual(res["flags"], [])

    def test_rule2_stated_volume(self):
        # With code having specific ml density (sunflower oil T508 -> 0.92)
        res = grams_for(None, None, None, None, 100, "T508")
        self.assertEqual(res["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res["grams"], 92.0)
        self.assertEqual(res["flags"], [])

        # With unmapped / unknown code -> density assumed 1.0
        res2 = grams_for(None, None, None, None, 50, None)
        self.assertEqual(res2["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res2["grams"], 50.0)
        self.assertIn("DENSITY_ASSUMED_1", res2["flags"])

    def test_rule3_missing_qty_or_unit(self):
        res1 = grams_for(None, "cup", None, None, None, "A504")
        self.assertIsNone(res1["grams"])
        self.assertEqual(res1["basis"], "UNQUANTIFIABLE")

        res2 = grams_for(1, None, None, None, None, "A504")
        self.assertIsNone(res2["grams"])
        self.assertEqual(res2["basis"], "UNQUANTIFIABLE")

    def test_rule4_mass_units(self):
        res_g = grams_for(250, "g", None, None, None, "UNMAPPED")
        self.assertEqual(res_g["basis"], "MASS_UNIT")
        self.assertAlmostEqual(res_g["grams"], 250.0)

        res_kg = grams_for(1, "kg", None, None, None, None)
        self.assertEqual(res_kg["basis"], "MASS_UNIT")
        self.assertAlmostEqual(res_kg["grams"], 1000.0)

    def test_rule5_volume_units(self):
        res_l = grams_for(1, "l", None, None, None, "L002")
        self.assertEqual(res_l["basis"], "VOLUME_UNIT")
        self.assertAlmostEqual(res_l["grams"], 1000.0)

    def test_rule6_code_measure_and_sizes(self):
        # Direct match on code
        res_besan = grams_for(1, "cup", None, None, None, "A504")
        self.assertEqual(res_besan["basis"], "CODE_MEASURE")
        self.assertAlmostEqual(res_besan["grams"], 92.0)
        self.assertEqual(res_besan["flags"], [])

        # Size substitution
        res_sub = grams_for(2, "piece", "large", None, None, "G017")
        self.assertEqual(res_sub["basis"], "CODE_MEASURE")
        self.assertAlmostEqual(res_sub["grams"], 120.0)
        self.assertIn("SIZE_SUBSTITUTED", res_sub["flags"])

        # Size assumed medium
        res_med = grams_for(1, "piece", None, None, None, "G017")
        self.assertEqual(res_med["basis"], "CODE_MEASURE")
        self.assertAlmostEqual(res_med["grams"], 60.0)
        self.assertIn("SIZE_ASSUMED_MEDIUM", res_med["flags"])

    def test_rule7_group_measure(self):
        res_hing = grams_for(1, "tsp", None, None, None, "G019")
        self.assertEqual(res_hing["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_hing["grams"], 2.0)
        self.assertEqual(res_hing["flags"], [])

    def test_rule8_pinch_and_dash(self):
        # Pinch hing -> 0.25 * 2.0 = 0.5
        res_pinch = grams_for(1, "pinch", None, None, None, "G019")
        self.assertEqual(res_pinch["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_pinch["grams"], 0.5)
        self.assertIn("PINCH_AS_QUARTER_TSP", res_pinch["flags"])

        # Dash salt -> has code measure in measures.csv
        res_dash = grams_for(1, "dash", None, None, None, "G528")
        self.assertEqual(res_dash["basis"], "CODE_MEASURE")
        self.assertAlmostEqual(res_dash["grams"], 0.4)
        self.assertNotIn("PINCH_AS_QUARTER_TSP", res_dash["flags"])

    def test_rule9_otherwise_unquantifiable(self):
        res_bunch = grams_for(1, "bunch", None, None, None, "G016")
        self.assertIsNone(res_bunch["grams"])
        self.assertEqual(res_bunch["basis"], "UNQUANTIFIABLE")

        res_unmapped = grams_for(1, "cup", None, None, None, "UNMAPPED")
        self.assertIsNone(res_unmapped["grams"])
        self.assertEqual(res_unmapped["basis"], "UNQUANTIFIABLE")


if __name__ == "__main__":
    unittest.main()
