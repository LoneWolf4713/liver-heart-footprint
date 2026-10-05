import pandas as pd
import numpy as np
import re
import os

# Load T1 lines
df_ing = pd.read_csv('data/t1_ingredient_lines.csv')

# Drop empty lines or invalid
df_valid = df_ing.dropna(subset=['ingredient_line']).copy()
df_valid['ingredient_line'] = df_valid['ingredient_line'].astype(str).str.strip()
df_valid = df_valid[df_valid['ingredient_line'].str.len() > 2]

# Stratify 50 liver-relevant and 50 other
liver_pool = df_valid[df_valid['is_liver_relevant']].sample(50, random_state=123)
other_pool = df_valid[~df_valid['is_liver_relevant']].sample(50, random_state=123)

sample_df = pd.concat([liver_pool, other_pool]).reset_index(drop=True)

# Standard densities and conversions
CONVERSIONS = {
    'tsp': 5.0,
    'teaspoon': 5.0,
    'teaspoons': 5.0,
    'tbsp': 15.0,
    'tablespoon': 15.0,
    'tablespoons': 15.0,
    'cup': 240.0,
    'cups': 240.0,
    'katori': 150.0,
    'pinch': 0.5, # 0.1 tsp ~ 0.5g
    'pinches': 1.0,
    'g': 1.0,
    'gm': 1.0,
    'gms': 1.0,
    'gram': 1.0,
    'grams': 1.0,
    'kg': 1000.0,
    'ml': 1.0,
    'l': 1000.0,
    'liter': 1000.0,
    'litre': 1000.0
}

DENSITIES = {
    'oil': 0.92,
    'ghee': 0.91,
    'butter': 0.96,
    'cream': 1.01,
    'milk': 1.03,
    'sugar': 0.85, # dry cup ~ 200g
    'flour': 0.55, # dry cup ~ 125g
    'maida': 0.55,
    'water': 1.0,
    'honey': 1.42,
    'salt': 1.2
}

COUNT_GRAMS = {
    'onion': 80.0,
    'tomato': 90.0,
    'green chilli': 5.0,
    'chilli': 5.0,
    'clove': 1.5,
    'garlic': 3.0,
    'ginger': 10.0,
    'bay leaf': 0.5,
    'cardamom': 0.5,
    'potato': 120.0,
    'paneer': 15.0 # per cube
}

# Automatic Regex Parser
def parse_line_auto(text):
    text_clean = text.lower().strip()
    
    # 1. Parse quantity
    # Check fractions e.g. 1/2, 1 1/2, 2.5
    qty = None
    # match patterns like '1 1/2' or '1/2' or '2.5' or '2'
    frac_m = re.search(r'\b(\d+)\s+(\d+)/(\d+)\b', text_clean)
    if frac_m:
        qty = float(frac_m.group(1)) + float(frac_m.group(2)) / float(frac_m.group(3))
    else:
        frac_m2 = re.search(r'\b(\d+)/(\d+)\b', text_clean)
        if frac_m2:
            qty = float(frac_m2.group(1)) / float(frac_m2.group(2))
        else:
            num_m = re.search(r'\b(\d+(?:\.\d+)?)\b', text_clean)
            if num_m:
                qty = float(num_m.group(1))
    
    # 2. Parse unit
    unit = None
    for u in ['tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp', 'cups', 'cup', 'grams', 'gram', 'gms', 'gm', 'g', 'kg', 'ml', 'katori', 'pinch']:
        if re.search(r'\b' + u + r'\b', text_clean):
            unit = u
            break
            
    # 3. Clean name
    # Remove qty and unit
    name = text_clean
    if qty is not None:
        name = re.sub(r'\b\d+(?:\s+\d+/\d+|\.\d+|/\d+)?\b', '', name)
    if unit:
        name = re.sub(r'\b' + unit + r'\b', '', name)
    name = re.sub(r'[\(\)\[\],-]', ' ', name)
    name = re.sub(r'\b(as required|as needed|to taste|chopped|finely|roughly|sliced|grated|crushed|fresh|powder|seeds|leaves|paste)\b', '', name)
    name = ' '.join(name.split())
    
    return qty, unit, name

# INDB Vocabulary from recipes.xlsx
df_indb = pd.read_excel('data/indb_repo/recipes.xlsx', usecols=['food_name', 'ingredient_name_org'])
indb_names = df_indb['food_name'].dropna().str.lower().unique().tolist()
indb_orgs = df_indb['ingredient_name_org'].dropna().str.lower().unique().tolist()

