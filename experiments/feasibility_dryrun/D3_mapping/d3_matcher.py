"""
D3 Ingredient Matcher
Maps raw recipe ingredient lines to INDB food codes.
Adheres to Integrity Protocol:
- Blind to gold labels (does NOT read d3_gold_labels.csv).
- Uses INDB food table from recipes.xlsx, UK_fct, and US_fct.
- Uses Alias Dictionary + Fuzzy Matching (rapidfuzz) + Head-Noun Fallback.
- Maps both the D2 200-sample and all 790 D1 ingredient lines.
- Extracts the top 50 ingredient strings and their mappings.
"""

import re
import os
import pandas as pd
from rapidfuzz import fuzz, process

# 1. Build Reference Database
def build_indb_reference():
    recipes_path = 'data/indb_repo/recipes.xlsx'
    df_rec = pd.read_excel(recipes_path)
    
    # Unique canonical food items
    foods_df = df_rec[['food_code', 'food_name']].drop_duplicates().dropna()
    food_dict = dict(zip(foods_df['food_code'], foods_df['food_name']))
    
    # Also load UK and US FCTs
    uk_path = 'data/indb_repo/UK_fct.xlsx'
    if os.path.exists(uk_path):
        df_uk = pd.read_excel(uk_path)
        for _, row in df_uk.iterrows():
            if pd.notna(row.get('food_code')) and row['food_code'] not in food_dict:
                food_dict[str(row['food_code'])] = str(row.get('food_name', ''))
                
    us_path = 'data/indb_repo/US_fct.xlsx'
    if os.path.exists(us_path):
        df_us = pd.read_excel(us_path)
        for _, row in df_us.iterrows():
            if pd.notna(row.get('food_code')) and row['food_code'] not in food_dict:
                food_dict[str(row['food_code'])] = str(row.get('food_name', ''))

    # Build corpus of known mappings from recipes.xlsx
    mappings = []
    for _, row in df_rec[['food_code', 'food_name', 'ingredient_name_org']].drop_duplicates().dropna().iterrows():
        f_code = str(row['food_code']).strip()
        f_name = str(row['food_name']).strip()
        org_name = str(row['ingredient_name_org']).strip().lower()
        mappings.append((org_name, f_code, f_name))
        
    return food_dict, mappings

