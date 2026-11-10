"""End-to-end recipe pipeline for Phase 1 core engine (SPEC §9)."""

import math
from lhf import composition, constants
from lhf.classify import class_totals, classes_for
from lhf.footprint import footprint
from lhf.grams import grams_for
from lhf.match import match_name
from lhf.parse import parse_line


def _clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nan(v) for v in obj]
    return obj


def analyse_recipe(recipe: dict, setting: str = "urban", risk: str = "general") -> dict:
    """Analyse a recipe and return per-serving nutrient totals and daily-budget footprint.

    recipe: dict with id, url, dish, servings, lines.
    setting: 'urban' or 'rural'.
    risk: 'general' or 'cardiometabolic'.
    """
    table = composition.load_table()
    table_index = table.index

    lines_raw = recipe.get("lines", [])
    lines_out = []
    inc_items = []
    unquantified_fat_lines = []
    warnings = []

    has_unquantified_salt = False

    for idx, raw in enumerate(lines_raw):
        parsed = parse_line(raw)
        status = parsed.get("status")

        if status == "WATER":
            lines_out.append({
                "index": idx,
                "raw": raw,
                "parsed": parsed,
                "match": None,
                "grams": None,
                "grams_basis": None,
                "grams_flags": [],
                "included": False,
                "exclusion_reason": "WATER",
                "classes": [],
                "nutrients": None,
            })
        elif status == "UNQUANTIFIED":
            name = parsed.get("name", "")
            unq_m = match_name(name)
            unq_code = unq_m.get("code")
            unq_classes = classes_for(unq_code) if unq_code and unq_code not in ("UNMAPPED", "NON_FOOD") else []

            if any(c in ("COOKING_OIL", "DAIRY_FAT", "HYDROGENATED_FAT") for c in unq_classes):
                unquantified_fat_lines.append(raw)

            if "SALT" in unq_classes or "salt" in name.lower() or "namak" in name.lower():
                has_unquantified_salt = True

            lines_out.append({
                "index": idx,
                "raw": raw,
                "parsed": parsed,
                "match": None,
                "grams": None,
                "grams_basis": None,
                "grams_flags": [],
                "included": False,
                "exclusion_reason": "UNQUANTIFIED",
                "classes": [],
                "nutrients": None,
            })
        elif status == "QUANTIFIED":
            name = parsed.get("name", "")
            m = match_name(name)
            code = m.get("code")

            if code == "NON_FOOD":
                lines_out.append({
                    "index": idx,
                    "raw": raw,
                    "parsed": parsed,
                    "match": m,
                    "grams": None,
                    "grams_basis": None,
                    "grams_flags": [],
                    "included": False,
                    "exclusion_reason": "NON_FOOD",
                    "classes": [],
                    "nutrients": None,
                })
            elif code == "UNMAPPED" or code not in table_index:
                lines_out.append({
                    "index": idx,
                    "raw": raw,
                    "parsed": parsed,
                    "match": m,
                    "grams": None,
                    "grams_basis": None,
                    "grams_flags": [],
                    "included": False,
                    "exclusion_reason": "UNMAPPED",
                    "classes": [],
                    "nutrients": None,
                })
            else:
                g_res = grams_for(
                    parsed.get("qty"),
                    parsed.get("unit"),
                    parsed.get("size"),
                    parsed.get("stated_g"),
                    parsed.get("stated_ml"),
                    code,
                )
                g = g_res.get("grams")
                g_basis = g_res.get("basis")
                g_flags = g_res.get("flags", [])
                c_list = classes_for(code)

                if g is None or g <= 0:
                    lines_out.append({
                        "index": idx,
                        "raw": raw,
                        "parsed": parsed,
                        "match": m,
                        "grams": None,
                        "grams_basis": g_basis,
                        "grams_flags": g_flags,
                        "included": False,
                        "exclusion_reason": "UNQUANTIFIABLE",
                        "classes": c_list,
                        "nutrients": None,
                    })
                else:
                    g_val = float(g)
                    raw_nuts = composition.nutrients_for(code, g_val)
                    line_dict = {
                        "index": idx,
                        "raw": raw,
                        "parsed": parsed,
                        "match": m,
                        "grams": g_val,
                        "grams_basis": g_basis,
                        "grams_flags": g_flags,
                        "included": True,
                        "exclusion_reason": None,
                        "classes": c_list,
                        "nutrients": raw_nuts,
                    }
                    lines_out.append(line_dict)
                    inc_items.append(line_dict)
        else:
            lines_out.append({
                "index": idx,
                "raw": raw,
                "parsed": parsed,
                "match": None,
                "grams": None,
                "grams_basis": None,
                "grams_flags": [],
                "included": False,
                "exclusion_reason": "UNQUANTIFIABLE",
                "classes": [],
                "nutrients": None,
            })

    # Coverage
    excluded_by_reason = {
        "WATER": 0,
        "UNQUANTIFIED": 0,
        "UNMAPPED": 0,
        "NON_FOOD": 0,
        "UNQUANTIFIABLE": 0,
    }
    for l in lines_out:
        if not l["included"]:
            reason = l["exclusion_reason"]
            if reason in excluded_by_reason:
                excluded_by_reason[reason] += 1

    included_mass = sum(l["grams"] for l in inc_items)

    coverage = {
        "lines_total": len(lines_out),
        "lines_included": len(inc_items),
        "excluded_by_reason": excluded_by_reason,
        "included_mass_g": float(included_mass),
        "unquantified_fat_lines": unquantified_fat_lines,
    }

    # Totals
    totals = {}
    for n in composition.NUTRIENT_COLUMNS:
        if n == "tfa_g":
            has_unknown = any(
                math.isnan(l["nutrients"]["tfa_g"])
                for l in inc_items
                if l["nutrients"].get("tfa_g") is not None
            )
            if has_unknown or not inc_items:
                totals[n] = float("nan") if has_unknown else 0.0
            else:
                totals[n] = sum(float(l["nutrients"]["tfa_g"]) for l in inc_items)
        elif n == "water_g":
            has_unknown = any(
                math.isnan(l["nutrients"]["water_g"])
                for l in inc_items
                if l["nutrients"].get("water_g") is not None
            )
            if has_unknown or not inc_items:
                totals[n] = float("nan") if has_unknown else 0.0
            else:
                totals[n] = sum(float(l["nutrients"]["water_g"]) for l in inc_items)
        else:
            totals[n] = sum(float(l["nutrients"][n] or 0.0) for l in inc_items)

    cls_tot = class_totals(
        [{"code": l["match"]["code"], "grams": l["grams"], "nutrients": l["nutrients"]} for l in inc_items]
    )
    totals["added_sugar_g"] = cls_tot["added_sugar_g"]
    totals["refined_carb_g"] = cls_tot["refined_carb_g"]
    totals["salt_g"] = cls_tot["salt_g"]

    # Warnings
    spice_max = constants.get("SPICE_LINE_MAX_G")
    for l in inc_items:
        if "SPICE" in l["classes"] and l["grams"] > spice_max:
            warnings.append(f"SPICE_OVER_LIMIT: line '{l['raw']}' exceeds {spice_max} g ({l['grams']} g)")

    mass_min = constants.get("RECIPE_MASS_MIN_G")
    mass_max = constants.get("RECIPE_MASS_MAX_G")
    if not (mass_min <= included_mass <= mass_max):
        warnings.append(f"MASS_IMPLAUSIBLE: included mass {included_mass} g outside range {mass_min}-{mass_max} g")

    servings = recipe.get("servings")
    if not servings:
        warnings.append("NO_SERVINGS: servings not specified in recipe")
        per_serving = None
        fp = None
    else:
        servings_val = float(servings)
        per_serving = {
            k: (v / servings_val if v is not None and not math.isnan(v) else None)
            for k, v in totals.items()
        }
        fp = footprint(per_serving, setting=setting, risk=risk)

    if has_unquantified_salt:
        warnings.append("SALT_UNQUANTIFIED: recipe contains unquantified salt line (sodium is a lower bound)")

    recipe_info = {
        "id": recipe.get("id"),
        "url": recipe.get("url"),
        "dish": recipe.get("dish"),
        "servings": recipe.get("servings"),
    }

    result = {
        "recipe": recipe_info,
        "lines": lines_out,
        "coverage": coverage,
        "totals": totals,
        "per_serving": per_serving,
        "footprint": fp,
        "warnings": warnings,
    }

    return _clean_nan(result)
