# Adversarial Code and Data Audit: Task T6 (Food Classification & Class Totals)

**Auditor:** Adversarial Code & Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Files:**
- `src/lhf/classify.py`
- `data/curated/classes.csv`  
**Associated Test Files:**
- `tests/test_t6.py`
- `acceptance/test_t6_classify.py`  
**Specification References:** `docs/SPEC.md` §7 (T6: food classes), `docs/SPEC.md` §1 (Package layout & Integrity rules), `docs/SPEC.md` §9 (Pipeline), `AGENTS.md`

---

## 1. Executive Summary & Verdict

### **Verdict: MINOR ISSUES**

The implementation of Task T6 in `src/lhf/classify.py` and the curated classification dataset `data/curated/classes.csv` faithfully fulfill the core scientific and mathematical requirements specified in `docs/SPEC.md` §7. The module correctly resolves multi-class food codes (e.g., `G528` and `G540` as both `SALT` and `SPICE`), enforces strict upper capping for free sugars (preventing the UK composition artifact where sugar exceeds 100 g per 100 g), accurately accumulates refined grain carbohydrates and salt mass, and partitions recipe fat into mutually exclusive buckets (`COOKING_OIL`, `HYDROGENATED_FAT`, `DAIRY_FAT`, and `OTHER`).

Dynamic verification against all 71 sample recipes in `data/samples/recipes_phase1.jsonl` (1,339 ingredient lines) demonstrated that:
$$\sum \text{fat\_by\_class\_g.values()} \equiv \text{total fat\_g}$$
with **0 mismatches** across the entire dataset.

Static analysis confirms **0 violations** of the numeric literal rule (only allowed literals `0.0`, `0`, and `100` appear; verified via AST inspection). No banned imports, network access, or cheating constructs (e.g. gold-set answer hardcoding) were detected.

However, deep adversarial probing identified notable robustness and consistency flaws:
1. **Unsafe Dictionary Key Checks Leading to `TypeError` Crashes:** The nutrient extraction logic checks `if "key" in nutrients:` rather than `if nutrients.get("key") is not None:`. If an item's `nutrients` dictionary contains explicit `None` values (which standardly occurs when deserializing pipeline results from JSON where `NaN becomes None` per SPEC §9), calling `float(nutrients[key])` immediately crashes the process with `TypeError: float() argument must be a string or a real number, not 'NoneType'`.
2. **Asymmetric and Incomplete NaN Defense:** In `class_totals()`, `fat_val` contains explicit NaN defense (`if fat_val != fat_val: fat_val = 0.0`), but neither `refined_carb_g` nor `added_sugar_g` has this check. Any incoming `NaN` in carbohydrate or free sugar permanently poisons the recipe sums.
3. **Inconsistent Hierarchy of Truth (`table` vs `nutrients`):** For `ADDED_SUGAR`, the code prioritizes querying `table.index` over the passed `item["nutrients"]`. Conversely, for `REFINED_GRAIN` and `fat_by_class_g`, the code prioritizes `item["nutrients"]` over `table.index`. Any caller providing custom or modified nutrients will find them respected for grains and fat, but silently discarded and overridden for sugars.
4. **Redundant DataFrame Lookups and Performance Drag:** `composition.load_table()` is retrieved on every call to `class_totals()`. Because $\min(\text{nutrients}[\text{"freesugar\_g"}], \text{grams}) \equiv \text{grams} \times \min(fs_{100}, 100) / 100$, pandas DataFrame lookups during sugar calculations are entirely redundant when precomputed nutrients are passed.
5. **Unit Test Suite Coverage Gaps:** `tests/test_t6.py` tests only the happy paths, failing to test `nutrients` containing `None` or `NaN`, missing `nutrients` dictionaries, or multi-class items in `class_totals()`.

---

## 2. Integrity Rules & Static Analysis Checks

### 2.1 Rule 1: No Invented Numbers (AST Analysis)
We parsed `src/lhf/classify.py` into an Abstract Syntax Tree (AST) to verify that no numeric literal exists outside the permitted set $\{0, 1, 2, \dots, 12, 100, 1000\}$:

```python
# AST Scan Results for src/lhf/classify.py:
Line 51:  0.0    # added_sugar_g accumulator initialisation (Allowed)
Line 52:  0.0    # refined_carb_g accumulator initialisation (Allowed)
Line 53:  0.0    # salt_g accumulator initialisation (Allowed)
Line 55:  0.0    # fat_by_class_g COOKING_OIL default (Allowed)
Line 56:  0.0    # fat_by_class_g HYDROGENATED_FAT default (Allowed)
Line 57:  0.0    # fat_by_class_g DAIRY_FAT default (Allowed)
Line 58:  0.0    # fat_by_class_g OTHER default (Allowed)
Line 63:  0.0    # empty-items fallback added_sugar_g (Allowed)
Line 64:  0.0    # empty-items fallback refined_carb_g (Allowed)
Line 65:  0.0    # empty-items fallback salt_g (Allowed)
Line 79:  0      # non-positive grams guard (Allowed)
Line 89:  100    # min(fs_100, 100) sugar capping bound (Allowed)
Line 89:  100    # per-100g denominator in sugar calculation (Allowed)
Line 98:  100    # per-100g denominator in carb fallback (Allowed)
Line 108: 100    # per-100g denominator in fat fallback (Allowed)
Line 110: 0.0    # fallback fat_val for unmapped item (Allowed)
Line 113: 0.0    # NaN reset for fat_val (Allowed)
```

- **Disallowed Numeric Literals Found:** 0
- **Compliance Status:** **PASS** (100% compliant with Rule 1).

### 2.2 Rule 2: No Silent Defaults for Missing Data
- `classes_for(code)`:
  - If `code` is empty, whitespace, or unknown, it returns `[]` (an unclassified food item).
  - It does not assume or guess a default class (e.g., does not assume an unknown oil is `COOKING_OIL`).
- `class_totals(items)`:
  - If `items` is empty (`[]`) or `None`, returns zeroes for all scalar accumulators and the four canonical fat classes.
  - If an item has `grams=None`, it is skipped without defaulting to 100 g or 1 serving.
  - If an item has non-positive or `NaN` grams, it is skipped without silently inventing a quantity.

### 2.3 Rule 3: No Hardcoding, Test Cheating, or Gold Answer Leakage
- `src/lhf/classify.py` contains **zero hardcoded food codes**, dish names, or test outputs.
- No references to `acceptance/gold`, `gold_public.json`, or `gold_holdout.json`.
- Standard libraries only (`csv`, `os`), plus internal project packages (`lhf.composition`, `lhf.paths`). No banned networking or subprocess libraries.

---

## 3. Data Integrity Audit: `data/curated/classes.csv`

The curated table `data/curated/classes.csv` defines food classification mappings with schema `(code, class, note)`:

| Metric | Result | Notes |
|---|---|---|
| Total Rows | 121 | All rows have valid, non-empty `code` and `class` |
| Duplicate Pairs | 0 | No duplicate `(code, class)` tuples exist |
| Unmapped Codes in FCT | 0 | Every code in `classes.csv` exists in the 746-row composition table |
| Class Distribution | 8 distinct classes | See breakdown below |

### Breakdown by Food Class:
- `SPICE`: 44 codes (Dried spices, seeds, condiments used for the 30 g recipe sanity check).
- `DAIRY_FAT`: 21 codes (Ghee, butter, fresh cream, whipping cream, cheeses, paneer, malai).
- `ADDED_SUGAR`: 18 codes (White/brown/icing sugars, jaggery, honey, syrups, condensed milk, jams, ketchup, cola).
- `COOKING_OIL`: 17 codes (Mustard, groundnut, sunflower, sesame, coconut, palm, rice bran, olive, etc.).
- `REFINED_GRAIN`: 16 codes (Maida, sooji/semolina, vermicelli, cornflour, polished rice, poha, sago, white bread).
- `SALT`: 2 codes (`G528` standard salt, `G540` Himalayan black salt).
- `HYDROGENATED_FAT`: 2 codes (`T014` vanaspati, `T504` margarine).
- `WATER`: 1 code (`K505` plain water).

### Multi-Class Codes:
Only two codes possess multiple classification entries in `classes.csv`:
- `G528`: `["SALT", "SPICE"]`
- `G540`: `["SALT", "SPICE"]`

