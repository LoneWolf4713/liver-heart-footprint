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

    def test_ampersand_and_mixed_fractions(self):
        # Ampersand mixed fraction (DEF-B6, holdout G058, recipe D1-29)
        p1 = parse_line("1 &amp; ½ tablespoons oil")
        self.assertEqual(p1["status"], "QUANTIFIED")
        self.assertTrue(close(p1["qty"], 1.5))
        self.assertEqual(p1["unit"], "tbsp")
        self.assertIn("oil", p1["name"])

        p2 = parse_line("1 & 1/2 cups flour")
        self.assertEqual(p2["status"], "QUANTIFIED")
        self.assertTrue(close(p2["qty"], 1.5))
        self.assertEqual(p2["unit"], "cup")

        p3 = parse_line("2 and 1/2 tsp sugar")
        self.assertEqual(p3["status"], "QUANTIFIED")
        self.assertTrue(close(p3["qty"], 2.5))
        self.assertEqual(p3["unit"], "tsp")

    def test_hindi_matras_and_quote_boundary(self):
        # Devanagari units ending in matras (DEF-C4)
        p_ml = parse_line("10 मिली तेल")
        self.assertEqual(p_ml["unit"], "ml")
        self.assertTrue(close(p_ml["qty"], 10.0))
        self.assertIn("तेल", p_ml["name"])

        p_kg = parse_line("1 किग्रा आलू")
        self.assertEqual(p_kg["unit"], "kg")
        self.assertTrue(close(p_kg["qty"], 1.0))
        self.assertTrue(close(p_kg["stated_g"], 1000.0))

        p_cm = parse_line("2 सेमी अदरक")
        self.assertEqual(p_cm["unit"], "cm")
        self.assertTrue(close(p_cm["qty"], 2.0))

        p_pc1 = parse_line("1 टुकड़ा पनीर")
        self.assertEqual(p_pc1["unit"], "piece")
        self.assertTrue(close(p_pc1["qty"], 1.0))

        p_pc2 = parse_line("2 टुकड़े पनीर")
        self.assertEqual(p_pc2["unit"], "piece")
        self.assertTrue(close(p_pc2["qty"], 2.0))

        p_pinch = parse_line("1 चुटकी नमक")
        self.assertEqual(p_pinch["unit"], "pinch")
        self.assertTrue(close(p_pinch["qty"], 1.0))

        p_pinch_standalone = parse_line("चुटकी नमक")
        self.assertEqual(p_pinch_standalone["unit"], "pinch")
        self.assertTrue(close(p_pinch_standalone["qty"], 1.0))

        # Inch quote boundary (DEF-C5)
        p_inch = parse_line('1" ginger')
        self.assertEqual(p_inch["unit"], "inch")
        self.assertTrue(close(p_inch["qty"], 1.0))
        self.assertIn("ginger", p_inch["name"])

        p_inch2 = parse_line('2" cinnamon stick')
        self.assertEqual(p_inch2["unit"], "inch")
        self.assertTrue(close(p_inch2["qty"], 2.0))

    def test_plain_water_isolation(self):
        # Compound culinary foods must NEVER be classified as WATER (DEF-B1)
        compounds = [
            ("1 scoop ice cream", "ice cream"),
            ("100 g water chestnuts", "water chestnuts"),
            ("1 cup watercress", "watercress"),
            ("50 g water cress", "water cress"),
            ("1 ice apple peeled", "ice apple"),
            ("2 tbsp tamarind water", "tamarind water"),
            ("1 cup coconut water", "coconut water"),
            ("1 cup dal water", "dal water"),
            ("1 cup rice water", "rice water"),
            ("1 tsp kewra water", "kewra water"),
        ]
        for line, expected_sub in compounds:
            p = parse_line(line)
            self.assertEqual(p["status"], "QUANTIFIED", f"Expected QUANTIFIED for {line}, got {p['status']}")
            self.assertIn(expected_sub, p["name"])

        p_unq = parse_line("ice cream for dessert")
        self.assertEqual(p_unq["status"], "UNQUANTIFIED")
        self.assertNotEqual(p_unq["status"], "WATER")

        p_tam = parse_line("tamarind water as needed")
        self.assertEqual(p_tam["status"], "UNQUANTIFIED")
        self.assertNotEqual(p_tam["status"], "WATER")

        # True plain water and ice lines
        self.assertEqual(parse_line("water")["status"], "WATER")
        self.assertEqual(parse_line("2 cups water")["status"], "WATER")
        self.assertEqual(parse_line("ice cubes as needed")["status"], "WATER")
        self.assertEqual(parse_line("1 cup पानी")["status"], "WATER")
        self.assertEqual(parse_line("बर्फ")["status"], "WATER")

    def test_dash_standalone(self):
        # Standalone dash without number (DEF-B7)
        p1 = parse_line("dash pepper")
        self.assertEqual(p1["status"], "QUANTIFIED")
        self.assertEqual(p1["unit"], "dash")
        self.assertTrue(close(p1["qty"], 1.0))
        self.assertIn("pepper", p1["name"])

        p2 = parse_line("a dash salt")
        self.assertEqual(p2["status"], "QUANTIFIED")
        self.assertEqual(p2["unit"], "dash")
        self.assertTrue(close(p2["qty"], 1.0))
        self.assertIn("salt", p2["name"])

        p3 = parse_line("dashes of cayenne")
        self.assertEqual(p3["status"], "QUANTIFIED")
        self.assertEqual(p3["unit"], "dash")
        self.assertTrue(close(p3["qty"], 1.0))

    def test_leaf_unit_rule(self):
        # SPEC §4: leaf only when name is something else (DEF-A5)
        p1 = parse_line("5 leaves mint")
        self.assertEqual(p1["unit"], "leaf")
        self.assertTrue(close(p1["qty"], 5.0))
        self.assertIn("mint", p1["name"])

        p2 = parse_line("10 leaves basil")
        self.assertEqual(p2["unit"], "leaf")
        self.assertTrue(close(p2["qty"], 10.0))
        self.assertIn("basil", p2["name"])

        # When leaf name is not preceded by another ingredient, defaults to piece
        p3 = parse_line("1 bay leaf")
        self.assertEqual(p3["unit"], "piece")
        self.assertIn("bay", p3["name"])

        p4 = parse_line("2 curry leaves")
        self.assertEqual(p4["unit"], "piece")
        self.assertIn("curry", p4["name"])

        p5 = parse_line("5 leaves")
        self.assertEqual(p5["unit"], "piece")

    def test_bunch_unit_decoupling(self):
        # Elimination of overfitted bunch search (DEF-A4)
        p1 = parse_line("2 tomatoes for a bunch of people")
        self.assertEqual(p1["unit"], "piece")
        self.assertTrue(close(p1["qty"], 2.0))
        self.assertIn("tomatoes for a bunch of people", p1["name"])

        # Valid unit bunch position directly after qty / size
        p2 = parse_line("1 bunch spinach")
        self.assertEqual(p2["unit"], "bunch")
        self.assertTrue(close(p2["qty"], 1.0))
        self.assertIn("spinach", p2["name"])

        p3 = parse_line("1 small bunch coriander")
        self.assertEqual(p3["unit"], "bunch")
        self.assertEqual(p3["size"], "small")
        self.assertTrue(close(p3["qty"], 1.0))
        self.assertIn("coriander", p3["name"])

    def test_range_vs_mixed_precedence_and_spacing(self):
        # Range with mixed number operand (DEF-D11)
        p1 = parse_line("1-1/2 to 2 cups flour")
        self.assertEqual(p1["status"], "QUANTIFIED")
        self.assertTrue(close(p1["qty"], 1.75))
        self.assertTrue(close(p1["qty_min"], 1.5))
        self.assertTrue(close(p1["qty_max"], 2.0))
        self.assertEqual(p1["unit"], "cup")

        p2 = parse_line("1 - 1/2 to 2 cups flour")
        self.assertEqual(p2["status"], "QUANTIFIED")
        self.assertTrue(close(p2["qty"], 1.75))
        self.assertTrue(close(p2["qty_min"], 1.5))
        self.assertTrue(close(p2["qty_max"], 2.0))

        # Mixed number with whitespace around hyphen
        p3 = parse_line("1 - 1/2 cups flour")
        self.assertEqual(p3["status"], "QUANTIFIED")
        self.assertTrue(close(p3["qty"], 1.5))
        self.assertTrue(close(p3["qty_min"], 1.5))
        self.assertTrue(close(p3["qty_max"], 1.5))

        p4 = parse_line("2 - 1/2 tbsp ghee")
        self.assertEqual(p4["status"], "QUANTIFIED")
        self.assertTrue(close(p4["qty"], 2.5))
        self.assertEqual(p4["unit"], "tbsp")

    def test_denominator_zero_and_invariants(self):
        # Denominator zero division prevention (DEF-C8)
        p1 = parse_line("1/0 tsp salt")
        self.assertEqual(p1["status"], "UNQUANTIFIED")
        self.assertIsNone(p1["qty"])

        # Non-positive quantity invariant (qty <= 0 -> UNQUANTIFIED)
        p2 = parse_line("0 tsp salt")
        self.assertEqual(p2["status"], "UNQUANTIFIED")
        self.assertIsNone(p2["qty"])

        p3 = parse_line("-2 tsp sugar")
        self.assertEqual(p3["status"], "UNQUANTIFIED")
        self.assertIsNone(p3["qty"])

    def test_v2_r18_curd_line_and_compound_foods(self):
        # Defect 1: V2-R18 Chicken Korma curd line must NEVER be classified as WATER
        curd_line = "2 teaspoon Curd (Dahi / Yogurt) beaten with a little water"
        p_curd = parse_line(curd_line)
        self.assertEqual(p_curd["status"], "QUANTIFIED")
        self.assertTrue(close(p_curd["qty"], 2.0))
        self.assertEqual(p_curd["unit"], "tsp")
        self.assertIn("curd", p_curd["name"])

        # Food mixed with water
        p_corn = parse_line("1 tbsp cornflour mixed in water")
        self.assertEqual(p_corn["status"], "QUANTIFIED")
        self.assertEqual(p_corn["unit"], "tbsp")
        self.assertIn("cornflour", p_corn["name"])

        # Compound foods containing water/ice words must NOT be classified as WATER
        compounds = [
            ("pani puri", "pani puri"),
            ("water chestnut", "water chestnut"),
            ("water spinach", "water spinach"),
            ("water melon", "water melon"),
            ("ice gola", "ice gola"),
            ("ice pop", "ice pop"),
        ]
        for line, expected_name in compounds:
            p = parse_line(line)
            self.assertEqual(p["status"], "UNQUANTIFIED", f"Expected UNQUANTIFIED for {line}, got {p['status']}")
            self.assertEqual(p["name"], expected_name)

        # Quantified compound foods
        p_wc = parse_line("100 g water chestnuts")
        self.assertEqual(p_wc["status"], "QUANTIFIED")
        self.assertEqual(p_wc["unit"], "g")
        self.assertTrue(close(p_wc["qty"], 100.0))
        self.assertIn("water chestnuts", p_wc["name"])

    def test_hindi_decomposed_nukta(self):
        # Defect 2: Hindi keyboards emit decomposed nukta U+0921 + U+093C
        # Decomposed nukta for tablespoon (बड़े चम्मच)
        tbsp_line = "2 ब\u0921\u093cे चम्मच तेल"
        p_tbsp = parse_line(tbsp_line)
        self.assertEqual(p_tbsp["status"], "QUANTIFIED")
        self.assertEqual(p_tbsp["unit"], "tbsp")
        self.assertTrue(close(p_tbsp["qty"], 2.0))
        self.assertEqual(p_tbsp["name"], "तेल")

        # Decomposed nukta for piece (टुकड़ा / टुकड़े)
        pc_line1 = "1 टुक\u0921\u093cा पनीर"
        p_pc1 = parse_line(pc_line1)
        self.assertEqual(p_pc1["status"], "QUANTIFIED")
        self.assertEqual(p_pc1["unit"], "piece")
        self.assertTrue(close(p_pc1["qty"], 1.0))
        self.assertEqual(p_pc1["name"], "पनीर")

        pc_line2 = "2 टुक\u0921\u093cे पनीर"
        p_pc2 = parse_line(pc_line2)
        self.assertEqual(p_pc2["status"], "QUANTIFIED")
        self.assertEqual(p_pc2["unit"], "piece")
        self.assertTrue(close(p_pc2["qty"], 2.0))

    def test_unspaced_quantities_and_leading_dot(self):
        # Defect 3: Unspaced quantities adjacent to units and leading dot decimals
        p_g = parse_line("100g flour")
        self.assertEqual(p_g["status"], "QUANTIFIED")
        self.assertTrue(close(p_g["qty"], 100.0))
        self.assertEqual(p_g["unit"], "g")
        self.assertTrue(close(p_g["stated_g"], 100.0))
        self.assertEqual(p_g["name"], "flour")

        p_ml = parse_line("250ml water")
        self.assertEqual(p_ml["status"], "WATER")
        self.assertTrue(close(p_ml["qty"], 250.0))
        self.assertEqual(p_ml["unit"], "ml")
        self.assertTrue(close(p_ml["stated_ml"], 250.0))

        p_kg = parse_line("1kg mutton")
        self.assertEqual(p_kg["status"], "QUANTIFIED")
        self.assertTrue(close(p_kg["qty"], 1.0))
        self.assertEqual(p_kg["unit"], "kg")
        self.assertTrue(close(p_kg["stated_g"], 1000.0))
        self.assertEqual(p_kg["name"], "mutton")

        p_dot = parse_line(".5 cups sugar")
        self.assertEqual(p_dot["status"], "QUANTIFIED")
        self.assertTrue(close(p_dot["qty"], 0.5))
        self.assertEqual(p_dot["unit"], "cup")
        self.assertEqual(p_dot["name"], "sugar")

    def test_stray_preposition_of(self):
        # Defect 4: Strip leading preposition 'of' in name cleanup
        p1 = parse_line("1 cup of flour")
        self.assertEqual(p1["status"], "QUANTIFIED")
        self.assertTrue(close(p1["qty"], 1.0))
        self.assertEqual(p1["unit"], "cup")
        self.assertEqual(p1["name"], "flour")

        p2 = parse_line("2 tbsp of olive oil")
        self.assertEqual(p2["status"], "QUANTIFIED")
        self.assertTrue(close(p2["qty"], 2.0))
        self.assertEqual(p2["unit"], "tbsp")
        self.assertEqual(p2["name"], "olive oil")


if __name__ == "__main__":
    unittest.main()
