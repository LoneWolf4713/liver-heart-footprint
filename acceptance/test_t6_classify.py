"""T6: lhf.classify computes added sugar, refined carbohydrate, salt and fat-by-class from classes.csv."""
import csv
import os
from _common import CUR, check, close, finish

from lhf import composition  # noqa: E402
from lhf.classify import class_totals, classes_for  # noqa: E402

t = composition.load_table()
rows = list(csv.DictReader(open(os.path.join(CUR, "classes.csv"), encoding="utf-8")))
for r in rows:
    check(r["class"] in classes_for(r["code"]), f"classes_for({r['code']}) must include {r['class']}")
check(classes_for("A019") == [], "atta has no class")


def item(code, grams):
    return {"code": code, "grams": grams, "nutrients": composition.nutrients_for(code, grams)}


items = [item("I502", 20), item("I001", 10), item("A018", 100), item("A015", 50), item("G528", 6), item("T508", 15),
         item("T506", 10), item("T014", 5), item("A019", 200), item("L508", 40)]
out = class_totals(items)
for k in ("added_sugar_g", "refined_carb_g", "salt_g", "fat_by_class_g"):
    check(k in out, f"class_totals missing {k}")
fs = lambda c: float(t.loc[c, "freesugar_g"])  # noqa: E731
exp_sugar = 20 * min(fs("I502"), 100) / 100 + 10 * min(fs("I001"), 100) / 100 + 40 * min(fs("L508"), 100) / 100
check(close(out["added_sugar_g"], exp_sugar), f"added_sugar_g {out['added_sugar_g']} != {exp_sugar}")
check(close(out["added_sugar_g"] - 10 * fs("I001") / 100 - 40 * fs("L508") / 100, 20.0), "sugar (105 g/100 g in UK table) must be capped at its own mass")
exp_ref = float(t.loc["A018", "carb_g"]) + 0.5 * float(t.loc["A015", "carb_g"])
check(close(out["refined_carb_g"], exp_ref), f"refined_carb_g {out['refined_carb_g']} != {exp_ref}")
check(close(out["salt_g"], 6), "salt_g must be 6")
f = out["fat_by_class_g"]
check(close(f.get("COOKING_OIL"), 15 * float(t.loc["T508", "fat_g"]) / 100), "COOKING_OIL fat")
check(close(f.get("DAIRY_FAT"), 10 * float(t.loc["T506", "fat_g"]) / 100), "DAIRY_FAT fat")
check(close(f.get("HYDROGENATED_FAT"), 5 * float(t.loc["T014", "fat_g"]) / 100), "HYDROGENATED_FAT fat")
other = sum(i["nutrients"]["fat_g"] for i in items if i["code"] in ("I502", "I001", "A018", "A015", "G528", "A019", "L508"))
check(close(f.get("OTHER"), other), "OTHER fat")
e = class_totals([])
check(e["added_sugar_g"] == 0 and e["refined_carb_g"] == 0 and e["salt_g"] == 0, "empty input -> zeros")
finish("T6 classify")
