"""
Frying correction module.

Detects deep-frying bath oil lines and replaces the stated oil mass with
lab-measured absorbed fat from data/curated/fried_foods_lab.csv.

A "frying bath" line is an ingredient line that:
  (a) has class COOKING_OIL or HYDROGENATED_FAT, AND
  (b) its raw_line contains a frying phrase (see FRYING_PHRASES below), AND
  (c) its grams value exceeds FRYING_BATH_MIN_G (50g)

If frying bath lines are detected in a recipe result, this module:
  1. Removes their nutrient contribution from totals
  2. Looks up the dish name in fried_foods_lab.csv to get lab fat_g_100g
  3. Estimates absorbed fat = (non-oil included mass / 100) * lab_fat_g_100g
  4. Estimates absorbed SFA = absorbed_fat * (SFA_pct_of_fat / 100)
  5. Adds the absorbed fat/SFA back to totals
  6. Re-derives per_serving and footprint
  7. Returns the corrected result dict with a FRYING_CORRECTED warning added
"""
import copy
import csv
import os
import re
import statistics

from lhf import constants
from lhf.footprint import footprint as compute_footprint
from lhf.paths import DATA_CURATED

FRYING_PHRASES = [
    "for deep frying", "to deep fry", "for frying", "to fry",
    "deep fry", "deep frying", "for deep-frying", "to deep-fry",
]

FRYING_BATH_MIN_G = float("50.0")  # grams — below this, treat as sautéing oil (not a bath)

# Default fat per 100g by dish category if no exact match found in lab data
CATEGORY_DEFAULTS = {
    "stuffed pastry": float("15.0"),     # samosa, kachori
    "battered fritter": float("17.0"),   # pakora, bhaji, vada
    "flat dough": float("20.0"),         # puri, bhatura, paratha
    "crisp namkeen": float("25.0"),      # mathri, sev, chakri, namakpara
    "syrup-soaked sweet": float("15.0"), # gulab jamun, jalebi
    "other": float("15.0"),              # aloo tikki, etc.
    "default": float("15.0"),            # fallback
}

# Default SFA % of fat by category (used if SFA_pct_of_fat is missing in lab data)
CATEGORY_SFA_PCT = {
    "stuffed pastry": float("42.0"),
    "battered fritter": float("38.0"),
    "flat dough": float("36.0"),
    "crisp namkeen": float("42.0"),
    "syrup-soaked sweet": float("55.0"),
    "other": float("40.0"),
    "default": float("40.0"),
}

STOPWORDS = {"and", "or", "with", "in", "of", "the", "a"}

NON_FRIED_DISHES = {
    "biryani", "pulao", "pilau", "curry", "dal", "sabzi", "korma",
    "masala", "jalfrezi", "saag", "sambar", "halwa", "poha", "khichdi",
}

FRIED_KEYWORDS = {
    "samosa", "kachori", "pakora", "pakoda", "bhaji", "fritter", "bonda",
    "vada", "batter", "puri", "poori", "bhatura", "bhature", "mathri",
    "namakpara", "sev", "chakri", "bhujia", "chivda", "chewda", "murukku",
    "papad", "gulab jamun", "jalebi", "ladoo", "boondi", "aloo tikki",
    "fried", "deep fry", "deep-fry", "fry",
}

_LAB_DATA = None


def _load_lab_data() -> list[dict]:
    """Loads and caches data/curated/fried_foods_lab.csv."""
    global _LAB_DATA
    if _LAB_DATA is not None:
        return _LAB_DATA

    path = os.path.join(DATA_CURATED, "fried_foods_lab.csv")
    data = []
    if not os.path.exists(path):
        _LAB_DATA = []
        return _LAB_DATA

    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_fat = (row.get("fat_g_100g") or "").strip()
            if not raw_fat:
                continue
            try:
                fat_val = float(raw_fat)
            except (ValueError, TypeError):
                continue

            raw_sfa = (row.get("SFA_pct_of_fat") or "").strip()
            sfa_val = None
            if raw_sfa:
                try:
                    sfa_val = float(raw_sfa)
                except (ValueError, TypeError):
                    sfa_val = None

            row_copy = dict(row)
            row_copy["fat_g_100g"] = fat_val
            row_copy["SFA_pct_of_fat"] = sfa_val
            data.append(row_copy)

    _LAB_DATA = data
    return _LAB_DATA


