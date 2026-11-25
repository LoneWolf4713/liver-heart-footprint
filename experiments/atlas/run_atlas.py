"""Deliverable 3: Liver and Heart Footprint Atlas of Indian Recipes.

Analyzes 1,014 standardized recipes from the Indian Nutrient Databank (INDB)
and 71 real web recipes across 10 top cooking websites, computing:
1. Cardiometabolic budget loads (% ICMR-NIN/WHO daily limits) by dish category.
2. Ingredient-group driver decomposition (Dairy Fat vs Cooking Oil vs Sugar).
3. Paired Textbook (INDB) vs Web recipes comparison across benchmark dishes.
4. Frying bath oil correction via src/lhf/frying.py and data/curated/fried_foods_lab.csv.
5. Publication-grade figures, machine-readable metrics, and verified summary tables.
"""

import os
import sys
import json
import math
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Ensure src is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from lhf import compute, composition, classify, footprint, pipeline, constants
from lhf.frying import correct_frying
from lhf.paths import DATA_RAW, DATA_CURATED

ATLAS_DIR = os.path.join(BASE_DIR, "experiments", "atlas")
os.makedirs(ATLAS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. INDB Unit Converter (reproducing INDB.do lines 166-210)
# ---------------------------------------------------------------------------
def indb_grams(a, u, food_code, food_name):
    """Convert amount and unit from INDB recipes.xlsx to grams."""
    c = str(food_code)[:1]
    g = np.nan
    rules = [
        (u == "g", a),
        (u == "tsp" and c in "GHBU", a * 2),
        (u == "tbsp" and c in "DGHBU", a * 7),
        (u == "tsp" and c == "D", a * 2),
        (u == "tbsp" and c == "F", a * 40),
        (u == "ml" and c in "GHIVX", a),
        (u == "tsp" and c == "A", a * 2.5),
        (u == "tsp" and c == "M", a * 5),
        (u == "tbsp" and c == "A", a * 7),
        (u == "tsp" and c == "V", a * 2),
        (u == "tsp" and c == "T", a * 4),
        (u == "tbsp" and c == "T", a * 13.5),
        (u == "tsp" and c in "XW", a * 6),
        (u == "tbsp" and c in "XW", a * 20),
        (u == "tsp" and c == "I", a * 4),
        (u == "tbsp" and c == "I", a * 12),
        (u == "C" and c == "I", a * 200),
        (u == "tbsp" and c == "Z", a * 15),
        (u == "tsp" and c == "L", a * 5),
        (u == "tbsp" and c == "L", a * 15),
        (u == "C" and c == "L", a * 240),
        (u == "ml" and c == "L", a),
        (u == "sprig" and c in "GUCA", a * 2),
        (u == "tsp" and c == "C", a * 0.5),
        (u == "tbsp" and c == "C", a * 5),
        (u == "tsp" and c == "T", a * 4),
        (u == "ml" and c == "T", a),
        (u == "C", a * 240),
        (u == "ml" and c == "K", a),
        (u == "ml" and c == "E", a),
        (u == "tsp" and c in "KE", a * 5),
        (u == "tbsp" and c in "KE", a * 15),
        (u == "tbsp" and c == "V", a * 8),
        (u == "small" and c == "G", a * 2),
        (food_name == "FENUGREEK LEAVES", a * 2),
        (u == "pinch", 0.125),
    ]
    for cond, val in rules:
        if cond:
            g = val
    return None if pd.isna(g) else float(g)


# ---------------------------------------------------------------------------
# 2. Culinary Dish Categorization Taxonomy (11 Categories, 100% Coverage)
# ---------------------------------------------------------------------------
CATEGORIES = [
    "Curries & Gravies",
    "Dals & Legumes",
    "Vegetables & Sabzis",
    "Rice & Grains",
    "Breads & Flatbreads",
    "Snacks & Street Food",
    "Sweets & Desserts",
    "Breakfast & Tiffin",
    "Beverages",
    "Soups & Stews",
    "Condiments & Chutneys",
]

def classify_recipe(recipe_code: str, recipe_name: str, recipe_code_org: str = "") -> str:
    code = str(recipe_code).strip()
    name = str(recipe_name).lower().strip()
    org = str(recipe_code_org).strip()

    # 1. Direct textbook chapter mapping for ASC
    if code.startswith("ASC"):
        ch = org.split(".")[0]
        if ch in ["5", "22"]:
            return "Beverages"
        if ch in ["6", "16", "21"]:
            return "Snacks & Street Food"
        if ch in ["7"]:
            return "Breakfast & Tiffin"
        if ch in ["8"]:
            return "Soups & Stews"
        if ch in ["9"]:
            if any(k in name for k in ["macaroni", "noodle", "spaghetti", "penne", "pasta"]):
                return "Rice & Grains"
            return "Breads & Flatbreads"
        if ch in ["10"]:
            return "Dals & Legumes"
        if ch in ["11"]:
            return "Vegetables & Sabzis"
        if ch in ["12"]:
            return "Curries & Gravies"
        if ch in ["13"]:
            return "Condiments & Chutneys"
        if ch in ["14", "15", "17", "18", "19", "23"]:
            return "Sweets & Desserts"
        if ch in ["20"]:
            return "Breakfast & Tiffin"
        if ch in ["24", "25"]:
            return "Condiments & Chutneys"

    # 2. Keyword & semantic mapping for BFP, OSR, and Web recipes
    if any(k in name for k in [
        "tea", "chai", "coffee", "shake", "sharbat", "squash", "thandai", "jal jeera",
        "drink", "cocoa", "cooler", "lemonade", "punch", "lassi", "syrup", "gingo",
        "mintade", "canjee", "smoothie", "saffron milk", "kesariya doodh", "chocolate"
    ]):
        return "Beverages"

    if any(k in name for k in [
        "kheer", "burfi", "halwa", "ladoo", "laddu", "jamun", "jalebi", "payasam",
        "cake", "pudding", "biscuit", "cookie", "sweet", "custard", "flan", "tart",
        "pastry", "pie", "fudge", "chikki", "marmalade", "jam", "jelly", "murabba",
        "shrikhand", "ice cream", "sweetened", "icing", "glaze", "gateau", "choux",
        "souffle", "marzipan", "butterscotch", "whip", "cream", "mousse", "fool",
        "pavlova", "chum chum", "dil bahar", "rasbhari", "rajbogh", "rasgulla",
        "rasmalai", "kesari bath", "putharekulu", "malpua", "chhena poda", "preserves",
        "dessert", "bavarian cream", "delight"
    ]):
        return "Sweets & Desserts"

    if any(k in name for k in [
        "dal", "daal", "sambar", "rasam", "channa", "chana", "chole", "rajma",
        "lentil", "kadhi", "pulse mix", "sprout", "lobia", "kulthi", "gram whole",
        "urad", "lentils"
    ]):
        return "Dals & Legumes"

    if any(k in name for k in [
        "rice", "pulao", "pilaf", "pilau", "biryani", "khichdi", "khichri", "tahar",
        "macaroni", "noodles", "spaghetti", "pasta", "lasagne", "daliya", "porridge"
    ]):
        return "Rice & Grains"

    if any(k in name for k in [
        "roti", "chapati", "paratha", "parantha", "poori", "puri", "naan", "kulcha",
        "bhatura", "thepla", "bread", "bun", "loaf", "pizza", "pancake", "toast",
        "scone", "pav "
    ]):
        return "Breads & Flatbreads"

    if any(k in name for k in [
        "idli", "dosa", "uttapam", "upma", "appam", "dhokla", "poha", "chilla",
        "cheela", "muthias", "omelette", "omlet", "waffle", "cereal", "shishu ahar",
        "sajina", "infant food"
    ]):
        return "Breakfast & Tiffin"

    if any(k in name for k in [
        "pakora", "pakoda", "samosa", "cutlet", "tikki", "mathri", "vada", "vadai",
        "patty", "patties", "puff", "croquette", "finger", "roll", "namak para",
        "sev", "bhujia", "crisp", "sandwich", "canape", "fritter", "kachori",
        "straws", "snack", "chaat", "chips", "khakhra", "pav bhaji", "handvo",
        "papdi", "kebab", "gobi 65", "horns"
    ]):
        return "Snacks & Street Food"

    if any(k in name for k in ["soup", "stew", "stock", "consomme", "broth", "shorba"]):
        return "Soups & Stews"

    if any(k in name for k in [
        "curry", "gravy", "korma", "kofta", "masala", "roghan josh", "chops",
        "roast", "bacon", "chicken", "mutton", "meat", "fish", "prawn", "egg",
        "paneer", "keema", "yakhani", "liver", "pork", "sausage", "fricassee",
        "do pyaza", "bhuna", "jalfrezi", "vindaloo"
    ]):
        return "Curries & Gravies"

    if any(k in name for k in [
        "aloo", "potato", "gobhi", "cauliflower", "bhindi", "okra", "baingan",
        "brinjal", "eggplant", "palak", "spinach", "methi", "matar", "pea",
        "cabbage", "carrot", "gourd", "tinda", "karela", "ghia", "lauki",
        "beans", "vegetable", "veg", "thoran", "avial", "saag", "poriyal",
        "capsicum", "turnip", "papaya", "arbi", "kathal", "jackfruit",
        "yam", "suran", "zimikand", "broccoli"
    ]):
        return "Vegetables & Sabzis"

    if any(k in name for k in [
        "chutney", "pickle", "achaar", "achar", "sauce", "ketchup", "raita",
        "masala powder", "baghar", "tadka", "puree", "paste", "dressing",
        "mayonnaise", "dip", "aspic", "panch phoran", "blend", "filling",
        "salad", "salaad"
    ]):
        return "Condiments & Chutneys"

    return "Condiments & Chutneys"


# ---------------------------------------------------------------------------
# 3. Processing INDB Recipes (with Frying Bath Correction)
# ---------------------------------------------------------------------------
def process_indb_corpus():
    print("Processing INDB Corpus (1,014 recipes)...")
    indb_path = os.path.join(DATA_RAW, "indb")
    rec_df = pd.read_excel(os.path.join(indb_path, "recipes.xlsx"))
    rec_df = rec_df[rec_df.recipe_code.notna() & rec_df.food_code.notna()]
    serv_df = pd.read_excel(os.path.join(indb_path, "recipes_servingsize.xlsx")).set_index("recipe_code")
    names_df = pd.read_excel(os.path.join(indb_path, "recipes_names.xlsx")).set_index("recipe_code")

    table = composition.load_table()

    processed_recipes = []
    frying_corrected_count = 0

    for code, grp in rec_df.groupby("recipe_code"):
        name = names_df.loc[code, "recipe_name"] if code in names_df.index else grp.iloc[0]["recipe_name"]
        code_org = names_df.loc[code, "recipe_code_org"] if code in names_df.index else ""
        source = names_df.loc[code, "primarysource"] if code in names_df.index else ""

        category = classify_recipe(code, name, code_org)

        items = []
        lines = []
        skipped_codes = []

        for idx, r in enumerate(grp.itertuples()):
            c = str(r.food_code).strip()
            g = indb_grams(r.amount, r.unit, r.food_code, r.food_name)

            # Preserve frying phrase in raw text if present in amount_org
            raw_text = f"{r.amount} {r.unit} {r.food_name}"
            if pd.notna(r.amount_org) and any(k in str(r.amount_org).lower() for k in ["fry", "frying"]):
                raw_text += f" {r.amount_org}"

            c_list = classify.classes_for(c)
            inc = g is not None and c in table.index
            nuts = composition.nutrients_for(c, g) if inc else None

            line_item = {
                "index": idx,
                "code": c,
                "raw": raw_text,
                "grams": g,
                "classes": c_list,
                "included": inc,
                "exclusion_reason": None if inc else "UNMAPPED",
                "nutrients": nuts,
            }
            lines.append(line_item)

            if inc:
                items.append(line_item)
            else:
                skipped_codes.append(c)

        if not items:
            continue

        # Compute initial totals
        compute_res = compute.sum_nutrients([{"code": i["code"], "grams": i["grams"]} for i in items])
        totals = compute_res["totals"]
        cls_tot = classify.class_totals(items)
        totals["added_sugar_g"] = cls_tot["added_sugar_g"]
        totals["refined_carb_g"] = cls_tot["refined_carb_g"]
        totals["salt_g"] = cls_tot["salt_g"]

        # Servings
        servings = None
        if code in serv_df.index:
            s_val = serv_df.loc[code, "no_of_servings"]
            if pd.notna(s_val):
                try:
                    s_float = float(s_val)
                    if math.isfinite(s_float) and s_float > 0:
                        servings = s_float
                except (ValueError, TypeError):
                    servings = None

        per_serving = (
            {
                k: (v / servings if v is not None and not math.isnan(v) else None)
                for k, v in totals.items()
            }
            if servings is not None
            else None
        )

        fp_general = footprint.footprint(per_serving, setting="urban", risk="general") if per_serving else None
        fp_cardio = footprint.footprint(per_serving, setting="urban", risk="cardiometabolic") if per_serving else None

        pre_result = {
            "recipe": {"id": code, "dish": name, "title": name, "servings": servings},
            "lines": lines,
            "coverage": {
                "included_mass_g": compute_res["total_g"],
                "lines_included": len(items),
                "excluded_by_reason": {},
            },
            "totals": totals,
            "per_serving": per_serving,
            "footprint": fp_general,
            "warnings": [],
        }

        # Apply frying correction
        corrected_gen = correct_frying(pre_result, setting="urban", risk="general")
        corrected_cardio = correct_frying(pre_result, setting="urban", risk="cardiometabolic") if per_serving else None

        final_totals = corrected_gen["totals"]
        final_per_serving = corrected_gen["per_serving"]
        final_fp_gen = corrected_gen["footprint"]
        final_fp_cardio = corrected_cardio["footprint"] if corrected_cardio else None

        fc = corrected_gen.get("frying_correction")
        if fc and fc.get("applied"):
            frying_corrected_count += 1
            absorbed_sfa = fc["absorbed_sfa_g"]
            absorbed_fat = fc["absorbed_fat_g"]
        else:
            absorbed_sfa = 0.0
            absorbed_fat = 0.0

        # Driver decomposition (reflecting frying correction)
        inc_items = [l for l in corrected_gen["lines"] if l.get("included")]
        total_sfa = final_totals.get("sfa_g") or 0.0
        dairy_sfa = sum(i["nutrients"]["sfa_g"] for i in inc_items if "DAIRY_FAT" in i["classes"] and i["nutrients"].get("sfa_g"))
        oil_sfa = sum(i["nutrients"]["sfa_g"] for i in inc_items if "COOKING_OIL" in i["classes"] and i["nutrients"].get("sfa_g")) + absorbed_sfa
        other_sfa = total_sfa - dairy_sfa - oil_sfa
        if other_sfa < 0:
            other_sfa = 0.0

        total_fat = final_totals.get("fat_g") or 0.0
        cls_tot_corr = classify.class_totals(inc_items)
        oil_fat = cls_tot_corr["fat_by_class_g"]["COOKING_OIL"] + absorbed_fat
        dairy_fat = cls_tot_corr["fat_by_class_g"]["DAIRY_FAT"]
        other_fat = total_fat - oil_fat - dairy_fat
        if other_fat < 0:
            other_fat = 0.0

        record = {
            "id": code,
            "title": name,
            "source": str(source),
            "category": category,
            "servings": servings,
            "total_mass_g": corrected_gen["coverage"]["included_mass_g"],
            "totals": final_totals,
            "per_serving": final_per_serving,
            "footprint_general": final_fp_gen,
            "footprint_cardio": final_fp_cardio,
            "frying_correction": fc,
            "drivers": {
                "total_sfa_g": total_sfa,
                "dairy_sfa_g": dairy_sfa,
                "oil_sfa_g": oil_sfa,
                "other_sfa_g": other_sfa,
                "dairy_sfa_pct": (dairy_sfa / total_sfa * 100) if total_sfa > 0 else 0.0,
                "oil_sfa_pct": (oil_sfa / total_sfa * 100) if total_sfa > 0 else 0.0,
                "total_fat_g": total_fat,
                "dairy_fat_g": dairy_fat,
                "oil_fat_g": oil_fat,
                "other_fat_g": other_fat,
                "dairy_fat_pct": (dairy_fat / total_fat * 100) if total_fat > 0 else 0.0,
                "oil_fat_pct": (oil_fat / total_fat * 100) if total_fat > 0 else 0.0,
            },
            "warnings": corrected_gen["warnings"],
            "skipped_codes": skipped_codes,
        }
        processed_recipes.append(record)

    print(f"  Processed {len(processed_recipes)} INDB recipes ({frying_corrected_count} corrected for frying bath).")
    return processed_recipes


# ---------------------------------------------------------------------------
# 4. Processing Web Recipe Corpus (71 Recipes)
# ---------------------------------------------------------------------------
def process_web_corpus():
    print("Processing Web Recipe Corpus (71 recipes)...")
    web_file = os.path.join(DATA_RAW, "../samples/recipes_phase1.jsonl")
    with open(web_file, encoding="utf-8") as f:
        recipes = [json.loads(line) for line in f]

    processed_recipes = []

    for r in recipes:
        dish_name = r.get("dish") or r.get("id")
        category = classify_recipe(r.get("id"), dish_name)

        out_gen = pipeline.analyse_recipe(r, setting="urban", risk="general")
        out_cardio = pipeline.analyse_recipe(r, setting="urban", risk="cardiometabolic")

        totals = out_gen["totals"]
        per_serving = out_gen["per_serving"]

        fc = out_gen.get("frying_correction")
        absorbed_sfa = fc["absorbed_sfa_g"] if (fc and fc.get("applied")) else 0.0
        absorbed_fat = fc["absorbed_fat_g"] if (fc and fc.get("applied")) else 0.0

        # Driver decomposition: SFA and Fat by class
        inc_items = [l for l in out_gen["lines"] if l["included"]]
        total_sfa = totals.get("sfa_g") or 0.0
        dairy_sfa = sum(i["nutrients"]["sfa_g"] for i in inc_items if "DAIRY_FAT" in i["classes"] and i["nutrients"].get("sfa_g"))
        oil_sfa = sum(i["nutrients"]["sfa_g"] for i in inc_items if "COOKING_OIL" in i["classes"] and i["nutrients"].get("sfa_g")) + absorbed_sfa
        other_sfa = total_sfa - dairy_sfa - oil_sfa
        if other_sfa < 0:
            other_sfa = 0.0

        total_fat = totals.get("fat_g") or 0.0
        cls_tot = classify.class_totals(inc_items)
        oil_fat = cls_tot["fat_by_class_g"]["COOKING_OIL"] + absorbed_fat
        dairy_fat = cls_tot["fat_by_class_g"]["DAIRY_FAT"]
        other_fat = total_fat - oil_fat - dairy_fat
        if other_fat < 0:
            other_fat = 0.0

        record = {
            "id": r.get("id"),
            "dish": r.get("dish"),
            "site": r.get("site"),
            "url": r.get("url"),
            "category": category,
            "servings": r.get("servings"),
            "coverage": out_gen["coverage"],
            "totals": totals,
            "per_serving": per_serving,
            "footprint_general": out_gen["footprint"],
            "footprint_cardio": out_cardio["footprint"],
            "frying_correction": fc,
            "drivers": {
                "total_sfa_g": total_sfa,
                "dairy_sfa_g": dairy_sfa,
                "oil_sfa_g": oil_sfa,
                "other_sfa_g": other_sfa,
                "dairy_sfa_pct": (dairy_sfa / total_sfa * 100) if total_sfa > 0 else 0.0,
                "oil_sfa_pct": (oil_sfa / total_sfa * 100) if total_sfa > 0 else 0.0,
                "total_fat_g": total_fat,
                "dairy_fat_g": dairy_fat,
                "oil_fat_g": oil_fat,
                "other_fat_g": other_fat,
                "dairy_fat_pct": (dairy_fat / total_fat * 100) if total_fat > 0 else 0.0,
                "oil_fat_pct": (oil_fat / total_fat * 100) if total_fat > 0 else 0.0,
            },
            "warnings": out_gen["warnings"],
        }
        processed_recipes.append(record)

    print(f"  Processed {len(processed_recipes)} web recipes successfully.")
    return processed_recipes


# ---------------------------------------------------------------------------
# 5. Statistical Aggregations by Dish Category
# ---------------------------------------------------------------------------
def compute_category_statistics(recipes):
    """Compute median, IQR, and driver shares for each dish category."""
    cat_data = {c: [] for c in CATEGORIES}

    for r in recipes:
        cat = r["category"]
        if cat in cat_data and r.get("per_serving") is not None:
            ps = r["per_serving"]
            fp_gen = r.get("footprint_general")
            fp_car = r.get("footprint_cardio")

            if fp_gen and fp_car:
                axes_gen = fp_gen["axes"]
                axes_car = fp_car["axes"]

                cat_data[cat].append({
                    "id": r["id"],
                    "sfa_g": ps.get("sfa_g", 0.0),
                    "sfa_pct_gen": axes_gen["sfa_g"]["pct_of_limit"],
                    "sfa_pct_car": axes_car["sfa_g"]["pct_of_limit"],
                    "sfa_pct_energy": axes_gen["sfa_g"]["pct_energy"],
                    "fat_g": ps.get("fat_g", 0.0),
                    "fat_pct_limit": axes_gen["fat_g"]["pct_of_limit"],
                    "fat_pct_energy": axes_gen["fat_g"]["pct_energy"],
                    "added_sugar_g": ps.get("added_sugar_g", 0.0),
                    "sugar_pct_limit": axes_gen["added_sugar_g"]["pct_of_limit"],
                    "sodium_mg": ps.get("sodium_mg", 0.0),
                    "sodium_pct_limit": axes_gen["sodium_mg"]["pct_of_limit"],
                    "refined_carb_g": ps.get("refined_carb_g", 0.0),
                    "energy_kcal": ps.get("energy_kcal", 0.0),
                    "energy_pct_limit": axes_gen["energy_kcal"]["pct_of_limit"],
                    "protein_g": ps.get("protein_g", 0.0),
                    "dairy_sfa_pct": r["drivers"]["dairy_sfa_pct"],
                    "oil_sfa_pct": r["drivers"]["oil_sfa_pct"],
                    "dairy_fat_pct": r["drivers"]["dairy_fat_pct"],
                    "oil_fat_pct": r["drivers"]["oil_fat_pct"],
                })

    rows = []
    driver_rows = []

    for cat in CATEGORIES:
        items = cat_data[cat]
        n_servings = len(items)
        n_total = sum(1 for r in recipes if r["category"] == cat)

        if n_servings == 0:
            continue

        df = pd.DataFrame(items)

        def q25(s): return s.quantile(0.25)
        def q75(s): return s.quantile(0.75)

        row = {
            "category": cat,
            "recipes_total": n_total,
            "recipes_with_servings": n_servings,
            # SFA
            "sfa_g_median": round(df["sfa_g"].median(), 2),
            "sfa_g_q25": round(q25(df["sfa_g"]), 2),
            "sfa_g_q75": round(q75(df["sfa_g"]), 2),
            "sfa_pct_gen_limit_median": round(df["sfa_pct_gen"].median(), 1),
            "sfa_pct_car_limit_median": round(df["sfa_pct_car"].median(), 1),
            "sfa_pct_energy_median": round(df["sfa_pct_energy"].median(), 1),
            # Total Fat
            "fat_g_median": round(df["fat_g"].median(), 2),
            "fat_pct_limit_median": round(df["fat_pct_limit"].median(), 1),
            "fat_pct_energy_median": round(df["fat_pct_energy"].median(), 1),
            # Added Sugar
            "added_sugar_g_median": round(df["added_sugar_g"].median(), 2),
            "sugar_pct_limit_median": round(df["sugar_pct_limit"].median(), 1),
            # Sodium
            "sodium_mg_median": round(df["sodium_mg"].median(), 1),
            "sodium_pct_limit_median": round(df["sodium_pct_limit"].median(), 1),
            # Energy & Refined Carb
            "refined_carb_g_median": round(df["refined_carb_g"].median(), 1),
            "energy_kcal_median": round(df["energy_kcal"].median(), 1),
            "energy_pct_limit_median": round(df["energy_pct_limit"].median(), 1),
            "protein_g_median": round(df["protein_g"].median(), 1),
        }
        rows.append(row)

        driver_row = {
            "category": cat,
            "recipes_analyzed": n_servings,
            "sfa_from_dairy_pct_mean": round(df["dairy_sfa_pct"].mean(), 1),
            "sfa_from_oil_pct_mean": round(df["oil_sfa_pct"].mean(), 1),
            "sfa_from_other_pct_mean": round(max(0, 100 - df["dairy_sfa_pct"].mean() - df["oil_sfa_pct"].mean()), 1),
            "fat_from_dairy_pct_mean": round(df["dairy_fat_pct"].mean(), 1),
            "fat_from_oil_pct_mean": round(df["oil_fat_pct"].mean(), 1),
            "fat_from_other_pct_mean": round(max(0, 100 - df["dairy_fat_pct"].mean() - df["oil_fat_pct"].mean()), 1),
        }
        driver_rows.append(driver_row)

    summary_df = pd.DataFrame(rows)
    drivers_df = pd.DataFrame(driver_rows)
    return summary_df, drivers_df


# ---------------------------------------------------------------------------
# 6. Paired Textbook vs Web Recipes Comparison
# ---------------------------------------------------------------------------
def compute_textbook_vs_web(indb_recipes, web_recipes):
    """Direct paired comparison for shared dishes between INDB and Web corpus."""
    benchmarks = {
        "paneer butter masala": {
            # INDB lacks exact Paneer Butter Masala; use nearest rich paneer gravies (excl. toast sandwich ASC042 & 502g-fat ASC225)
            "indb_codes": ["ASC221", "ASC195"],
            "web_dish": "paneer butter masala",
            "web_frying_unquantified": False,
        },
        "dal makhani": {
            "indb_codes": ["OSR139"],
            "web_dish": "dal makhani",
            "web_frying_unquantified": False,
        },
        "chole": {
            # Exact Safed Channa (white chickpea) curry in INDB
            "indb_codes": ["ASC162"],
            "web_dish": "chole",
            "web_frying_unquantified": False,
        },
        "gajar ka halwa": {
            # Exact Carrot halwa (ASC295) instead of Date & nut pie (ASC329)
            "indb_codes": ["ASC295"],
            "web_dish": "gajar ka halwa",
            "web_frying_unquantified": False,
        },
        "gulab jamun": {
            "indb_codes": ["ASC348", "BFP386"],
            "web_dish": "gulab jamun",
            "web_frying_unquantified": True,
        },
        "samosa": {
            "indb_codes": ["ASC361", "ASC362"],
            "web_dish": "samosa",
            "web_frying_unquantified": True,
        },
        "chicken biryani": {
            # INDB lacks Chicken Biryani; nearest meat/veg biryani baselines (excl. channa pulao BFP138)
            "indb_codes": ["ASC122", "ASC123"],
            "web_dish": "chicken biryani",
            "web_frying_unquantified": False,
        },
        "sambar": {
            "indb_codes": ["ASC167"],
            "web_dish": "sambar",
            "web_frying_unquantified": False,
        },
        "poha": {
            "indb_codes": ["ASC469"],  # Standard Sprouted Moong Poha
            "web_dish": "poha",
            "web_frying_unquantified": False,
        },
        "butter chicken": {
            "indb_codes": ["ASC242"],
            "web_dish": "butter chicken",
            "web_frying_unquantified": False,
        },
        "methi aloo": {
            "indb_codes": ["ASC175"],
            "web_dish": "methi aloo",
            "web_frying_unquantified": False,
        },
        "bhindi sabzi": {
            "indb_codes": ["BFP269", "ASC184"],
            "web_dish": "bhindi sabzi",
            "web_frying_unquantified": False,
        },
        "onion pakora": {
            "indb_codes": ["ASC352"],
            "web_dish": "onion pakora",
            "web_frying_unquantified": True,
        },
        "sarson ka saag": {
            "indb_codes": ["ASC217"],
            "web_dish": "saag",
            "web_frying_unquantified": False,
        },
        "vegetable pulao": {
            "indb_codes": ["ASC114", "ASC115"],
            "web_dish": "vegetable pilau",
            "web_frying_unquantified": False,
        },
    }

    indb_by_code = {r["id"]: r for r in indb_recipes}
    web_by_dish = {}
    for r in web_recipes:
        d = r.get("dish")
        if d not in web_by_dish:
            web_by_dish[d] = []
        web_by_dish[d].append(r)

    comparison_rows = []

    for label, config in benchmarks.items():
        w_list = web_by_dish.get(config["web_dish"], [])
        if not w_list:
            continue

        # Deduplicate duplicate portal URLs (e.g., D1-18 and V2-R08)
        w_valid = []
        seen_urls = set()
        for w in w_list:
            if w.get("per_serving") is None:
                continue
            url = (w.get("url") or "").strip().rstrip("/")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            w_valid.append(w)
        if not w_valid:
            continue

        i_valid = [indb_by_code[c] for c in config["indb_codes"] if c in indb_by_code and indb_by_code[c].get("per_serving") is not None]
        if not i_valid:
            continue

        w_fat = np.median([w["per_serving"]["fat_g"] for w in w_valid])
        w_sfa = np.median([w["per_serving"]["sfa_g"] for w in w_valid])
        w_sugar = np.median([w["per_serving"]["added_sugar_g"] for w in w_valid])
        w_sodium = np.median([w["per_serving"]["sodium_mg"] for w in w_valid])
        w_energy = np.median([w["per_serving"]["energy_kcal"] for w in w_valid])

        i_fat = np.median([i["per_serving"]["fat_g"] for i in i_valid])
        i_sfa = np.median([i["per_serving"]["sfa_g"] for i in i_valid])
        i_sugar = np.median([i["per_serving"]["added_sugar_g"] for i in i_valid])
        i_sodium = np.median([i["per_serving"]["sodium_mg"] for i in i_valid])
        i_energy = np.median([i["per_serving"]["energy_kcal"] for i in i_valid])

        fat_ratio = (w_fat / i_fat) if i_fat > 0 else np.nan
        sfa_ratio = (w_sfa / i_sfa) if i_sfa > 0 else np.nan
        energy_ratio = (w_energy / i_energy) if i_energy > 0 else np.nan

        comparison_rows.append({
            "dish": label,
            "indb_recipes_count": len(i_valid),
            "web_recipes_count": len(w_valid),
            "web_frying_unquantified": bool(config.get("web_frying_unquantified", False)),
            # Fat
            "indb_fat_g": round(i_fat, 2),
            "web_fat_g": round(w_fat, 2),
            "fat_inflation_ratio": round(fat_ratio, 2),
            # SFA
            "indb_sfa_g": round(i_sfa, 2),
            "web_sfa_g": round(w_sfa, 2),
            "sfa_inflation_ratio": round(sfa_ratio, 2),
            # Sugar & Sodium
            "indb_sugar_g": round(i_sugar, 2),
            "web_sugar_g": round(w_sugar, 2),
            "indb_sodium_mg": round(i_sodium, 1),
            "web_sodium_mg": round(w_sodium, 1),
            # Energy
            "indb_energy_kcal": round(i_energy, 1),
            "web_energy_kcal": round(w_energy, 1),
            "energy_inflation_ratio": round(energy_ratio, 2),
        })

    comp_df = pd.DataFrame(comparison_rows)
    return comp_df


# ---------------------------------------------------------------------------
# 7. Figure Generation (Publication Quality)
# ---------------------------------------------------------------------------
def generate_atlas_figures(summary_df, drivers_df, comp_df):
    print("Generating Publication-Quality Visual Figures...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # FIGURE 1: Cardiometabolic Budget Consumption across Dish Categories (clipped x-axis for Soups artifact)
    fig, ax = plt.subplots(figsize=(12.5, 7.6))
    df_sorted = summary_df.sort_values("sfa_pct_gen_limit_median", ascending=True).copy()
    y_pos = np.arange(len(df_sorted))

    bar_width = 0.25
    cap_x = 108.0
    sfa_vals = df_sorted["sfa_pct_gen_limit_median"].values
    sug_vals = df_sorted["sugar_pct_limit_median"].values
    na_vals = df_sorted["sodium_pct_limit_median"].values
    na_clipped = np.minimum(na_vals, cap_x)

    ax.barh(y_pos + bar_width, sfa_vals, bar_width, label="Saturated Fat (% of 24.9g <10%E Limit)", color="#D9534F")
    ax.barh(y_pos, sug_vals, bar_width, label="Added Sugar (% of 25.0g WHO Limit)", color="#F0AD4E")
    ax.barh(y_pos - bar_width, na_clipped, bar_width, label="Sodium (% of 1,967mg Salt Limit)", color="#0275D8")

    # Value labels + broken-bar annotation for off-scale Soups & Stews sodium
    for idx, (sfa_v, sug_v, na_v) in enumerate(zip(sfa_vals, sug_vals, na_vals)):
        if sfa_v >= 10:
            ax.text(sfa_v + 1.2, idx + bar_width, f"{sfa_v:.1f}%", va="center", fontsize=8.5, color="#9E2A2B", fontweight="bold")
        if sug_v >= 10:
            ax.text(sug_v + 1.2, idx, f"{sug_v:.1f}%", va="center", fontsize=8.5, color="#9C6500", fontweight="bold")
        if na_v > cap_x:
            # Visual diagonal break lines near the clipped bar tip
            bx = cap_x - 2.2
            by = idx - bar_width
            ax.plot([bx - 1.2, bx + 1.2], [by - 0.11, by + 0.11], color="white", linewidth=3.2, zorder=5)
            ax.plot([bx + 0.6, bx + 3.0], [by - 0.11, by + 0.11], color="white", linewidth=3.2, zorder=5)
            ax.text(cap_x + 1.4, by, f"{na_v:,.1f}% (off-scale: 26/47 INDB K506/K507 stock-cube coding)", va="center", fontsize=8.5, color="#014C8C", fontweight="bold")
        elif na_v >= 10:
            ax.text(na_v + 1.2, idx - bar_width, f"{na_v:.1f}%", va="center", fontsize=8.5, color="#014C8C")

    ax.axvline(33.3, color="#6C757D", linestyle=":", linewidth=1.3, alpha=0.85, label="33% One-Meal Target")
    ax.axvline(100, color="#C9302C", linestyle="--", linewidth=1.5, alpha=0.85, label="100% Daily Limit")

    ax.set_xlim(0, 192)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_sorted["category"], fontsize=11, fontweight="medium")
    ax.set_xlabel("Median Percentage of Daily Budget per Serving (%, X-axis broken above 108%)", fontsize=11.5, fontweight="bold")
    ax.set_title("Cardiometabolic Budget Consumption Across 11 Indian Culinary Categories\n(932 INDB Recipes with Verified Servings · ICMR-NIN 2024 / WHO Thresholds)", fontsize=13, fontweight="bold", pad=54)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.015), ncol=3, frameon=True, fontsize=9.5)
    plt.tight_layout()
    fig1_path_png = os.path.join(ATLAS_DIR, "fig1_category_footprint_bars.png")
    fig1_path_svg = os.path.join(ATLAS_DIR, "fig1_category_footprint_bars.svg")
    plt.savefig(fig1_path_png, dpi=300)
    plt.savefig(fig1_path_svg)
    plt.close()
    print(f"  Saved Figure 1 to {fig1_path_png}")

    # FIGURE 2: Culprit Decomposition (Dairy Fat vs Cooking Oil vs Other)
    fig, ax = plt.subplots(figsize=(12.5, 7.6))
    drv_sorted = drivers_df.set_index("category").loc[df_sorted["category"]].reset_index()

    d_sfa = drv_sorted["sfa_from_dairy_pct_mean"].values
    o_sfa = drv_sorted["sfa_from_oil_pct_mean"].values
    r_sfa = drv_sorted["sfa_from_other_pct_mean"].values

    ax.barh(y_pos, d_sfa, color="#F7B731", label="Dairy Fat (Ghee, Butter, Cream, Paneer)")
    ax.barh(y_pos, o_sfa, left=d_sfa, color="#E17055", label="Cooking Oil (Oil + Frying Absorption)")
    ax.barh(y_pos, r_sfa, left=d_sfa + o_sfa, color="#74B9FF", label="Inherent Food SFA (Pulses, Grains, Veg, Meat, Coconut)")

    for idx, (dv, ov, rv) in enumerate(zip(d_sfa, o_sfa, r_sfa)):
        if dv >= 11:
            ax.text(dv / 2, idx, f"{dv:.1f}%", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#222")
        if ov >= 11:
            ax.text(dv + ov / 2, idx, f"{ov:.1f}%", ha="center", va="center", fontsize=8.5, fontweight="bold", color="white")
        if rv >= 11:
            ax.text(dv + ov + rv / 2, idx, f"{rv:.1f}%", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#112233")

    ax.set_xlim(0, 100)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(drv_sorted["category"], fontsize=11, fontweight="medium")
    ax.set_xlabel("Mean Share of Total Recipe Saturated Fat (%)", fontsize=11.5, fontweight="bold")
    ax.set_title("Culprit Decomposition: What Drives Saturated Fat Across Indian Cuisine?\n(Dairy Fat vs. Cooking Oil vs. Inherent Ingredient SFA)", fontsize=13, fontweight="bold", pad=34)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=3, frameon=True, fontsize=9.5)
    plt.tight_layout()
    fig2_path_png = os.path.join(ATLAS_DIR, "fig2_culprit_decomposition.png")
    fig2_path_svg = os.path.join(ATLAS_DIR, "fig2_culprit_decomposition.svg")
    plt.savefig(fig2_path_png, dpi=300)
    plt.savefig(fig2_path_svg)
    plt.close()
    print(f"  Saved Figure 2 to {fig2_path_png}")

    # FIGURE 3: Textbook vs Web Recipe Inflation Factor
    fig, ax = plt.subplots(figsize=(12.5, 8.2))
    comp_sorted = comp_df.sort_values("fat_inflation_ratio", ascending=True).copy()
    y_pos_c = np.arange(len(comp_sorted))

    ax.scatter(comp_sorted["indb_fat_g"], y_pos_c, color="#2E86AB", s=105, label="Textbook Formulation (INDB)", zorder=4)
    ax.scatter(comp_sorted["web_fat_g"], y_pos_c, color="#E63946", s=105, label="Popular Web Recipe (Median)", zorder=4)

    y_labels = []
    max_x = max(comp_sorted["indb_fat_g"].max(), comp_sorted["web_fat_g"].max())
    for idx, row in enumerate(comp_sorted.itertuples()):
        is_unq = bool(getattr(row, "web_frying_unquantified", False))
        lbl = f"{row.dish} *" if is_unq else row.dish
        y_labels.append(lbl)
        if is_unq:
            ax.axhspan(idx - 0.38, idx + 0.38, color="#FFF3CD", alpha=0.45, zorder=1)
        ax.plot([row.indb_fat_g, row.web_fat_g], [idx, idx], color="#888888", linestyle="--" if is_unq else "-", linewidth=2, zorder=2)
        ratio_str = f"{row.fat_inflation_ratio:.2f}x" + (" (unquantified web fry oil)" if is_unq else "")
        txt_col = "#8A5A00" if is_unq else ("#A8201A" if row.fat_inflation_ratio > 1.25 else ("#1E7E34" if row.fat_inflation_ratio < 0.8 else "#495057"))
        ax.text(max(row.indb_fat_g, row.web_fat_g) + 1.0, idx, ratio_str, va="center", fontsize=9.5, fontweight="bold", color=txt_col)

    ax.set_xlim(0, max_x * 1.36)
    ax.set_yticks(y_pos_c)
    ax.set_yticklabels(y_labels, fontsize=11, fontweight="medium")
    ax.set_xlabel("Fat Content per Serving (g)", fontsize=11.5, fontweight="bold")
    ax.set_title("Textbook (INDB) vs. Web Recipe Fat per Serving Across 15 Benchmark Dishes\n(* Shaded rows: Web recipes list 'oil for deep frying' unquantified, so Soxhlet fry-oil injection is omitted)", fontsize=12.5, fontweight="bold", pad=34)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=True, fontsize=10.5)
    plt.tight_layout()
    fig3_path_png = os.path.join(ATLAS_DIR, "fig3_textbook_vs_web_inflation.png")
    fig3_path_svg = os.path.join(ATLAS_DIR, "fig3_textbook_vs_web_inflation.svg")
    plt.savefig(fig3_path_png, dpi=300)
    plt.savefig(fig3_path_svg)
    plt.close()
    print(f"  Saved Figure 3 to {fig3_path_png}")

    # FIGURE 4: Cardiometabolic Risk Matrix (Liver Axes: SFA vs Added Sugar)
    fig, ax = plt.subplots(figsize=(11, 7.6))
    # Custom label offsets so clustered zero-sugar categories never overlap
    label_offsets = {
        "Snacks & Street Food": (1.6, 0.8, "left"),
        "Sweets & Desserts": (-1.5, -2.5, "right"),
        "Curries & Gravies": (1.6, 0.8, "left"),
        "Rice & Grains": (1.5, 0.5, "left"),
        "Vegetables & Sabzis": (2.2, 1.2, "left"),
        "Breakfast & Tiffin": (2.2, -1.6, "left"),
        "Breads & Flatbreads": (1.8, 0.5, "left"),
        "Soups & Stews": (2.2, 0.9, "left"),
        "Condiments & Chutneys": (1.8, -1.6, "left"),
        "Beverages": (-1.5, 0.9, "right"),
        "Dals & Legumes": (1.6, -1.2, "left"),
    }
    for _, row in summary_df.iterrows():
        cat = row["category"]
        x_val = row["sugar_pct_limit_median"]
        y_val = row["sfa_pct_gen_limit_median"]
        ax.scatter(x_val, y_val, s=row["recipes_total"] * 2.2, alpha=0.72, edgecolors="black", linewidth=1.3, zorder=3)
        dx, dy, ha = label_offsets.get(cat, (1.5, 0.5, "left"))
        ax.annotate(
            cat,
            xy=(x_val, y_val),
            xytext=(x_val + dx, y_val + dy),
            ha=ha,
            va="center",
            fontsize=9.5,
            fontweight="medium",
            arrowprops=dict(arrowstyle="-", color="#999999", lw=0.7, alpha=0.7) if abs(dx) > 1.7 or abs(dy) > 1.1 else None,
            zorder=5,
        )

    ax.axhline(33.3, color="#E63946", linestyle="--", linewidth=1.2, alpha=0.75, label="33% Single-Meal SFA Ceiling")
    ax.axvline(33.3, color="#F77F00", linestyle="--", linewidth=1.2, alpha=0.75, label="33% Single-Meal Added Sugar Ceiling")

    ax.set_xlim(-6, 74)
    ax.set_ylim(-2, 41)
    ax.set_xlabel("Added Sugar Load (% of 25.0g WHO Daily Limit)", fontsize=11.5, fontweight="bold")
    ax.set_ylabel("Saturated Fat Load (% of 24.9g ICMR-NIN <10%E Limit)", fontsize=11.5, fontweight="bold")
    ax.set_title("The Dual-Organ Risk Matrix: Saturated Fat vs. Added Sugar Burden\n(Bubble area proportional to recipe count; dashed lines mark 1-meal 33% share)", fontsize=12.5, fontweight="bold", pad=15)
    ax.legend(loc="upper right", frameon=True, fontsize=10)
    plt.tight_layout()
    fig4_path_png = os.path.join(ATLAS_DIR, "fig4_liver_risk_matrix.png")
    fig4_path_svg = os.path.join(ATLAS_DIR, "fig4_liver_risk_matrix.svg")
    plt.savefig(fig4_path_png, dpi=300)
    plt.savefig(fig4_path_svg)
    plt.close()
    print(f"  Saved Figure 4 to {fig4_path_png}")


