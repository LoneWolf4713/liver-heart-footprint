# Adversarial Code and Data Audit: Task T2 (Nutrient Summing)

**Auditor:** Adversarial Code & Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Module:** `src/lhf/compute.py`  
**Associated Test Files:** `tests/test_t2.py`, `acceptance/test_t2_indb.py`  
**Specification Reference:** `docs/SPEC.md` §3 (Nutrient Summing), `docs/SPEC.md` §1 (Package layout & Integrity Rules), `AGENTS.md`  

---

## 1. Executive Summary & Verdict

### **Verdict: MINOR ISSUES**

The implementation of `lhf.compute` in `src/lhf/compute.py` is clean, robust, and mathematically sound. It reproduces INDB's published dish values across 995 real recipes with 100% agreement on 7 key macro/micronutrients and 97.5% on carbohydrates (passing all acceptance thresholds). It contains no hardcoded test answers, no prohibited imports, and no forbidden numeric literals (only 0.0, 0, and 100 appear, fully compliant with Rule 1).

However, our adversarial probe revealed:
1. **Spec Discrepancy (Architect Miscount):** SPEC.md §3 states `NUTRIENTS: a tuple of the 12 nutrient column names above`, but the composition table schema actually defines **13** nutrient columns. `src/lhf/compute.py` correctly includes all 13 columns.
2. **Boundary Asymmetry for Non-Positive Grams:** `sum_nutrients` does not filter out non-positive grams (`grams <= 0`). If an ingredient has `grams = 0.0` and its composition has `water_g = NaN`, it erroneously contaminates recipe `water_g` as `NaN`. If `grams < 0`, `totals` has negative values, but `per_100g` silently returns `0.0` due to `elif total_g > 0:`.
3. **Under-Assertive Unit Tests:** `tests/test_t2.py` checks only 7 of the 13 nutrients in `test_nutrients_tuple` and omits boundary and fuzz probes.

---

## 2. Integrity Rules & Static Analysis Checks

### 2.1 Rule 1: No Invented Numbers (AST Analysis)
We parsed `src/lhf/compute.py` into an Abstract Syntax Tree (AST) to extract all numeric constants:
```python
# AST Scan Results for src/lhf/compute.py:
Line 16: 0.0    # total_g initialization (Allowed: 0)
Line 17: 0.0    # totals dict initialization (Allowed: 0)
Line 58: 0      # elif total_g > 0 check (Allowed: 0)
Line 59: 100    # per_100g scaling factor (Allowed: 100)
Line 61: 0.0    # fallback per_100g value (Allowed: 0)
```
- **Total Numeric Literals:** 5
- **Forbidden Literals:** 0
- **Status:** **PASS** (Strictly adheres to Rule 1: only literals in `{0-12, 100, 1000}` are used).

### 2.2 Prohibited Imports and Network Isolation
- `src/lhf/compute.py` imports only:
  - `import math` (standard library)
  - `from lhf import composition` (internal package module)
- No network libraries (`urllib`, `requests`, `httpx`), no randomness (`random`), no subprocesses, and no imports from `acceptance/`.
- **Status:** **PASS**

### 2.3 Cheating / Hardcoding Detection
- No dish IDs, recipe codes, or specific food codes appear in `compute.py`.
- No branch conditions test for specific test harness fixtures.
- Git commit log analysis (`commit ffa634a67628cb3f3e927cc37f915c3e7bf096f0`) verifies standard algorithmic implementation.
- **Status:** **PASS**

---

## 3. Detailed Specification & Contract Audit

### 3.1 Spec Discrepancy: `NUTRIENTS` Tuple Count (12 vs 13)
- **Spec Text (`docs/SPEC.md` §3):**
  > `- NUTRIENTS: a tuple of the 12 nutrient column names above.`
- **Actual Composition Table (`docs/SPEC.md` §2, `src/lhf/composition.py`):**
  The table defines 16 columns:
  - 3 Non-Nutrient Columns: `name`, `source`, `energy_flag`.
  - 13 Nutrient Columns:
    1. `energy_kj`
    2. `energy_kcal`
    3. `fat_g`
    4. `sfa_g`
    5. `mufa_g`
    6. `pufa_g`
    7. `tfa_g`
    8. `carb_g`
    9. `freesugar_g`
    10. `fibre_g`
    11. `protein_g`
    12. `sodium_mg`
    13. `water_g`
