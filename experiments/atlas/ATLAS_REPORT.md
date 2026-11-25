# Liver and Heart Footprint Atlas of Indian Recipes
**Deliverable 3: Cuisine-Level Computational Analysis of 1,014 Standardized INDB Formulations and 71 Web Recipes**
*(Code-Verified & Synchronized with Integrated Frying Bath Correction)*

**Course:** BIO544 Computational Gastronomy, Monsoon 2026, IIIT-Delhi  
**Instructor:** Prof. Ganesh Bagler  
**Group:** 45 (Parth Verma [2024407], Pratyaksh Kumar [2024431])  
**Status:** Reconciled & Code-Verified via `PYTHONPATH=src python3 experiments/atlas/run_atlas.py`

---

## 1. Corpus Reconciliation, Recipe Share & Ingredient-Mass Coverage

Every statistic in this report comes directly from running the deterministic Phase 1 engine (`src/lhf`) with integrated deep-frying oil-bath replacement (`src/lhf/frying.py`) across **1,014** standardized Indian Nutrient Databank (INDB) formulations and **71** real web recipes scraped across **10** websites.

| Corpus | Total Recipes | With Valid Servings (%) | Ingredient Lines Included / Total (%) | Edible Mass Analyzed (g) | Frying Baths Corrected |
|---|---:|---:|---:|---:|---:|
| **INDB Textbook Recipes** | 1,014 | 932 (91.9%) | 10,025 / 10,148 (98.8%) | 460,166.3 g *(502,646.3 g pre-bath)* | 103 recipes *(42,480.0 g pan baths stripped)* |
| **Web Benchmark Recipes** | 71 | 71 (100.0%) | 1,141 / 1,339 (85.2%) | 58,030.6 g | 0 *(web blogs write fry oil unquantified)* |
| **Combined Atlas** | **1,085** | **1,003 (92.4%)** | **11,166 / 11,487 (97.2%)** | **518,196.9 g** | **103 INDB dishes** |

---

## 2. Daily Reference Ceilings (`data/curated/baselines.csv`)

Nutrient loads are evaluated per serving against ICMR-NIN Dietary Guidelines for Indians (2024), WHO guidelines, and the NSO HCES 2022–24 urban adult baseline (**2,240 kcal/day**):

- **Saturated Fat (General):** `24.9 g/day` (`<10.0%` of energy)
- **Saturated Fat (Cardiometabolic High-Risk):** `17.4 g/day` (`<7.0%` of energy)
- **Total Dietary Fat:** `74.7 g/day` (`30.0%` of energy)
- **Added Free Sugars:** `25.0 g/day` (`<5.0%` of energy conditional cap)
- **Sodium (Na):** `1,967 mg/day` (`5.0 g/day` salt ceiling)

---

## 3. Median Per-Serving Footprint Across 11 INDB Categories (n = 932)

| Culinary Category | Recipes (w/ Servings / Total) | SFA Median (`24.9g`) | High-Risk SFA (`17.4g`) | Added Sugar (`25g`) | Sodium (`1,967mg`) | Energy (`kcal`) |
|---|---:|---:|---:|---:|---:|---:|
| **Sweets & Desserts** | 262 / 282 | 7.85 g (**31.6%**) | **31.6%** | 15.46 g (**61.9%**) | 3.8% | 315.8 kcal |
| **Snacks & Street Food** | 116 / 130 | 7.72 g (**31.0%**) | **40.8%** | 0.0% | 22.3% | 343.3 kcal |
| **Curries & Gravies** | 70 / 73 | 6.80 g (**27.3%**) | **28.0%** | 0.0% | 18.5% | 323.7 kcal |
| **Rice & Grains** | 30 / 34 | 6.21 g (**25.0%**) | **25.0%** | 0.0% | 19.2% | 442.8 kcal |
| **Vegetables & Sabzis** | 94 / 98 | 4.62 g (**18.6%**) | 18.8% | 0.0% | 20.6% | 227.3 kcal |
| **Breakfast & Tiffin** | 72 / 72 | 4.54 g (**18.2%**) | 19.2% | 0.0% | 11.6% | 285.2 kcal |
| **Breads & Flatbreads** | 62 / 63 | 3.62 g (**14.5%**) | 14.5% | 0.0% | 20.4% | 478.0 kcal |
| **Soups & Stews** | 47 / 55 | 3.11 g (**12.5%**) | 12.5% | 0.0% | **1,028.3%*** | 157.4 kcal |
| **Beverages** | 65 / 72 | 2.54 g (**10.2%**) | 10.2% | 15.00 g (**60.0%**) | 2.9% | 171.5 kcal |
| **Condiments & Chutneys** | 67 / 85 | 1.94 g (**7.8%**) | 7.8% | 0.0% | 10.9% | 115.3 kcal |
| **Dals & Legumes** | 47 / 50 | 1.19 g (**4.8%**) | 5.2% | 0.0% | 20.8% | 188.3 kcal |

*\*Note on Soups & Stews sodium (1,028.3% · 20,226.3 mg median): Verified in raw INDB sources — 26 of 47 soups with servings (e.g., `BFP066`, `BFP067`, `ASC079`) code liquid stock volume (480 ml or 0.5 cup) directly onto dry stock cubes (`K506`/`K507`). Figure 1 breaks the axis at 108% so the remaining 10 categories remain clear.*

