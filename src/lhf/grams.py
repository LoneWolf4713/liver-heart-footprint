import csv
import math
import os

from lhf import constants
from lhf.paths import DATA_CURATED

_MEASURES = None


# load density and cup/spoon measure rules once
def _load_measures():
    global _MEASURES
    if _MEASURES is not None:
        return _MEASURES

    path = os.path.join(DATA_CURATED, "measures.csv")
    any_measures = {}
    code_measures = {}
    group_measures = {}

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grams_val = float(row["grams"])
            m_type = row["match_type"].strip()
            unit_val = row["unit"].strip().lower()
            size_val = row["size"].strip().lower() if row["size"] else ""

            if m_type == "any":
                any_measures[unit_val] = grams_val
            elif m_type == "code":
                for code_item in row["match"].split(";"):
                    clean_code = code_item.strip().upper()
                    key = (clean_code, unit_val)
                    if key not in code_measures:
                        code_measures[key] = []
                    code_measures[key].append({"size": size_val, "grams": grams_val})
            elif m_type == "group":
                grp = row["match"].strip().upper()
                group_measures[(grp, unit_val)] = grams_val

    _MEASURES = (any_measures, code_measures, group_measures)
    return _MEASURES


# look up g/ml density for code or food group, otherwise default to water (1 g/ml)
def _get_density(code):
    if not isinstance(code, str):
        code = None
    else:
        code = code.strip().upper()
        if not code:
            code = None

    if code and code not in ("UNMAPPED", "NON_FOOD"):
        _, code_measures, group_measures = _load_measures()
        if (code, "ml") in code_measures:
            return code_measures[(code, "ml")][0]["grams"], False
        if len(code) > 0 and (code[0], "ml") in group_measures:
            return group_measures[(code[0], "ml")], False
    return 1, True


def _resolve_code_measure(code, unit, size):
    _, code_measures, _ = _load_measures()
    rows = code_measures.get((code, unit))
    if not rows:
        return None, None

    chosen = None
    flag = None

    if size is not None:
        for r in rows:
            if r["size"] == size:
                chosen = r
                break

    if chosen is None:
        for r in rows:
            if not r["size"]:
                chosen = r
                break

    if chosen is None:
        for r in rows:
            if r["size"] == "medium":
                chosen = r
                if size is None:
                    flag = "SIZE_ASSUMED_MEDIUM"
                else:
                    flag = "SIZE_SUBSTITUTED"
                break

    return chosen, flag


# convert household units like cups, spoons and pieces to grams using food-specific rules
def grams_for(qty, unit, size, stated_g, stated_ml, code):
    if isinstance(code, str):
        code = code.strip().upper()
        if not code:
            code = None
    else:
        code = None

    # use explicit gram weight if the recipe already gave one
    if stated_g is not None:
        if isinstance(stated_g, bool):
            return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
        try:
            val = float(stated_g)
            if math.isnan(val):
                return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
            return {"grams": val, "basis": "STATED_MASS", "flags": []}
        except (ValueError, TypeError):
            return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}

    # use explicit ml multiplied by food density if given
    if stated_ml is not None:
        if isinstance(stated_ml, bool):
            return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
        try:
            val = float(stated_ml)
            if math.isnan(val):
                return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
            density, assumed = _get_density(code)
            flags = ["DENSITY_ASSUMED_1"] if assumed else []
            return {"grams": val * density, "basis": "STATED_VOLUME", "flags": flags}
        except (ValueError, TypeError):
            return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}

    if isinstance(unit, list):
        unit = unit[0] if len(unit) > 0 else None
    if isinstance(unit, str):
        unit = unit.strip().lower()
        if not unit:
            unit = None
    else:
        unit = None

    if isinstance(size, list):
        size = size[0] if len(size) > 0 else None
    if isinstance(size, str):
        size = size.strip().lower()
        if not size:
            size = None
    else:
        size = None

    if qty is None or unit is None:
        return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}

    if isinstance(qty, bool):
        return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}

    try:
        qty_val = float(qty)
        if math.isnan(qty_val):
            return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
    except (ValueError, TypeError):
        return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}

    any_measures, _, group_measures = _load_measures()

    # standard mass units (g, kg, mg, oz, lb)
    if unit in any_measures:
        return {"grams": qty_val * any_measures[unit], "basis": "MASS_UNIT", "flags": []}

    # ml or l multiplied by food density
    if unit in ("ml", "l"):
        mult = 1000 if unit == "l" else 1
        density, assumed = _get_density(code)
        flags = ["DENSITY_ASSUMED_1"] if assumed else []
        return {"grams": qty_val * mult * density, "basis": "VOLUME_UNIT", "flags": flags}

    # cup/piece conversions need a real food code first
    if not code or code in ("UNMAPPED", "NON_FOOD"):
        return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}

    # check exact food code measure first
    chosen, flag = _resolve_code_measure(code, unit, size)
    if chosen is not None:
        flags = [flag] if flag else []
        return {"grams": qty_val * chosen["grams"], "basis": "CODE_MEASURE", "flags": flags}

    # otherwise fall back to food group default (first letter of code)
    grp = code[0]
    if (grp, unit) in group_measures:
        return {"grams": qty_val * group_measures[(grp, unit)], "basis": "GROUP_MEASURE", "flags": []}

    # pinch or dash = fraction of 1 tsp for that food
    if unit in ("pinch", "dash"):
        tsp_chosen, _ = _resolve_code_measure(code, "tsp", None)
        tsp_grams = None
        tsp_basis = None
        if tsp_chosen is not None:
            tsp_grams = tsp_chosen["grams"]
            tsp_basis = "CODE_MEASURE"
        elif (grp, "tsp") in group_measures:
            tsp_grams = group_measures[(grp, "tsp")]
            tsp_basis = "GROUP_MEASURE"

        if tsp_grams is not None:
            pinch_frac = constants.get("PINCH_FRACTION_OF_TSP")
            return {
                "grams": qty_val * pinch_frac * tsp_grams,
                "basis": tsp_basis,
                "flags": ["PINCH_AS_QUARTER_TSP"],
            }

    return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