Both black salt and table salt act as seasoning/spices in recipe quantities, while also providing the primary dietary salt/sodium load. Both classes are correctly loaded into a list for each code.

---

## 4. Deep Algorithmic Audit & Code Analysis

### 4.1 `classes_for(code: str) -> list[str]`
Implemented in lines 32–37:
```python
def classes_for(code: str) -> list[str]:
    """Return the list of food classes for a given food code."""
    if not code:
        return []
    classes_map = _load_classes()
    return list(classes_map.get(str(code).strip(), []))
```

#### Observations & Findings:
1. **Cache Immutability Protection:** The function executes `list(classes_map.get(...))`, constructing a shallow copy. Mutating the returned list does not pollute `_CLASSES_BY_CODE`. (Verified dynamically via probe script).
2. **Whitespace Stripping:** Uses `str(code).strip()`, properly handling strings like `" G528 "`.
3. **Falsy Input Handling:** `if not code:` intercepts `None` and `""`. Note that `classes_for(0)` returns `[]` because integer `0` is falsy. While food codes in this project are alphanumeric strings (`A018`, `T508`), explicit check `if code is None or code == ""` is preferred over `if not code:`.

---

### 4.2 `class_totals(items: list) -> dict`

Implemented in lines 40–129:

#### 4.2.1 Added Sugar (`added_sugar_g`)
SPEC §7 contract:
$$\text{added\_sugar\_g} = \sum_{i \in \text{ADDED\_SUGAR}} \text{grams}_i \times \frac{\min(\text{freesugar\_g per 100 g}_i, 100)}{100}$$

Implementation lines 85–92:
```python
if "ADDED_SUGAR" in item_classes:
    if code_str in table.index:
        fs_100 = float(table.loc[code_str, "freesugar_g"])
        added_sugar_g += grams_val * min(fs_100, 100) / 100
    elif "freesugar_g" in nutrients:
        added_sugar_g += min(float(nutrients["freesugar_g"]), grams_val)
```

- **Capping Verification:** In the UK composition dataset (INDB_UK), analytical measurements of sugars occasionally exceed 100 g/100 g (e.g. `I502` white sugar = 105.0 g/100 g, `I503` brown sugar = 101.3 g/100 g, `I504` icing sugar = 103.8 g/100 g). The code strictly caps `min(fs_100, 100)`. For 20 g of white sugar:
  $$20 \times \frac{\min(105.0, 100)}{100} = 20.0\text{ g added sugar}$$
  This strictly prevents sugar from exceeding the mass of the ingredient itself.
- **Mathematical Equivalence of Fallback:** In the `elif "freesugar_g" in nutrients:` branch:
  $$\min(\text{nutrients}[\text{"freesugar\_g"}], \text{grams}) \equiv \text{grams} \times \frac{\min(fs_{100}, 100)}{100}$$
  Both expressions yield identical results.
- **Flaw — Source Hierarchy Inconsistency:** Notice that `code_str in table.index` is checked **first**. If a caller passes mock or adjusted nutrients in `item["nutrients"]`, they are silently ignored in favor of `table.loc[code_str]`.

---

#### 4.2.2 Refined Carbohydrates (`refined_carb_g`)
SPEC §7 contract:
$$\text{refined\_carb\_g} = \sum_{i \in \text{REFINED\_GRAIN}} \text{carb\_g}_i$$

Implementation lines 94–98:
```python
if "REFINED_GRAIN" in item_classes:
    if "carb_g" in nutrients:
        refined_carb_g += float(nutrients["carb_g"])
    elif code_str in table.index:
        refined_carb_g += float(table.loc[code_str, "carb_g"]) * grams_val / 100
```

- **Correctness:** Correctly queries `carb_g` of the item. For 100 g of maida (`A018`, carb = 74.27 g/100 g) and 50 g of polished raw rice (`A015`, carb = 78.24 g/100 g), accurately yields $74.27 + 39.12 = 113.39\text{ g}$.
- **Flaw — Missing Value Crash:** If `nutrients` has `{"carb_g": None}`, `if "carb_g" in nutrients:` evaluates to `True`, and `float(None)` crashes with `TypeError`.
- **Flaw — NaN Propagation:** If `nutrients["carb_g"]` is `NaN`, `refined_carb_g` becomes `NaN`, contaminating the entire recipe summary.

