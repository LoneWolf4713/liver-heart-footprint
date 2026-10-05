"""T7: lhf.footprint.footprint converts per-serving amounts into daily-budget bars using only baselines.csv and constants.csv."""
import os
import pandas as pd
from _common import CUR, check, close, finish

from lhf.footprint import footprint  # noqa: E402

B = pd.read_csv(os.path.join(CUR, "baselines.csv")).set_index("metric_id")["value"].astype(float)
C = pd.read_csv(os.path.join(CUR, "constants.csv")).set_index("id")["value"].astype(float)
ps = {"energy_kcal": 450.0, "fat_g": 22.0, "sfa_g": 9.0, "added_sugar_g": 12.0, "sodium_mg": 800.0, "refined_carb_g": 40.0}
for setting, ekey in (("urban", "NSO_CALORIES_URBAN"), ("rural", "NSO_CALORIES_RURAL")):
    for risk, skey in (("general", "LIMIT_SFA_GENERAL"), ("cardiometabolic", "LIMIT_SFA_CARDIOMETABOLIC")):
        out = footprint(ps, setting=setting, risk=risk)
        ax = out["axes"]
        E = B[ekey]
        exp_lim = {"energy_kcal": E, "fat_g": B["LIMIT_TOTAL_FAT_PCT"] / 100 * E / C["FAT_KCAL_PER_G"],
                   "sfa_g": B[skey] / 100 * E / C["FAT_KCAL_PER_G"], "added_sugar_g": B["LIMIT_ADDED_SUGAR_GRAMS"],
                   "sodium_mg": B["LIMIT_SALT_GRAMS"] * C["SODIUM_MG_PER_G_SALT"]}
        for k, lim in exp_lim.items():
            check(k in ax, f"axis {k} missing")
            if k not in ax:
                continue
            check(close(ax[k]["amount"], ps[k]), f"{setting}/{risk} {k} amount")
            check(close(ax[k]["limit"], lim), f"{setting}/{risk} {k} limit {ax[k]['limit']} != {lim}")
            check(close(ax[k]["pct_of_limit"], ps[k] / lim * 100), f"{setting}/{risk} {k} pct_of_limit")
            check(isinstance(ax[k]["limit_sources"], list) and ax[k]["limit_sources"], f"{k}: limit_sources must list ids")
            for sid in ax[k]["limit_sources"]:
                check(sid in B.index or sid in C.index, f"{k}: unknown source id {sid}")
        check(ekey in ax["energy_kcal"]["limit_sources"], f"energy limit must cite {ekey}")
        check(skey in ax["sfa_g"]["limit_sources"], f"sfa limit must cite {skey}")
        check(close(ax["fat_g"]["pct_energy"], ps["fat_g"] * C["FAT_KCAL_PER_G"] / E * 100), "fat pct_energy")
        check(close(ax["sfa_g"]["pct_energy"], ps["sfa_g"] * C["FAT_KCAL_PER_G"] / E * 100), "sfa pct_energy")
        check("refined_carb_g" in ax and ax["refined_carb_g"]["limit"] is None and ax["refined_carb_g"]["pct_of_limit"] is None,
              "refined_carb_g has no limit -> limit None, pct None")
        check(ax["added_sugar_g"]["pct_energy"] is None, "added sugar pct_energy must be None (no sourced kcal/g constant)")
        ctx = out.get("context", {})
        check(any(k.startswith("NSO_FAT") for k in ctx), "context must include the NSO fat intake row")
        check("INDIAB_SFA_NATIONAL" in ctx, "context must include INDIAB_SFA_NATIONAL")
z = footprint({k: 0.0 for k in ps})
check(all(v["pct_of_limit"] in (0, 0.0, None) for v in z["axes"].values()), "zero input -> zero percentages")
finish("T7 footprint")
