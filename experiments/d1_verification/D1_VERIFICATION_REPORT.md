# Deliverable 1 (D1) · Dataset Range & Holdout Verification Report

- **Dataset:** `data/curated/fried_foods_lab.csv`
- **Total Rows / Samples:** **69 rows** (233 lab samples) across **10 published sources**
- **Provenance Completeness:** **69/69** rows have non-empty `source` and `table_page` citations (`0` missing)

## 1. Recomputed Fat Ranges by Category (g fat / 100 g cooked food)

| Category | Rows | Samples (n) | Sources | Min | Q1 | Median | Q3 | Max | Mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| crisp namkeen | 21 | 51 | 5 | 6.10 | 13.00 | 21.80 | 35.00 | 57.18 | 24.03 |
| battered fritter | 20 | 99 | 5 | 6.28 | 9.77 | 18.85 | 22.55 | 47.60 | 18.53 |
| stuffed pastry | 10 | 29 | 4 | 7.71 | 10.08 | 23.25 | 31.03 | 46.61 | 22.46 |
| flat dough | 10 | 42 | 6 | 5.20 | 11.40 | 17.00 | 20.95 | 22.30 | 15.96 |
| syrup-soaked sweet | 7 | 11 | 3 | 4.80 | 14.70 | 20.20 | 23.70 | 39.00 | 20.11 |
| other | 1 | 1 | 1 | 27.41 | 27.41 | 27.41 | 27.41 | 27.41 | 27.41 |

## 2. Leave-One-Source-Out (LOSO) Holdout Validation

Each study is held out in turn; remaining sources build the `[min, max]` category envelope for every overlapping category.

- **Evaluable held-out measurements:** **68** (`1` held-out row had no other-source category peer)
- **Exact in-range coverage:** **49 / 68 (72.1%)**
- **Within ±2.0 g/100g of envelope:** **60 / 68 (88.2%)**

| Held-Out Source | Total Rows | Evaluable Rows | Inside Other-Source Range | Coverage % |
|---|---:|---:|---:|---:|
| Chen 2009 | 2 | 2 | 2 | 100.0% |
| Gaikwad 2022 | 2 | 2 | 2 | 100.0% |
| Gupta 2016 | 21 | 20 | 11 | 55.0% |
| Jain 2024 | 3 | 3 | 3 | 100.0% |
| Joshee 2019 | 15 | 15 | 6 | 40.0% |
| Neethu 2025 | 2 | 2 | 2 | 100.0% |
| Sakhale 2011 | 2 | 2 | 2 | 100.0% |
| UK CoFID 2021 | 18 | 18 | 17 | 94.4% |
| Yadav 2012 | 2 | 2 | 2 | 100.0% |
| safefood 2015 | 2 | 2 | 2 | 100.0% |
