import csv
import math
import os

from lhf import constants
from lhf.paths import DATA_CURATED

_BASELINES = None

ALLOWED_SETTINGS = {"urban", "rural"}
ALLOWED_RISKS = {"general", "cardiometabolic"}


# load daily limits and baseline stats from csv once
def _load_baselines():
    global _BASELINES
    if _BASELINES is None:
        path = os.path.join(DATA_CURATED, "baselines.csv")
        baselines = {}
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metric_id = row["metric_id"].strip()
                baselines[metric_id] = float(row["value"])
        _BASELINES = baselines
    return _BASELINES


def get_baseline(metric_id):
    table = _load_baselines()
    if metric_id not in table:
        raise KeyError(metric_id)
    return table[metric_id]


# turn per-serving amounts into daily budget percentages
def footprint(per_serving, setting="urban", risk="general"):
    if not isinstance(setting, str) or setting.strip().lower() not in ALLOWED_SETTINGS:
        raise ValueError(f"Invalid setting {setting!r}. Must be one of {ALLOWED_SETTINGS}")
    setting_norm = setting.strip().lower()

    if not isinstance(risk, str) or risk.strip().lower() not in ALLOWED_RISKS:
        raise ValueError(f"Invalid risk {risk!r}. Must be one of {ALLOWED_RISKS}")
    risk_norm = risk.strip().lower()

    if per_serving is None:
        return None

    is_rural = setting_norm == "rural"
    ekey = "NSO_CALORIES_RURAL" if is_rural else "NSO_CALORIES_URBAN"
    fat_context_key = "NSO_FAT_RURAL" if is_rural else "NSO_FAT_URBAN"

    is_cardiometabolic = risk_norm == "cardiometabolic"
    skey = "LIMIT_SFA_CARDIOMETABOLIC" if is_cardiometabolic else "LIMIT_SFA_GENERAL"

    e_energy = get_baseline(ekey)
    fat_kcal_factor = constants.get("FAT_KCAL_PER_G")
    sodium_salt_factor = constants.get("SODIUM_MG_PER_G_SALT")

    limits = {
        "energy_kcal": e_energy,
        "fat_g": get_baseline("LIMIT_TOTAL_FAT_PCT") / 100 * e_energy / fat_kcal_factor,
        "sfa_g": get_baseline(skey) / 100 * e_energy / fat_kcal_factor,
        "added_sugar_g": get_baseline("LIMIT_ADDED_SUGAR_GRAMS"),
        "sodium_mg": get_baseline("LIMIT_SALT_GRAMS") * sodium_salt_factor,
        "refined_carb_g": None,
    }

    limit_sources = {
        "energy_kcal": [ekey],
        "fat_g": ["LIMIT_TOTAL_FAT_PCT", ekey, "FAT_KCAL_PER_G"],
        "sfa_g": [skey, ekey, "FAT_KCAL_PER_G"],
        "added_sugar_g": ["LIMIT_ADDED_SUGAR_GRAMS"],
        "sodium_mg": ["LIMIT_SALT_GRAMS", "SODIUM_MG_PER_G_SALT"],
        "refined_carb_g": [],
    }

    units = {
        "energy_kcal": "kcal",
        "fat_g": "g",
        "sfa_g": "g",
        "added_sugar_g": "g",
        "sodium_mg": "mg",
        "refined_carb_g": "g",
    }

    axes_keys = [
        "energy_kcal",
        "fat_g",
        "sfa_g",
        "added_sugar_g",
        "sodium_mg",
        "refined_carb_g",
    ]

    axes = {}
    for k in axes_keys:
        raw_val = per_serving.get(k)
        if raw_val is None:
            amount = None
        else:
            try:
                val = float(raw_val)
                if math.isnan(val):
                    amount = None
                else:
                    amount = val
            except (ValueError, TypeError):
                amount = None

        lim = limits[k]

        if amount is None:
            pct_of_limit = None
            pct_energy = None
        else:
            if lim is not None and lim > 0:
                pct_of_limit = amount / lim * 100
            else:
                pct_of_limit = None

            if k in ("fat_g", "sfa_g"):
                if e_energy > 0:
                    pct_energy = amount * fat_kcal_factor / e_energy * 100
                else:
                    pct_energy = None
            else:
                pct_energy = None

        axes[k] = {
            "amount": amount,
            "unit": units[k],
            "limit": lim,
            "pct_of_limit": pct_of_limit,
            "pct_energy": pct_energy,
            "limit_sources": limit_sources[k],
        }

    reference = {
        "setting": setting_norm,
        "risk": risk_norm,
        "energy_kcal": e_energy,
        "energy_metric": ekey,
    }

    context = {
        fat_context_key: get_baseline(fat_context_key),
        "INDIAB_SFA_NATIONAL": get_baseline("INDIAB_SFA_NATIONAL"),
    }

    return {
        "axes": axes,
        "reference": reference,
        "context": context,
    }