# 2. Curated Alias Dictionary (Common Indian English & Hindi culinary terms)
ALIAS_MAP = {
    # Fats & Oils
    'ghee': ('T506', 'Ghee, butter'),
    'clarified butter': ('T506', 'Ghee, butter'),
    'desi ghee': ('T506', 'Ghee, butter'),
    'butter': ('T501', 'Butter, unsalted'),
    'salted butter': ('T500', 'Butter, salted'),
    'unsalted butter': ('T501', 'Butter, unsalted'),
    'makhan': ('T501', 'Butter, unsalted'),
    'oil': ('T508', 'Oil, sunflower'),
    'cooking oil': ('T508', 'Oil, sunflower'),
    'vegetable oil': ('T508', 'Oil, sunflower'),
    'refined oil': ('T508', 'Oil, sunflower'),
    'sunflower oil': ('T508', 'Oil, sunflower'),
    'avocado oil': ('T508', 'Oil, sunflower'),
    'canola oil': ('T508', 'Oil, sunflower'),
    'mustard oil': ('T510', 'Oil, mustard'),
    'sarson ka tel': ('T510', 'Oil, mustard'),
    'coconut oil': ('T507', 'Oil, coconut'),
    'sesame oil': ('T509', 'Oil, sesame'),
    'til oil': ('T509', 'Oil, sesame'),
    'olive oil': ('T502', 'Oil, olive'),
    'cream': ('L519', 'Cream, fresh, single'),
    'fresh cream': ('L519', 'Cream, fresh, single'),
    'heavy cream': ('L519', 'Cream, fresh, single'),
    'whipping cream': ('L512', 'Cream, fresh, whipping'),
    'malai': ('L519', 'Cream, fresh, single'),
    
    # Sugars & Sweeteners
    'sugar': ('I502', 'Sugar, white'),
    'granulated sugar': ('I502', 'Sugar, white'),
    'white sugar': ('I502', 'Sugar, white'),
    'brown sugar': ('I503', 'Sugar, brown'),
    'icing sugar': ('I504', 'Sugar, icing'),
    'powdered sugar': ('I504', 'Sugar, icing'),
    'jaggery': ('I505', 'Jaggery, cane'),
    'gur': ('I505', 'Jaggery, cane'),
    'gud': ('I505', 'Jaggery, cane'),
    'honey': ('I507', 'Honey'),
    'condensed milk': ('L504', 'Condensed milk, sweetened'),
    
    # Flours & Grains
    'maida': ('A018', 'Wheat flour, refined (Triticum aestivum)'),
    'all-purpose flour': ('A018', 'Wheat flour, refined (Triticum aestivum)'),
    'all purpose flour': ('A018', 'Wheat flour, refined (Triticum aestivum)'),
    'plain flour': ('A018', 'Wheat flour, refined (Triticum aestivum)'),
    'refined flour': ('A018', 'Wheat flour, refined (Triticum aestivum)'),
    'atta': ('A019', 'Wheat flour, atta (Triticum aestivum)'),
    'wheat flour': ('A019', 'Wheat flour, atta (Triticum aestivum)'),
    'whole wheat flour': ('A019', 'Wheat flour, atta (Triticum aestivum)'),
    'besan': ('A504', 'Flour, gram'),
    'gram flour': ('A504', 'Flour, gram'),
    'chickpea flour': ('A504', 'Flour, gram'),
    'rice flour': ('A505', 'Flour, rice'),
    'corn flour': ('A503', 'Flour, corn'),
    'cornstarch': ('A503', 'Flour, corn'),
    'semolina': ('A020', 'Wheat, semolina (Triticum aestivum)'),
    'suji': ('A020', 'Wheat, semolina (Triticum aestivum)'),
    'rava': ('A020', 'Wheat, semolina (Triticum aestivum)'),
    'poha': ('A017', 'Rice flakes (Oryza sativa)'),
    'flattened rice': ('A017', 'Rice flakes (Oryza sativa)'),
    'rice flakes': ('A017', 'Rice flakes (Oryza sativa)'),
    'rice': ('A014', 'Rice, parboiled, milled (Oryza sativa )'),
    'basmati rice': ('A014', 'Rice, parboiled, milled (Oryza sativa )'),
    
    # Dairy
    'paneer': ('L003', 'Paneer'),
    'cottage cheese': ('L003', 'Paneer'),
    'milk': ('L002', 'Milk, whole, Cow'),
    'doodh': ('L002', 'Milk, whole, Cow'),
    'curd': ('L520', 'Yogurt, plain, whole milk'),
    'yogurt': ('L520', 'Yogurt, plain, whole milk'),
    'dahi': ('L520', 'Yogurt, plain, whole milk'),
    'khoya': ('L005', 'Khoa (Mawa)'),
    'mawa': ('L005', 'Khoa (Mawa)'),
    'khoa': ('L005', 'Khoa (Mawa)'),
    'coconut milk': ('H508', 'Nuts, coconut water (liquid from coconuts)'),
    
    # Salt
    'salt': ('G528', 'Salt'),
    'namak': ('G528', 'Salt'),
    'black salt': ('G540', 'HIMALAYAN BLACK SALT'),
    'kala namak': ('G540', 'HIMALAYAN BLACK SALT'),
    'rock salt': ('G540', 'HIMALAYAN BLACK SALT'),
    
    # Spices & Seasonings
    'cumin': ('G025', 'Cumin seeds (Cuminum cyminum)'),
    'jeera': ('G025', 'Cumin seeds (Cuminum cyminum)'),
    'cumin seeds': ('G025', 'Cumin seeds (Cuminum cyminum)'),
    'cumin powder': ('G025', 'Cumin seeds (Cuminum cyminum)'),
    'black pepper': ('G031', 'Pepper, black (Piper nigrum)'),
    'kali mirch': ('G031', 'Pepper, black (Piper nigrum)'),
    'pepper powder': ('G031', 'Pepper, black (Piper nigrum)'),
    'red chilli': ('G516', 'Chilli powder'),
    'chilli powder': ('G516', 'Chilli powder'),
    'red chilli powder': ('G516', 'Chilli powder'),
    'kashmiri chilli powder': ('G516', 'Chilli powder'),
    'lal mirch': ('G516', 'Chilli powder'),
    'green chilli': ('G008', 'Chillies, green - all varieties (Capsicum annum)'),
    'green chillies': ('G008', 'Chillies, green - all varieties (Capsicum annum)'),
    'hari mirch': ('G008', 'Chillies, green - all varieties (Capsicum annum)'),
    'turmeric': ('G033', 'Turmeric powder (Curcuma domestica)'),
    'haldi': ('G033', 'Turmeric powder (Curcuma domestica)'),
    'turmeric powder': ('G033', 'Turmeric powder (Curcuma domestica)'),
    'coriander powder': ('G024', 'Coriander seeds (Coriandrum sativum)'),
    'dhania powder': ('G024', 'Coriander seeds (Coriandrum sativum)'),
    'coriander seeds': ('G024', 'Coriander seeds (Coriandrum sativum)'),
    'coriander leaves': ('G009', 'Coriander leaves (Coriandrum sativum)'),
    'cilantro': ('G009', 'Coriander leaves (Coriandrum sativum)'),
    'hara dhania': ('G009', 'Coriander leaves (Coriandrum sativum)'),
    'cardamom': ('G020', 'Cardamom, green (Elettaria cardamomum)'),
    'green cardamom': ('G020', 'Cardamom, green (Elettaria cardamomum)'),
    'elaichi': ('G020', 'Cardamom, green (Elettaria cardamomum)'),
    'black cardamom': ('G021', 'Cardamom, black (Elettaria cardamomum)'),
    'badi elaichi': ('G021', 'Cardamom, black (Elettaria cardamomum)'),
    'clove': ('G023', 'Cloves (Syzygium aromaticum)'),
    'cloves': ('G023', 'Cloves (Syzygium aromaticum)'),
    'laung': ('G023', 'Cloves (Syzygium aromaticum)'),
    'cinnamon': ('G518', 'Cinnamon, ground'),
    'dalchini': ('G518', 'Cinnamon, ground'),
    'bay leaf': ('G018', 'Bay leaf (Laurus nobilis)'),
    'bay leaves': ('G018', 'Bay leaf (Laurus nobilis)'),
    'tej patta': ('G018', 'Bay leaf (Laurus nobilis)'),
    'garam masala': ('G523', 'Curry powder'),
    'kasuri methi': ('D044', 'Fenugreek leaves (Trigonella foenum-graecum)'),
    'kasoori methi': ('D044', 'Fenugreek leaves (Trigonella foenum-graecum)'),
    'fenugreek leaves': ('D044', 'Fenugreek leaves (Trigonella foenum-graecum)'),
    'ginger': ('G014', 'Ginger, fresh (Zingiber officinale)'),
    'adrak': ('G014', 'Ginger, fresh (Zingiber officinale)'),
    'fresh ginger': ('G014', 'Ginger, fresh (Zingiber officinale)'),
    'dry ginger': ('G554', 'Ginger, ground'),
    'saunth': ('G554', 'Ginger, ground'),
    'garlic': ('G012', 'Garlic, small clove (Allium sativum)'),
    'lehsun': ('G012', 'Garlic, small clove (Allium sativum)'),
    'garlic clove': ('G012', 'Garlic, small clove (Allium sativum)'),
    'mustard seeds': ('G027', 'Mustard seeds (Brassica nigra)'),
    'rai': ('G027', 'Mustard seeds (Brassica nigra)'),
    'asafoetida': ('G019', 'Asafoetida (Ferula foetida)'),
    'hing': ('G019', 'Asafoetida (Ferula foetida)'),
    'curry leaves': ('G011', 'Curry leaves (Murraya koenigii)'),
    'kadi patta': ('G011', 'Curry leaves (Murraya koenigii)'),
    'fennel seeds': ('G026', 'Fennel seeds (Foeniculum vulgare)'),
    'saunf': ('G026', 'Fennel seeds (Foeniculum vulgare)'),
    'nutmeg': ('G028', 'Nutmeg (Myristica fragrans)'),
    'amchur': ('D057', 'Mango, green, raw (Mangifera indica)'),
    'amchoor': ('D057', 'Mango, green, raw (Mangifera indica)'),
    'dry mango powder': ('D057', 'Mango, green, raw (Mangifera indica)'),
    
    # Vegetables & Aromatics
    'onion': ('G017', 'Onion, big (Allium cepa)'),
    'onions': ('G017', 'Onion, big (Allium cepa)'),
    'pyaaz': ('G017', 'Onion, big (Allium cepa)'),
    'spring onion': ('G547', 'Spring onions, bulbs and tops, raw'),
    'tomato': ('D075', 'Tomato, ripe, hybrid (Solanum lycopersicum)'),
    'tomatoes': ('D075', 'Tomato, ripe, hybrid (Solanum lycopersicum)'),
    'tamatar': ('D075', 'Tomato, ripe, hybrid (Solanum lycopersicum)'),
    'tomato puree': ('X505', 'Tomato sauce, homemade'),
    'tomato paste': ('X505', 'Tomato sauce, homemade'),
    'potato': ('D067', 'Potato, brown skin (Solanum tuberosum)'),
    'potatoes': ('D067', 'Potato, brown skin (Solanum tuberosum)'),
    'aloo': ('D067', 'Potato, brown skin (Solanum tuberosum)'),
    'carrot': ('D034', 'Carrot, red (Daucus carota carota)'),
    'carrots': ('D034', 'Carrot, red (Daucus carota carota)'),
    'gajar': ('D034', 'Carrot, red (Daucus carota carota)'),
    'peas': ('D065', 'Peas, green (Pisum sativum)'),
    'green peas': ('D065', 'Peas, green (Pisum sativum)'),
    'matar': ('D065', 'Peas, green (Pisum sativum)'),
    'lemon': ('E520', 'Lemons, flesh only, raw, weighed with peel and pips'),
    'lemon juice': ('E033', 'Lemon, juice (Citrus limon)'),
    'lime juice': ('E033', 'Lemon, juice (Citrus limon)'),
    'nimbu': ('E033', 'Lemon, juice (Citrus limon)'),
    
    # Pulses / Legumes
    'chole': ('B001', 'Bengal gram, dal (Cicer arietinum)'),
    'chana': ('B001', 'Bengal gram, dal (Cicer arietinum)'),
    'kabuli chana': ('B001', 'Bengal gram, dal (Cicer arietinum)'),
    'chickpeas': ('B001', 'Bengal gram, dal (Cicer arietinum)'),
    'urad dal': ('B003', 'Black gram, dal (Phaseolus mungo)'),
    'black lentil': ('B003', 'Black gram, dal (Phaseolus mungo)'),
    'black lentils': ('B003', 'Black gram, dal (Phaseolus mungo)'),
    'rajma': ('B018', 'Rajmah (Phaseolus vulgaris)'),
    'kidney beans': ('B018', 'Rajmah (Phaseolus vulgaris)'),
    'moong dal': ('B010', 'Green gram, dal (Vigna radiata)'),
    'masoor dal': ('B013', 'Lentil dal (Lens culinaris)'),
    'toor dal': ('B021', 'Red gram, dal (Cajanus cajan)'),
    
    # Nuts / Dry fruits
    'cashew': ('H004', 'Cashewnut (Anacardium occidentale)'),
    'cashews': ('H004', 'Cashewnut (Anacardium occidentale)'),
    'kaju': ('H004', 'Cashewnut (Anacardium occidentale)'),
    'almond': ('H001', 'Almond (Prunus amygdalus)'),
    'almonds': ('H001', 'Almond (Prunus amygdalus)'),
    'badam': ('H001', 'Almond (Prunus amygdalus)'),
    'peanuts': ('H012', 'Ground nut (Arachis hypogea)'),
    'peanut': ('H012', 'Ground nut (Arachis hypogea)'),
    'moongfali': ('H012', 'Ground nut (Arachis hypogea)'),
    'raisins': ('E054', 'Raisins, black (Vitis vinifera)'),
    'kishmish': ('E054', 'Raisins, black (Vitis vinifera)'),
    'pistachio': ('H013', 'Pistachio nut (Pistacia vera)'),
    'pista': ('H013', 'Pistachio nut (Pistacia vera)'),
    
    # Non-Veg
    'chicken': ('N003', 'Chicken, poultry, breast, skinless'),
    'murgh': ('N003', 'Chicken, poultry, breast, skinless'),
    'egg': ('M001', 'Egg, poultry, whole, raw'),
    'eggs': ('M001', 'Egg, poultry, whole, raw'),
    'anda': ('M001', 'Egg, poultry, whole, raw'),
    'mutton': ('N013', 'Goat, lean only, raw'),
    
    # Water / Miscellaneous
    'water': ('K505', 'Water, distilled'),
    'pani': ('K505', 'Water, distilled'),
    'baking soda': ('G502', 'Baking soda (sodium bicarbonate)'),
    'tea leaves': ('V510', 'Tea, black, infusion, average'),
    'tea': ('V510', 'Tea, black, infusion, average'),
    'coffee': ('V502', 'Coffee, powder, instant'),
}