- **Root Cause:** In SPEC §2, the architect mapped 12 nutrients from the raw IFCT transcription (`enerc`, `fatce`, `fasat`, `fams`, `fapu`, `fatrn`, `choavldf`, `fsugar`, `fibtg`, `protcnt`, `na`, `water`), and then added `energy_kcal = energy_kj / KJ_PER_KCAL` on the next line. When writing §3, the author counted the 12 mapped IFCT items, failing to include `energy_kcal`.
- **Code Behavior:** `compute.py` defines `NUTRIENTS = composition.NUTRIENT_COLUMNS`, which contains all 13 columns.
- **Evaluation:** The code is **scientifically correct**. Omitting `energy_kcal` would break downstream modules (e.g. `footprint.py` and `pipeline.py`). However, the discrepancy between the text of SPEC §3 ("12") and the data model ("13") must be noted.

### 3.2 Contract Compliance: `sum_nutrients(items)`
Contract requirements per SPEC §3:
1. `items`: List of dicts `{"code": str, "grams": float or None}`.
2. Return dictionary containing:
   - `"total_g"`: Sum of mass of valid items.
   - `"totals"`: Sum of each nutrient across valid items.
   - `"per_100g"`: Nutrient density per 100g (`totals[k] / total_g * 100`).
   - `"skipped"`: 0-based indices of items with `grams is None` or `code not in table`.
   - `"unknown_tfa_items"`: Indices of included items having `tfa_g = NaN`.
   - `"unknown_water_items"`: Indices of included items having `water_g = NaN`.

All 6 keys are unconditionally returned across all execution paths.

---

## 4. Adversarial Probing & Edge-Case Findings

We executed custom adversarial probe scripts across boundary conditions, type oddities, missing fields, and numerical limits.

### 4.1 Empty / Null / Sequence Variations
| Input | Behavior | Evaluation |
|---|---|---|
| `items = []` | Returns `total_g=0.0`, all totals `0.0`, all per_100g `0.0`, skipped/unknown lists empty. | **PASS** |
| `items = None` | Evaluates `if items:` as False; returns zero totals. | **PASS** |
| `items = ()` (empty tuple) | Evaluates `if items:` as False; returns zero totals. | **PASS** |
| `items = (x for x in [...])` (generator) | Iterates cleanly; returns correct sums. | **PASS** |

### 4.2 Skipped Items Handling
- `grams is None`: Correctly added to `"skipped"` (Line 29).
- `grams = float("nan")` or `np.nan`: Correctly added to `"skipped"` (Line 28).
- `code is None` or `code = ""`: Correctly added to `"skipped"` (Line 28).
- `code` not in table index: Correctly added to `"skipped"` (Line 28).
- Items missing `"code"` or `"grams"` keys: `.get()` returns `None`, correctly added to `"skipped"`.
- Total grams exclusion: Skipped items do **not** contribute to `total_g` or `totals`.

### 4.3 NaN Handling for `tfa_g` and `water_g`
The spec requires: *"For tfa_g and water_g, the total is NaN if any included item has NaN. Report unknown_tfa_items and unknown_water_items as lists of indexes."*

Adversarial testing confirmed:
1. **Order Independence:**
   - Valid item followed by NaN item: `totals["water_g"] = NaN`, `unknown_water_items = [1]`.
   - NaN item followed by valid item: `totals["water_g"] = NaN`, `unknown_water_items = [0]`.
   - Both items NaN: `totals["water_g"] = NaN`, `unknown_water_items = [0, 1]`.
2. **Skipped Item Isolation:**
   - If an item with `water_g = NaN` is skipped (e.g. `grams = None`), it does **not** contaminate `totals` with NaN, and its index is **not** placed in `unknown_water_items`.
3. **Per-100g Reflection:**
   - When `totals[k]` is NaN, `per_100g[k]` evaluates to `float("nan")` without triggering float errors.

### 4.4 Discovered Edge-Case Vulnerabilities & Anomalies

#### [FINDING 1 - MINOR] Zero-gram ingredients with unknown water/tfa contaminate recipe totals
- **Location:** `src/lhf/compute.py:28-48`
- **Description:** Line 28 filters out `grams is None` and `isnan(grams)`, but permits `grams == 0.0`.
  If an item has `grams = 0.0` and its composition code is UK Sunflower Oil (`T508`, where `water_g = NaN`), `composition.nutrients_for("T508", 0.0)` computes `nan * 0.0 = nan`.
  Lines 40 & 46 detect `math.isnan(v)` and append the index to `unknown_water_items`, setting `totals["water_g"] = NaN`.
