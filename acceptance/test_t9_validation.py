"""T9: experiments/phase1_validation produces results.json and REPORT.md by code; the test recomputes every pair
from the pipeline and the lab file. No pass mark on the ratio (an honest result is the deliverable)."""
import json
import os
import re
import statistics
import subprocess
import sys
import pandas as pd
from _common import CUR, REPO, check, close, finish, samples

from lhf.pipeline import analyse_recipe  # noqa: E402

D = os.path.join(REPO, "experiments", "phase1_validation")
env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "src"))
p = subprocess.run([sys.executable, os.path.join(D, "run.py")], capture_output=True, text=True, env=env, cwd=REPO)
check(p.returncode == 0, f"run.py exit {p.returncode}: {p.stderr[-400:]}")
res_p, rep_p = os.path.join(D, "results.json"), os.path.join(D, "REPORT.md")
if not (os.path.exists(res_p) and os.path.exists(rep_p)):
    check(False, "results.json and REPORT.md must exist"); finish("T9 validation")
res = json.load(open(res_p))
C = pd.read_csv(os.path.join(CUR, "constants.csv")).set_index("id")["value"].astype(float)
gt = pd.read_csv(os.path.join(CUR, "validation_ground_truth.csv"))
recs = {r["id"]: r for r in samples() if r["id"].startswith("V2-")}
exp = []
for rid, r in recs.items():
    out = analyse_recipe(r)
    t = out["totals"]
    if not t["energy_kcal"]:
        continue
    rm = t["fat_g"] * C["FAT_KCAL_PER_G"] / t["energy_kcal"] * 100
    for g in gt[gt.dish == r["dish"]].itertuples():
        lm = g.fat * C["FAT_KCAL_PER_G"] / g.energy_kcal * 100
        exp.append((r["dish"], rid, str(g.code), g.setting, rm, lm, rm / lm))
pairs = res.get("pairs", [])
check(len(pairs) == len(exp), f"expected {len(exp)} pairs, got {len(pairs)}")
key = {(p_["recipe_id"], str(p_["lab_code"])): p_ for p_ in pairs if "recipe_id" in p_ and "lab_code" in p_}
for dish, rid, code, setting, rm, lm, ratio in exp:
    q = key.get((rid, code))
    if not check(q is not None, f"missing pair {rid} x {code}"):
        continue
    check(close(q["recipe_M2"], rm, rel=1e-6) and close(q["lab_M2"], lm, rel=1e-6) and close(q["ratio"], ratio, rel=1e-6),
          f"pair {rid} x {code} values differ from recomputation")
    check(q.get("setting") == setting and q.get("dish") == dish, f"pair {rid} x {code} dish/setting wrong")
s = res.get("summary", {})
if exp:
    check(s.get("n_pairs") == len(exp), "summary.n_pairs wrong")
    check(close(s.get("median_ratio"), statistics.median(x[6] for x in exp), rel=1e-6), "summary.median_ratio wrong")
    for st in sorted({x[3] for x in exp}):
        check(close(s.get("median_ratio_by_setting", {}).get(st), statistics.median(x[6] for x in exp if x[3] == st), rel=1e-6),
              f"median_ratio_by_setting[{st}] wrong")
rep = open(rep_p, encoding="utf-8").read()
for sec in ("Summary", "Per-dish", "By setting", "Coverage", "Limitations"):
    check(re.search(rf"^#+ .*{sec}", rep, re.M | re.I) is not None, f"REPORT.md needs a '{sec}' section")
nums_json = set()


def walk(x):
    if isinstance(x, dict):
        [walk(v) for v in x.values()]
    elif isinstance(x, list):
        [walk(v) for v in x]
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        nums_json.add(float(x))


walk(res)
for tok in re.findall(r"(?<![\w.\-/:])\d+(?:\.\d+)?(?![\w.\-/:])", rep):
    v = float(tok)
    if v in (0, 1, 2) or (v.is_integer() and 1 <= v <= 9 and len(tok) == 1):
        continue
    dec = len(tok.split(".")[1]) if "." in tok else 0
    check(any(abs(round(n, dec) - v) < 1e-9 for n in nums_json), f"REPORT.md number {tok} does not appear in results.json")
check("conclusively" not in rep.lower() and "proves" not in rep.lower(), "REPORT.md must not say 'conclusively'/'proves'")
finish("T9 validation")
