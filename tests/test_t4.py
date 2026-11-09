"""Unit tests for T4: ingredient name matcher and alias table (lhf.match)."""

import unittest
from lhf.match import match_name


class TestT4Match(unittest.TestCase):
    def test_keys_and_types(self):
        m = match_name("maida")
        self.assertEqual(set(m.keys()), {"code", "method", "score"})
        self.assertEqual(m["code"], "A018")
        self.assertEqual(m["method"], "alias")
        self.assertAlmostEqual(m["score"], 1.0)

    def test_project_defaults(self):
        cases = [
            ("maida", "A018"),
            ("besan", "A504"),
            ("ghee", "T013"),
            ("oil", "T508"),
            ("cooking oil", "T508"),
            ("refined oil", "T508"),
            ("vegetable oil", "T508"),
            ("milk", "L901"),
            ("toned milk", "L901"),
            ("full cream milk", "L002"),
            ("curd", "L902"),
            ("dahi", "L902"),
            ("yogurt", "L902"),
            ("paneer", "L903"),
            ("cottage cheese", "L903"),
            ("butter", "L904"),
            ("unsalted butter", "T501"),
            ("fresh cream", "L905"),
            ("cream", "L905"),
            ("light cream", "L905"),
            ("malai", "L906"),
            ("chicken", "N500"),
            ("boneless chicken", "N500"),
            ("mustard oil", "T510"),
            ("jeera", "G025"),
            ("hing", "G019"),
            ("kasuri methi", "C020"),
            ("toor dal", "B021"),
            ("tur dal", "B021"),
        ]
        for name, expected_code in cases:
            res = match_name(name)
            self.assertEqual(res["code"], expected_code, f"{name} expected {expected_code}, got {res['code']}")

    def test_hindi_devanagari(self):
        cases = [
            ("बेसन", "A504"),
            ("मैदा", "A018"),
            ("घी", "T013"),
            ("तेल", "T508"),
            ("हल्दी", "G033"),
            ("हींग", "G019"),
            ("जीरा", "G025"),
            ("प्याज", "G017"),
            ("टमाटर", "D075"),
            ("नमक", "G528"),
        ]
        for name, expected_code in cases:
            res = match_name(name)
            self.assertEqual(res["code"], expected_code, f"{name} expected {expected_code}, got {res['code']}")

    def test_non_food(self):
        res = match_name("charcoal")
        self.assertEqual(res["code"], "NON_FOOD")
        self.assertIn(res["method"], ("alias", "exact"))
        res_phrase = match_name("charcoal for smoking")
        self.assertEqual(res_phrase["code"], "NON_FOOD")

    def test_unmapped(self):
        res = match_name("xqzv blorf")
        self.assertEqual(res["code"], "UNMAPPED")
        self.assertEqual(res["method"], "none")
        self.assertEqual(res["score"], 0.0)

    def test_alternatives_and_prep(self):
        res1 = match_name("ghee / clarified butter")
        self.assertEqual(res1["code"], "T013")
        res2 = match_name("butter or oil")
        self.assertEqual(res2["code"], "L904")
        res3 = match_name("tomatoes chopped")
        self.assertEqual(res3["code"], "D075")
        res4 = match_name("finely chopped ginger")
        self.assertEqual(res4["code"], "G014")
        res5 = match_name("onion diced")
        self.assertEqual(res5["code"], "G017")


if __name__ == "__main__":
    unittest.main()