# 3. Text cleaning function
def clean_ingredient_text(text):
    t = str(text).lower()
    # Remove quantities, units, fractions
    t = re.sub(r'\b\d+(?:[\./\s-]\d+)*\s*(?:tbsp|tsp|tablespoon|teaspoon|cup|cups|gram|grams|gm|gms|g|kg|ml|l|liter|pinch|pinches|katori|inch|piece|pieces)?\b', ' ', t)
    # Remove common parenthetical remarks
    t = re.sub(r'\(.*?\)', ' ', t)
    # Remove punctuation
    t = re.sub(r'[,/;:_\-\+]', ' ', t)
    # Remove instructional boilerplate words
    stopwords = ['for', 'frying', 'deep', 'shallow', 'greasing', 'serving', 'garnishing', 'optional', 'divided', 'melted',
                 'warm', 'hot', 'cold', 'boiled', 'soaked', 'diced', 'chopped', 'finely', 'roughly', 'sliced', 'grated',
                 'crushed', 'fresh', 'dry', 'raw', 'ripe', 'store', 'bought', 'homemade', 'as', 'needed', 'required',
                 'per', 'taste', 'firstly', 'large', 'small', 'medium', 'bowl', 'take', 'can', 'use', 'alternatively',
                 'mixing', 'inch', 'piece', 'cubed', 'cubes', 'paste', 'extract', 'powder', 'seeds', 'leaves']
    words = [w for w in t.split() if w not in stopwords and len(w) > 1]
    return ' '.join(words).strip()

