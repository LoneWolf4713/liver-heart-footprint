import pandas as pd
import numpy as np

# Ground truth lab-measured values
# Sources:
# 1. safefood Ireland 2015 "What's in your Indian takeaway?" (Foodtest Labs, n=30 takeaway samples each, analysed)
# 2. UK CoFID 2021 (McCance & Widdowson / Univ. of Leeds 2007 analytical data & Aspland & James 1997)
# 3. Chen, Gilbert & Khokhar 2009 (Food Chem 113:825, Zenodo 10043766)
# 4. Jain, Passi & Selvamurthy 2024 (J Food Sci Technol 61:2185)

FRIED_ITEMS = [
    {
        "item": "Puri (Poori)",
        "source": "UK CoFID 2021 (Univ. of Leeds 2007, n=9 samples) / Chen 2009",
        "sample_type": "Cooked food, lab-analysed (6 homemade, 3 cafe)",
        "lab_fat_g_per_100g": 22.3,
        "lab_sd": 3.1,
        "raw_fat_in_dough_g": 2.0, # minimal fat in whole wheat flour + 1 tsp moin
        "water_loss_pct": 20.0, # Chen 2009: 18-24%
        "oil_uptake_factor_low": 15.0, # % of cooked weight
        "oil_uptake_factor_high": 24.0,
        "uptake_source": "Chen 2009 (up to 18.4g uptake/100g) + McCance & Widdowson fried chapati factor"
    },
    {
        "item": "Onion Pakora / Bhaji",
        "source": "safefood Ireland 2015 (n=30 takeaway portions, Foodtest Labs)",
        "sample_type": "Takeaway food, lab-analysed",
        "lab_fat_g_per_100g": 16.98,
        "lab_sd": 5.46,
        "raw_fat_in_dough_g": 3.5, # besan fat ~5g/100g, onions ~0.1g
        "water_loss_pct": 25.0,
        "oil_uptake_factor_low": 12.0,
        "oil_uptake_factor_high": 22.0,
        "uptake_source": "safefood 2015 + CoFID 15-828 (14.7g) & 15-620 (22.0g)"
    },
    {
        "item": "Onion Bhaji / Pakora (Restaurant UK)",
        "source": "UK CoFID 2021 (Univ. of Leeds 2007, Food code 15-620, n=11)",
        "sample_type": "Restaurant/takeaway London/Bham/Leeds, lab-analysed",
        "lab_fat_g_per_100g": 22.0,
        "lab_sd": 4.2,
        "raw_fat_in_dough_g": 3.5,
        "water_loss_pct": 28.0,
        "oil_uptake_factor_low": 15.0,
        "oil_uptake_factor_high": 25.0,
        "uptake_source": "Univ. of Leeds 2007 (crispy vegetable fritters)"
    },
    {
        "item": "Chicken Pakora",
        "source": "safefood Ireland 2015 (n=30 takeaway portions, Foodtest Labs)",
        "sample_type": "Takeaway food, lab-analysed",
        "lab_fat_g_per_100g": 10.32,
        "lab_sd": 5.34,
        "raw_fat_in_dough_g": 2.5, # chicken breast ~1.5g fat, light batter
        "water_loss_pct": 18.0,
        "oil_uptake_factor_low": 7.0,
        "oil_uptake_factor_high": 14.0,
        "uptake_source": "safefood 2015 (batter coating uptake on lean poultry)"
    },
    {
        "item": "Meat Samosa",
        "source": "UK CoFID 2021 (Aspland & James 1997, Food code 19-326, n=10)",
        "sample_type": "Indian restaurants takeaway, lab-analysed",
        "lab_fat_g_per_100g": 17.3,
        "lab_sd": 3.8,
        "raw_fat_in_dough_g": 6.5, # lamb filling fat + moin in pastry
        "water_loss_pct": 15.0,
        "oil_uptake_factor_low": 10.0,
        "oil_uptake_factor_high": 18.0,
        "uptake_source": "Aspland & James 1997 / USDA deep-fried turnover factors"
    },
    {
        "item": "Vegetable Samosa (Retail)",
        "source": "UK CoFID 2021 (LGC 1989-1990, Food code 15-305, n=5)",
        "sample_type": "Retail brands, lab-analysed",
        "lab_fat_g_per_100g": 9.3,
        "lab_sd": 2.1,
        "raw_fat_in_dough_g": 3.0, # potato-pea filling low fat + moin
        "water_loss_pct": 12.0,
        "oil_uptake_factor_low": 6.0,
        "oil_uptake_factor_high": 12.0,
        "uptake_source": "LGC 1990 retail baked/flash-fried samosa"
    },
    {
        "item": "Bread Pakora",
        "source": "Jain, Passi & Selvamurthy 2024 (J Food Sci Technol 61:2185)",
        "sample_type": "Delhi street-food fried snack (fresh cycle)",
        "lab_fat_g_per_100g": 18.1, # converted from 24.1% dry basis with ~25% moisture
        "lab_sd": 2.5,
        "raw_fat_in_dough_g": 2.0, # bread + potato + besan
        "water_loss_pct": 22.0,
        "oil_uptake_factor_low": 14.0,
        "oil_uptake_factor_high": 22.0,
        "uptake_source": "Jain & Passi 2024 (bread crumb high porosity absorption)"
    },
    {
        "item": "Mathri",
        "source": "Jain, Passi & Selvamurthy 2024 (J Food Sci Technol 61:2185)",
        "sample_type": "Traditional fried pastry snack (fresh cycle)",
        "lab_fat_g_per_100g": 21.8, # low moisture snack (~5% moisture, 22.9% dry basis)
        "lab_sd": 1.9,
        "raw_fat_in_dough_g": 12.0, # heavy moin in mathri dough (10-15g/100g)
        "water_loss_pct": 10.0,
        "oil_uptake_factor_low": 18.0,
        "oil_uptake_factor_high": 26.0,
        "uptake_source": "Jain & Passi 2024 / NIN Indian Recipes"
    }
]

