"""Unit tests for T1: paths, constants, and composition."""
import unittest
import os
import math
from lhf import paths, constants, composition


class TestT1(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(os.path.isdir(paths.REPO))
        self.assertTrue(os.path.isdir(paths.DATA_RAW))
        self.assertTrue(os.path.isdir(paths.DATA_CURATED))

    def test_constants(self):
        self.assertEqual(constants.get("KJ_PER_KCAL"), 4.184)
        with self.assertRaises(KeyError):
            constants.get("NON_EXISTENT_KEY")

    def test_composition(self):
        table = composition.load_table()
        self.assertEqual(len(table), 746)
        self.assertTrue(table.index.is_unique)

        # Check IFCT oil energy fix
        row_t001 = composition.get("T001")
        self.assertEqual(row_t001["energy_flag"], "FAT_ENERGY_DERIVED")
        self.assertGreater(row_t001["energy_kj"], 0)
        self.assertGreater(row_t001["energy_kcal"], 0)

        # Check nutrients_for
        n = composition.nutrients_for("T013", 12.8)
        self.assertAlmostEqual(n["fat_g"], 12.8, places=5)


if __name__ == "__main__":
    unittest.main()
