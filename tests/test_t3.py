"""Unit tests for T3: ingredient line parser (lhf.parse)."""

import math
import unittest
from lhf.parse import parse_line


def close(a, b, rel=0.01, abs_=1e-6):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b)
    return abs(a - b) <= max(abs_, rel * abs(b))


class TestT3Parse(unittest.TestCase):
    def test_keys(self):
        res = parse_line("1 cup rice")
        expected_keys = {
            "raw", "status", "qty", "qty_min", "qty_max", "unit",
            "size", "stated_g", "stated_ml", "optional", "name"
        }
        self.assertEqual(set(res.keys()), expected_keys)
        self.assertEqual(res["raw"], "1 cup rice")

    def test_mixed_numbers_vs_ranges(self):
        # Mixed number with hyphen
        p1 = parse_line("2-1/2 cups flour")
        self.assertTrue(close(p1["qty"], 2.5))
        self.assertTrue(close(p1["qty_min"], 2.5))
        self.assertTrue(close(p1["qty_max"], 2.5))
        self.assertEqual(p1["unit"], "cup")

        # Range with hyphen
        p2 = parse_line("1-2 tbsp oil")
        self.assertTrue(close(p2["qty"], 1.5))
        self.assertTrue(close(p2["qty_min"], 1.0))
        self.assertTrue(close(p2["qty_max"], 2.0))
        self.assertEqual(p2["unit"], "tbsp")

        # Range with 'to'
        p3 = parse_line("¾ to 1 teaspoon garam masala")
        self.assertTrue(close(p3["qty"], 0.875))
        self.assertTrue(close(p3["qty_min"], 0.75))
        self.assertTrue(close(p3["qty_max"], 1.0))
        self.assertEqual(p3["unit"], "tsp")

    def test_stated_grams_and_ml(self):
        p1 = parse_line("1½ lbs (700 grams) chicken")
        self.assertTrue(close(p1["qty"], 1.5))
        self.assertEqual(p1["unit"], "lb")
        self.assertTrue(close(p1["stated_g"], 700.0))
        self.assertIsNone(p1["stated_ml"])

        p2 = parse_line("4 cups (960 ml) water")
        self.assertEqual(p2["status"], "WATER")
        self.assertTrue(close(p2["qty"], 4.0))
        self.assertEqual(p2["unit"], "cup")
        self.assertIsNone(p2["stated_g"])
        self.assertTrue(close(p2["stated_ml"], 960.0))

        p3 = parse_line("1 kg mutton")
        self.assertEqual(p3["unit"], "kg")
        self.assertTrue(close(p3["stated_g"], 1000.0))

    def test_water_status(self):
        p1 = parse_line("water for soaking")
        self.assertEqual(p1["status"], "WATER")
        self.assertIsNone(p1["qty"])
        self.assertIsNone(p1["unit"])

        p2 = parse_line("ice cubes as needed")
        self.assertEqual(p2["status"], "WATER")

        p3 = parse_line("1 tsp rose water")
        self.assertEqual(p3["status"], "QUANTIFIED")
        self.assertIn("rose water", p3["name"])

    def test_unquantified(self):
        p1 = parse_line("Salt to taste")
        self.assertEqual(p1["status"], "UNQUANTIFIED")
        self.assertIsNone(p1["qty"])
        self.assertIsNone(p1["unit"])
        self.assertIsNone(p1["stated_g"])
        self.assertIsNone(p1["stated_ml"])

        p2 = parse_line("Milk or water to knead (if needed)")
        self.assertEqual(p2["status"], "UNQUANTIFIED")

    def test_sizes(self):
        p1 = parse_line("1 small piece charcoal")
        self.assertEqual(p1["size"], "small")
        self.assertEqual(p1["unit"], "piece")

        p2 = parse_line("1 medium onion diced")
        self.assertEqual(p2["size"], "medium")
        self.assertEqual(p2["unit"], "piece")

        p3 = parse_line("350 g Large King Prawns")
        self.assertEqual(p3["unit"], "g")
        self.assertIsNone(p3["size"])  # mass unit zeroes size

    def test_cloves_and_garlic(self):
        p1 = parse_line("4 cloves")
        self.assertEqual(p1["unit"], "piece")
        self.assertIn("clove", p1["name"])

        p2 = parse_line("5 cloves garlic")
        self.assertEqual(p2["unit"], "clove")
        self.assertIn("garlic", p2["name"])

        p3 = parse_line("8 Garlic pods")
        self.assertEqual(p3["unit"], "clove")

    def test_hindi_lines(self):
        p1 = parse_line("चुटकी भर हींग")
        self.assertEqual(p1["unit"], "pinch")
        self.assertTrue(close(p1["qty"], 1.0))
        self.assertIn("हींग", p1["name"])

        p2 = parse_line("1 इंच अदरक")
        self.assertEqual(p2["unit"], "inch")
        self.assertTrue(close(p2["qty"], 1.0))
        self.assertIn("अदरक", p2["name"])

        p3 = parse_line("2 टेबल स्पून धनिया पत्ती")
        self.assertEqual(p3["unit"], "tbsp")
        self.assertTrue(close(p3["qty"], 2.0))