def _detect_frying_bath_lines(lines: list) -> list[dict]:
    """Detects frying bath lines from the pipeline lines list."""
    bath_lines = []
    for line in lines:
        if not line.get("included", False):
            continue
        classes = line.get("classes") or []
        if "COOKING_OIL" not in classes and "HYDROGENATED_FAT" not in classes:
            continue
        raw_text = (line.get("raw") or "").lower()
        if not any(phrase in raw_text for phrase in FRYING_PHRASES):
            continue
        grams = line.get("grams")
        if grams is None or grams < FRYING_BATH_MIN_G:
            continue
        bath_lines.append(line)
    return bath_lines


def _normalize_name(name: str) -> str:
    """Normalizes dish/item name: lowercase and strip punctuation."""
    cleaned = re.sub(r"[^\w\s]", " ", name.lower())
    return " ".join(cleaned.split())


def _is_non_fried_dish(dish_name: str) -> bool:
    """Checks if a dish name refers to an inherently non-fried staple."""
    norm = _normalize_name(dish_name)
    has_non_fried = any(nf in norm.split() for nf in NON_FRIED_DISHES)
    has_fried = any(fk in norm for fk in FRIED_KEYWORDS)
    return has_non_fried and not has_fried


ALLOWED_FRYING_SETTINGS = {
    "auto",
    "all",
    "street",
    "home",
    "restaurant-takeaway",
    "retail-packaged",
    "lab-controlled",
}