---

## 4. Saturated Fat Culprit Decomposition (`atlas_drivers_by_category.csv`)

Mean percentage of each recipe's total saturated fat originating from **Dairy Fat** (`DAIRY_FAT`), **Cooking Oil & Frying** (`COOKING_OIL`), vs. **Inherent Food Lipids** (`OTHER`):

| Culinary Category | Dairy Fat SFA (%) | Cooking Oil & Frying SFA (%) | Inherent Food SFA (%) |
|---|---:|---:|---:|
| **Sweets & Desserts** | **63.6%** | 4.2% | 32.2% |
| **Soups & Stews** | **45.3%** | 15.3% | 39.4% |
| **Rice & Grains** | **34.4%** | 31.3% | 34.3% |
| **Snacks & Street Food** | 32.8% | **46.0%** | 21.2% |
| **Breakfast & Tiffin** | 23.6% | 27.1% | **49.2%** |
| **Vegetables & Sabzis** | 23.5% | **51.7%** | 24.8% |
| **Breads & Flatbreads** | 20.9% | **58.2%** | 20.9% |
| **Beverages** | 19.7% | 2.2% | **78.1%** |
| **Dals & Legumes** | 18.5% | **50.4%** | 31.1% |
| **Curries & Gravies** | 16.5% | 38.1% | **45.4%** |
| **Condiments & Chutneys** | 12.0% | 19.9% | **68.1%** |

---

## 5. Textbook (INDB) vs. Modern Web Comparison Across 15 Benchmark Dishes (`atlas_textbook_vs_web.csv`)

Across the **12 directly comparable dishes** (excluding the 3 deep-fried dishes where consumer blogs write *"oil for deep frying"* without quantities), web recipes pack **1.10× median fat**, **1.18× median SFA**, and **1.11× median energy** over standardized INDB textbook versions.

| Dish Name | INDB / Web Count | INDB Fat | Web Fat | Fat Ratio | INDB SFA | Web SFA | SFA Ratio | Note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Vegetable Pulao | 2 / 1 | 14.4 g | 11.0 g | 0.77× | 1.8 g | 7.4 g | **4.01×** | Ghee finishing vs refined oil |
| Chicken Biryani | 2 / 4 | 19.0 g | 30.6 g | 1.61× | 2.7 g | 9.4 g | **3.54×** | Heavy web ghee layering |
| Chole | 1 / 5 | 8.2 g | 9.4 g | 1.15× | 1.0 g | 2.9 g | **2.97×** | Ghee/butter tadka online |
| Poha | 1 / 3 | 13.2 g | 21.2 g | 1.61× | 2.4 g | 3.1 g | 1.31× | Extra oil + peanut garnish |
| Dal Makhani | 1 / 6 | 10.8 g | 13.5 g | 1.25× | 6.3 g | 7.9 g | 1.26× | Cream + butter finish |
| Gajar Ka Halwa | 1 / 5 | 16.3 g | 18.0 g | 1.10× | 9.1 g | 10.8 g | 1.19× | Ghee/khoya enrichment |
| Paneer Butter Masala | 2 / 6 | 28.5 g | 31.3 g | 1.10× | 13.6 g | 15.9 g | 1.17× | Butter + cream saturation |
| Butter Chicken | 1 / 3 | 23.9 g | 22.1 g | 0.92× | 8.4 g | 9.1 g | 1.09× | Lipid parity; 10× higher web Na |
| Bhindi Sabzi | 2 / 2 | 11.9 g | 12.1 g | 1.01× | 1.5 g | 1.5 g | 1.01× | Home stir-fry parity control |
| Sarson Ka Saag | 1 / 2 | 8.3 g | 14.7 g | 1.77× | 4.7 g | 4.1 g | 0.89× | Extra white butter/oil |
| Methi Aloo | 1 / 3 | 20.5 g | 9.5 g | 0.46× | 2.6 g | 1.2 g | 0.45× | INDB 1-serving oil vs 3-serving blog |
| Sambar | 1 / 4 | 11.3 g | 5.2 g | 0.46× | 4.9 g | 1.9 g | 0.39× | INDB 2-serving oil vs home blog |
| Samosa *(fry artifact)* | 2 / 4 | 24.6 g | 6.1 g | 0.25×* | 10.7 g | 1.7 g | 0.15×* | Web omits deep-fry oil quantity |
| Onion Pakora *(fry artifact)* | 1 / 2 | 33.6 g | 3.4 g | 0.10×* | 12.1 g | 0.4 g | 0.07×* | Web omits deep-fry oil quantity |
| Gulab Jamun *(fry artifact)* | 2 / 5 | 54.5 g | 3.4 g | 0.06×* | 22.0 g | 2.1 g | 0.09×* | Web omits deep-fry oil quantity |

---

## 6. Generated Files (`experiments/atlas/`)

1. `run_atlas.py` — Reproducible end-to-end Atlas generator
2. `atlas_metrics.json` — Summary snapshot & mass/line coverage metrics
3. `atlas_category_summary.csv` & `atlas_drivers_by_category.csv` — 11-category tables
4. `atlas_textbook_vs_web.csv` — 15-dish paired benchmark comparison
5. `fig1_category_footprint_bars.{png,svg}` through `fig4_liver_risk_matrix.{png,svg}` (synced into `app/static/figures/` and `app/static/js/atlas_data.js`)