---

#### 4.2.3 Salt (`salt_g`)
SPEC §7 contract:
$$\text{salt\_g} = \sum_{i \in \text{SALT}} \text{grams}_i$$

Implementation lines 100–102:
```python
if "SALT" in item_classes:
    salt_g += grams_val
```

- **Correctness:** Accurately sums the mass of ingredients classified as `SALT` (`G528` and `G540`).
- **Unquantified Lines Handling:** If an ingredient has `grams=None` (e.g., `"salt as required"`, `"salt to taste"`), line 76 intercepts it:
  ```python
  if grams is None:
      continue
  ```
  The unquantified line is skipped, avoiding any crash or silent defaulting. The unquantified salt warning (`SALT_UNQUANTIFIED`) is delegated to the pipeline as required by SPEC §9.

---

#### 4.2.4 Fat Partitioning (`fat_by_class_g`)
SPEC §7 contract:
$$\text{fat\_by\_class\_g} = \{\text{class}: \sum \text{fat\_g}\} \quad \text{for COOKING\_OIL, HYDROGENATED\_FAT, DAIRY\_FAT, and OTHER}$$

Implementation lines 104–123:
```python
if "fat_g" in nutrients:
    fat_val = float(nutrients["fat_g"])
elif code_str in table.index:
    fat_val = float(table.loc[code_str, "fat_g"]) * grams_val / 100
else:
    fat_val = 0.0

if fat_val != fat_val:
    fat_val = 0.0

if "COOKING_OIL" in item_classes:
    fat_by_class_g["COOKING_OIL"] += fat_val
elif "HYDROGENATED_FAT" in item_classes:
    fat_by_class_g["HYDROGENATED_FAT"] += fat_val
elif "DAIRY_FAT" in item_classes:
    fat_by_class_g["DAIRY_FAT"] += fat_val
else:
    fat_by_class_g["OTHER"] += fat_val
```

- **Partition Exhaustiveness & Conservation of Mass:**
  The `if / elif / elif / else` structure guarantees that every item with fat is placed into exactly one bucket. Trace fat in grains, legumes, meats, nuts, and spices (not belonging to the three targeted fat classes) flows directly into `"OTHER"`.
- **Dynamic Dataset Validation:**
  We ran an automated audit across all 71 recipe samples in `data/samples/recipes_phase1.jsonl`:
  $$\sum_{c} \text{fat\_by\_class\_g}[c] == \text{totals}[\text{"fat\_g"}]$$
  Result: **100% agreement (71/71 recipes, 0 discrepancies)**.
- **Flaw — Missing Value Crash:** As with carbohydrates, if `nutrients` contains `"fat_g": None`, `float(nutrients["fat_g"])` raises a `TypeError`.

---

## 5. Adversarial Probe Results

We developed and executed dynamic test probes against `src/lhf/classify.py` to identify behavioral edge cases:

| Probe Scenario | Input | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|
| **Empty Items List** | `items = []` | Returns 0.0s for all keys | Returns zeroes dictionary | **PASS** |
| **None Items Input** | `items = None` | Returns 0.0s for all keys | Returns zeroes dictionary | **PASS** |
| **Salt with `grams=None`** | `[{"code": "G528", "grams": None}]` | Skip item, return 0.0 | Skipped, returns 0.0 | **PASS** |
| **Salt with Non-Positive grams** | `[{"code": "G528", "grams": 0}, {"code": "G528", "grams": -5}]` | Skip item, return 0.0 | Skipped, returns 0.0 | **PASS** |
| **Salt with `grams=NaN`** | `[{"code": "G528", "grams": float("nan")}]` | Skip item, return 0.0 | Skipped (`grams_val != grams_val`) | **PASS** |
| **Refined Grain with `nutrients=None`** | `[{"code": "A018", "grams": 50, "nutrients": None}]` | Fall back to composition table | Uses table fallback: 37.135 g | **PASS** |
| **Refined Grain with `carb_g=None`** | `[{"code": "A018", "grams": 50, "nutrients": {"carb_g": None}}]` | Fall back to table or 0.0 | **CRASH: `TypeError`** (`float(None)`) | **FAIL** |
| **Refined Grain with `carb_g=NaN`** | `[{"code": "A018", "grams": 50, "nutrients": {"carb_g": float("nan")}}]` | Reset NaN or handle | **Returns `refined_carb_g: nan`** | **FAIL** |
| **Added Sugar Capping** | `[{"code": "I502", "grams": 25.0}]` (fs=105 g/100g) | Capped at 25.0 g | Exactly 25.0 g | **PASS** |
| **Added Sugar with `freesugar_g=None`** | `[{"code": "I502", "grams": 20, "nutrients": {"freesugar_g": None}}]` | Uses table if code in table | Uses table (20.0 g) | **PASS** |
| **Added Sugar with Custom Code & None** | `[{"code": "MOCK_SUGAR", "grams": 20, "nutrients": {"freesugar_g": None}}]` | Graceful fallback | **CRASH: `TypeError`** | **FAIL** |
| **Fat Item with `fat_g=None`** | `[{"code": "T508", "grams": 15, "nutrients": {"fat_g": None}}]` | Fall back to table or 0.0 | **CRASH: `TypeError`** (`float(None)`) | **FAIL** |
| **Fat Item with `fat_g=NaN`** | `[{"code": "T508", "grams": 15, "nutrients": {"fat_g": float("nan")}}]` | Coerced to 0.0 | Reset to 0.0 (`fat_val != fat_val`) | **PASS** |
| **Item Missing `code` Key** | `[{"grams": 10, "nutrients": {"fat_g": 5}}]` | Classify as OTHER | Added 5.0 g to `OTHER` fat | **PASS** |
| **Multi-Class Item in Totals** | `[{"code": "G528", "grams": 5.0, ...}]` | Both SALT and SPICE | Added to `salt_g`, fat to `OTHER` | **PASS** |
| **Caller List Mutation** | Caller mutates returned `classes_for` | Internal cache unaffected | Independent list returned | **PASS** |

---

## 6. Detailed Issue Log & Line Citations

### Issue T6-01: `TypeError` Crash on `None` Nutrient Values (Brittle Key Membership)
- **File:** `src/lhf/classify.py`
- **Lines:** 90–91, 95–96, 105–106
- **Code:**
  ```python
  # Line 90-91:
  elif "freesugar_g" in nutrients:
      added_sugar_g += min(float(nutrients["freesugar_g"]), grams_val)
  
  # Line 95-96:
  if "carb_g" in nutrients:
      refined_carb_g += float(nutrients["carb_g"])
  
  # Line 105-106:
  if "fat_g" in nutrients:
      fat_val = float(nutrients["fat_g"])
  ```
- **Vulnerability:** In Python, `"key" in nutrients` is `True` even when `nutrients["key"] is None`. If `class_totals()` is called on deserialized recipe lines (where missing/unknown nutrients were serialized to `None` per SPEC §9), `float(None)` raises `TypeError: float() argument must be a string or a real number, not 'NoneType'`.
- **Severity:** Medium.
- **Fix:** Replace `"key" in nutrients` with `nutrients.get("key") is not None:` across all three blocks.

---

### Issue T6-02: Asymmetric NaN Handling and Total Contamination
- **File:** `src/lhf/classify.py`
- **Lines:** 96, 112–113
- **Code:**
  ```python
  # Lines 112-113: Fat is protected
  if fat_val != fat_val:
      fat_val = 0.0

  # Line 96: Refined carb is completely unprotected
  if "carb_g" in nutrients:
      refined_carb_g += float(nutrients["carb_g"])
  ```
- **Vulnerability:** The developer realized that `fat_val` could be `NaN` and added `if fat_val != fat_val: fat_val = 0.0`, but neglected to apply the same safeguard to `refined_carb_g` or `added_sugar_g`. If an item provides `carb_g = NaN`, `refined_carb_g` accumulates `NaN`, irreversibly ruining the recipe totals.
- **Severity:** Low.
- **Fix:** Apply `if carb_val != carb_val: carb_val = 0.0` or coerce `NaN` to `0.0`.

---