# ---------------------------------------------------------------------------
# 8. Master Runner
# ---------------------------------------------------------------------------
def run_atlas():
    print("=" * 70)
    print("DELIVERABLE 3: LIVER AND HEART FOOTPRINT ATLAS GENERATION")
    print("=" * 70)

    # 1. Process INDB
    indb_recipes = process_indb_corpus()
    with open(os.path.join(ATLAS_DIR, "atlas_indb_recipes.json"), "w", encoding="utf-8") as f:
        json.dump(indb_recipes, f, indent=2)

    # 2. Process Web Corpus
    web_recipes = process_web_corpus()
    with open(os.path.join(ATLAS_DIR, "atlas_web_recipes.json"), "w", encoding="utf-8") as f:
        json.dump(web_recipes, f, indent=2)

    # 3. Compute Category Statistics
    summary_df, drivers_df = compute_category_statistics(indb_recipes)
    summary_csv = os.path.join(ATLAS_DIR, "atlas_category_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"Saved Category Summary to {summary_csv}")

    drivers_csv = os.path.join(ATLAS_DIR, "atlas_drivers_by_category.csv")
    drivers_df.to_csv(drivers_csv, index=False)
    print(f"Saved Drivers Summary to {drivers_csv}")

    # 4. Compute Paired Textbook vs Web
    comp_df = compute_textbook_vs_web(indb_recipes, web_recipes)
    comp_csv = os.path.join(ATLAS_DIR, "atlas_textbook_vs_web.csv")
    comp_df.to_csv(comp_csv, index=False)
    print(f"Saved Textbook vs Web Comparison to {comp_csv}")

    # 5. Generate Figures
    generate_atlas_figures(summary_df, drivers_df, comp_df)

    # 6. Overall Metrics Snapshot
    frying_count = sum(1 for r in indb_recipes if r.get("frying_correction") and r["frying_correction"].get("applied"))
    comp_clean = comp_df[~comp_df["web_frying_unquantified"]]
    overall_metrics = {
        "indb_recipes_total": len(indb_recipes),
        "indb_recipes_with_servings": sum(1 for r in indb_recipes if r.get("servings") is not None),
        "indb_recipes_corrected_for_frying": frying_count,
        "web_recipes_total": len(web_recipes),
        "categories_count": len(CATEGORIES),
        "highest_sfa_category": summary_df.loc[summary_df["sfa_pct_gen_limit_median"].idxmax()]["category"],
        "highest_sfa_median_pct": float(summary_df["sfa_pct_gen_limit_median"].max()),
        "highest_sugar_category": summary_df.loc[summary_df["sugar_pct_limit_median"].idxmax()]["category"],
        "highest_sugar_median_pct": float(summary_df["sugar_pct_limit_median"].max()),
        "highest_sodium_category": summary_df.loc[summary_df["sodium_pct_limit_median"].idxmax()]["category"],
        "highest_sodium_median_pct": float(summary_df["sodium_pct_limit_median"].max()),
        "overall_median_fat_inflation": round(float(comp_clean["fat_inflation_ratio"].median()), 2),
        "overall_median_sfa_inflation": round(float(comp_clean["sfa_inflation_ratio"].median()), 2),
        "overall_median_energy_inflation": round(float(comp_clean["energy_inflation_ratio"].median()), 2),
        "overall_median_fat_inflation_all15": round(float(comp_df["fat_inflation_ratio"].median()), 2),
        "overall_median_sfa_inflation_all15": round(float(comp_df["sfa_inflation_ratio"].median()), 2),
        "overall_median_energy_inflation_all15": round(float(comp_df["energy_inflation_ratio"].median()), 2),
    }
    metrics_json = os.path.join(ATLAS_DIR, "atlas_metrics.json")
    with open(metrics_json, "w", encoding="utf-8") as f:
        json.dump(overall_metrics, f, indent=2)
    print(f"Saved Atlas Metrics to {metrics_json}")

    # 7. Sync static figures and atlas_data.js into app/static/
    app_fig_dir = os.path.join(BASE_DIR, "app", "static", "figures")
    if os.path.isdir(app_fig_dir):
        for fn in (
            "fig1_category_footprint_bars.png",
            "fig2_culprit_decomposition.png",
            "fig3_textbook_vs_web_inflation.png",
            "fig4_liver_risk_matrix.png",
        ):
            src_png = os.path.join(ATLAS_DIR, fn)
            if os.path.exists(src_png):
                shutil.copy2(src_png, os.path.join(app_fig_dir, fn))
        print(f"Synced 4 PNG figures to {app_fig_dir}")

    atlas_js_path = os.path.join(BASE_DIR, "app", "static", "js", "atlas_data.js")
    if os.path.isdir(os.path.dirname(atlas_js_path)):
        def _stringify_records(df_in):
            return [{k: str(v) for k, v in rec.items()} for rec in df_in.to_dict(orient="records")]

        atlas_payload = {
            "metrics": overall_metrics,
            "categories": _stringify_records(summary_df),
            "textbook_vs_web": _stringify_records(comp_df),
            "drivers": _stringify_records(drivers_df),
        }
        with open(atlas_js_path, "w", encoding="utf-8") as f:
            f.write("window.ATLAS_DATA = " + json.dumps(atlas_payload, indent=2) + ";\n")
        print(f"Synced Atlas JS payload to {atlas_js_path}")

    print("\nAtlas Generation Complete!")
    print(f"Key Findings:")
    print(f"  Frying Corrections Applied: {overall_metrics['indb_recipes_corrected_for_frying']} recipes")
    print(f"  Highest SFA Category: {overall_metrics['highest_sfa_category']} ({overall_metrics['highest_sfa_median_pct']:.1f}% of daily limit per serving)")
    print(f"  Highest Sugar Category: {overall_metrics['highest_sugar_category']} ({overall_metrics['highest_sugar_median_pct']:.1f}% of daily limit per serving)")
    print(f"  Highest Sodium Category: {overall_metrics['highest_sodium_category']} ({overall_metrics['highest_sodium_median_pct']:.1f}% of daily limit per serving)")
    print(f"  Web vs Textbook Fat Inflation: {overall_metrics['overall_median_fat_inflation']:.2f}x median")
    print(f"  Web vs Textbook SFA Inflation: {overall_metrics['overall_median_sfa_inflation']:.2f}x median")


if __name__ == "__main__":
    run_atlas()
