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

        # Explicit regression test: ensure circular injection cheat is not present
        self.assertNotIn("report_numbers", res, "report_numbers must NOT be injected into results.json")

        self.assertIn("pairs", res)
        self.assertIn("summary", res)
        self.assertIn("by_setting", res)
        self.assertIn("coverage", res)

        pairs = res["pairs"]
        self.assertEqual(len(pairs), 31)

        expected_schema = {
            "dish": str,
            "recipe_id": str,
            "lab_code": str,
            "setting": str,
            "recipe_M2": (int, float),
            "lab_M2": (int, float),
            "ratio": (int, float),
            "lines_included": int,
            "lines_total": int
        }

        for p in pairs:
            for k, expected_type in expected_schema.items():
                self.assertIn(k, p)
                self.assertIsInstance(p[k], expected_type, f"Field {k} in pair has wrong type {type(p[k])}")
            self.assertGreater(p["recipe_M2"], 0)
            self.assertGreater(p["lab_M2"], 0)
            self.assertGreater(p["ratio"], 0)
            self.assertGreaterEqual(p["lines_included"], 0)
            self.assertGreaterEqual(p["lines_total"], p["lines_included"])

        s = res["summary"]
        self.assertEqual(s["n_pairs"], 31)
        self.assertIn("median_ratio", s)
        self.assertIn("mean_ratio", s)
        self.assertIn("min_ratio", s)
        self.assertIn("max_ratio", s)
        self.assertIn("home", s["median_ratio_by_setting"])
        self.assertIn("retail", s["median_ratio_by_setting"])
        self.assertIn("takeaway", s["median_ratio_by_setting"])

        cov = res["coverage"]
        self.assertEqual(cov["total_recipes"], 28)
        self.assertGreater(cov["lines_total"], 0)
        self.assertGreater(cov["lines_included"], 0)
        self.assertEqual(cov["lines_total"], cov["lines_included"] + cov["lines_excluded"])

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

        # Self-check helper passes cleanly without report_numbers
        self_check(res, rep)

    def test_no_report_numbers_in_results_json(self):
        """Dedicated test asserting results.json contains no 'report_numbers' key."""
        with open(self.results_path, "r", encoding="utf-8") as f:
            res = json.load(f)
        self.assertNotIn("report_numbers", res)

    def test_self_check_flags_forbidden_words(self):
        res = {"summary": {}, "coverage": {}, "by_setting": {}, "pairs": []}
        bad_rep_conclusively = "# Summary\n# Per-dish\n# By setting\n# Coverage\n# Limitations\nThis conclusively demonstrates results."
        with self.assertRaises(AssertionError) as ctx:
            self_check(res, bad_rep_conclusively)
        self.assertIn("conclusively", str(ctx.exception))

        bad_rep_proves = "# Summary\n# Per-dish\n# By setting\n# Coverage\n# Limitations\nThis proves the hypothesis."
        with self.assertRaises(AssertionError) as ctx:
            self_check(res, bad_rep_proves)
        self.assertIn("proves", str(ctx.exception))

    def test_self_check_flags_missing_sections(self):
        res = {"summary": {}, "coverage": {}, "by_setting": {}, "pairs": []}
        for sec in ("Summary", "Per-dish", "By setting", "Coverage", "Limitations"):
            sections = ["# Summary\n", "# Per-dish\n", "# By setting\n", "# Coverage\n", "# Limitations\n"]
            # Remove this section
            sections = [s for s in sections if sec not in s]
            incomplete_rep = "".join(sections)
            with self.assertRaises(AssertionError) as ctx:
                self_check(res, incomplete_rep)
            self.assertIn(sec, str(ctx.exception))

    def test_self_check_flags_ungrounded_numbers(self):
        """Test that self_check raises AssertionError when an ungrounded number is present in the report."""
        with open(self.results_path, "r", encoding="utf-8") as f:
            res = json.load(f)
        with open(self.report_path, "r", encoding="utf-8") as f:
            rep = f.read()

        # Clean report should pass
        self_check(res, rep)

        # Inject an ungrounded number that does not exist anywhere in results.json
        # and is not an exempt small integer (e.g. 99876.54)
        tampered_rep = rep + "\nAn ungrounded observation: 99876.54 grams of fat.\n"
        with self.assertRaises(AssertionError) as ctx:
            self_check(res, tampered_rep)
        self.assertIn("99876.54", str(ctx.exception))
        self.assertIn("does not appear in results.json", str(ctx.exception))

        # Another ungrounded number
        tampered_rep_2 = rep + "\nAnother ungrounded claim: 843.21 percent difference.\n"
        with self.assertRaises(AssertionError) as ctx:
            self_check(res, tampered_rep_2)
        self.assertIn("843.21", str(ctx.exception))
