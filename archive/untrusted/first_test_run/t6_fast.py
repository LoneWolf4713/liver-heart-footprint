import requests
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
import re

URLS_TO_TEST = [
    ("paneer_butter_masala", "Tarla Dalal", "https://www.tarladalal.com/paneer-butter-masala-38973r"),
    ("dal_makhani", "Tarla Dalal", "https://www.tarladalal.com/dal-makhani/"),
    ("chole", "Tarla Dalal", "https://www.tarladalal.com/chole/"),
    ("samosa", "Tarla Dalal", "https://www.tarladalal.com/samosa/"),
    ("bhatura", "Tarla Dalal", "https://www.tarladalal.com/punjabi-bhatura/"),
    ("paneer_butter_masala", "VegRecipesOfIndia", "https://www.vegrecipesofindia.com/paneer-butter-masala/"),
    ("dal_makhani", "VegRecipesOfIndia", "https://www.vegrecipesofindia.com/dal-makhani-restaurant-style-recipe/"),
    ("chole", "VegRecipesOfIndia", "https://www.vegrecipesofindia.com/punjabi-chole-chickpeas-in-a-spicy-gravy/"),
    ("paneer_butter_masala", "HebbarsKitchen", "https://hebbarskitchen.com/paneer-butter-masala-recipe/"),
    ("dal_makhani", "HebbarsKitchen", "https://hebbarskitchen.com/punjabi-dal-makhani-recipe/")
]

TARGET_YEARS = [2014, 2016, 2018, 2020, 2022, 2024, 2026]

def check_snapshots(url):
    snaps_found = {}
    for yr in TARGET_YEARS:
        api_url = f"https://archive.org/wayback/available?url={url}&timestamp={yr}0101"
        try:
            r = requests.get(api_url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                closest = data.get("archived_snapshots", {}).get("closest")
                if closest and closest.get("available") and closest.get("status") == "200":
                    ts = closest.get("timestamp")
                    snap_yr = ts[:4]
                    if snap_yr not in snaps_found:
                        snaps_found[snap_yr] = closest.get("url")
        except Exception as e:
            pass
        time.sleep(0.3)
    return snaps_found

def extract_ingredients_from_url(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 1. Try JSON-LD
        for s in soup.find_all('script', type='application/ld+json'):
            txt = s.get_text().strip()
            if not txt: continue
            try:
                data = json.loads(txt, strict=False)
                items = data.get('@graph', [data]) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for item in items:
                    if isinstance(item, dict) and item.get('@type') in ['Recipe', ['Recipe']]:
                        return item.get('recipeIngredient', [])
            except:
                pass
        
        # 2. Try list items or recipe ingredient classes
        lines = []
        for li in soup.find_all(['li', 'p', 'span']):
            t = li.get_text().strip()
            if any(k in t.lower() for k in ['butter', 'ghee', 'oil', 'cream', 'sugar', 'paneer', 'dal']) and any(u in t.lower() for u in ['tbsp', 'tsp', 'cup', 'gm', 'g', 'spoon']):
                if len(t) < 80 and t not in lines:
                    lines.append(t)
        return lines
    except Exception as e:
        return []

def main():
    print("Querying Wayback Availability for 10 recipe URLs across 2014-2026...")
    records = []
    
    for dish_id, site, url in URLS_TO_TEST:
        print(f"Checking [{site}] {dish_id}...")
        snaps = check_snapshots(url)
        years = sorted(list(snaps.keys()))
        earliest_yr = years[0] if years else None
        latest_yr = years[-1] if years else None
        print(f"  -> Found {len(years)} unique years: {years}")
        
        records.append({
            "dish_id": dish_id,
            "site": site,
            "url": url,
            "snapshots_found": len(years),
            "earliest_year": earliest_yr,
            "latest_year": latest_yr,
            "years_list": ", ".join(years),
            "earliest_snap_url": snaps.get(earliest_yr),
            "latest_snap_url": snaps.get(latest_yr)
        })

    df_t6 = pd.DataFrame(records)
    df_t6.to_csv("data/t6_wayback_snapshots.csv", index=False)
    print("Saved data/t6_wayback_snapshots.csv!")

    # Longitudinal diff on 4 URLs with multiple snapshots
    diff_records = []
    candidates = df_t6[df_t6['snapshots_found'] >= 2].head(4)
    for idx, r in candidates.iterrows():
        dish = r['dish_id']
        site = r['site']
        u_early = r['earliest_snap_url']
        u_late = r['latest_snap_url']
        yr_early = r['earliest_year']
        yr_late = r['latest_year']

        print(f"\nDiffing [{site}] {dish}: {yr_early} vs {yr_late}...")
        ing_early = extract_ingredients_from_url(u_early)
        time.sleep(1.0)
        ing_late = extract_ingredients_from_url(u_late)
        time.sleep(1.0)

        # Filter liver lines
        liver_early = [i for i in ing_early if any(k in i.lower() for k in ['oil', 'ghee', 'butter', 'cream', 'sugar', 'salt'])]
        liver_late = [i for i in ing_late if any(k in i.lower() for k in ['oil', 'ghee', 'butter', 'cream', 'sugar', 'salt'])]

        print(f"  {yr_early} liver lines ({len(liver_early)}): {liver_early[:4]}")
        print(f"  {yr_late} liver lines ({len(liver_late)}): {liver_late[:4]}")

        diff_records.append({
            "dish_id": dish,
            "site": site,
            "earliest_year": yr_early,
            "latest_year": yr_late,
            "earliest_snap_url": u_early,
            "latest_snap_url": u_late,
            "earliest_liver_lines": "; ".join(liver_early[:5]),
            "latest_liver_lines": "; ".join(liver_late[:5]),
            "quantities_changed": (len(liver_early) > 0 and len(liver_late) > 0 and liver_early != liver_late),
            "notes": "Quantities compared across snapshots"
        })

    df_diff = pd.DataFrame(diff_records)
    df_diff.to_csv("data/t6_wayback_diffs.csv", index=False)
    print("Saved data/t6_wayback_diffs.csv!")
    print(df_diff[['dish_id', 'site', 'earliest_year', 'latest_year', 'quantities_changed']])

if __name__ == "__main__":
    main()
