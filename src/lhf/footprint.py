"""Daily-budget footprint (SPEC §8)."""
import csv
import math
import os

from lhf import constants
from lhf.paths import DATA_CURATED

_BASELINES = None


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


def get_baseline(metric_id: str) -> float:
    """Return the baseline value for a given metric id from baselines.csv."""
    table = _load_baselines()
    if metric_id not in table:
        raise KeyError(metric_id)
    return table[metric_id]


def footprint(per_serving: dict, setting: str = "urban", risk: str = "general") -> dict:
    """Convert per-serving amounts into daily-budget bars using baselines and constants.

    per_serving: dict with keys energy_kcal, fat_g, sfa_g, added_sugar_g, sodium_mg, refined_carb_g.
    setting: 'urban' or 'rural'.
    risk: 'general' or 'cardiometabolic'.
    """
    if per_serving is None:
        return None

    setting_norm = str(setting).lower() if setting else "urban"
    is_rural = setting_norm == "rural"
    ekey = "NSO_CALORIES_RURAL" if is_rural else "NSO_CALORIES_URBAN"
    fat_context_key = "NSO_FAT_RURAL" if is_rural else "NSO_FAT_URBAN"

    risk_norm = str(risk).lower() if risk else "general"
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
        raw_val = per_serving.get(k, 0.0)
        if raw_val is None or (isinstance(raw_val, float) and math.isnan(raw_val)):
            amount = 0.0
        else:
            amount = float(raw_val)

        lim = limits[k]
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
        "setting": setting,
        "risk": risk,
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
