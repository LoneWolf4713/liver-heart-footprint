# Deliverable 2 (D2) · Engine Verification Summary Report

Consolidated proof across all three D2 verification criteria specified in `FORM_FIELDS.md`.

## 1. Parse, Match & Gram Accuracy on Hand-Annotated Real Lines (160 Lines >= 150 Target)

| Metric | Public Gold (120) | Holdout (40) | Combined (160) |
|---|---:|---:|---:|
| Parse status | **100.0%** (120/120) | **100.0%** (40/40) | **100.0%** (160/160) |
| Quantity value | **100.0%** (109/109) | **100.0%** (36/36) | **100.0%** (145/145) |
| Unit canonicalization | **99.1%** (108/109) | **100.0%** (36/36) | **99.3%** (144/145) |
| Ingredient name keyword | **100.0%** (120/120) | **100.0%** (40/40) | **100.0%** (160/160) |
| Stated g / ml extraction | **100.0%** (109/109) | **100.0%** (36/36) | **100.0%** (145/145) |
| Database code match | **100.0%** (112/112) | **100.0%** (37/37) | **100.0%** (149/149) |
| Gram conversion (given code) | **100.0%** (106/106) | **100.0%** (36/36) | **100.0%** (142/142) |
| End-to-end grams from raw text | **100.0%** (106/106) | **100.0%** (36/36) | **100.0%** (142/142) |

## 2. INDB Published Value Reproduction (Target: >=95% across ~1,000 dishes)

- **Corpus tested:** 1014 INDB recipes (10271 ingredient lines; 0 lines without grams).
- **IFCT-dependent test set (`982` recipes):**
  - Energy, Fat, Protein, Fibre, SFA, Sodium, Free Sugars: **982 / 982 (100.0%)** within 2% or absolute tolerance.
  - Carbohydrates: **957 / 982 (97.5%)**.
- **Control (UK/US only, `13` recipes):** **13 / 13 (100.0%)** on all 8 nutrients.

## 3. Laboratory-Analysed Cooked Dish Comparison (Target: >=10 dishes)

- **Dishes evaluated:** **10 distinct dishes** across **31 recipe-lab pairs** (28 recipes across home, retail, takeaway).
- **Overall median Ratio (Recipe M2 / Lab M2):** **1.06** (mean 1.12; takeaway median 0.98).
- **Line & mass coverage on validation corpus:** 474 / 549 lines included (86.3%, 21,521.9 g edible mass).
