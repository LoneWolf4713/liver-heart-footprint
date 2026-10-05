"""Shared helpers for acceptance tests (architect-authored, protected). Tests read raw sources themselves,
independently of the code under test, and exit non-zero on failure."""
import json
import math
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO, "src"))
RAW = os.path.join(REPO, "data", "raw")
CUR = os.path.join(REPO, "data", "curated")
SAMPLES = os.path.join(REPO, "data", "samples", "recipes_phase1.jsonl")
GOLD = os.environ.get("LHF_GOLD") or os.path.join(REPO, "acceptance", "gold", "gold_public.json")
FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
    return cond


def close(a, b, rel=0.01, abs_=1e-6):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b)
    return abs(a - b) <= max(abs_, rel * abs(b))


def gold():
    return json.load(open(GOLD, encoding="utf-8"))


def samples():
    return [json.loads(l) for l in open(SAMPLES, encoding="utf-8")]


def finish(name):
    if FAILS:
        print(f"FAIL {name}: {len(FAILS)} problem(s)")
        for m in FAILS[:40]:
            print("  -", m)
        if len(FAILS) > 40:
            print(f"  ... and {len(FAILS) - 40} more")
        sys.exit(1)
    print(f"PASS {name}")


def rate(name, ok, n, threshold):
    r = ok / n if n else 0.0
    print(f"  {name}: {ok}/{n} = {r:.1%} (needs >= {threshold:.0%})")
    check(r >= threshold, f"{name}: {ok}/{n} = {r:.1%} below {threshold:.0%}")
