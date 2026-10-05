import pandas as pd
import numpy as np

# Reference daily limits (2,000 kcal reference diet, ICMR-NIN 2024 / INDIAB)
SFA_BUDGET_7PCT = 15.56  # 7% of 2000 kcal = 140 kcal / 9 kcal/g
SFA_BUDGET_10PCT = 22.22 # 10% of 2000 kcal = 200 kcal / 9 kcal/g
ADDED_SUGAR_BUDGET = 25.0 # grams
SALT_BUDGET = 5.0 # grams

# 10 Representative Dishes from T1
# Stratified: 3 Fried, 3 Creamy gravies, 2 Sweets, 2 Light
SAMPLE_RECIPES = [
    # 1. Fried
    {
        "dish_id": "samosa",
        "dish_name": "Samosa",
        "category": "Fried snack",
        "servings": 4, # makes 8 samosas, 2 per serving
        "ingredients": [
            ("maida", 200), ("potato", 300), ("oil_filling", 15),
            ("spices", 10), ("salt", 3), ("deep_fry_oil_uptake", 50) # T3 uptake ~16% on ~320g cooked
        ],
        "tarla_dalal_kcal": 256
    },
    {
        "dish_id": "puri_bhature",
        "dish_name": "Bhatura",
        "category": "Fried bread",
        "servings": 4, # makes 4 bhaturas
        "ingredients": [
            ("maida", 250), ("curd", 50), ("oil_moin", 15),
            ("salt", 3), ("deep_fry_oil_uptake", 60) # T3 uptake ~20% on ~300g cooked
        ],
        "tarla_dalal_kcal": 294
    },
    {
        "dish_id": "onion_pakora",
        "dish_name": "Onion Pakora / Bhaji",
        "category": "Fried snack",
        "servings": 4,
        "ingredients": [
            ("onion", 250), ("besan", 100), ("spices", 8),
            ("salt", 3), ("deep_fry_oil_uptake", 45) # T3 uptake ~16% on ~280g cooked
        ],
        "tarla_dalal_kcal": 215
    },
    # 2. Creamy gravies
    {
        "dish_id": "paneer_butter_masala",
        "dish_name": "Paneer Butter Masala",
        "category": "Creamy gravy",
        "servings": 4,
        "ingredients": [
            ("paneer", 250), ("butter", 30), ("oil", 15),
            ("cream", 50), ("tomato", 300), ("onion", 150),
            ("cashew", 25), ("sugar", 10), ("salt", 5), ("spices", 10)
        ],
        "tarla_dalal_kcal": 395
    },
    {
        "dish_id": "dal_makhani",
        "dish_name": "Dal Makhani",
        "category": "Creamy gravy",
        "servings": 5,
        "ingredients": [
            ("urad_dal", 150), ("rajma", 40), ("butter", 45),
            ("cream", 60), ("tomato", 200), ("salt", 5), ("spices", 10)
        ],
        "tarla_dalal_kcal": 348
    },
    {
        "dish_id": "butter_chicken",
        "dish_name": "Butter Chicken",
        "category": "Creamy gravy",
        "servings": 4,
        "ingredients": [
            ("chicken", 400), ("butter", 40), ("oil", 15),
            ("cream", 60), ("tomato", 300), ("sugar", 8), ("salt", 5), ("spices", 15)
        ],
        "tarla_dalal_kcal": 380 # Standard restaurant benchmark
    },
    # 3. Sweets
    {
        "dish_id": "gulab_jamun",
        "dish_name": "Gulab Jamun",
        "category": "Sweet / Mithai",
        "servings": 6, # 12 pieces, 2 per serving
        "ingredients": [
            ("khoya", 200), ("maida", 40), ("sugar", 250), # sugar syrup
            ("cardamom", 2), ("deep_fry_ghee_uptake", 40) # fried in ghee
        ],
        "tarla_dalal_kcal": 312
    },
    {
        "dish_id": "gajar_halwa",
        "dish_name": "Gajar Ka Halwa",
        "category": "Sweet / Mithai",
        "servings": 4,
        "ingredients": [
            ("carrot", 500), ("milk", 500), ("ghee", 45),
            ("sugar", 100), ("cashew", 20), ("cardamom", 2)
        ],
        "tarla_dalal_kcal": 288
    },
    # 4. Light dishes
    {
        "dish_id": "poha",
        "dish_name": "Kanda Poha",
        "category": "Light breakfast",
        "servings": 3,
        "ingredients": [
            ("poha", 150), ("onion", 100), ("potato", 80),
            ("oil", 15), ("peanut", 20), ("salt", 3), ("spices", 5)
        ],
        "tarla_dalal_kcal": 182
    },
    {
        "dish_id": "sambar",
        "dish_name": "Sambar",
        "category": "Light soup/dal",
        "servings": 5,
        "ingredients": [
            ("toor_dal", 100), ("vegetables", 300), ("oil", 10),
            ("tamarind", 20), ("sambar_powder", 15), ("salt", 5)
        ],
        "tarla_dalal_kcal": 125
    }
]