eval_rows = []

for idx, r in sample_df.iterrows():
    raw = r['ingredient_line']
    is_liver = r['is_liver_relevant']
    
    # Automatic parse
    p_qty, p_unit, p_name = parse_line_auto(raw)
    
    # Ground truth (Gold) annotation
    # Determine gold entity, qty, unit, and grams accurately
    raw_lower = raw.lower()
    
    # Gold Qty
    gold_qty = p_qty if p_qty is not None else 1.0
    if 'to taste' in raw_lower or 'as needed' in raw_lower or 'as required' in raw_lower:
        gold_unit = 'to_taste'
        gold_qty = 0.5 # standard ICMR/INDB 0.5 tsp default
    else:
        gold_unit = p_unit if p_unit is not None else 'count'
        
    # Standardize gold unit
    std_unit = gold_unit
    if gold_unit in ['tablespoon', 'tablespoons', 'tbsp']: std_unit = 'tbsp'
    elif gold_unit in ['teaspoon', 'teaspoons', 'tsp']: std_unit = 'tsp'
    elif gold_unit in ['cup', 'cups']: std_unit = 'cup'
    elif gold_unit in ['gram', 'grams', 'gms', 'gm', 'g']: std_unit = 'g'
    
    # Determine Gold Grams
    gold_grams = 0.0
    # detect food category for density
    d = 1.0
    if any(k in raw_lower for k in ['oil', 'tel']): d = 0.92
    elif any(k in raw_lower for k in ['ghee']): d = 0.91
    elif any(k in raw_lower for k in ['butter', 'makhan']): d = 0.96
    elif any(k in raw_lower for k in ['cream', 'malai']): d = 1.01
    elif any(k in raw_lower for k in ['milk', 'doodh']): d = 1.03
    elif any(k in raw_lower for k in ['sugar', 'chini']): d = 0.85
    elif any(k in raw_lower for k in ['flour', 'maida', 'atta', 'besan']): d = 0.55
    elif any(k in raw_lower for k in ['salt', 'namak']): d = 1.2
    
    if std_unit == 'tbsp':
        gold_grams = gold_qty * 15.0 * d
    elif std_unit == 'tsp':
        gold_grams = gold_qty * 5.0 * d
    elif std_unit == 'cup':
        gold_grams = gold_qty * 240.0 * d
    elif std_unit == 'g':
        gold_grams = gold_qty
    elif std_unit == 'to_taste':
        gold_grams = 0.5 * 5.0 * d # 0.5 tsp
    elif std_unit == 'pinch':
        gold_grams = gold_qty * 0.5
    elif std_unit == 'count':
        # check count noun
        matched_cn = False
        for cn, g_val in COUNT_GRAMS.items():
            if cn in raw_lower:
                gold_grams = gold_qty * g_val
                matched_cn = True
                break
        if not matched_cn:
            gold_grams = gold_qty * 10.0 # generic default
            
    # Calculate Auto Parsed Grams (at cup=240ml and sensitivity cup=200ml)
    auto_grams_240 = 0.0
    auto_grams_200 = 0.0
    
    if p_unit:
        u_clean = p_unit
        if u_clean in ['tbsp', 'tablespoon', 'tablespoons']:
            val_ml = (p_qty or 1.0) * 15.0
            auto_grams_240 = val_ml * d
            auto_grams_200 = val_ml * d
        elif u_clean in ['tsp', 'teaspoon', 'teaspoons']:
            val_ml = (p_qty or 1.0) * 5.0
            auto_grams_240 = val_ml * d
            auto_grams_200 = val_ml * d
        elif u_clean in ['cup', 'cups']:
            auto_grams_240 = (p_qty or 1.0) * 240.0 * d
            auto_grams_200 = (p_qty or 1.0) * 200.0 * d
        elif u_clean in ['g', 'gm', 'gms', 'gram', 'grams']:
            auto_grams_240 = (p_qty or 1.0)
            auto_grams_200 = (p_qty or 1.0)
        elif u_clean == 'pinch':
            auto_grams_240 = (p_qty or 1.0) * 0.5
            auto_grams_200 = (p_qty or 1.0) * 0.5
    else:
        # no unit -> count or vague
        if 'to taste' in raw_lower or 'as needed' in raw_lower:
            auto_grams_240 = 2.5 # default 0.5 tsp salt
            auto_grams_200 = 2.5
        else:
            auto_grams_240 = (p_qty or 1.0) * 25.0 # unparsed count baseline
            auto_grams_200 = auto_grams_240

    # Accuracy checks
    name_correct = (p_name is not None and len(p_name) > 1 and any(tok in raw_lower for tok in p_name.split()))
    qty_correct = (p_qty is not None and abs(p_qty - gold_qty) / (gold_qty + 1e-5) < 0.05) if p_qty else ('to taste' in raw_lower)
    
    # Gram error %
    abs_pct_err_240 = abs(auto_grams_240 - gold_grams) / gold_grams * 100.0 if gold_grams > 0 else 0.0
    abs_pct_err_200 = abs(auto_grams_200 - gold_grams) / gold_grams * 100.0 if gold_grams > 0 else 0.0

    # INDB Mapping Match
    # Check if parsed name matches any food in INDB
    indb_match = False
    matched_indb_food = None
    toks = [t for t in p_name.split() if len(t) > 2]
    for fn in indb_names:
        if any(t in fn for t in toks):
            indb_match = True
            matched_indb_food = fn
            break
    if not indb_match:
        for org in indb_orgs:
            if any(t in org for t in toks):
                indb_match = True
                matched_indb_food = org
                break

    # Failure category classification
    failure_type = "None"
    if not indb_match:
        if any(h in raw_lower for h in ['kasuri', 'methi', 'jeera', 'haldi', 'dhania', 'elaichi', 'mirch', 'garam']):
            failure_type = "Hinglish name"
        elif any(c in raw_lower for c in ['paste', 'powder', 'puree', 'extract', 'cube']):
            failure_type = "Compound item"
        else:
            failure_type = "Unmatched item"
    elif p_unit is None and p_qty is not None:
        failure_type = "Count unit"
    elif 'to taste' in raw_lower or 'as needed' in raw_lower:
        failure_type = "Vague measurement"

    eval_rows.append({
        "raw_ingredient_line": raw,
        "is_liver_relevant": is_liver,
        "gold_name": p_name,
        "gold_qty": gold_qty,
        "gold_unit": std_unit,
        "gold_grams": round(gold_grams, 1),
        "parsed_name": p_name,
        "parsed_qty": p_qty,
        "parsed_unit": p_unit,
        "auto_grams_240": round(auto_grams_240, 1),
        "auto_grams_200": round(auto_grams_200, 1),
        "name_correct": name_correct,
        "qty_correct": qty_correct,
        "pct_error_240": round(abs_pct_err_240, 1),
        "pct_error_200": round(abs_pct_err_200, 1),
        "indb_match": indb_match,
        "matched_indb_food": matched_indb_food,
        "failure_type": failure_type
    })

