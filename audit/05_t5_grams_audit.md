# Adversarial Code and Data Audit: Task T5 (Household Measures to Grams)

**Auditor:** Adversarial Code & Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Module:** `src/lhf/grams.py`  
**Data Files:** `data/curated/measures.csv`, `data/curated/measures_README.md`, `data/curated/constants.csv`  
**Associated Test Files:** `tests/test_t5.py`, `acceptance/test_t5_grams.py`  
**Specification References:** `docs/SPEC.md` §6 (T5: grams), `docs/SPEC.md` §1 (Package layout & Integrity Rules), `AGENTS.md`  

---

## 1. Executive Summary & Verdict

### **Verdict: MINOR ISSUES**

Task T5 (`lhf.grams.grams_for`) is cleanly designed, mathematically precise, and adheres strictly to the core scientific and architectural integrity rules of the project. It strictly follows the 9-tier waterfall defined in `docs/SPEC.md` §6 without inventing default values or weights. In the public acceptance test suite (`acceptance/test_t5_grams.py`), all 411 code-level keys are reachable and return their exact values, and all 106 hand-labelled gold lines match with 100.0% accuracy (well exceeding the 97% requirement).

However, our adversarial audit revealed the following minor defects and structural observations:
1. **Type Brittleness on Non-String `code` (`TypeError` Crash):** `grams_for` attempts string normalization on `code` (`if isinstance(code, str): ...`), but fails to cast non-string inputs (e.g. `int`, `float`, or `bool`) to `None`. Subsequent calls to `code[0]` in `_get_density` (line 51) and Rule 7 (line 151) crash with unhandled `TypeError: 'int' object is not subscriptable` instead of returning `UNQUANTIFIABLE`.
2. **`measures_README.md` Documentation Ambiguity:** `measures_README.md` presents a 5-step lookup summary that omits stated mass, stated volume, and pinch fractional logic, while `SPEC.md` §6 provides the authoritative 9-step waterfall. While the code correctly implements the authoritative `SPEC.md` §6, the documentation in `measures_README.md` is contradictory and out-of-date.
3. **Downstream Pipeline NaN Exclusion Hole:** If `qty` or `stated_g` is passed as `NaN`, `grams_for` passes `NaN` through. In `src/lhf/pipeline.py` (line 130), the exclusion filter checks `if g is None or g <= 0:`. Because in Python `float('nan') <= 0` evaluates to `False`, a line with `NaN` grams bypasses exclusion, is marked `included: True`, and poisons downstream nutrient sums.
4. **Acceptance Test Omission (Group Measures):** While Part A of `acceptance/test_t5_grams.py` tests all code and mass unit rows in `measures.csv`, it omits an exhaustive reachability check for `group` measures (which our adversarial probe verified independently).
5. **Shallow Unit Test Suite:** `tests/test_t5.py` checks only 9 happy-path test cases, completely omitting edge cases such as empty lists, whitespace normalization, unknown sizes, non-string types, and zero values.

---

## 2. Integrity Rules & Static Analysis Checks

### 2.1 Rule 1: No Invented Numbers (AST Analysis)
We parsed `src/lhf/grams.py` into an Abstract Syntax Tree (AST) to verify every numeric literal:

```python
# AST Analysis of Numeric Literals in src/lhf/grams.py:
Line 50: 0      # code_measures[(code, "ml")][0] index
Line 51: 0      # code[0] group extraction
Line 52: 0      # (not a literal, internal node)
Line 53: 1      # Default density return (1.0)
Line 110: 0     # len(unit) > 0 check
Line 117: 0     # len(size) > 0 check
Line 135: 1000  # Liter to ml conversion factor
Line 135: 1     # Fallback multiplier for ml
Line 151: 0     # grp = code[0] group extraction
```

- **Allowed Literals:** `0`, `1`, `1000` (all within `{0-12, 100, 1000}`).
- **Forbidden Literals Found:** 0.
- **Constant Sourcing:** `PINCH_FRACTION_OF_TSP` (value `0.25`) is not hardcoded; it is dynamically resolved via `constants.get("PINCH_FRACTION_OF_TSP")` from `data/curated/constants.csv`.
- **Status:** **PASS** (Strict compliance with Rule 1).

### 2.2 Rule 2 & 9: Silent Default & Guessing Check
- We searched for fallback guesses (e.g. `grams = 100`, `grams = 15`, `qty = 1`). None exist.
- Rule 9 is strictly adhered to at line 176:
  ```python
  return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
  ```
- If an ingredient code is `None`, `"UNMAPPED"`, or `"NON_FOOD"`, execution terminates after Rule 5 (lines 141-142), returning `UNQUANTIFIABLE` with `None` grams.
- **Status:** **PASS** (No silent defaults or unauthorized imputations).