def match_ingredient(raw_line, food_dict, indb_mappings):
    raw_lower = str(raw_line).lower().strip()
    cleaned = clean_ingredient_text(raw_line)
    
    # Strategy 1: Check Alias Map directly against raw line or cleaned string
    # Check multi-word keys first (longest key first)
    sorted_aliases = sorted(ALIAS_MAP.keys(), key=lambda x: len(x), reverse=True)
    for alias in sorted_aliases:
        # Check boundary regex
        if re.search(r'\b' + re.escape(alias) + r'\b', raw_lower):
            code, name = ALIAS_MAP[alias]
            return code, name, 'alias_direct', 1.0

    # Strategy 2: Exact or high-confidence match on INDB known recipe ingredient names
    for org_name, f_code, f_name in indb_mappings:
        if len(org_name) > 3 and org_name in raw_lower:
            return f_code, f_name, 'indb_recipes_exact', 0.95

    # Strategy 3: Rapidfuzz match against INDB known terms
    if cleaned and len(cleaned) > 2:
        org_terms = [m[0] for m in indb_mappings]
        match, score, idx = process.extractOne(cleaned, org_terms, scorer=fuzz.token_sort_ratio)
        if score >= 75:
            matched_mapping = indb_mappings[idx]
            return matched_mapping[1], matched_mapping[2], 'rapidfuzz_term', score / 100.0

    # Strategy 4: Rapidfuzz match against canonical food_name
    if cleaned and len(cleaned) > 2:
        codes = list(food_dict.keys())
        names = [food_dict[c] for c in codes]
        match, score, idx = process.extractOne(cleaned, names, scorer=fuzz.partial_ratio)
        if score >= 80:
            matched_code = codes[idx]
            return matched_code, food_dict[matched_code], 'rapidfuzz_canonical', score / 100.0

    # Fallback: No match found
    return 'NO_MATCH', 'NO_MATCH', 'unmatched', 0.0

