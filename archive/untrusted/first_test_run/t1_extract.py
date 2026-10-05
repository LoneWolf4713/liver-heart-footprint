import json
import re
import os
import time
import pandas as pd
from curl_cffi import requests
from bs4 import BeautifulSoup

LIVER_KEYWORDS = {
    "oil": ["oil", "tel"],
    "ghee": ["ghee", "clarified butter"],
    "butter": ["butter", "makhan"],
    "cream": ["cream", "malai"],
    "khoya": ["khoya", "mawa"],
    "condensed_milk": ["condensed milk", "milkmaid"],
    "coconut_milk": ["coconut milk"],
    "vanaspati": ["vanaspati", "dalda", "hydrogenated"],
    "sugar": ["sugar", "chini", "cheeni", "sugar syrup"],
    "jaggery": ["jaggery", "gur", "gud"],
    "honey": ["honey", "shehed"],
    "maida": ["maida", "all purpose flour", "refined flour", "plain flour"],
    "salt": ["salt", "namak"]
}

VAGUE_PATTERNS = [
    r'\bas required\b', r'\bas needed\b', r'\bto taste\b', r'\bfor frying\b',
    r'\bfor deep frying\b', r'\bdeep frying\b', r'\bfor shallow frying\b',
    r'\bswad anusar\b', r'\blittle\b', r'\benough\b', r'\bsome\b', r'\boptional\b',
    r'\bfew drops\b'
]

RANGE_PATTERNS = [
    r'\d+\s*(?:to|-)\s*\d+',
    r'\d+/\d+\s*(?:to|-)\s*\d+/\d+',
    r'\d+\s*or\s*\d+'
]

EXACT_UNITS = [
    'cup', 'cups', 'tbsp', 'tablespoon', 'tablespoons', 'tsp', 'teaspoon', 'teaspoons',
    'g', 'gm', 'gms', 'gram', 'grams', 'kg', 'kilogram', 'ml', 'milliliter', 'l', 'liter', 'litre',
    'oz', 'ounce', 'katori', 'pinch', 'pinches'
]

COUNT_NOUNS = [
    'cube', 'cubes', 'piece', 'pieces', 'onion', 'onions', 'tomato', 'tomatoes',
    'chilli', 'chillies', 'chili', 'chilies', 'clove', 'cloves', 'inch', 'strand',
    'strands', 'cardamom', 'bay leaf', 'leaves', 'potato', 'potatoes', 'egg', 'eggs',
    'bhatura', 'puri', 'samosa'
]

def classify_ingredient(line):
    line_clean = line.strip().lower()
    
    # 1. Identify liver relevance
    is_liver = False
    liver_cat = None
    for cat, kws in LIVER_KEYWORDS.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', line_clean):
                is_liver = True
                liver_cat = cat
                break
        if is_liver:
            break

    # 2. Classify quantity status
    # Check vague first
    is_vague = any(re.search(p, line_clean) for p in VAGUE_PATTERNS)
    
    # Check range
    is_range = any(re.search(p, line_clean) for p in RANGE_PATTERNS)

    # Check exact unit with number
    has_exact_unit = any(re.search(r'\b' + re.escape(u) + r'\b', line_clean) for u in EXACT_UNITS)
    has_number = bool(re.search(r'\d', line_clean) or re.search(r'\b(one|two|three|half|quarter)\b', line_clean))

    # Check count
    has_count_noun = any(re.search(r'\b' + re.escape(c) + r'\b', line_clean) for c in COUNT_NOUNS)

    if is_vague and not (has_number and has_exact_unit):
        status = "vague"
    elif is_range:
        status = "range"
    elif has_number and has_exact_unit:
        status = "exact"
    elif has_number and (has_count_noun or not has_exact_unit):
        status = "count"
    elif not has_number:
        status = "missing" if not is_vague else "vague"
    else:
        status = "exact"

    return status, is_liver, liver_cat

def is_recipe_deep_fried(instructions_text, title=""):
    text = (instructions_text + " " + title).lower()
    patterns = [
        r'deep[- ]?fry', r'fry till golden', r'fry until golden', r'drop in hot oil',
        r'hot oil for frying', r'heat oil.*deep fry', r'fry on medium.*crisp'
    ]
    return any(re.search(p, text) for p in patterns)

def parse_page_data(url):
    try:
        r = requests.get(url, impersonate='chrome120', timeout=15)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        
        soup = BeautifulSoup(r.text, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')
        recipe_data = None
        for s in scripts:
            txt = s.get_text().strip()
            if not txt:
                continue
            try:
                data = json.loads(txt, strict=False)
                items = data.get('@graph', [data]) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for item in items:
                    if isinstance(item, dict) and item.get('@type') in ['Recipe', ['Recipe']]:
                        recipe_data = item
                        break
            except Exception:
                continue
            if recipe_data:
                break
        
        if not recipe_data:
            return None, "No Recipe JSON-LD found"
        
        return recipe_data, "OK"
    except Exception as e:
        return None, str(e)
