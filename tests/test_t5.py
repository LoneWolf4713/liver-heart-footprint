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

    def test_non_string_code_types(self):
        # Int, float, bool, or None code should not raise TypeError (DEF-C7)
        for bad_code in (123, 45.67, True, False, None, object()):
            res = grams_for(1, "tsp", None, None, None, bad_code)
            self.assertIsNone(res["grams"])
            self.assertEqual(res["basis"], "UNQUANTIFIABLE")

        # Stated volume with non-string code assumes density 1.0 safely
        res_ml = grams_for(None, None, None, None, 100, 999)
        self.assertEqual(res_ml["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res_ml["grams"], 100.0)
        self.assertIn("DENSITY_ASSUMED_1", res_ml["flags"])

        # Mass units work regardless of non-string code
        res_mass = grams_for(2, "kg", None, None, None, 123)
        self.assertEqual(res_mass["basis"], "MASS_UNIT")
        self.assertAlmostEqual(res_mass["grams"], 2000.0)

    def test_nan_and_invalid_values(self):
        # NaN values for qty, stated_g, stated_ml (DEF-D10)
        res_nan_qty = grams_for(float("nan"), "cup", None, None, None, "A504")
        self.assertIsNone(res_nan_qty["grams"])
        self.assertEqual(res_nan_qty["basis"], "UNQUANTIFIABLE")

        res_nan_sg = grams_for(1, "cup", None, float("nan"), None, "A504")
        self.assertIsNone(res_nan_sg["grams"])
        self.assertEqual(res_nan_sg["basis"], "UNQUANTIFIABLE")

        res_nan_sml = grams_for(None, None, None, None, float("nan"), "A504")
        self.assertIsNone(res_nan_sml["grams"])
        self.assertEqual(res_nan_sml["basis"], "UNQUANTIFIABLE")

        # Invalid types for numeric fields (e.g. bool, non-numeric strings)
        for invalid in (True, False, "not_a_number"):
            res_inv_qty = grams_for(invalid, "cup", None, None, None, "A504")
            self.assertIsNone(res_inv_qty["grams"])
            self.assertEqual(res_inv_qty["basis"], "UNQUANTIFIABLE")

            res_inv_sg = grams_for(1, "cup", None, invalid, None, "A504")
            self.assertIsNone(res_inv_sg["grams"])
            self.assertEqual(res_inv_sg["basis"], "UNQUANTIFIABLE")

            res_inv_sml = grams_for(None, None, None, None, invalid, "A504")
            self.assertIsNone(res_inv_sml["grams"])
            self.assertEqual(res_inv_sml["basis"], "UNQUANTIFIABLE")

    def test_group_measures_reachability(self):
        # Group T: tsp (4 g), tbsp (13.5 g), stated_volume ml density (1.0)
        res_t_tsp = grams_for(1, "tsp", None, None, None, "T999")
        self.assertEqual(res_t_tsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_t_tsp["grams"], 4.0)

        res_t_tbsp = grams_for(1, "tbsp", None, None, None, "T999")
        self.assertEqual(res_t_tbsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_t_tbsp["grams"], 13.5)

        res_t_ml = grams_for(None, None, None, None, 100, "T999")
        self.assertEqual(res_t_ml["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res_t_ml["grams"], 100.0)
        self.assertEqual(res_t_ml["flags"], [])

        # Group L: cup (240 g), tbsp (15 g), tsp (5 g), ml density (1.0)
        res_l_cup = grams_for(1, "cup", None, None, None, "L999")
        self.assertEqual(res_l_cup["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_l_cup["grams"], 240.0)

        res_l_tbsp = grams_for(1, "tbsp", None, None, None, "L999")
        self.assertEqual(res_l_tbsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_l_tbsp["grams"], 15.0)

        res_l_tsp = grams_for(1, "tsp", None, None, None, "L999")
        self.assertEqual(res_l_tsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_l_tsp["grams"], 5.0)

        res_l_ml = grams_for(None, None, None, None, 100, "L999")
        self.assertEqual(res_l_ml["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res_l_ml["grams"], 100.0)
        self.assertEqual(res_l_ml["flags"], [])

        # Group K: cup (240 g), tbsp (15 g), tsp (5 g), ml density (1.0)
        res_k_cup = grams_for(1, "cup", None, None, None, "K505")
        self.assertEqual(res_k_cup["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_k_cup["grams"], 240.0)

        res_k_tbsp = grams_for(1, "tbsp", None, None, None, "K505")
        self.assertEqual(res_k_tbsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_k_tbsp["grams"], 15.0)

        res_k_tsp = grams_for(1, "tsp", None, None, None, "K505")
        self.assertEqual(res_k_tsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_k_tsp["grams"], 5.0)

        res_k_ml = grams_for(None, None, None, None, 100, "K505")
        self.assertEqual(res_k_ml["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res_k_ml["grams"], 100.0)
        self.assertEqual(res_k_ml["flags"], [])

        # Group E: cup (240 g), tbsp (15 g), tsp (5 g), ml density (1.0)
        res_e_cup = grams_for(1, "cup", None, None, None, "E001")
        self.assertEqual(res_e_cup["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_e_cup["grams"], 240.0)

        res_e_tbsp = grams_for(1, "tbsp", None, None, None, "E001")
        self.assertEqual(res_e_tbsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_e_tbsp["grams"], 15.0)

        res_e_tsp = grams_for(1, "tsp", None, None, None, "E001")
        self.assertEqual(res_e_tsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_e_tsp["grams"], 5.0)

        res_e_ml = grams_for(None, None, None, None, 100, "E001")
        self.assertEqual(res_e_ml["basis"], "STATED_VOLUME")
        self.assertAlmostEqual(res_e_ml["grams"], 100.0)
        self.assertEqual(res_e_ml["flags"], [])

        # Group G: tsp (2 g), tbsp (7 g), sprig (2 g)
        res_g_tsp = grams_for(1, "tsp", None, None, None, "G019")
        self.assertEqual(res_g_tsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_g_tsp["grams"], 2.0)

        res_g_tbsp = grams_for(1, "tbsp", None, None, None, "G019")
        self.assertEqual(res_g_tbsp["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_g_tbsp["grams"], 7.0)

        res_g_sprig = grams_for(1, "sprig", None, None, None, "G019")
        self.assertEqual(res_g_sprig["basis"], "GROUP_MEASURE")
        self.assertAlmostEqual(res_g_sprig["grams"], 2.0)


if __name__ == "__main__":
    unittest.main()