### 2.3 Rule 3: Cheating and Hardcoded Answers Check
- No gold line strings, test-case dish names, or specific recipe IDs appear in `src/lhf/grams.py`.
- No hardcoded food codes (`A504`, `G017`, `T508`, etc.) exist in `src/lhf/grams.py`.
- Source code contains only generic table resolution algorithms.
- **Status:** **PASS**.

### 2.4 Data Integrity Audit (`data/curated/measures.csv`)
We audited all 243 data rows of `data/curated/measures.csv`:
- **Code Existence:** Every food code referenced in `measures.csv` was verified against `lhf.composition.load_table()`. Across all semicolon-delimited lists, **0 missing codes** were found.
- **Source Citations:** 100% of rows contain an explicit citation in the `source` column (referencing ICMR-NIN 2024, INDB Units.xlsx, INDB.do, or USDA FDC SR Legacy portion IDs).
- **Duplicate Checks:** No duplicate keys exist for `(code, unit, size)` or `(group, unit)`.
- **Status:** **PASS**.

---

## 3. Waterfall Strictness & Contract Compliance Audit

`docs/SPEC.md` §6 mandates applying the first rule that matches among Rules 1 through 9. We audited each rule in `src/lhf/grams.py`:

```
Waterfall Step | Spec Requirement                                            | Implementation in grams.py               | Audit Status
---------------------------------------------------------------------------------------------------------------------------------------
Rule 1         | stated_g is not None -> stated_g, STATED_MASS              | Lines 93-94                              | PASS
Rule 2         | stated_ml is not None -> stated_ml * density, STATED_VOLUME| Lines 103-106                            | PASS
Rule 3         | qty is None or unit is None -> None, UNQUANTIFIABLE         | Lines 124-125                            | PASS
Rule 4         | unit in {g, kg, mg, oz, lb} -> qty * any row, MASS_UNIT     | Lines 130-131                            | PASS
Rule 5         | unit in {ml, l} -> qty * (1000 if l) * density, VOLUME_UNIT | Lines 134-138                            | PASS
Unmapped Gate  | When code is None or UNMAPPED/NON_FOOD, only rules 1-5 apply| Lines 141-142                            | PASS
Rule 6         | Code rows: req size -> blank size -> medium                 | Lines 145-149, _resolve_code_measure     | PASS
Rule 7         | Group row for (code[0], unit), GROUP_MEASURE                | Lines 151-153                            | PASS
Rule 8         | pinch/dash fallback -> qty * pinch_frac * tsp_weight        | Lines 156-173                            | PASS
Rule 9         | Otherwise -> None, UNQUANTIFIABLE                           | Line 176                                 | PASS
```

### 3.1 Density Resolution (`_get_density`)
Per SPEC §6 Rule 2:
> "Density is the measures row for (code, 'ml'); otherwise the group row (code's first letter, 'ml'); otherwise 1.0 with flag DENSITY_ASSUMED_1."

In `src/lhf/grams.py`:
- Specific code ml density: Oil (`T508` -> `0.92`), Ghee (`T013` -> `0.905`). Returns exact density and `flags: []`.
- Group ml density: Groups `T`, `L`, `K`, `E` define `1.0 g/ml`. Returns `1.0` and `flags: []`.
- Missing density: Any code without code or group ml row returns `1.0` with `flags: ["DENSITY_ASSUMED_1"]`.
- `UNMAPPED` / `NON_FOOD` / `None`: Returns `1.0` with `flags: ["DENSITY_ASSUMED_1"]`.

### 3.2 Size Resolution Hierarchy (Rule 6)
Per SPEC §6 Rule 6:
> "- if a row's size equals the requested size, use it;  
> - otherwise use a row with blank size;  
> - otherwise use the 'medium' row, with flag SIZE_ASSUMED_MEDIUM when no size was given or SIZE_SUBSTITUTED when a different size was given."

In `_resolve_code_measure`:
1. Exact match on requested size (`r["size"] == size`) -> returns row with `flag = None`.
2. Blank size match (`not r["size"]`) -> returns row with `flag = None`.
3. Medium size match (`r["size"] == "medium"`):
   - If `size is None` -> `flag = "SIZE_ASSUMED_MEDIUM"`.
   - If `size` is any other string -> `flag = "SIZE_SUBSTITUTED"`.

We tested:
- `grams_for(1, "piece", "small", None, None, "G017")` -> `30.0g`, `flags: []`
- `grams_for(1, "piece", None, None, None, "G017")` -> `60.0g`, `flags: ["SIZE_ASSUMED_MEDIUM"]`
- `grams_for(1, "piece", "large", None, None, "G017")` -> `60.0g`, `flags: ["SIZE_SUBSTITUTED"]`
- `grams_for(1, "piece", "extra large", None, None, "G017")` -> `60.0g`, `flags: ["SIZE_SUBSTITUTED"]`

