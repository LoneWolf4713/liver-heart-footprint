import json
import re
import os
import time
import pandas as pd
from t1_extract import parse_page_data, classify_ingredient, is_recipe_deep_fried

def run_t1():
    url_file = "data/t1_dish_urls.json"
    if not os.path.exists(url_file):
        print("URL file not found yet.")
        return

    with open(url_file, "r") as f:
        url_map = json.load(f)

    recipes_records = []
    ingredient_records = []

    total_dishes = 0
    for site_key, dishes in url_map.items():
        print(f"\n================ Processing Site: {site_key} ================")
        for dish_id, info in dishes.items():
            url = info.get("url")
            dish_name = info.get("dish_name", dish_id)
            is_sub = info.get("substituted", False)
            total_dishes += 1

            if not url:
                print(f"Skipping {dish_id} (No URL found)")
                recipes_records.append({
                    "site": site_key,
                    "dish_id": dish_id,
                    "dish_name": dish_name,
                    "url": "",
                    "has_jsonld": False,
                    "recipe_title": "",
                    "servings": "",
                    "ingredient_count": 0,
                    "nutrition_present": False,
                    "is_deep_fried": False,
                    "frying_oil_quantified": False,
                    "fetch_status": "No URL found"
                })
                continue

            print(f"Fetching [{dish_id}] {url} ...")
            data, status = parse_page_data(url)
            time.sleep(1.0) # Polite crawling <= 1 req/sec

            if not data:
                print(f"  -> Failed: {status}")
                recipes_records.append({
                    "site": site_key,
                    "dish_id": dish_id,
                    "dish_name": dish_name,
                    "url": url,
                    "has_jsonld": False,
                    "recipe_title": "",
                    "servings": "",
                    "ingredient_count": 0,
                    "nutrition_present": False,
                    "is_deep_fried": False,
                    "frying_oil_quantified": False,
                    "fetch_status": status
                })
                continue

            # Recipe JSON-LD found
            title = data.get("name", "")
            raw_yield = data.get("recipeYield", "")
            if isinstance(raw_yield, list):
                raw_yield = raw_yield[0] if raw_yield else ""
            servings = str(raw_yield).strip()
            
            raw_ingrs = data.get("recipeIngredient", [])
            ingr_count = len(raw_ingrs)
            nutrition_present = "nutrition" in data and bool(data["nutrition"])

            # Check instructions for deep frying
            instructions = data.get("recipeInstructions", "")
            instr_text = ""
            if isinstance(instructions, list):
                for item in instructions:
                    if isinstance(item, dict):
                        instr_text += " " + str(item.get("text", ""))
                    elif isinstance(item, str):
                        instr_text += " " + item
            elif isinstance(instructions, str):
                instr_text = instructions

            deep_fried = is_recipe_deep_fried(instr_text, title)

            # Process ingredient lines
            frying_oil_quantified = False
            for line in raw_ingrs:
                st, is_liver, cat = classify_ingredient(line)
                
                # Check if this line is frying oil
                if "oil" in line.lower() and any(k in line.lower() for k in ["fry", "deep fry"]):
                    if st in ["exact", "range"]:
                        frying_oil_quantified = True

                ingredient_records.append({
                    "site": site_key,
                    "dish_id": dish_id,
                    "dish_name": dish_name,
                    "url": url,
                    "ingredient_line": line,
                    "quantity_status": st,
                    "is_liver_relevant": is_liver,
                    "liver_category": cat,
                    "is_deep_fried_recipe": deep_fried
                })

            recipes_records.append({
                "site": site_key,
                "dish_id": dish_id,
                "dish_name": dish_name,
                "url": url,
                "has_jsonld": True,
                "recipe_title": title,
                "servings": servings,
                "ingredient_count": ingr_count,
                "nutrition_present": nutrition_present,
                "is_deep_fried": deep_fried,
                "frying_oil_quantified": frying_oil_quantified,
                "fetch_status": "OK"
            })

    # Save outputs
    df_recipes = pd.DataFrame(recipes_records)
    df_ingrs = pd.DataFrame(ingredient_records)

    df_recipes.to_csv("data/t1_recipes.csv", index=False)
    df_ingrs.to_csv("data/t1_ingredient_lines.csv", index=False)

    print("\nSaved data/t1_recipes.csv and data/t1_ingredient_lines.csv!")
    print(f"Total recipes recorded: {len(df_recipes)}")
    print(f"Total ingredient lines recorded: {len(df_ingrs)}")

if __name__ == "__main__":
    run_t1()