rows = []
for item in FRIED_ITEMS:
    # Model calculation:
    # Cooked fat % = baseline dough/filling fat + oil uptake factor
    # Because oil uptake is measured directly as % of cooked food weight:
    est_low = item["raw_fat_in_dough_g"] * 0.8 + item["oil_uptake_factor_low"]
    est_high = item["raw_fat_in_dough_g"] * 1.1 + item["oil_uptake_factor_high"]
    
    lab_val = item["lab_fat_g_per_100g"]
    within_range = (est_low <= lab_val <= est_high)
    
    # Midpoint error
    est_mid = (est_low + est_high) / 2.0
    abs_err = abs(est_mid - lab_val)
    pct_err = (abs_err / lab_val) * 100.0
    
    rows.append({
        "item": item["item"],
        "source": item["source"],
        "sample_type": item["sample_type"],
        "lab_fat_g_100g": lab_val,
        "lab_sd": item["lab_sd"],
        "model_est_low": round(est_low, 1),
        "model_est_high": round(est_high, 1),
        "model_est_mid": round(est_mid, 1),
        "within_range": within_range,
        "abs_error_g": round(abs_err, 2),
        "pct_error": round(pct_err, 1),
        "uptake_literature_basis": item["uptake_source"]
    })

df_t3 = pd.DataFrame(rows)
df_t3.to_csv("data/t3_fried_fat_validation.csv", index=False)
print("Saved data/t3_fried_fat_validation.csv")
print(df_t3[['item', 'lab_fat_g_100g', 'model_est_low', 'model_est_high', 'within_range', 'pct_error']])
print(f"\nItems within literature uptake range: {df_t3['within_range'].sum()} / {len(df_t3)} ({df_t3['within_range'].mean()*100:.1f}%)")
print(f"Median Absolute Percentage Error: {df_t3['pct_error'].median():.1f}%")