def main():
    print("Building INDB reference database...")
    food_dict, indb_mappings = build_indb_reference()
    print(f"Loaded {len(food_dict)} food items and {len(indb_mappings)} historical ingredient mappings.")
    
    # 1. Match the 200 sample lines from D2
    sample_df = pd.read_csv('dryrun/D2_normaliser/d2_sample_200.csv')
    mapped_sample = []
    for _, row in sample_df.iterrows():
        sid = row['sample_id']
        dish = row['dish']
        line = row['line']
        code, name, method, conf = match_ingredient(line, food_dict, indb_mappings)
        mapped_sample.append({
            'sample_id': sid,
            'dish': dish,
            'line': line,
            'is_liver_relevant': row['is_liver_relevant'],
            'liver_category': row['liver_category'],
            'matched_code': code,
            'matched_name': name,
            'match_method': method,
            'confidence': conf
        })
    df_sample_mapped = pd.DataFrame(mapped_sample)
    df_sample_mapped.to_csv('dryrun/D3_mapping/d3_mapped_sample200.csv', index=False)
    print(f"Mapped {len(df_sample_mapped)} sample lines to dryrun/D3_mapping/d3_mapped_sample200.csv")

    # 2. Match ALL 790 D1 lines
    d1_df = pd.read_csv('dryrun/D1_link_reader/d1_ingredient_lines.csv')
    mapped_all = []
    for idx, row in d1_df.iterrows():
        line = row['line']
        code, name, method, conf = match_ingredient(line, food_dict, indb_mappings)
        mapped_all.append({
            'line_id': idx + 1,
            'dish': row['dish'],
            'site': row['site'],
            'url': row['url'],
            'line': line,
            'is_liver_relevant': row['is_liver_relevant'],
            'liver_category': row['liver_category'],
            'matched_code': code,
            'matched_name': name,
            'match_method': method,
            'confidence': conf
        })
    df_all_mapped = pd.DataFrame(mapped_all)
    df_all_mapped.to_csv('dryrun/D3_mapping/d3_mapped_all_d1.csv', index=False)
    print(f"Mapped {len(df_all_mapped)} total D1 lines to dryrun/D3_mapping/d3_mapped_all_d1.csv")

    # 3. Extract top 50 most frequent ingredient strings in D1 and their mappings
    clean_lines = df_all_mapped['line'].apply(clean_ingredient_text)
    # Get top 50 strings
    top50_counts = clean_lines[clean_lines.str.len() > 1].value_counts().head(50)
    top50_rows = []
    for term, count in top50_counts.items():
        code, name, method, conf = match_ingredient(term, food_dict, indb_mappings)
        top50_rows.append({
            'ingredient_term': term,
            'frequency_in_d1': count,
            'matched_food_code': code,
            'matched_food_name': name,
            'match_method': method,
            'confidence': conf
        })
    df_top50 = pd.DataFrame(top50_rows)
    df_top50.to_csv('dryrun/D3_mapping/d3_top50_mappings.csv', index=False)
    print(f"Extracted top 50 ingredient strings to dryrun/D3_mapping/d3_top50_mappings.csv")

if __name__ == '__main__':
    main()