def _lookup_lab_fat_details(dish_name: str, frying_setting: str = "auto") -> dict:
    """
    Looks up lab fat values for a dish name, optionally filtered by cooking setting.

    frying_setting:
      - 'auto': preserve default behaviour (prefer 'home' if present, else all matched rows)
      - 'all': median across all matched rows regardless of setting
      - specific setting ('street', 'home', 'restaurant-takeaway', 'retail-packaged', 'lab-controlled'):
        filter matched rows to that setting; if none exist, fall back to all matched rows
        (or category default) and record fallback_used=True.
    """
    norm_setting = (frying_setting or "auto").strip().lower()
    if norm_setting not in ALLOWED_FRYING_SETTINGS:
        raise ValueError(
            f"Invalid frying_setting {frying_setting!r}. Must be one of {sorted(ALLOWED_FRYING_SETTINGS)}"
        )

    norm_dish = _normalize_name(dish_name)
    lab_data = _load_lab_data()

    # Step 3: Exact base / substring match
    matched_rows = []

    # 3a. Exact base match (item before parentheses matches normalized dish)
    exact_base = [
        r for r in lab_data
        if _normalize_name(r["item"].split("(")[0]) == norm_dish
    ]
    if exact_base:
        matched_rows = exact_base
    else:
        # 3b. Substring match
        sub_matches = []
        for r in lab_data:
            item_base = _normalize_name(r["item"].split("(")[0])
            item_full = _normalize_name(r["item"])
            if (item_base and (item_base in norm_dish or norm_dish in item_base)) or \
               (item_full and (item_full in norm_dish or norm_dish in item_full)):
                sub_matches.append(r)
        if sub_matches:
            matched_rows = sub_matches

    # Step 5: Word overlap if still no match
    if not matched_rows:
        dish_words = {w for w in norm_dish.split() if w not in STOPWORDS}
        if dish_words:
            scored = []
            for r in lab_data:
                item_words = {w for w in _normalize_name(r["item"]).split() if w not in STOPWORDS}
                overlap = len(dish_words & item_words)
                if overlap > 0:
                    scored.append((overlap, r))
            if scored:
                max_score = max(s[0] for s in scored)
                matched_rows = [r for score, r in scored if score == max_score]

    # Step 6: Category fallback if still no match
    if not matched_rows:
        category = "default"
        if any(w in norm_dish for w in ("samosa", "kachori")):
            category = "stuffed pastry"
        elif any(w in norm_dish for w in ("pakora", "pakoda", "bhaji", "fritter", "bonda", "vada", "batter")):
            category = "battered fritter"
        elif any(w in norm_dish for w in ("puri", "poori", "bhatura", "bhature", "paratha")):
            category = "flat dough"
        elif any(w in norm_dish for w in ("mathri", "namakpara", "sev", "chakri", "bhujia", "chivda", "chewda", "murukku", "papad")):
            category = "crisp namkeen"
        elif any(w in norm_dish for w in ("gulab jamun", "jalebi", "ladoo", "boondi")):
            category = "syrup-soaked sweet"

        fat_default = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS["default"])
        sfa_default = CATEGORY_SFA_PCT.get(category, CATEGORY_SFA_PCT["default"])
        return {
            "fat_g_100g": fat_default,
            "sfa_pct_of_fat": sfa_default,
            "lab_match": f"category_default:{category}",
            "setting_requested": norm_setting,
            "setting_used": "category_default",
            "fallback_used": norm_setting != "auto",
            "fallback_reason": f"No dish-specific lab rows for {dish_name!r}; used '{category}' category default.",
            "matched_rows_count": 0,
            "matched_sources": [],
            "category": category,
        }

    # Step 4: Cooking setting filter / fallback
    all_matched = matched_rows
    setting_used = "all_matched"
    fallback_used = False
    fallback_reason = None

    if norm_setting == "auto":
        home_matches = [r for r in all_matched if r.get("setting") == "home"]
        if home_matches:
            matched_rows = home_matches
            setting_used = "home"
        else:
            matched_rows = all_matched
            setting_used = "all_matched"
    elif norm_setting == "all":
        matched_rows = all_matched
        setting_used = "all_matched"
    else:
        setting_matches = [r for r in all_matched if r.get("setting") == norm_setting]
        if setting_matches:
            matched_rows = setting_matches
            setting_used = norm_setting
        else:
            matched_rows = all_matched
            setting_used = "all_matched_fallback"
            fallback_used = True
            fallback_reason = (
                f"No direct lab measurements found for {dish_name!r} under '{norm_setting}' setting; "
                f"fell back to pooled median across {len(all_matched)} matched row(s)."
            )

    # Step 7: Derive median fat and SFA from matched rows
    fat_vals = [r["fat_g_100g"] for r in matched_rows if r.get("fat_g_100g") is not None]
    fat_g_100g = statistics.median(fat_vals) if fat_vals else CATEGORY_DEFAULTS["default"]

    sfa_vals = [r["SFA_pct_of_fat"] for r in matched_rows if r.get("SFA_pct_of_fat") is not None]
    if not sfa_vals and matched_rows != all_matched:
        # If setting-specific rows lack SFA% (e.g. UK CoFID), fall back to dish's SFA% rows before category default
        sfa_vals = [r["SFA_pct_of_fat"] for r in all_matched if r.get("SFA_pct_of_fat") is not None]

    if sfa_vals:
        sfa_pct_of_fat = statistics.median(sfa_vals)
    else:
        row_cat = matched_rows[0].get("category") if matched_rows else "default"
        sfa_pct_of_fat = CATEGORY_SFA_PCT.get(row_cat, CATEGORY_SFA_PCT["default"])

    item_names = sorted(set(r["item"].split("(")[0].strip() for r in matched_rows))
    matched_items_joined = ", ".join(item_names)
    match_desc = f"lab_match:{matched_items_joined}"

    matched_sources = [
        {
            "source": r.get("source", ""),
            "item": r.get("item", ""),
            "setting": r.get("setting", ""),
            "category": r.get("category", ""),
            "oil": r.get("oil", ""),
            "fat_g_100g": r.get("fat_g_100g"),
            "sfa_pct_of_fat": r.get("SFA_pct_of_fat"),
            "method": r.get("method", ""),
            "n_samples": r.get("n_samples", ""),
        }
        for r in matched_rows
    ]

    return {
        "fat_g_100g": fat_g_100g,
        "sfa_pct_of_fat": sfa_pct_of_fat,
        "lab_match": match_desc,
        "setting_requested": norm_setting,
        "setting_used": setting_used,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "matched_rows_count": len(matched_rows),
        "matched_sources": matched_sources,
    }