- **Impact:** Adding 0 grams of an ingredient causes the entire recipe's water content to become `NaN` (Unknown).
- **Remediation:** If `grams == 0.0`, the item should either contribute 0 without contaminating NaN totals, or lines with `grams <= 0` should be handled consistently.

#### [FINDING 2 - MINOR] Asymmetric behavior on negative `total_g`
- **Location:** `src/lhf/compute.py:58-61`
- **Description:**
  ```python
  elif total_g > 0:
      per_100g[k] = val / total_g * 100
  else:
      per_100g[k] = 0.0
  ```
  If `items` contains negative grams (e.g. `[{"code": "A019", "grams": -50.0}]`), `total_g` is `-50.0`.
  `totals["fat_g"]` is `-0.765`.
  However, `total_g > 0` evaluates to `False`. The code falls into `else: per_100g[k] = 0.0`.
- **Impact:** `per_100g` silently returns `0.0` for all nutrients despite non-zero `totals`. While recipe pipelines reject negative grams upstream, `sum_nutrients` as a public library function exhibits contradictory state outputs (`totals != 0`, `per_100g == 0`).

#### [FINDING 3 - CODE HEALTH] Unit tests in `tests/test_t2.py` are incomplete
- **Location:** `tests/test_t2.py:8-12`
- **Description:**
  ```python
  def test_nutrients_tuple(self):
      self.assertIsInstance(compute.NUTRIENTS, tuple)
      for col in ("energy_kj", "energy_kcal", "fat_g", "sfa_g", "carb_g", "protein_g", "sodium_mg"):
          self.assertIn(col, compute.NUTRIENTS)
  ```
  The unit test asserts only 7 columns. It omits: `mufa_g`, `pufa_g`, `tfa_g`, `freesugar_g`, `fibre_g`, and `water_g`.
  Furthermore, `test_t2.py` does not test NaN grams, non-numeric inputs, missing keys, or generator inputs.

---

## 5. Acceptance Test Verification (`acceptance/test_t2_indb.py`)

We executed the official acceptance suite:
```
recipes compared: 995; skipped (codes in no table): 19
agreement energy_kj: 995/995 = 100.0% (needs >= 100%)
agreement fat_g: 995/995 = 100.0% (needs >= 100%)
agreement sfa_g: 995/995 = 100.0% (needs >= 100%)
agreement sodium_mg: 995/995 = 100.0% (needs >= 100%)
agreement protein_g: 995/995 = 100.0% (needs >= 100%)
agreement fibre_g: 995/995 = 100.0% (needs >= 100%)
agreement freesugar_g: 995/995 = 100.0% (needs >= 100%)
agreement carb_g: 970/995 = 97.5% (needs >= 95%)
PASS T2 INDB reproduction
```
- **Analysis of 19 skipped recipes:** These 19 INDB recipes contain ingredient food codes that do not exist in INDB's own composition tables (`UK_fct.xlsx` / `US_fct.xlsx` / `ifct2017`). They are properly identified and skipped by `sum_nutrients`.
- **Analysis of carb_g 97.5% agreement:** The 25 recipes with small discrepancies (e.g. `ASC251`, `ASC264`, `BFP026`) stem from INDB's original source spreadsheet mixing available carbohydrate vs total difference carbohydrate calculations. The acceptance test explicitly specifies a 95% threshold for carb_g to account for this INDB dataset defect.

---

## 6. Recommendations for Remediation

1. **Clarify SPEC.md §3:** Update the specification text from `"the 12 nutrient column names above"` to `"the 13 nutrient column names above"` to eliminate confusion for future maintainers.
2. **Defensive Non-Positive Mass Check:** In `src/lhf/compute.py:28`, consider treating `grams <= 0` or non-finite values (`math.isinf`) either as skipped items or explicitly disallow zero-mass NaN contamination.
3. **Expand `tests/test_t2.py`:** Add comprehensive unit tests asserting all 13 columns in `compute.NUTRIENTS`, verifying `unknown_tfa_items` / `unknown_water_items` ordering, and probing zero/negative/invalid grams.