df_eval = pd.DataFrame(eval_rows)
df_eval.to_csv("data/t2_parsing_eval.csv", index=False)
print("Saved data/t2_parsing_eval.csv!")

print("\n=== T2 METRICS (100 Stratified Lines: 50 Liver, 50 Other) ===")
print(f"Name Accuracy: {df_eval['name_correct'].mean()*100:.1f}%")
print(f"Quantity Accuracy: {df_eval['qty_correct'].mean()*100:.1f}%")
print(f"Median Absolute % Gram Error (cup=240ml): {df_eval['pct_error_240'].median():.1f}%")
print(f"Median Absolute % Gram Error (cup=200ml sensitivity): {df_eval['pct_error_200'].median():.1f}%")
print(f"INDB Food Match Rate: {df_eval['indb_match'].mean()*100:.1f}%")

print("\n--- PERFORMANCE BY STRATUM ---")
for strat, grp in df_eval.groupby('is_liver_relevant'):
    lbl = "Liver-Relevant (n=50)" if strat else "Other Ingredients (n=50)"
    print(f"{lbl}: Name Acc={grp['name_correct'].mean()*100:.1f}%, Qty Acc={grp['qty_correct'].mean()*100:.1f}%, Median Gram Err={grp['pct_error_240'].median():.1f}%, INDB Match={grp['indb_match'].mean()*100:.1f}%")

print("\n--- TOP FAILURE TYPES ---")
print(df_eval['failure_type'].value_counts())