def _lookup_lab_fat(dish_name: str, frying_setting: str = "auto") -> tuple[float, float, str]:
    """
    Looks up lab fat values for a dish name.
    Returns (fat_g_100g, sfa_pct_of_fat, match_description).
    """
    info = _lookup_lab_fat_details(dish_name, frying_setting=frying_setting)
    return (info["fat_g_100g"], info["sfa_pct_of_fat"], info["lab_match"])


def correct_frying(
    result: dict,
    setting: str = "urban",
    risk: str = "general",
    frying_setting: str = "auto",
) -> dict:
    """
    Main entry point. Corrects deep-frying bath oil lines in a pipeline result dict.
    """
    lines = result.get("lines") or []
    frying_bath_lines = _detect_frying_bath_lines(lines)
    if not frying_bath_lines:
        return result

    recipe_info = result.get("recipe") or {}
    dish_name = recipe_info.get("dish") or recipe_info.get("title") or ""

    # If the recipe is a non-fried dish (e.g. biryani, curry), do not apply frying correction
    if _is_non_fried_dish(dish_name):
        return result

    oil_mass_g = sum(l["grams"] for l in frying_bath_lines if l.get("grams") is not None)

    lab_info = _lookup_lab_fat_details(dish_name, frying_setting=frying_setting)
    fat_g_100g = lab_info["fat_g_100g"]
    sfa_pct_of_fat = lab_info["sfa_pct_of_fat"]
    match_desc = lab_info["lab_match"]

    # Step 6: Non-oil included mass
    non_oil_mass_g = sum(
        l["grams"]
        for l in lines
        if l.get("included") and l not in frying_bath_lines and l.get("grams") is not None
    )

    if non_oil_mass_g <= 0:
        return result

    absorbed_fat_g = (non_oil_mass_g / float("100.0")) * fat_g_100g
    absorbed_sfa_g = absorbed_fat_g * (sfa_pct_of_fat / float("100.0"))

    # Step 9: Nutrient contribution of bath oil lines to remove
    fat_to_remove_g = 0.0
    sfa_to_remove_g = 0.0
    energy_to_remove_kcal = 0.0

    for line in frying_bath_lines:
        nuts = line.get("nutrients")
        grams = line.get("grams") or 0.0
        if nuts and isinstance(nuts, dict):
            fat_to_remove_g += nuts.get("fat_g") or 0.0
            sfa_to_remove_g += nuts.get("sfa_g") or 0.0
            energy_to_remove_kcal += nuts.get("energy_kcal") or 0.0
        else:
            fat_to_remove_g += grams * float("0.995")
            energy_to_remove_kcal += grams * float("9")

    # Step 10: Rebuild corrected totals
    corrected_totals = copy.deepcopy(result.get("totals") or {})
    fat_readd_kcal = absorbed_fat_g * float("9")

    if "fat_g" in corrected_totals and corrected_totals["fat_g"] is not None:
        corrected_totals["fat_g"] = max(0.0, corrected_totals["fat_g"] - fat_to_remove_g + absorbed_fat_g)
    if "sfa_g" in corrected_totals and corrected_totals["sfa_g"] is not None:
        corrected_totals["sfa_g"] = max(0.0, corrected_totals["sfa_g"] - sfa_to_remove_g + absorbed_sfa_g)
    if "energy_kcal" in corrected_totals and corrected_totals["energy_kcal"] is not None:
        corrected_totals["energy_kcal"] = max(0.0, corrected_totals["energy_kcal"] - energy_to_remove_kcal + fat_readd_kcal)

    if "energy_kj" in corrected_totals and corrected_totals["energy_kj"] is not None:
        kj_factor = constants.get("KJ_PER_KCAL")
        energy_to_remove_kj = energy_to_remove_kcal * kj_factor
        corrected_totals["energy_kj"] = max(0.0, corrected_totals["energy_kj"] - energy_to_remove_kj + (fat_readd_kcal * kj_factor))

    # Step 11: Mark frying bath lines in lines list
    for line in frying_bath_lines:
        line["included"] = False
        line["exclusion_reason"] = "FRYING_BATH"

    # Step 12: Recompute coverage
    corrected_coverage = copy.deepcopy(result.get("coverage") or {})
    if "excluded_by_reason" in corrected_coverage:
        corrected_coverage["excluded_by_reason"]["FRYING_BATH"] = len(frying_bath_lines)
    corrected_coverage["included_mass_g"] = max(0.0, corrected_coverage.get("included_mass_g", 0.0) - oil_mass_g)
    corrected_coverage["lines_included"] = max(0, corrected_coverage.get("lines_included", 0) - len(frying_bath_lines))

    # Step 13: Recompute per_serving
    servings_raw = recipe_info.get("servings")
    servings_val = None
    if servings_raw is not None and not isinstance(servings_raw, bool):
        try:
            s_cand = float(servings_raw)
            if s_cand > 0:
                servings_val = s_cand
        except (ValueError, TypeError):
            servings_val = None

    if servings_val is not None:
        corrected_per_serving = {
            k: (v / servings_val if v is not None else None)
            for k, v in corrected_totals.items()
        }
        corrected_footprint = compute_footprint(corrected_per_serving, setting=setting, risk=risk)
    else:
        corrected_per_serving = None
        corrected_footprint = None

    # Step 15: Build warning string
    warn = (
        f"FRYING_CORRECTED: detected {len(frying_bath_lines)} frying bath line(s) "
        f"({oil_mass_g:.0f}g oil excluded). "
        f"Absorbed fat estimated at {absorbed_fat_g:.1f}g using lab data "
        f"({fat_g_100g}g/100g, match={match_desc}). "
        f"Original stated-oil fat: {fat_to_remove_g:.1f}g."
    )

    # Step 16: Return corrected result dict
    corrected_result = copy.copy(result)
    corrected_result["totals"] = corrected_totals
    corrected_result["per_serving"] = corrected_per_serving
    corrected_result["footprint"] = corrected_footprint
    corrected_result["coverage"] = corrected_coverage
    corrected_result["lines"] = lines
    corrected_result["warnings"] = list(result.get("warnings") or []) + [warn]
    corrected_result["frying_correction"] = {
        "applied": True,
        "frying_bath_lines_count": len(frying_bath_lines),
        "oil_mass_removed_g": oil_mass_g,
        "non_oil_mass_g": non_oil_mass_g,
        "absorbed_fat_g": absorbed_fat_g,
        "absorbed_sfa_g": absorbed_sfa_g,
        "absorbed_fat_per_serving_g": (absorbed_fat_g / servings_val) if servings_val else None,
        "absorbed_sfa_per_serving_g": (absorbed_sfa_g / servings_val) if servings_val else None,
        "fat_g_per_100g_lab": fat_g_100g,
        "sfa_pct_of_fat_lab": sfa_pct_of_fat,
        "calculation_formula": (
            f"absorbed_fat_g = ({non_oil_mass_g:.1f}g non-oil mass / 100) * "
            f"{fat_g_100g:.2f}g/100g = {absorbed_fat_g:.2f}g"
        ),
        "lab_match": match_desc,
        "setting_requested": lab_info["setting_requested"],
        "setting_used": lab_info["setting_used"],
        "fallback_used": lab_info["fallback_used"],
        "fallback_reason": lab_info["fallback_reason"],
        "matched_rows_count": lab_info["matched_rows_count"],
        "matched_sources": lab_info["matched_sources"],
    }

    return corrected_result
