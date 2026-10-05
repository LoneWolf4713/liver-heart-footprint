import json
import re
import os
import time
import pandas as pd
from curl_cffi import requests
from bs4 import BeautifulSoup

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

def query_cdx(url):
    # CDX query collapsed by year
    cdx_url = f"https://web.archive.org/cdx/search/cdx?url={url}&output=json&fl=timestamp,statuscode&filter=statuscode:200&collapse=timestamp:4"
    try:
        r = requests.get(cdx_url, impersonate="chrome120", timeout=20)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 1:
                snaps = data[1:]
                return snaps
        return []
    except Exception as e:
        print(f"CDX error for {url}: {e}")
        return []

def extract_ingredients_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    # try json-ld first
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
    # fallback to li elements
    ingrs = []
    for li in soup.find_all('li'):
        t = li.get_text().strip()
        if any(k in t.lower() for k in ['butter', 'oil', 'ghee', 'cream', 'sugar', 'paneer', 'dal']):
            if len(t) < 100:
                ingrs.append(t)
    return ingrs

def run_t6():
    print("Running T6 Wayback longitudinal feasibility check...")
    results = []

    for dish_id, site, url in URLS_TO_TEST:
        print(f"\nQuerying CDX for [{site}] {dish_id} ({url})...")
        snaps = query_cdx(url)
        time.sleep(2.0) # Polite pause for archive.org
        
        count = len(snaps)
        years = [s[0][:4] for s in snaps]
        earliest_yr = years[0] if years else None
        latest_yr = years[-1] if years else None
        earliest_ts = snaps[0][0] if snaps else None
        latest_ts = snaps[-1][0] if snaps else None

        print(f"  -> Found {count} yearly snapshots: {years}")

        results.append({
            "dish_id": dish_id,
            "site": site,
            "url": url,
            "snapshot_count": count,
            "earliest_year": earliest_yr,
            "latest_year": latest_yr,
            "years_available": ", ".join(years),
            "earliest_timestamp": earliest_ts,
            "latest_timestamp": latest_ts
        })

    df_t6 = pd.DataFrame(results)
    df_t6.to_csv("data/t6_wayback_snapshots.csv", index=False)
    print("\nSaved data/t6_wayback_snapshots.csv!")

    # Now fetch and diff earliest vs latest for 3 URLs with snapshots spanning >= 3 years
    diff_candidates = df_t6[df_t6['snapshot_count'] >= 2].copy()
    print(f"\nFound {len(diff_candidates)} candidates for longitudinal quantity diff.")

    diff_records = []
    for idx, r in diff_candidates.head(4).iterrows():
        url = r['url']
        dish = r['dish_id']
        site = r['site']
        t_early = r['earliest_timestamp']
        t_late = r['latest_timestamp']

        early_wayback_url = f"https://web.archive.org/web/{t_early}id_/{url}"
        late_wayback_url = f"https://web.archive.org/web/{t_late}id_/{url}"

        print(f"Diffing [{site}] {dish}: {r['earliest_year']} vs {r['latest_year']}...")
        
        try:
            r_early = requests.get(early_wayback_url, impersonate="chrome120", timeout=25)
            time.sleep(2.0)
            r_late = requests.get(late_wayback_url, impersonate="chrome120", timeout=25)
            time.sleep(2.0)

            ing_early = extract_ingredients_from_html(r_early.text) if r_early.status_code == 200 else []
            ing_late = extract_ingredients_from_html(r_late.text) if r_late.status_code == 200 else []

            # Filter liver items
            liver_early = [i for i in ing_early if any(k in i.lower() for k in ['oil', 'ghee', 'butter', 'cream', 'sugar', 'salt'])]
            liver_late = [i for i in ing_late if any(k in i.lower() for k in ['oil', 'ghee', 'butter', 'cream', 'sugar', 'salt'])]

            diff_records.append({
                "dish_id": dish,
                "site": site,
                "earliest_year": r['earliest_year'],
                "latest_year": r['latest_year'],
                "earliest_liver_lines": "; ".join(liver_early[:5]),
                "latest_liver_lines": "; ".join(liver_late[:5]),
                "changed_quantities": len(liver_early) > 0 and liver_early != liver_late
            })
        except Exception as e:
            print(f"Error fetching wayback diff for {dish}: {e}")

    df_diff = pd.DataFrame(diff_records)
    df_diff.to_csv("data/t6_wayback_diffs.csv", index=False)
    print("Saved data/t6_wayback_diffs.csv!")
    print(df_diff)

if __name__ == "__main__":
    run_t6()
