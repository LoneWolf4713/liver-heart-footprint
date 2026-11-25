"""Unit tests for T4: ingredient name matcher and alias table (lhf.match)."""

import csv
import os
import unittest
from lhf import composition
from lhf.match import match_name
from lhf.paths import DATA_CURATED


class TestT4Match(unittest.TestCase):
    def test_keys_and_types(self):
        m = match_name("maida")
        self.assertEqual(set(m.keys()), {"code", "method", "score"})
        self.assertEqual(m["code"], "A018")
        self.assertEqual(m["method"], "alias")
        self.assertAlmostEqual(m["score"], 1.0)

    def test_chicken_priority_rule(self):
        chicken_cases = [
            "chicken",
            "boneless chicken",
            "chicken breast",
            "chicken breasts",
            "chicken thigh",
            "chicken thighs",
            "chicken drumsticks",
            "chicken curry cut",
            "chicken keema",
            "chicken pieces",
            "murgh",
            "murgh keema",
            "murg makhani",
            "चिकन",
        ]
        for name in chicken_cases:
            res = match_name(name)
            self.assertEqual(res["code"], "N500", f"{name} expected N500, got {res['code']}")
            self.assertEqual(res["method"], "alias")
            self.assertEqual(res["score"], 1.0)

        # Non-chicken meat exclusions
        stock_cube_cases = [
            "chicken stock",
            "chicken cube",
            "chicken bouillon cube",
            "chicken masala",
            "chicken curry masala",
            "chicken egg",
            "vegan chicken",
        ]
        for name in stock_cube_cases:
            res = match_name(name)
            self.assertNotEqual(res["code"], "N500", f"{name} must not map to whole chicken N500")

    def test_generic_cooking_oil_and_deep_frying(self):
        oil_cases = [
            "oil",
            "cooking oil",
            "refined oil",
            "vegetable oil",
            "oil for deep frying",
            "oil to deep fry",
            "oil to fry",
            "oil for frying",
            "refined sunflower oil",
            "sunflower oil",
        ]
        for name in oil_cases:
            res = match_name(name)
            self.assertEqual(res["code"], "T508", f"{name} expected T508, got {res['code']}")

        # Named oils must keep their specific codes
        self.assertEqual(match_name("mustard oil")["code"], "T510")
        self.assertEqual(match_name("coconut oil")["code"], "T507")
        self.assertEqual(match_name("sesame oil")["code"], "T509")

        # Non-oil frying foods must not be hijacked to T508
        frying_food_cases = [
            ("fish for deep frying", "S006"),
            ("potatoes for frying", "F006"),
            ("onions to fry", "G017"),
        ]
        for name, exp_code in frying_food_cases:
            res = match_name(name)
            self.assertNotEqual(res["code"], "T508", f"{name} must not be hijacked to T508")
            self.assertEqual(res["code"], exp_code, f"{name} expected {exp_code}, got {res['code']}")

    def test_dairy_baselines(self):
        # Paneer / Cottage Cheese -> L903
        paneer_cases = [
            "paneer",
            "cottage cheese",
            "fresh paneer",
            "paneer - fresh",
            "paneer fresh",
            "malai paneer",
            "paneer cubes",
            "grated paneer",
        ]
        for name in paneer_cases:
            res = match_name(name)
            self.assertEqual(res["code"], "L903", f"{name} expected L903, got {res['code']}")

        # Curd / Dahi / Yogurt -> L902 (or L520 for greek)
        curd_cases = [
            ("curd", "L902"),
            ("dahi", "L902"),
            ("yogurt", "L902"),
            ("yoghurt", "L902"),
            ("plain yogurt", "L902"),
            ("hung curd", "L902"),
            ("hung dahi", "L902"),
            ("greek yogurt", "L520"),
        ]
        for name, exp in curd_cases:
            res = match_name(name)
            self.assertEqual(res["code"], exp, f"{name} expected {exp}, got {res['code']}")

        # Butter -> L904 (or T501 for unsalted)
        butter_cases = [
            ("butter", "L904"),
            ("salted butter", "L904"),
            ("butter softened", "L904"),
            ("makhan", "L904"),
            ("unsalted butter", "T501"),
        ]
        for name, exp in butter_cases:
            res = match_name(name)
            self.assertEqual(res["code"], exp, f"{name} expected {exp}, got {res['code']}")

        # Non-dairy butter exclusions
        for nd_butter in ["butter beans", "butter fruit", "butter paper", "butter cookies"]:
            res = match_name(nd_butter)
            self.assertNotEqual(res["code"], "L904", f"{nd_butter} must not map to dairy butter L904")

        # Ghee -> T013
        self.assertEqual(match_name("ghee")["code"], "T013")
        self.assertEqual(match_name("clarified butter")["code"], "T013")

        # Milk -> L901, whole -> L002, buffalo -> L001
        milk_cases = [
            ("milk", "L901"),
            ("toned milk", "L901"),
            ("doodh", "L901"),
            ("whole milk", "L002"),
            ("full cream milk", "L002"),
            ("cow milk", "L002"),
            ("buffalo milk", "L001"),
        ]
        for name, exp in milk_cases:
            res = match_name(name)
            self.assertEqual(res["code"], exp, f"{name} expected {exp}, got {res['code']}")

        # Non-dairy or specialized milks
        self.assertEqual(match_name("coconut milk")["code"], "H501")
        self.assertEqual(match_name("buttermilk")["code"], "L521")

        # Cream / Malai
        cream_cases = [
            ("cream", "L905"),
            ("fresh cream", "L905"),
            ("light cream", "L905"),
            ("heavy cream", "L512"),
            ("whipping cream", "L512"),
            ("heavy whipping cream", "L512"),
            ("malai", "L906"),
        ]
        for name, exp in cream_cases:
            res = match_name(name)
            self.assertEqual(res["code"], exp, f"{name} expected {exp}, got {res['code']}")

    def test_plural_stemming_and_staples(self):
        cases = [
            ("apples", "E001"),
            ("apple", "E001"),
            ("grapes", "E029"),
            ("grape", "E029"),
            ("dates", "E020"),
            ("date", "E020"),
            ("banana", "E503"),
            ("mango", "E039"),
            ("orange", "E047"),
            ("bengal gram", "B001"),
            ("black gram", "B011"),
            ("tomatoes", "D075"),
            ("tomato", "D075"),
        ]
        for name, exp in cases:
            res = match_name(name)
            self.assertEqual(res["code"], exp, f"{name} expected {exp}, got {res['code']}")

    def test_prep_and_conjunction_cleaning(self):
        cases = [
            ("potatoes boiled and diced small", "F006"),
            ("whole almonds blanched and cut lengthwise", "H001"),
            ("fennel seeds roasted and pounded coarsely", "G510"),
            ("boneless chicken cut into pieces of uniform size", "N500"),
            ("mint leaves small bunch, chopped", "G016"),
            ("ghee / clarified butter", "T013"),
            ("butter or oil", "L904"),
        ]
        for name, exp in cases:
            res = match_name(name)
            self.assertEqual(res["code"], exp, f"{name} expected {exp}, got {res['code']}")

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
            ("पनीर", "L903"),
            ("मक्खन", "L904"),
            ("दूध", "L901"),
            ("चिकन", "N500"),
        ]
        for name, expected_code in cases:
            res = match_name(name)
            self.assertEqual(res["code"], expected_code, f"{name} expected {expected_code}, got {res['code']}")

    def test_non_food(self):
        res = match_name("charcoal")
        self.assertEqual(res["code"], "NON_FOOD")
        self.assertEqual(res["method"], "alias")
        res_phrase = match_name("charcoal for smoking")
        self.assertEqual(res_phrase["code"], "NON_FOOD")

    def test_unmapped(self):
        for val in ["xqzv blorf", "", None, 123]:
            res = match_name(val)
            self.assertEqual(res["code"], "UNMAPPED")
            self.assertEqual(res["method"], "none")
            self.assertEqual(res["score"], 0.0)

    def test_aliases_csv_integrity(self):
        path = os.path.join(DATA_CURATED, "aliases.csv")
        self.assertTrue(os.path.exists(path))
        codes = set(composition.load_table().index) | {"UNMAPPED", "NON_FOOD"}
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertGreater(len(rows), 4000)
        for r in rows:
            alias = r["alias"]
            code = r["code"]
            self.assertNotIn("/", alias, f"Slash found in alias row: {r}")
            self.assertLessEqual(len(alias), 40, f"Alias exceeds 40 chars: {alias}")
            self.assertFalse(any(ch.isdigit() for ch in alias), f"Alias has digits: {alias}")
            self.assertIn(code, codes, f"Unknown code in alias: {code}")

    def test_audit_round2_remediations(self):
        # 1. Frying priority hijacking check
        res_fish = match_name("fish for deep frying")
        self.assertNotEqual(res_fish["code"], "T508")
        self.assertEqual(res_fish["code"], "S006")

        # 2. Chicken priority over-matching exclusions
        res_chk_masala = match_name("chicken masala")
        self.assertNotEqual(res_chk_masala["code"], "N500")

        # 3. Butter priority over-matching exclusions
        res_butter_beans = match_name("butter beans")
        self.assertNotEqual(res_butter_beans["code"], "L904")

        # 4. Plural & irregular stemmer
        self.assertEqual(match_name("chillies")["code"], "G516")
        self.assertEqual(match_name("curry leaf")["code"], "G010")
        self.assertEqual(match_name("curry leaves")["code"], "G010")

        # 5. Exact composition match preemption
        self.assertEqual(match_name("refined wheat flour")["code"], "A018")
        self.assertEqual(match_name("tomato puree")["code"], "X504")

        # 6. Clean aliases (bishop's weed backtick fix)
        self.assertEqual(match_name("bishop's weed")["code"], "G029")


if __name__ == "__main__":
    unittest.main()