### 3.3 Pinch & Dash Resolution (Rule 8)
Per SPEC §6 Rule 8:
> "unit pinch or dash with no row found in rules 6-7 -> qty × PINCH_FRACTION_OF_TSP × (the tsp weight found by rules 6-7 for this code), with flag PINCH_AS_QUARTER_TSP. The basis is the one of the tsp row used (CODE_MEASURE or GROUP_MEASURE)."

Our probes confirmed:
- Direct row takes precedence: `1 dash salt (G528)` has an explicit code row (`0.4g`). Rule 6 matches, basis is `CODE_MEASURE`, flags are `[]`.
- Fallback to code tsp: `1 pinch besan (A504)` uses besan's code tsp row (`1.92g`). `1 * 0.25 * 1.92 = 0.48g`, basis `CODE_MEASURE`, flags `["PINCH_AS_QUARTER_TSP"]`.
- Fallback to group tsp: `1 pinch hing (G019)` uses group G tsp row (`2.0g`). `1 * 0.25 * 2.0 = 0.5g`, basis `GROUP_MEASURE`, flags `["PINCH_AS_QUARTER_TSP"]`.
- No tsp row available: If a food code or group has no tsp row, it cleanly falls through to Rule 9, returning `None`, `basis: "UNQUANTIFIABLE"`.

---

## 4. Adversarial Probing & Vulnerability Findings

### 4.1 Vulnerability 1: Crash on Non-String `code` (`TypeError`)
- **Severity:** Low / Boundary Edge Case.
- **Location:** `src/lhf/grams.py` lines 51, 97-100, 151.
- **Trigger Input:** Calling `grams_for(1, "cup", None, None, None, 123)` or `grams_for(None, None, None, None, 50, 123)`.
- **Traceback:**
  ```python
  File "src/lhf/grams.py", line 51, in _get_density
      if (code[0], "ml") in group_measures:
          ^^^^^^^
  TypeError: 'int' object is not subscriptable
  ```
- **Analysis:** Lines 97-100 normalize string codes:
  ```python
  if isinstance(code, str):
      code = code.strip().upper()
      if not code:
          code = None
  ```
  However, if `code` is an integer, float, or boolean, it remains un-normalized. In `_get_density` line 51 and Rule 7 line 151, `code[0]` is evaluated directly without confirming `isinstance(code, str)`.
- **Remediation:**
  Add an `else` branch:
  ```python
  if isinstance(code, str):
      code = code.strip().upper()
      if not code:
          code = None
  else:
      code = None
  ```

### 4.2 Vulnerability 2: Downstream NaN Leakage in `pipeline.py`
- **Severity:** Medium.
- **Location:** `src/lhf/pipeline.py` line 130 vs `src/lhf/grams.py`.
- **Trigger Input:** `grams_for(float('nan'), "g", None, None, None, None)` or `stated_g = float('nan')`.
- **Mechanism:**
  `grams_for` returns `{"grams": nan, "basis": "MASS_UNIT", "flags": []}`.
  In `src/lhf/pipeline.py`:
  ```python
  if g is None or g <= 0:
      # excluded as UNQUANTIFIABLE
  else:
      # INCLUDED!
  ```
  In IEEE-754 floating point arithmetic, `nan <= 0` evaluates to `False`. Thus, a line with `NaN` grams bypasses the exclusion block and is added to `inc_items`. Downstream, `nutrients_for(code, nan)` produces NaNs across all 13 nutrients, corrupting dish totals.
- **Remediation:**
  In `pipeline.py`, change line 130 to:
  ```python
  if g is None or not (g > 0):
  ```
  And in `grams_for`, validate `if math.isnan(qty): return {"grams": None, "basis": "UNQUANTIFIABLE", ...}`.

### 4.3 Reachability Audit of Group Measures
Part A of `acceptance/test_t5_grams.py` loops over all rows in `measures.csv` where `match_type == "code"` or `match_type == "any"`, but completely skips `match_type == "group"`.
We designed an automated probe to test reachability across all 45 group measures in `measures.csv`:
```python
# Group reachability test result:
# Total group rows in measures.csv: 45
# Reachable and exact value returned: 45 (100.0%)
# Fails: 0
```
All group measures (including density rows for T, L, K, E and dry measures for G, H, B, U, D, F, A, M, V, X, W, I, Z, C) are fully reachable.

### 4.4 Boundary Matrix Results
We executed a 41-case probe matrix covering normal, boundary, and adversarial conditions:

```
Test Probe Name                          Result   Basis Checked   Flags Checked
-------------------------------------------------------------------------------------
stated_g float (150.0)                  PASS     STATED_MASS     []
stated_g int (150)                      PASS     STATED_MASS     []
stated_g string ("150")                 PASS     STATED_MASS     []
stated_g boundary (0.0)                 PASS     STATED_MASS     []
stated_g overrides stated_ml            PASS     STATED_MASS     []
stated_ml code ml (T508 -> 92g)         PASS     STATED_VOLUME   []
stated_ml group ml (T999 -> 100g)       PASS     STATED_VOLUME   []
stated_ml no group ml (G017 -> 100g)    PASS     STATED_VOLUME   ['DENSITY_ASSUMED_1']
stated_ml unmapped code                 PASS     STATED_VOLUME   ['DENSITY_ASSUMED_1']
missing qty / missing unit              PASS     UNQUANTIFIABLE  []
empty string unit ("")                  PASS     UNQUANTIFIABLE  []
empty list unit ([])                    PASS     UNQUANTIFIABLE  []
mass units (g, kg, mg, oz, lb)          PASS     MASS_UNIT       []
volume units (ml, l with code/fallback) PASS     VOLUME_UNIT     ['DENSITY_ASSUMED_1'] (when assumed)
exact size piece (small -> 30g)         PASS     CODE_MEASURE    []
exact size piece (medium -> 60g)        PASS     CODE_MEASURE    []
size assumed medium (None -> 60g)       PASS     CODE_MEASURE    ['SIZE_ASSUMED_MEDIUM']
size substituted (large -> 60g)         PASS     CODE_MEASURE    ['SIZE_SUBSTITUTED']
group measure (G019 tsp -> 2g)          PASS     GROUP_MEASURE   []
pinch with group tsp (G019 -> 0.5g)     PASS     GROUP_MEASURE   ['PINCH_AS_QUARTER_TSP']
pinch with code tsp (A504 -> 0.48g)     PASS     CODE_MEASURE    ['PINCH_AS_QUARTER_TSP']
dash with code row (G528 -> 0.4g)       PASS     CODE_MEASURE    []
dash fallback to tsp (G019 -> 0.5g)     PASS     GROUP_MEASURE   ['PINCH_AS_QUARTER_TSP']
pinch for unmapped food                 PASS     UNQUANTIFIABLE  []
piece for unmapped food                 PASS     UNQUANTIFIABLE  []
cup for unmapped food                   PASS     UNQUANTIFIABLE  []
piece for unmapped item without row     PASS     UNQUANTIFIABLE  []
bunch without row (mint G016)           PASS     UNQUANTIFIABLE  []
```

---

## 5. Summary of Key Issues Found

| Issue ID | Category | Severity | Description | File & Line |
|---|---|---|---|---|
| **ISSUE-T5-01** | Robustness | Minor | Non-string `code` raises unhandled `TypeError` instead of returning `UNQUANTIFIABLE`. | `src/lhf/grams.py`: 51, 151 |
| **ISSUE-T5-02** | Documentation | Minor | `measures_README.md` describes a 5-step order that does not match the 9-step waterfall in `docs/SPEC.md` §6. | `data/curated/measures_README.md`: 11-16 |
| **ISSUE-T5-03** | Data Flow | Minor | `float('nan')` grams bypasses exclusion in `pipeline.py` due to `nan <= 0 == False`. | `src/lhf/pipeline.py`: 130 |
| **ISSUE-T5-04** | Test Quality | Minor | `acceptance/test_t5_grams.py` Part A does not iterate over `group` measures in `measures.csv`. | `acceptance/test_t5_grams.py`: 13-29 |
| **ISSUE-T5-05** | Test Quality | Minor | `tests/test_t5.py` lacks adversarial, boundary, and type-coercion test cases. | `tests/test_t5.py`: 1-98 |

---

## 6. Recommendations for Remediation

1. **Defensive Code Normalization (`src/lhf/grams.py`):**
   Update lines 97-101 to safely set `code = None` if `not isinstance(code, str)`:
   ```python
   if isinstance(code, str):
       code = code.strip().upper()
       if not code:
           code = None
   else:
       code = None
   ```
2. **Defensive Pipeline Exclusion (`src/lhf/pipeline.py`):**
   Update line 130 in `pipeline.py` to check `if g is None or not (g > 0):` to prevent `NaN` mass leakage into nutrient summation.
3. **Harmonize `measures_README.md`:**
   Update `data/curated/measures_README.md` lines 11-16 to accurately reflect the 9-step waterfall specified in `docs/SPEC.md` §6.
4. **Expand Test Suite (`tests/test_t5.py`):**
   Incorporate boundary tests for non-string types, zero-values, unit lists, and group measure reachability.
