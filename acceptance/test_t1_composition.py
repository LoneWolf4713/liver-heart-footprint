"""T1: lhf.constants and lhf.composition reproduce the raw source files exactly (after the documented unit changes)."""
import math
import os
import pandas as pd
from _common import RAW, CUR, check, close, finish

from lhf import constants, composition  # noqa: E402

# constants
c = pd.read_csv(os.path.join(CUR, "constants.csv"))
for r in c.itertuples():
    check(close(constants.get(r.id), float(r.value), rel=0), f"constants.get({r.id}) != {r.value}")
try:
    constants.get("NOT_A_CONSTANT")
    check(False, "constants.get(unknown) must raise KeyError")
except KeyError:
    pass

t = composition.load_table()
COLS = ["name", "source", "energy_kj", "energy_kcal", "fat_g", "sfa_g", "mufa_g", "pufa_g", "tfa_g", "carb_g",
        "freesugar_g", "fibre_g", "protein_g", "sodium_mg", "water_g", "energy_flag"]
for col in COLS:
    check(col in t.columns, f"missing column {col}")
check(t.index.is_unique, "codes must be unique")

ifct = pd.read_csv(os.path.join(RAW, "ifct2017_transcription", "ifct2017_compositions.csv"))
uk = pd.read_excel(os.path.join(RAW, "indb", "UK_fct.xlsx"), sheet_name="Sheet1")
us = pd.read_excel(os.path.join(RAW, "indb", "US_fct.xlsx"), sheet_name="Sheet1")
uk, us = uk[uk.food_code.notna()], us[us.food_code.notna()]
KJ = float(c.set_index("id").loc["KJ_PER_KCAL", "value"])
FKJ = float(c.set_index("id").loc["FAT_KJ_PER_G", "value"])
FKC = float(c.set_index("id").loc["FAT_KCAL_PER_G", "value"])


def num(x):
    v = pd.to_numeric(x, errors="coerce")
    return 0.0 if pd.isna(v) else float(v)


def nan_or(x):
    v = pd.to_numeric(x, errors="coerce")
    return float("nan") if pd.isna(v) else float(v)


inp = pd.read_csv(os.path.join(CUR, "indian_products.csv"))
check(len(t) == len(ifct) + len(uk) + len(us) + len(inp), f"expected {len(ifct) + len(uk) + len(us) + len(inp)} rows, got {len(t)}")
for r in inp.itertuples():
    if r.code not in t.index:
        check(False, f"IN_LABEL code {r.code} missing"); continue
    row = t.loc[r.code]
    check(row["source"] == "IN_LABEL" and row["energy_flag"] == r.energy_flag, f"{r.code}: source/energy_flag wrong")
    for k in ("energy_kj", "energy_kcal", "fat_g", "sfa_g", "mufa_g", "pufa_g", "carb_g", "freesugar_g", "fibre_g", "protein_g", "sodium_mg"):
        check(close(float(row[k]), num(getattr(r, k)), rel=1e-6, abs_=1e-9), f"{r.code} {k}: got {row[k]}, expected {getattr(r, k)}")
    for k in ("tfa_g", "water_g"):
        v = nan_or(getattr(r, k))
        check((math.isnan(v) and math.isnan(row[k])) or close(float(row[k]), v, rel=1e-6, abs_=1e-9), f"{r.code} {k}: unknown must stay NaN")

bad = 0
for r in ifct.itertuples():
    if r.code not in t.index:
        check(False, f"IFCT code {r.code} missing"); continue
    row = t.loc[r.code]
    fat = num(r.fatce)
    oil = r.code.startswith("T0")
    exp = {"fat_g": fat, "sfa_g": num(r.fasat), "mufa_g": num(r.fams), "pufa_g": num(r.fapu), "carb_g": num(r.choavldf),
           "freesugar_g": num(r.fsugar), "fibre_g": num(r.fibtg), "protein_g": num(r.protcnt), "sodium_mg": num(r.na) * 1000,
           "energy_kj": fat * FKJ if oil else num(r.enerc), "energy_kcal": fat * FKC if oil else num(r.enerc) / KJ}
    for k, v in exp.items():
        if not close(float(row[k]), v, rel=1e-6, abs_=1e-9):
            bad += 1; check(False, f"{r.code} {k}: got {row[k]}, expected {v}")
    check(row["source"] == "IFCT2017", f"{r.code} source should be IFCT2017")
    check(close(float(row["water_g"]), nan_or(r.water), rel=1e-6) or (math.isnan(row["water_g"]) and math.isnan(nan_or(r.water))), f"{r.code} water_g")
    check(close(float(row["tfa_g"]), nan_or(r.fatrn), rel=1e-6) or (math.isnan(row["tfa_g"]) and math.isnan(nan_or(r.fatrn))), f"{r.code} tfa_g")
    check((row["energy_flag"] == "FAT_ENERGY_DERIVED") == oil, f"{r.code} energy_flag wrong")

for df, src in ((uk, "INDB_UK"), (us, "INDB_US")):
    for r in df.itertuples():
        if r.food_code not in t.index:
            check(False, f"{src} code {r.food_code} missing"); continue
        row = t.loc[r.food_code]
        check(row["source"] == src, f"{r.food_code} source should be {src}")
        exp = {"energy_kj": num(r.energy_kj), "energy_kcal": num(r.energy_kcal), "fat_g": num(r.fat_g), "sfa_g": num(r.sfa_mg) / 1000,
               "mufa_g": num(r.mufa_mg) / 1000, "pufa_g": num(r.pufa_mg) / 1000, "carb_g": num(r.carb_g), "freesugar_g": num(r.freesugar_g),
               "fibre_g": num(r.fibre_g), "protein_g": num(r.protein_g), "sodium_mg": num(r.sodium_mg)}
        for k, v in exp.items():
            if not close(float(row[k]), v, rel=1e-6, abs_=1e-9):
                check(False, f"{r.food_code} {k}: got {row[k]}, expected {v}")
        check(math.isnan(row["water_g"]) and math.isnan(row["tfa_g"]), f"{r.food_code}: water_g and tfa_g must be NaN (unknown)")

g = composition.get("A019")
check(g["code"] == "A019" and close(g["fat_g"], 1.53), "get('A019') wrong")
try:
    composition.get("ZZZ999"); check(False, "get(unknown) must raise KeyError")
except KeyError:
    pass
n = composition.nutrients_for("T013", 12.8)
check(close(n["fat_g"], 12.8) and close(n["energy_kcal"], 12.8 * FKC), "nutrients_for('T013', 12.8) fat/energy wrong")
n2 = composition.nutrients_for("L002", 250)
check(close(n2["sodium_mg"], float(t.loc["L002", "sodium_mg"]) * 2.5), "nutrients_for must scale linearly")
print(f"  rows: {len(t)}")
finish("T1 composition")