# Ingredient Nutrient Profiles per 100g (IFCT 2017 / INDB)
# kcal, fat_g, sfa_g, added_fat_g, added_sugar_g, salt_g
NUTRI_DB = {
    "oil": (900, 100.0, 12.0, 100.0, 0.0, 0.0),
    "oil_filling": (900, 100.0, 12.0, 100.0, 0.0, 0.0),
    "oil_moin": (900, 100.0, 12.0, 100.0, 0.0, 0.0),
    "deep_fry_oil_uptake": (900, 100.0, 12.0, 100.0, 0.0, 0.0),
    "deep_fry_ghee_uptake": (900, 99.5, 62.0, 99.5, 0.0, 0.0),
    "ghee": (900, 99.5, 62.0, 99.5, 0.0, 0.0),
    "butter": (717, 81.0, 51.0, 81.0, 0.0, 0.5),
    "cream": (290, 28.0, 17.5, 28.0, 0.0, 0.0),
    "khoya": (321, 22.3, 14.0, 22.3, 0.0, 0.0),
    "sugar": (387, 0.0, 0.0, 0.0, 100.0, 0.0),
    "paneer": (265, 20.8, 13.5, 0.0, 0.0, 0.0),
    "maida": (364, 1.0, 0.2, 0.0, 0.0, 0.0),
    "besan": (372, 5.6, 0.8, 0.0, 0.0, 0.0),
    "urad_dal": (341, 1.4, 0.3, 0.0, 0.0, 0.0),
    "rajma": (333, 1.3, 0.3, 0.0, 0.0, 0.0),
    "toor_dal": (343, 1.5, 0.3, 0.0, 0.0, 0.0),
    "potato": (97, 0.1, 0.0, 0.0, 0.0, 0.0),
    "onion": (40, 0.1, 0.0, 0.0, 0.0, 0.0),
    "tomato": (18, 0.2, 0.0, 0.0, 0.0, 0.0),
    "carrot": (48, 0.2, 0.0, 0.0, 0.0, 0.0),
    "vegetables": (35, 0.2, 0.0, 0.0, 0.0, 0.0),
    "chicken": (165, 3.6, 1.0, 0.0, 0.0, 0.1),
    "cashew": (553, 43.8, 7.8, 0.0, 0.0, 0.0),
    "peanut": (567, 49.2, 6.8, 0.0, 0.0, 0.0),
    "curd": (60, 3.1, 2.0, 0.0, 0.0, 0.0),
    "milk": (65, 3.6, 2.2, 0.0, 0.0, 0.0),
    "poha": (346, 1.2, 0.2, 0.0, 0.0, 0.0),
    "tamarind": (239, 0.6, 0.1, 0.0, 0.0, 0.0),
    "spices": (300, 10.0, 2.0, 0.0, 0.0, 0.0),
    "sambar_powder": (300, 10.0, 2.0, 0.0, 0.0, 0.0),
    "cardamom": (311, 6.7, 0.7, 0.0, 0.0, 0.0),
    "salt": (0, 0.0, 0.0, 0.0, 0.0, 100.0)
}

