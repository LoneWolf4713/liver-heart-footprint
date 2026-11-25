"""Unit tests for T1: paths, constants, and composition."""
import unittest
import os
import math
from fractions import Fraction
from lhf import paths, constants, composition


class TestT1(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(os.path.isdir(paths.REPO))
        self.assertTrue(os.path.isdir(paths.DATA_RAW))
        self.assertTrue(os.path.isdir(paths.DATA_CURATED))

    def test_constants_lookup(self):
        self.assertEqual(constants.get("KJ_PER_KCAL"), 4.184)
        self.assertEqual(constants.get("FAT_KJ_PER_G"), 37.0)
        self.assertEqual(constants.get("FAT_KCAL_PER_G"), 9.0)
        self.assertEqual(constants.get("SODIUM_MG_PER_G_SALT"), 393.4)

    def test_constants_invalid_keys(self):
        with self.assertRaises(KeyError):
            constants.get("NON_EXISTENT_KEY")
        with self.assertRaises(KeyError):
            constants.get(None)
        with self.assertRaises(KeyError):
            constants.get(123)

    def test_table_structure_and_unique_codes(self):
        table = composition.load_table()
        self.assertEqual(len(table), 746)
        self.assertTrue(table.index.is_unique)
        for col in composition.COLUMNS:
            self.assertIn(col, table.columns)

    def test_table_immutability_and_cache_mutation(self):
        table1 = composition.load_table()
        orig_len = len(table1)
        orig_fat = table1.loc["T001", "fat_g"]

        # Mutate table1 in place
        table1.loc["T001", "fat_g"] = 999.0
        table1.drop(table1.index[0], inplace=True)
        self.assertEqual(len(table1), orig_len - 1)

        # Subsequent load_table() must return an uncorrupted copy
        table2 = composition.load_table()
        self.assertEqual(len(table2), orig_len)
        self.assertEqual(table2.loc["T001", "fat_g"], orig_fat)

        # get() must also use the uncorrupted internal table
        row = composition.get("T001")
        self.assertEqual(row["fat_g"], orig_fat)

    def test_oil_codes_derivation(self):
        # Explicit OIL_CODES check (T001 through T014)
        expected_oil_codes = {f"T{i:03d}" for i in range(1, 15)}
        self.assertEqual(composition.OIL_CODES, expected_oil_codes)
        self.assertEqual(len(composition.OIL_CODES), 14)

        fkj = constants.get("FAT_KJ_PER_G")
        fkc = constants.get("FAT_KCAL_PER_G")

        for code in expected_oil_codes:
            row = composition.get(code)
            self.assertEqual(row["energy_flag"], "FAT_ENERGY_DERIVED")
            self.assertEqual(row["source"], "IFCT2017")
            fat = row["fat_g"]
            self.assertAlmostEqual(row["energy_kj"], fat * fkj, places=4)
            self.assertAlmostEqual(row["energy_kcal"], fat * fkc, places=4)

    def test_non_oil_ifct_derivation(self):
        kj = constants.get("KJ_PER_KCAL")
        row = composition.get("A001")
        self.assertEqual(row["energy_flag"], "")
        self.assertEqual(row["source"], "IFCT2017")
        self.assertAlmostEqual(row["energy_kcal"], row["energy_kj"] / kj, places=4)

    def test_indb_datasets_uk_us(self):
        table = composition.load_table()
        uk_df = table[table["source"] == "INDB_UK"]
        us_df = table[table["source"] == "INDB_US"]

        self.assertEqual(len(uk_df), 144)
        self.assertEqual(len(us_df), 54)

        # water_g and tfa_g must be NaN for all INDB entries
        self.assertTrue(uk_df["water_g"].isna().all())
        self.assertTrue(uk_df["tfa_g"].isna().all())
        self.assertTrue(us_df["water_g"].isna().all())
        self.assertTrue(us_df["tfa_g"].isna().all())

        # energy_flag must be empty string
        self.assertTrue((uk_df["energy_flag"] == "").all())
        self.assertTrue((us_df["energy_flag"] == "").all())

        # SFA/MUFA/PUFA scaled from mg to g (values should be small floats, not thousands)
        for code in ["G509", "G536"]:
            row = composition.get(code)
            self.assertLess(row["sfa_g"], 100.0)
            self.assertLess(row["mufa_g"], 100.0)
            self.assertLess(row["pufa_g"], 100.0)

    def test_in_label_products(self):
        label_codes = ["L901", "L902", "L903", "L904"]
        derived_codes = ["L905", "L906"]

        for code in label_codes:
            row = composition.get(code)
            self.assertEqual(row["source"], "IN_LABEL")
            self.assertEqual(row["energy_flag"], "LABEL")
            self.assertEqual(row["tfa_g"], 0.0)
            self.assertTrue(math.isnan(row["water_g"]))

        for code in derived_codes:
            row = composition.get(code)
            self.assertEqual(row["source"], "IN_LABEL")
            self.assertEqual(row["energy_flag"], "DERIVED_ENERGY")
            self.assertTrue(math.isnan(row["tfa_g"]))

        # L906 has measured water_g = 49.6
        row_l906 = composition.get("L906")
        self.assertAlmostEqual(row_l906["water_g"], 49.6, places=2)

    def test_composition_get(self):
        row = composition.get("A019")
        self.assertEqual(row["code"], "A019")
        self.assertAlmostEqual(row["fat_g"], 1.53, places=2)

        # Mutating dictionary from get() must not affect subsequent get() calls
        row["fat_g"] = 999.0
        row2 = composition.get("A019")
        self.assertAlmostEqual(row2["fat_g"], 1.53, places=2)

        # Invalid codes
        with self.assertRaises(KeyError):
            composition.get("ZZZ999")
        with self.assertRaises(KeyError):
            composition.get(None)

    def test_nutrients_for(self):
        # Standard positive float scaling
        fkc = constants.get("FAT_KCAL_PER_G")
        n = composition.nutrients_for("T013", 12.8)
        self.assertAlmostEqual(n["fat_g"], 12.8, places=5)
        self.assertAlmostEqual(n["energy_kcal"], 12.8 * fkc, places=5)

        # Linear scaling check
        table = composition.load_table()
        n2 = composition.nutrients_for("L002", 250)
        self.assertAlmostEqual(n2["sodium_mg"], float(table.loc["L002", "sodium_mg"]) * 2.5, places=5)

        # Fraction scaling
        n_half = composition.nutrients_for("T013", Fraction(1, 2))
        self.assertAlmostEqual(n_half["fat_g"], 0.5, places=5)

        # Zero grams scaling: all numeric nutrients are 0.0, NaN stays NaN
        n_zero = composition.nutrients_for("G509", 0)
        self.assertEqual(n_zero["fat_g"], 0.0)
        self.assertEqual(n_zero["protein_g"], 0.0)
        self.assertTrue(math.isnan(n_zero["water_g"]))
        self.assertTrue(math.isnan(n_zero["tfa_g"]))

        # Defensive error handling
        with self.assertRaises(ValueError):
            composition.nutrients_for("T013", None)
        with self.assertRaises(ValueError):
            composition.nutrients_for("T013", "not_a_number")
        with self.assertRaises(KeyError):
            composition.nutrients_for("NON_EXISTENT", 50.0)


if __name__ == "__main__":
    unittest.main()
