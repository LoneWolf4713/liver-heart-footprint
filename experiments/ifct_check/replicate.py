"""Verify the unofficial IFCT 2017 transcription (nodef/ifct2017) against INDB's own published dish values.

INDB.do (data/raw/indb/INDB.do, lines 137-270) computes each dish as:
    per-100 g nutrient = sum(amount_g * nutrient/100) / sum(amount_g)
using NIN_fct (IFCT, not released) + UK_fct + US_fct, with no retention factor and no cooking yield.
We port that procedure exactly, substitute the transcription for NIN_fct, and compare with INDB.xlsx.

Control: recipes using ONLY UK/US codes test the port itself (should match ~exactly).
Test: recipes using IFCT codes test the transcription.
Outputs: per_recipe.csv, per_code.csv, results.json (all numbers in the report come from these).
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
INDB = os.path.join(REPO, "data", "raw", "indb")
TRANSCRIPTION = os.path.join(REPO, "data", "raw", "ifct2017_transcription", "ifct2017_compositions.csv")

# INDB column <- transcription column, scale (transcription units are g/100 g, kJ/100 g)
NUTRIENTS = {
    "energy_kj": ("enerc", 1.0),
    "fat_g": ("fatce", 1.0),
    "protein_g": ("protcnt", 1.0),
    "carb_g": ("choavldf", 1.0),
    "fibre_g": ("fibtg", 1.0),
    "sfa_mg": ("fasat", 1000.0),
    "sodium_mg": ("na", 1000.0),
    "freesugar_g": ("fsugar", 1.0),
}


def to_grams(r):
    """Exact port of INDB.do lines 166-210, in the same order (later rules overwrite earlier ones)."""
    a, u, c, name = r["amount"], r["unit"], str(r["food_code"])[:1], str(r["food_name"])
    g = np.nan
    rules = [
        (u == "g", a),
        (u == "tsp" and c in "GHBU", a * 2),
        (u == "tbsp" and c in "DGHBU", a * 7),
        (u == "tsp" and c == "D", a * 2),
        (u == "tbsp" and c == "F", a * 40),
        (u == "ml" and c in "GHIVX", a * 1),
        (u == "tsp" and c == "A", a * 2.5),
        (u == "tsp" and c == "M", a * 5),
        (u == "tbsp" and c == "A", a * 7),
        (u == "tsp" and c == "V", a * 2),
        (u == "tsp" and c == "T", a * 4),
        (u == "tbsp" and c == "T", a * 13.5),
        (u == "tsp" and c in "XW", a * 6),
        (u == "tbsp" and c in "XW", a * 20),
        (u == "tsp" and c == "I", a * 4),
        (u == "tbsp" and c == "I", a * 12),
        (u == "C" and c == "I", a * 200),
        (u == "tbsp" and c == "Z", a * 15),
        (u == "tsp" and c == "L", a * 5),
        (u == "tbsp" and c == "L", a * 15),
        (u == "C" and c == "L", a * 240),
        (u == "ml" and c == "L", a * 1),
        (u == "sprig" and c in "GUCA", a * 2),
        (u == "tsp" and c == "C", a * 0.5),
        (u == "tbsp" and c == "C", a * 5),
        (u == "tsp" and c == "T", a * 4),
        (u == "ml" and c == "T", a * 1),
        (u == "C", a * 240),
        (u == "ml" and c == "K", a * 1),
        (u == "ml" and c == "E", a * 1),
        (u == "tsp" and c in "KE", a * 5),
        (u == "tsp" and c == "E", a * 5),
        (u == "tbsp" and c in "KE", a * 15),
        (u == "tbsp" and c == "E", a * 15),
        (u == "tbsp" and c == "V", a * 8),
        (u == "C" and c == "L", a * 240),
        (u == "small" and c == "G", a * 2),
        (name == "FENUGREEK LEAVES", a * 2),
        (u == "pinch", 0.125),
    ]
    for cond, val in rules:
        if cond:
            g = val
    return g


def load_fct():
    cols = list(NUTRIENTS)
    uk = pd.read_excel(os.path.join(INDB, "UK_fct.xlsx"))
    us = pd.read_excel(os.path.join(INDB, "US_fct.xlsx"))
    frames = []
    for df, src in ((uk, "UK"), (us, "US")):
        df = df[df.food_code.notna()].copy()
        for k in cols:
            df[k] = pd.to_numeric(df[k], errors="coerce").fillna(0.0)  # INDB.do: N/Tr/NA/"" -> 0
        df["fct"] = src
        frames.append(df[["food_code", "fct"] + cols])
    t = pd.read_csv(TRANSCRIPTION)
    nin = pd.DataFrame({"food_code": t["code"], "fct": "IFCT_transcription"})
    for k, (src, scale) in NUTRIENTS.items():
        nin[k] = pd.to_numeric(t[src], errors="coerce").fillna(0.0) * scale
    fct = pd.concat(frames + [nin], ignore_index=True)
    dup = fct[fct.food_code.duplicated(keep=False)]
    return fct.drop_duplicates("food_code", keep="first"), sorted(dup.food_code.unique())


def main():
    rec = pd.read_excel(os.path.join(INDB, "recipes.xlsx"))
    rec = rec[rec.recipe_code.notna()].copy()
    n_lines_all = len(rec)
    rec = rec[rec.food_code.notna()].copy()  # INDB.do drops ingredients without food codes
    rec["amount_g"] = rec.apply(to_grams, axis=1)
    fct, dup_codes = load_fct()
    m = rec.merge(fct, on="food_code", how="left")
    m["fct"] = m["fct"].fillna("MISSING")
    for k in NUTRIENTS:
        m["r_" + k] = (m["amount_g"] * m[k] / 100).fillna(0.0)

    published = pd.read_excel(os.path.join(INDB, "INDB.xlsx")).set_index("food_code")
    rows = []
    for code, g in m.groupby("recipe_code"):
        mass = g["amount_g"].fillna(0).sum()
        ifct_mass = g.loc[g.fct == "IFCT_transcription", "amount_g"].fillna(0).sum()
        row = {
            "recipe_code": code,
            "n_lines": len(g),
            "uses_ifct": bool((g.fct == "IFCT_transcription").any()),
            "missing_codes": int((g.fct == "MISSING").sum()),
            "ifct_mass_share": round(ifct_mass / mass, 3) if mass else np.nan,
        }
        for k in NUTRIENTS:
            ours = g["r_" + k].sum() / (mass / 100) if mass else np.nan
            pub = published.loc[code, k] if code in published.index else np.nan
            row[k + "_ours"], row[k + "_pub"] = ours, pub
        rows.append(row)
    pr = pd.DataFrame(rows)
    pr.to_csv(os.path.join(HERE, "per_recipe.csv"), index=False)

    def agree(df, k, tol):
        o, p = df[k + "_ours"], df[k + "_pub"]
        ok = (o - p).abs() <= np.maximum(tol, 0.02 * p.abs())  # within 2% or absolute tolerance
        return int(ok.sum()), int(ok.notna().sum() and len(df))

    tol = {"energy_kj": 1, "fat_g": 0.05, "protein_g": 0.05, "carb_g": 0.05, "fibre_g": 0.05,
           "sfa_mg": 50, "sodium_mg": 2, "freesugar_g": 0.05}
    clean = pr[pr.missing_codes == 0]
    groups = {"control_UK_US_only": clean[~clean.uses_ifct], "test_uses_IFCT": clean[clean.uses_ifct]}
    res = {"inputs": {"recipe_lines_total": n_lines_all, "lines_with_food_code": len(rec),
                      "lines_without_grams": int(rec.amount_g.isna().sum()),
                      "recipes": len(pr), "recipes_with_missing_codes": int((pr.missing_codes > 0).sum()),
                      "codes_in_more_than_one_fct": dup_codes,
                      "transcription_commit": open(os.path.join(REPO, "data", "raw", "ifct2017_transcription", "commit.txt")).read().split()[0]},
           "agreement_within_2pct_or_abs_tol": {}, "tolerance_abs": tol}
    for name, df in groups.items():
        res["agreement_within_2pct_or_abs_tol"][name] = {
            k: {"agree": agree(df, k, tol[k])[0], "of": len(df)} for k in NUTRIENTS}

    # Per IFCT code: median relative fat/energy error over test recipes that contain it
    test = groups["test_uses_IFCT"].set_index("recipe_code")
    codes = []
    for code, g in m[m.fct == "IFCT_transcription"].groupby("food_code"):
        rs = [r for r in g.recipe_code.unique() if r in test.index]
        if not rs:
            continue
        sub = test.loc[rs]
        ent = {"food_code": code, "n_recipes": len(rs)}
        for k in ("energy_kj", "fat_g", "sfa_mg", "sodium_mg"):
            rel = ((sub[k + "_ours"] - sub[k + "_pub"]) / sub[k + "_pub"].replace(0, np.nan)).abs()
            ent[k + "_median_abs_rel_err"] = round(float(rel.median()), 4) if rel.notna().any() else None
        codes.append(ent)
    pc = pd.DataFrame(codes)
    pc.to_csv(os.path.join(HERE, "per_code.csv"), index=False)
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
