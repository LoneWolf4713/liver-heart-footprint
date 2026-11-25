import math
from lhf import composition, constants
from lhf.classify import class_totals, classes_for
from lhf.compute import sum_nutrients
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


# run all 5 stages on a recipe dict (parse -> match -> weigh -> frying fix -> daily % limits)
def analyse_recipe(recipe, setting="urban", risk="general", frying_setting="auto"):
    table = composition.load_table()
    table_index = table.index

    lines_raw = recipe.get("lines") or []
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

            if "SALT" in unq_classes:
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
            # match food name before weighing cups/spoons because density depends on what the food is
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
                c_list = classes_for(code)
                if "WATER" in c_list or code == "K505":
                    lines_out.append({
                        "index": idx,
                        "raw": raw,
                        "parsed": parsed,
                        "match": m,
                        "grams": None,
                        "grams_basis": None,
                        "grams_flags": [],
                        "included": False,
                        "exclusion_reason": "WATER",
                        "classes": c_list,
                        "nutrients": None,
                    })
                    continue

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

    compute_res = sum_nutrients([{"code": l["match"]["code"], "grams": l["grams"]} for l in inc_items])
    totals = compute_res["totals"]
    cls_tot = class_totals(
        [{"code": l["match"]["code"], "grams": l["grams"], "nutrients": l["nutrients"]} for l in inc_items]
    )
    totals["added_sugar_g"] = cls_tot["added_sugar_g"]
    totals["refined_carb_g"] = cls_tot["refined_carb_g"]
    totals["salt_g"] = cls_tot["salt_g"]

    # sanity warnings for huge spice amounts or weird recipe weights
    spice_max = constants.get("SPICE_LINE_MAX_G")
    for l in inc_items:
        if "SPICE" in l["classes"] and l["grams"] > spice_max:
            warnings.append(f"SPICE_OVER_LIMIT: line '{l['raw']}' exceeds {spice_max} g ({l['grams']} g)")

    mass_min = constants.get("RECIPE_MASS_MIN_G")
    mass_max = constants.get("RECIPE_MASS_MAX_G")
    if not (mass_min <= included_mass <= mass_max):
        warnings.append(f"MASS_IMPLAUSIBLE: included mass {included_mass} g outside range {mass_min}-{mass_max} g")

    servings_raw = recipe.get("servings")
    servings_val = None
    if servings_raw is not None and not isinstance(servings_raw, bool):
        try:
            s_cand = float(servings_raw)
            if math.isfinite(s_cand) and s_cand > 0:
                servings_val = s_cand
        except (ValueError, TypeError):
            servings_val = None

    if servings_val is None:
        warnings.append("NO_SERVINGS: servings not specified or invalid in recipe")
        per_serving = None
        fp = None
    else:
        per_serving = {
            k: (v / servings_val if v is not None and not math.isnan(v) else None)
            for k, v in totals.items()
        }
        fp = footprint(per_serving, setting=setting, risk=risk)

    # salt to taste adds 0g so we warn that reported sodium is a lower bound
    if has_unquantified_salt:
        warnings.append("SALT_UNQUANTIFIED: recipe contains unquantified salt line (sodium is a lower bound)")

    recipe_info = {
        "id": recipe.get("id"),
        "url": recipe.get("url"),
        "dish": recipe.get("dish"),
        "servings": recipe.get("servings"),
        "deep_fried_hint": bool(recipe.get("deep_fried_hint", False)),
        "deep_fry_evidence": recipe.get("deep_fry_evidence"),
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

    # swap out deep frying pan oil bath with lab absorbed oil numbers
    from lhf.frying import correct_frying
    result = correct_frying(result, setting=setting, risk=risk, frying_setting=frying_setting)

    return _clean_nan(result)
