"""T5: lhf.grams.grams_for follows the measures policy (docs/SPEC.md section 6).
Part A: every row of measures.csv is reachable and returns its own value.
Part B: hand-labelled gold lines (gold parse + gold code -> expected grams, basis, flags).
Part C: policy edge cases."""
import csv
import os
from _common import CUR, check, close, finish, gold, rate

from lhf.grams import grams_for  # noqa: E402

rows = list(csv.DictReader(open(os.path.join(CUR, "measures.csv"), encoding="utf-8")))
seen = 0
for r in rows:
    g = float(r["grams"])
    if r["match_type"] == "code":
        for code in r["match"].split(";"):
            size = r["size"] or None
            if r["unit"] == "ml":
                out = grams_for(None, None, None, None, 100, code)
                check(close(out["grams"], 100 * g), f"density row {code} ml: got {out['grams']}, expected {100 * g}")
            else:
                out = grams_for(2, r["unit"], size, None, None, code)
                check(close(out["grams"], 2 * g) and out["basis"] == "CODE_MEASURE",
                      f"code row {code} {r['unit']} {size}: got {out}, expected {2 * g} CODE_MEASURE")
            seen += 1
    elif r["match_type"] == "any":
        out = grams_for(3, r["unit"], None, None, None, None)
        check(close(out["grams"], 3 * g) and out["basis"] == "MASS_UNIT", f"mass unit {r['unit']}: got {out}")
print(f"  measures rows checked: {seen} code-level keys")

ok = n = 0
for gl in gold():
    if gl["status"] != "QUANTIFIED" or (gl["grams_code"] is None and gl["stated_g"] is None):
        continue
    n += 1
    unit = gl["unit"][0] if isinstance(gl["unit"], list) else gl["unit"]
    out = grams_for(gl["qty"], unit, gl["size"], gl["stated_g"], gl["stated_ml"], gl["grams_code"])
    good = close(out["grams"], gl["grams"], rel=0.01) and out["basis"] == gl["grams_basis"] and sorted(out["flags"]) == sorted(gl["grams_flags"])
    ok += good
    if not good:
        print(f"    {gl['gid']} {gl['line'][:40]!r}: got {out}, expected {gl['grams']} {gl['grams_basis']} {gl['grams_flags']}")
rate("gold grams/basis/flags exact", ok, n, 0.97)

# Part C
o = grams_for(1, "cup", None, None, None, "A504")
check(close(o["grams"], 92) and o["basis"] == "CODE_MEASURE", "1 cup besan (A504) -> 92 g CODE_MEASURE")
o = grams_for(1, "tsp", None, None, None, "G019")
check(close(o["grams"], 2) and o["basis"] == "GROUP_MEASURE", "1 tsp hing (G019) -> group G tsp 2 g")
o = grams_for(1, "pinch", None, None, None, "G019")
check(close(o["grams"], 0.5) and "PINCH_AS_QUARTER_TSP" in o["flags"], "pinch hing -> 0.25 x 2 g")
o = grams_for(1, "dash", None, None, None, "G528")
check(close(o["grams"], 0.4) and "PINCH_AS_QUARTER_TSP" not in o["flags"], "dash salt -> code row 0.4 g")
o = grams_for(2, "piece", "large", None, None, "G017")
check(close(o["grams"], 120) and "SIZE_SUBSTITUTED" in o["flags"], "2 large onions -> medium 60 g each, SIZE_SUBSTITUTED")
o = grams_for(1, "cup", None, None, None, "D056")
check(close(o["grams"], 100), "1 cup okra -> 100 g")
o = grams_for(1, "bunch", None, None, None, "G016")
check(o["grams"] is None and o["basis"] == "UNQUANTIFIABLE", "1 bunch mint -> UNQUANTIFIABLE (no row; never default)")
o = grams_for(1, "cup", None, None, None, "UNMAPPED")
check(o["grams"] is None and o["basis"] == "UNQUANTIFIABLE", "unmapped code with cup -> UNQUANTIFIABLE")
o = grams_for(250, "g", None, None, None, "UNMAPPED")
check(close(o["grams"], 250) and o["basis"] == "MASS_UNIT", "250 g of anything -> 250 g")
o = grams_for(None, None, None, None, 50, None)
check(close(o["grams"], 50) and "DENSITY_ASSUMED_1" in o["flags"], "50 ml unknown food -> 50 g, DENSITY_ASSUMED_1")
o = grams_for(2, "tbsp", None, None, None, "T508")
check(close(o["grams"], 27.2), "2 tbsp sunflower oil -> 27.2 g (FDC 13.6 g/tbsp)")
o = grams_for(1, "l", None, None, None, "L002")
check(close(o["grams"], 1000) and o["basis"] == "VOLUME_UNIT", "1 l milk -> 1000 g")
o = grams_for(None, None, None, None, None, "A019")
check(o["grams"] is None and o["basis"] == "UNQUANTIFIABLE", "no qty -> UNQUANTIFIABLE")
finish("T5 grams")
