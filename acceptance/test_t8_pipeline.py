"""T8: lhf.pipeline.analyse_recipe on all 71 real sample recipes: structure, reconciliation, exclusions, sanity; plus the CLI."""
import json
import math
import os
import subprocess
import sys
import tempfile
from _common import REPO, check, close, finish, samples

from lhf import composition  # noqa: E402
from lhf.pipeline import analyse_recipe  # noqa: E402

codes = set(composition.load_table().index)
import csv  # noqa: E402
SPICE = {r["code"] for r in csv.DictReader(open(os.path.join(REPO, "data", "curated", "classes.csv"), encoding="utf-8")) if r["class"] == "SPICE"}
NUTS = ["energy_kj", "energy_kcal", "fat_g", "sfa_g", "mufa_g", "pufa_g", "carb_g", "freesugar_g", "fibre_g", "protein_g", "sodium_mg"]
REASONS = {"WATER", "UNQUANTIFIED", "UNMAPPED", "NON_FOOD", "UNQUANTIFIABLE"}
recs = samples()
plausible = 0
for r in recs:
    out = analyse_recipe(r)
    json.dumps(out, allow_nan=False)  # must be serialisable without NaN
    for k in ("recipe", "lines", "coverage", "totals", "per_serving", "footprint", "warnings"):
        check(k in out, f"{r['id']}: missing key {k}")
    L = out["lines"]
    check(len(L) == len(r["lines"]), f"{r['id']}: {len(L)} output lines for {len(r['lines'])} input lines")
    check([l["raw"] for l in L] == r["lines"], f"{r['id']}: lines must keep input order and text")
    inc = [l for l in L if l["included"]]
    for l in L:
        if l["included"]:
            check(l["exclusion_reason"] is None, f"{r['id']}: included line has a reason")
            check(l["match"]["code"] in codes, f"{r['id']}: included line code {l['match']['code']} not in table")
            check(l["grams"] is not None and l["grams"] > 0 and l["grams_basis"], f"{r['id']}: included line needs grams and basis")
        else:
            check(l["exclusion_reason"] in REASONS, f"{r['id']}: bad exclusion reason {l['exclusion_reason']!r}")
    for n in NUTS:
        s = sum((l["nutrients"][n] or 0.0) for l in inc)
        check(close(out["totals"][n], s, rel=1e-9, abs_=1e-9), f"{r['id']}: totals[{n}] {out['totals'][n]} != sum of lines {s}")
    cov = out["coverage"]
    check(cov["lines_total"] == len(L) and cov["lines_included"] == len(inc), f"{r['id']}: coverage counts wrong")
    check(sum(cov["excluded_by_reason"].values()) == len(L) - len(inc), f"{r['id']}: exclusions do not reconcile")
    mass = sum(l["grams"] for l in inc)
    check(close(cov["included_mass_g"], mass, rel=1e-9), f"{r['id']}: included_mass_g wrong")
    if r["servings"]:
        check(out["per_serving"] is not None and out["footprint"] is not None, f"{r['id']}: servings given -> per_serving and footprint")
        if out["per_serving"]:
            check(close(out["per_serving"]["fat_g"], out["totals"]["fat_g"] / r["servings"], rel=1e-9), f"{r['id']}: per_serving = totals / servings")
    else:
        check(out["per_serving"] is None and any(w.startswith("NO_SERVINGS") for w in out["warnings"]), f"{r['id']}: no servings -> None + warning")
    for l in inc:
        c = l["match"]["code"]
        spice = c in SPICE
        if spice and l["grams"] > 30:
            check(any(w.startswith("SPICE_OVER_LIMIT") for w in out["warnings"]), f"{r['id']}: spice line {l['raw'][:40]!r} {l['grams']} g needs SPICE_OVER_LIMIT warning")
    if 200 <= mass <= 5000:
        plausible += 1
    else:
        check(any(w.startswith("MASS_IMPLAUSIBLE") for w in out["warnings"]), f"{r['id']}: mass {mass:.0f} g needs MASS_IMPLAUSIBLE warning")
print(f"  recipes: {len(recs)}; included mass within 200-5000 g: {plausible}")
check(plausible >= 0.85 * len(recs), f"only {plausible}/{len(recs)} recipes have plausible included mass (needs 85%)")

# CLI
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(recs[0], f)
env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "src"))
p = subprocess.run([sys.executable, "-m", "lhf.cli", f.name, "--setting", "rural"], capture_output=True, text=True, env=env, cwd=REPO)
check(p.returncode == 0, f"CLI exit {p.returncode}: {p.stderr[-300:]}")
if p.returncode == 0:
    o = json.loads(p.stdout)
    check(o["recipe"]["id"] == recs[0]["id"], "CLI output must be the analysis JSON")
p = subprocess.run([sys.executable, "-m", "lhf.cli", "/nonexistent.json"], capture_output=True, text=True, env=env, cwd=REPO)
check(p.returncode == 2 and p.stderr.strip(), "CLI must exit 2 with a message for an unreadable file")
finish("T8 pipeline")
