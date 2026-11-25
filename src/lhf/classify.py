"""Food classes: added sugar, refined carbohydrate, salt, and fat sources (SPEC §7)."""
import csv
import math
import os

from lhf import composition
from lhf.paths import DATA_CURATED

_CLASSES_BY_CODE = None


def _load_classes():
    global _CLASSES_BY_CODE
    if _CLASSES_BY_CODE is not None:
        return _CLASSES_BY_CODE

    path = os.path.join(DATA_CURATED, "classes.csv")
    classes_by_code = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["code"].strip()
            cls_name = row["class"].strip()
            if code not in classes_by_code:
                classes_by_code[code] = []
            if cls_name not in classes_by_code[code]:
                classes_by_code[code].append(cls_name)

    _CLASSES_BY_CODE = classes_by_code
    return _CLASSES_BY_CODE


def classes_for(code: str) -> list[str]:
    """Return the list of food classes for a given food code."""
    if code is None or code == "":
        return []
    classes_map = _load_classes()
    return list(classes_map.get(str(code).strip(), []))


def class_totals(items: list) -> dict:
    """Compute food class totals for a list of ingredient items.

    Items are dicts with code, grams and nutrients (from composition.nutrients_for).

    Returns:
      added_sugar_g: Σ over ADDED_SUGAR items of grams × min(freesugar_g per 100 g, 100) / 100
      refined_carb_g: Σ carb_g of REFINED_GRAIN items
      salt_g: Σ grams of SALT items
      fat_by_class_g: {class: Σ fat_g} for COOKING_OIL, HYDROGENATED_FAT, DAIRY_FAT, and OTHER
    """
    added_sugar_g = 0.0
    refined_carb_g = 0.0
    salt_g = 0.0
    fat_by_class_g = {
        "COOKING_OIL": 0.0,
        "HYDROGENATED_FAT": 0.0,
        "DAIRY_FAT": 0.0,
        "OTHER": 0.0,
    }

    if not items:
        return {
            "added_sugar_g": 0.0,
            "refined_carb_g": 0.0,
            "salt_g": 0.0,
            "fat_by_class_g": fat_by_class_g,
        }

    table = composition.load_table()

    for item in items:
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        code_str = str(code).strip() if code is not None else ""

        grams = item.get("grams")
        if grams is None or isinstance(grams, bool):
            continue
        try:
            grams_val = float(grams)
        except (ValueError, TypeError):
            continue
        if grams_val <= 0 or not math.isfinite(grams_val):
            continue

        item_classes = classes_for(code_str)
        nutrients = item.get("nutrients") or {}

        # 1. Added sugar:
        if "ADDED_SUGAR" in item_classes:
            if nutrients.get("freesugar_g") is not None:
                try:
                    fs_val = float(nutrients["freesugar_g"])
                    if not math.isnan(fs_val):
                        added_sugar_g += min(fs_val, grams_val)
                except (ValueError, TypeError):
                    pass
            elif code_str in table.index:
                try:
                    fs_100 = float(table.loc[code_str, "freesugar_g"])
                    if not math.isnan(fs_100):
                        added_sugar_g += grams_val * min(fs_100, 100) / 100
                except (ValueError, TypeError):
                    pass

        # 2. Refined carbohydrate:
        if "REFINED_GRAIN" in item_classes:
            if nutrients.get("carb_g") is not None:
                try:
                    carb_val = float(nutrients["carb_g"])
                    if not math.isnan(carb_val):
                        refined_carb_g += carb_val
                except (ValueError, TypeError):
                    pass
            elif code_str in table.index:
                try:
                    carb_100 = float(table.loc[code_str, "carb_g"])
                    if not math.isnan(carb_100):
                        refined_carb_g += carb_100 * grams_val / 100
                except (ValueError, TypeError):
                    pass

        # 3. Salt: Σ grams of SALT items
        if "SALT" in item_classes:
            salt_g += grams_val

        # 4. Fat by class: COOKING_OIL, HYDROGENATED_FAT, DAIRY_FAT, and OTHER
        if nutrients.get("fat_g") is not None:
            try:
                fat_val = float(nutrients["fat_g"])
            except (ValueError, TypeError):
                fat_val = 0.0
        elif code_str in table.index:
            try:
                fat_val = float(table.loc[code_str, "fat_g"]) * grams_val / 100
            except (ValueError, TypeError):
                fat_val = 0.0
        else:
            fat_val = 0.0

        if math.isnan(fat_val):
            fat_val = 0.0

        if "COOKING_OIL" in item_classes:
            fat_by_class_g["COOKING_OIL"] += fat_val
        elif "HYDROGENATED_FAT" in item_classes:
            fat_by_class_g["HYDROGENATED_FAT"] += fat_val
        elif "DAIRY_FAT" in item_classes:
            fat_by_class_g["DAIRY_FAT"] += fat_val
        else:
            fat_by_class_g["OTHER"] += fat_val

    return {
        "added_sugar_g": added_sugar_g,
        "refined_carb_g": refined_carb_g,
        "salt_g": salt_g,
        "fat_by_class_g": fat_by_class_g,
    }
