"""Unit tests for T9: Validation run against lab-analysed dishes."""
import json
import os
import re
import unittest

from lhf.paths import REPO
from experiments.phase1_validation.run import run_validation, self_check, generate_report


class TestT9Validation(unittest.TestCase):
    def setUp(self):
        self.val_dir = os.path.join(REPO, "experiments", "phase1_validation")
        self.results_path = os.path.join(self.val_dir, "results.json")
        self.report_path = os.path.join(self.val_dir, "REPORT.md")

    def test_run_validation_creates_valid_files(self):
        # Run validation
        run_validation()

        self.assertTrue(os.path.exists(self.results_path))
        self.assertTrue(os.path.exists(self.report_path))

        with open(self.results_path, "r", encoding="utf-8") as f:
            res = json.load(f)

        self.assertIn("pairs", res)
        self.assertIn("summary", res)
        self.assertIn("by_setting", res)
        self.assertIn("coverage", res)

        pairs = res["pairs"]
        self.assertEqual(len(pairs), 31)

        for p in pairs:
            for k in ("dish", "recipe_id", "lab_code", "setting", "recipe_M2", "lab_M2", "ratio", "lines_included", "lines_total"):
                self.assertIn(k, p)
            self.assertGreater(p["recipe_M2"], 0)
            self.assertGreater(p["lab_M2"], 0)
            self.assertGreater(p["ratio"], 0)
            self.assertGreaterEqual(p["lines_included"], 0)
            self.assertGreaterEqual(p["lines_total"], p["lines_included"])

        s = res["summary"]
        self.assertEqual(s["n_pairs"], 31)
        self.assertIn("median_ratio", s)
        self.assertIn("home", s["median_ratio_by_setting"])
        self.assertIn("retail", s["median_ratio_by_setting"])
        self.assertIn("takeaway", s["median_ratio_by_setting"])

        with open(self.report_path, "r", encoding="utf-8") as f:
            rep = f.read()

        # Sections check
        for sec in ("Summary", "Per-dish", "By setting", "Coverage", "Limitations"):
            self.assertIsNotNone(
                re.search(rf"^#+ .*{sec}", rep, re.M | re.I),
                f"Missing section {sec}"
            )

        # Prohibited words
        self.assertNotIn("conclusively", rep.lower())
        self.assertNotIn("proves", rep.lower())

        # Self-check helper
        self_check(res, rep)

    def test_self_check_flags_forbidden_words(self):
        res = {"summary": {}, "coverage": {}, "by_setting": {}, "pairs": []}
        bad_rep = "# Summary\n# Per-dish\n# By setting\n# Coverage\n# Limitations\nThis conclusively proves it."
        with self.assertRaises(AssertionError):
            self_check(res, bad_rep)

    def test_self_check_flags_missing_sections(self):
        res = {"summary": {}, "coverage": {}, "by_setting": {}, "pairs": []}
        incomplete_rep = "# Summary\n# Per-dish\n# By setting\n# Coverage\n"
        with self.assertRaises(AssertionError):
            self_check(res, incomplete_rep)
