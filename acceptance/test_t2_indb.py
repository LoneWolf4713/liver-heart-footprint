"""T2: lhf.compute.sum_nutrients reproduces INDB's published per-100 g dish values.
INDB's own unit conversion (INDB.do lines 166-210) is done HERE, in the test; the code under test only sums."""
import math
import os
import numpy as np
import pandas as pd
from _common import RAW, check, close, finish, rate

from lhf import compute  # noqa: E402

INDB = os.path.join(RAW, "indb")


def indb_grams(a, u, food_code, food_name):
    c = str(food_code)[:1]
    g = np.nan
    rules = [(u == "g", a), (u == "tsp" and c in "GHBU", a * 2), (u == "tbsp" and c in "DGHBU", a * 7), (u == "tsp" and c == "D", a * 2),
             (u == "tbsp" and c == "F", a * 40), (u == "ml" and c in "GHIVX", a), (u == "tsp" and c == "A", a * 2.5), (u == "tsp" and c == "M", a * 5),
             (u == "tbsp" and c == "A", a * 7), (u == "tsp" and c == "V", a * 2), (u == "tsp" and c == "T", a * 4), (u == "tbsp" and c == "T", a * 13.5),
             (u == "tsp" and c in "XW", a * 6), (u == "tbsp" and c in "XW", a * 20), (u == "tsp" and c == "I", a * 4), (u == "tbsp" and c == "I", a * 12),
             (u == "C" and c == "I", a * 200), (u == "tbsp" and c == "Z", a * 15), (u == "tsp" and c == "L", a * 5), (u == "tbsp" and c == "L", a * 15),
             (u == "C" and c == "L", a * 240), (u == "ml" and c == "L", a), (u == "sprig" and c in "GUCA", a * 2), (u == "tsp" and c == "C", a * 0.5),
             (u == "tbsp" and c == "C", a * 5), (u == "tsp" and c == "T", a * 4), (u == "ml" and c == "T", a), (u == "C", a * 240),
             (u == "ml" and c == "K", a), (u == "ml" and c == "E", a), (u == "tsp" and c in "KE", a * 5), (u == "tbsp" and c in "KE", a * 15),
             (u == "tbsp" and c == "V", a * 8), (u == "small" and c == "G", a * 2), (food_name == "FENUGREEK LEAVES", a * 2), (u == "pinch", 0.125)]
    for cond, val in rules:
        if cond:
            g = val
    return None if pd.isna(g) else float(g)


rec = pd.read_excel(os.path.join(INDB, "recipes.xlsx"))
rec = rec[rec.recipe_code.notna() & rec.food_code.notna()]
pub = pd.read_excel(os.path.join(INDB, "INDB.xlsx")).set_index("food_code")
MAP = {"energy_kj": ("energy_kj", 1), "fat_g": ("fat_g", 1), "sfa_g": ("sfa_mg", 1000), "sodium_mg": ("sodium_mg", 1),
       "protein_g": ("protein_g", 1), "fibre_g": ("fibre_g", 1), "freesugar_g": ("freesugar_g", 1), "carb_g": ("carb_g", 1)}
TOL = {"energy_kj": 1, "fat_g": 0.05, "sfa_g": 0.05, "sodium_mg": 2, "protein_g": 0.05, "fibre_g": 0.05, "freesugar_g": 0.05, "carb_g": 0.05}
agree = {k: 0 for k in MAP}
n = 0
skipped_recipes = 0
for code, grp in rec.groupby("recipe_code"):
    items = [{"code": str(r.food_code), "grams": indb_grams(r.amount, r.unit, r.food_code, r.food_name)} for r in grp.itertuples()]
    out = compute.sum_nutrients(items)
    for key in ("total_g", "totals", "per_100g", "skipped"):
        check(key in out, f"sum_nutrients output missing '{key}'")
    if not all(k in out for k in ("total_g", "totals", "per_100g", "skipped")):
        break
    unknown_codes = [i for i in out["skipped"] if items[i]["grams"] is not None]
    if unknown_codes:  # recipes using codes in no table (INDB itself has 19 such recipes)
        skipped_recipes += 1
        continue
    exp_total = sum(i["grams"] for i in items if i["grams"] is not None)
    check(close(out["total_g"], exp_total, rel=1e-9), f"{code}: total_g {out['total_g']} != {exp_total}")
    n += 1
    for k, (pk, scale) in MAP.items():
        ours = out["per_100g"][k] * scale
        p = float(pub.loc[code, pk])
        if abs(ours - p) <= max(TOL[k], 0.02 * abs(p)):
            agree[k] += 1
print(f"  recipes compared: {n}; skipped (codes in no table): {skipped_recipes}")
check(skipped_recipes <= 19, f"{skipped_recipes} recipes skipped; INDB has only 19 recipes with codes in no table")
check(n >= 990, f"only {n} recipes compared (expected 995)")
for k in MAP:
    rate(f"agreement {k}", agree[k], n, 0.95 if k == "carb_g" else 0.995)

# linearity and NaN handling
o = compute.sum_nutrients([{"code": "A019", "grams": 100}, {"code": "T508", "grams": 10}, {"code": "A019", "grams": None}])
check(o["skipped"] == [2], "items with grams None must be listed in 'skipped'")
check(close(o["total_g"], 110), "total_g wrong")
check(math.isnan(o["totals"]["water_g"]) and 1 in o.get("unknown_water_items", []), "water unknown for UK code T508 -> total NaN and listed")
finish("T2 INDB reproduction")
