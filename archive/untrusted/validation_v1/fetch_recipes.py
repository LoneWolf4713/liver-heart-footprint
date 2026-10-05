import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from recipe_scrapers import scrape_me

with open("research_log/validation/ground_truth.json", "r") as f:
    dishes = json.load(f)

domains = [
    "indianhealthyrecipes.com",
    "hebbarskitchen.com",
    "archanaskitchen.com",
    "cookwithmanali.com",
    "pipingpotcurry.com"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def search_bing(query):
    url = f"https://www.bing.com/search?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and href.startswith('http'):
                links.append(href)
        return links
    except:
        return []

ingredient_lines = []

for dish in dishes:
    name = dish["dish"]
    valid_links = []
    seen = set()
    
    print(f"\nSearching for {name}...")
    for domain in domains:
        if len(valid_links) >= 3:
            break
        query = f"{name} recipe site:{domain}"
        links = search_bing(query)
        for link in links:
            d = urlparse(link).netloc.replace("www.", "")
            if d == domain and link not in seen:
                if "category" not in link and "tag" not in link and "author" not in link:
                    valid_links.append(link)
                    seen.add(link)
                    if len(valid_links) >= 3:
                        break
        time.sleep(1)

    urls_to_scrape = valid_links[:3]
    print(f"URLs for {name}: {urls_to_scrape}")
    
    dish_recipes = []
    for url in urls_to_scrape:
        time.sleep(1)
        print(f"Scraping {url}...")
        try:
            html_content = requests.get(url, headers=headers, timeout=10).text
            scraper = scrape_me(url, html=html_content)
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
            
    dish["recipes"] = dish_recipes

with open("research_log/validation/recipes.json", "w") as f:
    json.dump(dishes, f, indent=2)

import csv
with open("research_log/validation/ingredient_lines.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["dish", "url", "ingredient_line"])
    writer.writeheader()
    writer.writerows(ingredient_lines)
    
print("Done scraping.")