### Issue T6-03: Inconsistent Source Hierarchy (`table` vs `nutrients`)
- **File:** `src/lhf/classify.py`
- **Lines:** 87–91 vs 95–98
- **Code:**
  ```python
  # Added sugar: checks table first, ignores nutrients
  if code_str in table.index:
      fs_100 = float(table.loc[code_str, "freesugar_g"])
      ...
  elif "freesugar_g" in nutrients:
      ...

  # Refined carb: checks nutrients first, ignores table
  if "carb_g" in nutrients:
      refined_carb_g += float(nutrients["carb_g"])
  elif code_str in table.index:
      ...
  ```
- **Vulnerability:** An architectural inconsistency exists where sugar calculations discard user-supplied/precomputed `nutrients` whenever `code_str in table.index`, while grain and fat calculations prioritize `nutrients`.
- **Severity:** Low.
- **Fix:** Standardize resolution order across all nutrients (check `nutrients.get(col) is not None` first; fall back to `table.loc[code_str, col]` if omitted).

---

### Issue T6-04: Suboptimal Performance via Unnecessary DataFrame Lookups
- **File:** `src/lhf/classify.py`
- **Lines:** 69, 88
- **Code:**
  ```python
  table = composition.load_table()
  ...
  fs_100 = float(table.loc[code_str, "freesugar_g"])
  ```
- **Vulnerability:** `class_totals()` receives items that have already passed through `composition.nutrients_for()`. Querying the pandas DataFrame `.loc` index inside an ingredient loop is significantly slower than reading the precomputed nutrient dictionary. Since $\min(\text{nutrients}[\text{"freesugar\_g"}], \text{grams}) \equiv \text{grams} \times \min(fs_{100}, 100) / 100$, pandas indexing is completely redundant for standard pipeline items.
- **Severity:** Low (Code optimization).

---

### Issue T6-05: Test Suite Blind Spots (`tests/test_t6.py`)
- **File:** `tests/test_t6.py`
- **Lines:** 1–96
- **Vulnerability:** `tests/test_t6.py` has 9 unit tests that only exercise standard happy-path inputs. It does not test items with `None` or `NaN` nutrient fields, missing `nutrients` keys, items with codes outside the composition table, or multi-class items in `class_totals()`.
- **Severity:** Low.

---

## 7. Remediation Recommendations

1. **Defensive Nutrient Extraction:**
   Refactor lines 86–123 in `src/lhf/classify.py` to use `.get()` with explicit `None` and `NaN` guards:
   ```python
   # 1. Added sugar
   if "ADDED_SUGAR" in item_classes:
       if nutrients.get("freesugar_g") is not None:
           fs_val = float(nutrients["freesugar_g"])
           if fs_val == fs_val:  # not NaN
               added_sugar_g += min(fs_val, grams_val)
       elif code_str in table.index:
           fs_100 = float(table.loc[code_str, "freesugar_g"])
           if fs_100 == fs_100:
               added_sugar_g += grams_val * min(fs_100, 100) / 100

   # 2. Refined carbohydrate
   if "REFINED_GRAIN" in item_classes:
       if nutrients.get("carb_g") is not None:
           carb_val = float(nutrients["carb_g"])
           if carb_val == carb_val:
               refined_carb_g += carb_val
       elif code_str in table.index:
           carb_100 = float(table.loc[code_str, "carb_g"])
           if carb_100 == carb_100:
               refined_carb_g += carb_100 * grams_val / 100

   # 4. Fat by class
   if nutrients.get("fat_g") is not None:
       fat_val = float(nutrients["fat_g"])
   elif code_str in table.index:
       fat_val = float(table.loc[code_str, "fat_g"]) * grams_val / 100
   else:
       fat_val = 0.0

   if fat_val != fat_val:
       fat_val = 0.0
   ```
2. **Defensive Guard in `classes_for`:**
   Replace `if not code:` with `if code is None or code == "":` to prevent unintended truthiness issues with edge-case types.
3. **Comprehensive Unit Tests:**
   Expand `tests/test_t6.py` to include adversarial test cases covering `nutrients` containing `None`, `NaN`, multi-class codes (`G528`, `G540`), and conservation of mass across fat categories.

---

## 8. Final Sign-off

- **Module Integrity:** Verified. No cheated logic or invented numeric constants.
- **Scientific Soundness:** Verified. Added sugar capping matches WHO/UK guidelines, and fat partitioning satisfies strict conservation of mass.
- **Overall Grade:** **PASS (with Minor Issues)**.
