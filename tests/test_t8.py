"""Unit tests for T8: End-to-end recipe pipeline and command line (lhf.pipeline, lhf.cli)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from lhf.pipeline import analyse_recipe
from lhf.paths import REPO


class TestT8Pipeline(unittest.TestCase):
    def test_analyse_recipe_basic(self):
        recipe = {
            "id": "TEST-01",
            "url": "http://example.com/test",
            "dish": "test dish",
            "servings": 2,
            "lines": [
                "2 tbsp oil",
                "1 cup water",
                "salt to taste",
                "1 piece charcoal",
                "1 piece unknown_xyz_ingredient",
            ],
        }
        res = analyse_recipe(recipe, setting="urban", risk="general")

        # Serialisability check
        json_str = json.dumps(res, allow_nan=False)
        self.assertTrue(len(json_str) > 0)

        # Keys check
        for k in ("recipe", "lines", "coverage", "totals", "per_serving", "footprint", "warnings"):
            self.assertIn(k, res)

        # Lines check
        lines = res["lines"]
        self.assertEqual(len(lines), 5)

        # 0: 2 tbsp oil -> included
        self.assertTrue(lines[0]["included"])
        self.assertIsNone(lines[0]["exclusion_reason"])
        self.assertGreater(lines[0]["grams"], 0)
        self.assertIsNotNone(lines[0]["nutrients"])

        # 1: 1 cup water -> WATER
        self.assertFalse(lines[1]["included"])
        self.assertEqual(lines[1]["exclusion_reason"], "WATER")
        self.assertIsNone(lines[1]["nutrients"])

        # 2: salt to taste -> UNQUANTIFIED
        self.assertFalse(lines[2]["included"])
        self.assertEqual(lines[2]["exclusion_reason"], "UNQUANTIFIED")

        # 3: charcoal -> NON_FOOD
        self.assertFalse(lines[3]["included"])
        self.assertEqual(lines[3]["exclusion_reason"], "NON_FOOD")

        # 4: unknown_xyz_ingredient -> UNMAPPED
        self.assertFalse(lines[4]["included"])
        self.assertEqual(lines[4]["exclusion_reason"], "UNMAPPED")

        # Coverage check
        cov = res["coverage"]
        self.assertEqual(cov["lines_total"], 5)
        self.assertEqual(cov["lines_included"], 1)
        self.assertEqual(sum(cov["excluded_by_reason"].values()), 4)
        self.assertAlmostEqual(cov["included_mass_g"], lines[0]["grams"])

        # Per-serving check
        self.assertIsNotNone(res["per_serving"])
        self.assertAlmostEqual(res["per_serving"]["fat_g"], res["totals"]["fat_g"] / 2.0)
        self.assertIsNotNone(res["footprint"])

    def test_servings_edge_cases(self):
        invalid_servings = [0, "0", -2, "-2", "four", None, True, False, float("nan"), float("inf"), float("-inf")]
        for s in invalid_servings:
            recipe = {
                "id": "SERV-INV",
                "dish": "invalid servings dish",
                "servings": s,
                "lines": ["2 tbsp oil"],
            }
            res = analyse_recipe(recipe)
            self.assertIsNone(res["per_serving"], f"servings={s!r} should produce per_serving=None")
            self.assertIsNone(res["footprint"], f"servings={s!r} should produce footprint=None")
            self.assertTrue(
                any(w.startswith("NO_SERVINGS") for w in res["warnings"]),
                f"servings={s!r} must emit NO_SERVINGS warning",
            )

        valid_servings = [1, 2, "2", 3.5, "4.0"]
        for s in valid_servings:
            recipe = {
                "id": "SERV-VAL",
                "dish": "valid servings dish",
                "servings": s,
                "lines": ["2 tbsp oil"],
            }
            res = analyse_recipe(recipe)
            self.assertIsNotNone(res["per_serving"], f"servings={s!r} should produce per_serving dict")
            self.assertIsNotNone(res["footprint"], f"servings={s!r} should produce footprint dict")
            self.assertFalse(
                any(w.startswith("NO_SERVINGS") for w in res["warnings"]),
                f"servings={s!r} should not emit NO_SERVINGS warning",
            )
            s_val = float(s)
            self.assertAlmostEqual(res["per_serving"]["fat_g"], res["totals"]["fat_g"] / s_val)

    def test_lines_null_and_empty(self):
        for lines_val in [None, []]:
            recipe = {
                "id": "NULL-LINES",
                "dish": "empty lines dish",
                "servings": 2,
                "lines": lines_val,
            }
            res = analyse_recipe(recipe)
            self.assertEqual(len(res["lines"]), 0)
            self.assertEqual(res["coverage"]["lines_total"], 0)
            self.assertEqual(res["coverage"]["lines_included"], 0)
            self.assertEqual(res["coverage"]["included_mass_g"], 0.0)

    def test_water_exclusion(self):
        recipe = {
            "id": "WATER-TEST",
            "dish": "water test dish",
            "servings": 2,
            "lines": ["1 cup water", "1 cup pani"],
        }
        res = analyse_recipe(recipe)
        lines = res["lines"]
        self.assertEqual(len(lines), 2)
        for l in lines:
            self.assertFalse(l["included"], f"Water line {l['raw']} must not be included")
            self.assertEqual(l["exclusion_reason"], "WATER", f"Line {l['raw']} exclusion reason must be WATER")
            self.assertIsNone(l["nutrients"], f"Water line {l['raw']} must have null nutrients")
            self.assertIsNone(l["grams"], f"Water line {l['raw']} must have null grams")

        self.assertEqual(res["coverage"]["excluded_by_reason"]["WATER"], 2)
        self.assertEqual(res["coverage"]["included_mass_g"], 0.0)

    def test_salt_warning(self):
        # salt to taste should emit SALT_UNQUANTIFIED
        recipe_salt = {
            "id": "SALT-TEST",
            "dish": "salty dish",
            "servings": 1,
            "lines": ["salt to taste"],
        }
        res_salt = analyse_recipe(recipe_salt)
        self.assertTrue(any(w.startswith("SALT_UNQUANTIFIED") for w in res_salt["warnings"]))

        # salted butter to grease should NOT emit SALT_UNQUANTIFIED
        recipe_butter = {
            "id": "BUTTER-TEST",
            "dish": "buttery dish",
            "servings": 1,
            "lines": ["salted butter to grease"],
        }
        res_butter = analyse_recipe(recipe_butter)
        self.assertFalse(any(w.startswith("SALT_UNQUANTIFIED") for w in res_butter["warnings"]))
        # But should be captured in unquantified_fat_lines
        self.assertIn("salted butter to grease", res_butter["coverage"]["unquantified_fat_lines"])

    def test_cli(self):
        recipe = {
            "id": "CLI-TEST",
            "dish": "cli dish",
            "servings": 4,
            "lines": ["2 tbsp oil"],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(recipe, f)
            f_path = f.name

        try:
            env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "src"))
            p = subprocess.run(
                [sys.executable, "-m", "lhf.cli", f_path, "--setting", "rural", "--risk", "cardiometabolic"],
                capture_output=True,
                text=True,
                env=env,
                cwd=REPO,
            )
            self.assertEqual(p.returncode, 0)
            data = json.loads(p.stdout)
            self.assertEqual(data["recipe"]["id"], "CLI-TEST")
            self.assertEqual(data["footprint"]["reference"]["setting"], "rural")
            self.assertEqual(data["footprint"]["reference"]["risk"], "cardiometabolic")

            # Non-existent file
            p_err = subprocess.run(
                [sys.executable, "-m", "lhf.cli", "/does_not_exist_file.json"],
                capture_output=True,
                text=True,
                env=env,
                cwd=REPO,
            )
            self.assertEqual(p_err.returncode, 2)
            self.assertTrue(p_err.stderr.strip())
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)


if __name__ == "__main__":
    unittest.main()
