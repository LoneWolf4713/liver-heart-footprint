import pandas as pd
import json
import re

file_path = "research_log/data/CoFID_2021.xlsx"
df = pd.read_excel(file_path, sheet_name="1.3 Proximates", header=0)

cols = df.columns.tolist()

foods = []
for idx, row in df.iterrows():
    code = row['Food Code']
    name = str(row['Food Name'])
    ref = str(row['Main data references'])
    footnote = str(row['Footnote'])
    fat = row['Fat (g)']
    
    name_lower = name.lower()
    if pd.isna(code) or str(code) == 'nan':
        continue
        
    keywords = ["curry", "masala", "dal", "aloo", "chana", "saag", "korma", "bhaji", "rogan", "kebab", "kofta", "tikka", "balti", "madras", "jalfrezi", "samosa", "pilau", "naan", "dhal", "vindaloo", "pasanda", "makhani"]
    is_indian = any(k in name_lower for k in keywords)
    
    if is_indian:
        is_analysed = "anal" in ref.lower() or "anal" in footnote.lower()
        is_recipe = "recipe" in ref.lower() or "recipe" in footnote.lower() or "calculated" in ref.lower() or "calculated" in footnote.lower()
        # also we want non-fried cooked
        if "fried" in name_lower and "non-fried" not in name_lower and "not fried" not in name_lower:
            continue
        if is_analysed and not is_recipe:
            foods.append({"code": code, "name": name, "fat": fat, "ref": ref, "footnote": footnote})

print(json.dumps(foods, indent=2))
