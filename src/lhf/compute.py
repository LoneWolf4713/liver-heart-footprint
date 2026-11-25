"""Nutrient summing and per-100g computation."""
import math
from lhf import composition

NUTRIENTS = composition.NUTRIENT_COLUMNS


def sum_nutrients(items: list) -> dict:
    """Sum nutrients for a list of items and compute per-100g amounts.

    items: list of dicts with keys "code" and "grams".
    """
    table = composition.load_table()
    table_index = table.index

    total_g = 0.0
    totals = {k: 0.0 for k in NUTRIENTS}
    skipped = []
    unknown_tfa_items = []
    unknown_water_items = []

    if items is not None:
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                skipped.append(idx)
                continue

            code = item.get("code")
            code_str = str(code) if code is not None else ""
            grams = item.get("grams")

            if grams is None or isinstance(grams, bool):
                skipped.append(idx)
                continue

            try:
                grams_val = float(grams)
            except (ValueError, TypeError):
                skipped.append(idx)
                continue

            if math.isnan(grams_val) or not math.isfinite(grams_val) or grams_val <= 0 or code is None or code_str not in table_index:
                skipped.append(idx)
                continue

            total_g += grams_val
            nuts = composition.nutrients_for(code_str, grams_val)

            for k in NUTRIENTS:
                v = nuts[k]
                # Propagate NaN honestly when any ingredient lacks trans-fat or moisture data
                # rather than treating missing analytical cells as zero.
                if k == "tfa_g":
                    if math.isnan(v):
                        unknown_tfa_items.append(idx)
                        totals[k] = float("nan")
                    elif not math.isnan(totals[k]):
                        totals[k] += v
                elif k == "water_g":
                    if math.isnan(v):
                        unknown_water_items.append(idx)
                        totals[k] = float("nan")
                    elif not math.isnan(totals[k]):
                        totals[k] += v
                else:
                    totals[k] += v

    per_100g = {}
    for k in NUTRIENTS:
        val = totals[k]
        if math.isnan(val):
            per_100g[k] = float("nan")
        elif total_g > 0:
            per_100g[k] = val / total_g * 100
        else:
            per_100g[k] = 0.0

    return {
        "total_g": total_g,
        "totals": totals,
        "per_100g": per_100g,
        "skipped": skipped,
        "unknown_tfa_items": unknown_tfa_items,
        "unknown_water_items": unknown_water_items,
    }
