import subprocess
import json
import time
import os

DISHES = [
    ("paneer_butter_masala", "paneer butter masala"),
    ("dal_makhani", "dal makhani"),
    ("chole", "chole chana masala"),
    ("rajma", "rajma"),
    ("aloo_paratha", "aloo paratha"),
    ("samosa", "samosa"),
    ("onion_pakora", "onion pakora onion bhajji"),
    ("puri_bhature", "puri bhature"),
    ("pav_bhaji", "pav bhaji"),
    ("butter_chicken", "butter chicken"),
    ("chicken_biryani", "chicken biryani"),
    ("egg_curry", "egg curry"),
    ("gulab_jamun", "gulab jamun"),
    ("gajar_halwa", "gajar ka halwa"),
    ("jalebi", "jalebi"),
    ("poha", "poha"),
    ("masala_dosa", "masala dosa"),
    ("sambar", "sambar"),
    ("kheer", "rice kheer"),
    ("aloo_tikki", "aloo tikki"),
]

SITES = [
    ("indianhealthyrecipes", "indianhealthyrecipes.com", False),
    ("archanaskitchen", "archanaskitchen.com", False),
    ("vegrecipesofindia", "vegrecipesofindia.com", True),
    ("hebbarskitchen", "hebbarskitchen.com", True),
    ("tarladalal", "tarladalal.com", True)
]

VEG_SUBSTITUTES = {
    "butter_chicken": "paneer makhani",
    "chicken_biryani": "veg biryani",
    "egg_curry": "paneer curry"
}

def search_site(domain, query):
    cmd = [
        "/home/prtyksh/tmp/web_search_tool/run_tool.sh",
        "search",
        f"site:{domain} {query}",
        "--num", "3",
        "--json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        # Find first matching url belonging to domain
        for item in data:
            url = item.get("href", "")
            if domain in url and not any(x in url for x in ["/tag/", "/category/", "/page/", "?"]):
                return url
        if data:
            return data[0].get("href", "")
    except Exception as e:
        print(f"Error searching {domain} for {query}: {e}")
    return None

def main():
    out_file = "data/t1_dish_urls.json"
    if os.path.exists(out_file):
        with open(out_file, "r") as f:
            url_map = json.load(f)
    else:
        url_map = {}

    for site_key, domain, is_veg_only in SITES:
        if site_key not in url_map:
            url_map[site_key] = {}
        for dish_id, dish_name in DISHES:
            if dish_id in url_map[site_key] and url_map[site_key][dish_id].get("url"):
                continue
            
            search_query = dish_name
            substituted = False
            if is_veg_only and dish_id in VEG_SUBSTITUTES:
                search_query = VEG_SUBSTITUTES[dish_id]
                substituted = True

            print(f"Searching {site_key} ({domain}) for {search_query}...")
            url = search_site(domain, search_query)
            print(f" -> Found: {url}")
            url_map[site_key][dish_id] = {
                "dish_id": dish_id,
                "dish_name": dish_name,
                "search_query": search_query,
                "substituted": substituted,
                "url": url
            }
            time.sleep(1.0)
            
            # Save incrementally
            with open(out_file, "w") as f:
                json.dump(url_map, f, indent=2)

    print("Completed URL gathering.")

if __name__ == "__main__":
    main()