rows = []
for recipe in SAMPLE_RECIPES:
    servings = recipe["servings"]
    tot_kcal = 0.0
    tot_fat = 0.0
    tot_sfa = 0.0
    tot_added_fat = 0.0
    tot_added_sugar = 0.0
    tot_salt = 0.0
    
    for ingr, grams in recipe["ingredients"]:
        nut = NUTRI_DB.get(ingr, (100, 1.0, 0.2, 0.0, 0.0, 0.0))
        factor = grams / 100.0
        tot_kcal += nut[0] * factor
        tot_fat += nut[1] * factor
        tot_sfa += nut[2] * factor
        tot_added_fat += nut[3] * factor
        tot_added_sugar += nut[4] * factor
        tot_salt += nut[5] * factor
        
    per_serv_kcal = tot_kcal / servings
    per_serv_fat = tot_fat / servings
    per_serv_sfa = tot_sfa / servings
    per_serv_added_fat = tot_added_fat / servings
    per_serv_added_sugar = tot_added_sugar / servings
    per_serv_salt = tot_salt / servings
    
    # % Energy from Added Fat (HFSS rule >15%)
    added_fat_kcal = per_serv_added_fat * 9.0
    pct_energy_from_added_fat = (added_fat_kcal / per_serv_kcal) * 100.0 if per_serv_kcal > 0 else 0
    is_hfss_added_fat = pct_energy_from_added_fat > 15.0
    
    # % Daily Budgets
    pct_sfa_7 = (per_serv_sfa / SFA_BUDGET_7PCT) * 100.0
    pct_sfa_10 = (per_serv_sfa / SFA_BUDGET_10PCT) * 100.0
    pct_sugar = (per_serv_added_sugar / ADDED_SUGAR_BUDGET) * 100.0
    pct_salt = (per_serv_salt / SALT_BUDGET) * 100.0
    
    # Comparison vs Tarla Dalal
    td_kcal = recipe["tarla_dalal_kcal"]
    kcal_diff = per_serv_kcal - td_kcal
    kcal_pct_diff = (kcal_diff / td_kcal) * 100.0
    
    # Composite Liver Load Score (heuristic prototype for ranking)
    # Weights: SFA (35%) + Sugar (30%) + Added Fat (20%) + Salt (15%)
    liver_load_score = (0.35 * pct_sfa_7) + (0.30 * pct_sugar) + (0.20 * pct_energy_from_added_fat) + (0.15 * pct_salt)
    
    rows.append({
        "dish_name": recipe["dish_name"],
        "category": recipe["category"],
        "servings": servings,
        "calc_energy_kcal": round(per_serv_kcal, 1),
        "tarla_dalal_kcal": td_kcal,
        "energy_diff_pct": round(kcal_pct_diff, 1),
        "total_fat_g": round(per_serv_fat, 1),
        "sfa_g": round(per_serv_sfa, 1),
        "pct_sfa_budget_7pct": round(pct_sfa_7, 1),
        "added_sugar_g": round(per_serv_added_sugar, 1),
        "pct_sugar_budget": round(pct_sugar, 1),
        "pct_energy_added_fat": round(pct_energy_from_added_fat, 1),
        "icmr_hfss_flag": is_hfss_added_fat,
        "salt_g": round(per_serv_salt, 2),
        "pct_salt_budget": round(pct_salt, 1),
        "prototype_liver_score": round(liver_load_score, 1)
    })

df_t5 = pd.DataFrame(rows).sort_values(by="prototype_liver_score", ascending=False)
df_t5.to_csv("data/t5_score_sanity.csv", index=False)
print("Saved data/t5_score_sanity.csv!\n")
print(df_t5[['dish_name', 'category', 'calc_energy_kcal', 'tarla_dalal_kcal', 'energy_diff_pct', 'pct_sfa_budget_7pct', 'pct_sugar_budget', 'icmr_hfss_flag', 'prototype_liver_score']])
