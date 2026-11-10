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

    def test_no_servings(self):
        recipe = {
            "id": "TEST-02",
            "dish": "no servings dish",
            "servings": None,
            "lines": ["2 tbsp oil"],
        }
        res = analyse_recipe(recipe)
        self.assertIsNone(res["per_serving"])
        self.assertIsNone(res["footprint"])
        self.assertTrue(any(w.startswith("NO_SERVINGS") for w in res["warnings"]))

    def test_salt_unquantified_warning(self):
        recipe = {
            "id": "TEST-03",
            "dish": "salty dish",
            "servings": 1,
            "lines": ["salt to taste"],
        }
        res = analyse_recipe(recipe)
        self.assertTrue(any(w.startswith("SALT_UNQUANTIFIED") for w in res["warnings"]))

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
