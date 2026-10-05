import json
import time
import requests
from recipe_scrapers import scrape_html
import csv

with open("research_log/validation/ground_truth.json", "r") as f:
    dishes = json.load(f)

with open("research_log/validation/urls.json", "r") as f:
    urls_dict = json.load(f)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

ingredient_lines = []

for dish in dishes:
    name = dish["dish"]
    urls_to_scrape = urls_dict.get(name, [])
    dish_recipes = []
    
    for url in urls_to_scrape:
        print(f"Scraping {url}...")
        try:
            html_content = requests.get(url, headers=headers, timeout=10).text
            scraper = scrape_html(html=html_content, org_url=url, supported_only=False)
            dish_recipes.append({
                "dish": name,
                "url": url,
                "title": scraper.title(),
                "yields": scraper.yields() if hasattr(scraper, "yields") else "NOT AVAILABLE"
            })
            for ing in scraper.ingredients():
                ingredient_lines.append({
                    "dish": name,
                    "url": url,
                    "ingredient_line": ing
                })
        except Exception as e:
            print(f"Failed {url}: {e}")
        time.sleep(1)
            
    dish["recipes"] = dish_recipes

with open("research_log/validation/recipes.json", "w") as f:
    json.dump(dishes, f, indent=2)

with open("research_log/validation/ingredient_lines.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["dish", "url", "ingredient_line"])
    writer.writeheader()
    writer.writerows(ingredient_lines)
    
print("Done scraping.")
