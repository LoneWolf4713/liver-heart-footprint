# Round 2 Adversarial Code & Data Audit: Task T1 (Food Composition & Unified Table)

**Auditor:** Round 2 Adversarial Red Team Auditor (Auditor 1)  
**Date:** 2026-11-11  
**Project:** Liver and Heart Footprint of Indian Recipes  
**Target Files:**
- `src/lhf/composition.py`
- `src/lhf/constants.py`
- `src/lhf/paths.py`
- `acceptance/test_t1_composition.py`
- `tests/test_t1.py`
- `data/curated/constants.csv`
- `data/raw/ifct2017_transcription/`

---

## 1. Executive Summary & Verdict

### **Verdict: MINOR ISSUES**

Following an independent, adversarial red-team re-audit of Task T1 from a clean-slate perspective ("guilty until proven innocent"), the implementation of the Food Composition Table and Constants Reader exhibits solid scientific accuracy and strict compliance with the core data specifications. The unified composition table correctly aggregates 746 foods across four distinct source datasets (IFCT 2017, INDB UK, INDB US, and curated Indian Products), faithfully converting units, respecting missing-value conventions (coercing unmeasured non-trans-fat nutrients to 0.0 while preserving `NaN` for `tfa_g` and `water_g`), and correctly repairing the IFCT energy defect for pure edible fats and oils.

Previous critical vulnerabilities flagged in Round 1 (such as in-place cache pollution via `load_table()` and undocumented `None` propagation) have been largely addressed: `load_table()` now returns an insulated `.copy()`, and `tests/test_t1.py` has been substantially expanded from 36 lines (4 assertions) to 174 lines (11 test methods).

However, deep adversarial probing exposed several remaining edge-case defects, silent type-coercion bugs, and an AST compliance workaround:
1. **Silent Boolean Coercion in `nutrients_for`:** Passing boolean values `True` or `False` for `grams` does not raise an error. Because Python's `bool` is a subclass of `int`, `float(True)` evaluates to `1.0` and `float(False)` evaluates to `0.0`, silently scaling food nutrients to 1 gram or 0 grams.
2. **Silent Acceptance of Negative, NaN, and Infinite Grams in `nutrients_for`:** Calling `nutrients_for(code, -50)` returns negative nutrients (e.g. -50 g fat, -450 kcal energy). Calling `nutrients_for(code, float("nan"))` silently returns a dictionary where all 13 nutrient values are `NaN` without raising a `ValueError`. Calling `nutrients_for(code, float("inf"))` returns `inf` and `nan`.
3. **AST Rule 1 Literal Synthesis Workaround:** `OIL_CODES = {f"T{i:03d}" for i in range(1, 12 + 3)}` synthetically constructs the integer 15 via constant folding (`12 + 3`) to evade the AST literal check while hardcoding the range 1..14.
4. **Thread-Safety Deficit in Singleton Initialization:** Neither `composition._get_table()` nor `constants._load_constants()` uses synchronization primitives (e.g. `threading.Lock`). In concurrent multi-threaded execution, multiple worker threads can trigger duplicate disk I/O and DataFrame concatenations.

---

## 2. Rigorous Investigation of Mandated Audit Questions

### 2.1 Question 1: Does `load_table()` return a defensive copy or can callers mutate the cached table?

**Finding: DEFENSIVE COPY RETURNED BY `load_table()`; INTERNAL CACHE IS PROTECTED FROM CALLERS OF PUBLIC API.**

#### Adversarial Probe:
We executed an adversarial probe testing row deletion, column dropping, cell modification, index corruption, and subsequent lookup isolation:
```python
t1 = composition.load_table()
orig_fat = t1.loc['T001', 'fat_g']
t1.loc['T001', 'fat_g'] = 999999.0
t1.drop(columns=['fat_g'], inplace=True)
t1.rename(index={'T001': 'HACKED'}, inplace=True)

t2 = composition.load_table()
assert 'fat_g' in t2.columns
assert t2.loc['T001', 'fat_g'] == orig_fat
assert 'HACKED' not in t2.index

g = composition.get('T001')
assert g['fat_g'] == orig_fat

n = composition.nutrients_for('T001', 100)
assert n['fat_g'] == orig_fat
```
**Outcome:** PASSED. All mutations to `t1` remained strictly local to `t1`.

#### Architecture Analysis:
1. `src/lhf/composition.py` separates internal singleton access (`_get_table()`) from public table retrieval (`load_table()`):
   ```python
   def _get_table() -> pd.DataFrame:
       global _TABLE
       if _TABLE is None:
           _TABLE = _build_table()
       return _TABLE

   def load_table() -> pd.DataFrame:
       return _get_table().copy()
   ```
2. Because `pd.DataFrame.copy()` defaults to `deep=True`, all underlying numpy ndarrays are copied. All columns are immutable primitive types (`str` and `float64`), preventing any indirect reference mutation.
3. In `composition.get(code)`:
   ```python
   row = table.loc[code_str].to_dict()
   row["code"] = code_str
   return row
   ```
   Calling `.to_dict()` generates a brand-new Python dictionary. Mutating `row["fat_g"] = 999` in the caller does not impact subsequent lookups.
4. **Remaining Exposure (Internal Attribute Access):** In `src/lhf/constants.py`, `_load_constants()` returns the raw mutable dict `_CONSTANTS`. While `constants.get(id_)` returns an immutable float, a caller directly importing `lhf.constants._CONSTANTS` or calling `_load_constants()` can mutate the dictionary in-place. Standard access via `constants.get()` is safe.

---

### 2.2 Question 2: Are oil codes derived dynamically or hardcoded? Does the derivation cover all oil codes in IFCT?

**Finding: OIL CODES ARE HARDCODED; DERIVATION COVERS EXACTLY ALL 14 OIL CODES IN IFCT 2017.**

#### Code Analysis:
In `src/lhf/composition.py`:
```python
# SPEC §2: 14 fats and oils (codes T001-T014) have energy derived from fat
OIL_CODES = {f"T{i:03d}" for i in range(1, 12 + 3)}
...
oil = ifct_raw["code"].astype(str).isin(OIL_CODES)
```

1. **Derivation Mechanism:**
   The oil codes are **hardcoded** via set comprehension `OIL_CODES = {f"T{i:03d}" for i in range(1, 12 + 3)}`. This evaluates to:
   `{'T001', 'T002', 'T003', 'T004', 'T005', 'T006', 'T007', 'T008', 'T009', 'T010', 'T011', 'T012', 'T013', 'T014'}`.
   The code does NOT dynamically inspect the food category, fat content, or `enerc` value.

2. **IFCT 2017 Group T Coverage:**
   We audited the entire raw transcription (`data/raw/ifct2017_transcription/ifct2017_compositions.csv`, 542 rows) by grouping food codes by their prefix letter:
   ```
   Letter  Count  Min_Code  Max_Code  enerc==0 Count
   A          24  A001      A024      0
   B          25  B001      B025      0
   C          34  C001      C034      0
   ...
   S          10  S001      S010      0
   T          14  T001      T014      14
   ```
   - In IFCT 2017, Group T ("Fats and Edible Oils") contains **exactly 14 items** (`T001` through `T014`).
   - Across the entire IFCT dataset of 542 foods, **only Group T rows have `enerc == 0`**.
   - Every single one of these 14 rows is an oil or fat (Coconut oil, Corn oil, Cotton seed oil, Gingelly oil, Groundnut oil, Mustard oil, Palm oil, Rice bran oil, Safflower oil, Safflower blended, Soyabean oil, Sunflower oil, Ghee, Vanaspati).
   - Therefore, the hardcoded set `{T001..T014}` covers **100.0% of the fats and oils in the IFCT 2017 transcription**.

3. **Distinction from INDB Oils:**
   INDB UK and US contain additional oils (e.g., `T500 Butter`, `T501 Butter unsalted`, `T506 Ghee`, `T507 Coconut oil`, `T508 Sunflower oil`, `T510 Mustard oil`). However, INDB tables already contain verified non-zero energy values (`energy_kj` and `energy_kcal`). Per `SPEC.md` §2, the energy defect fix (`energy_flag = "FAT_ENERGY_DERIVED"`) is prescribed strictly for the IFCT transcription defect (`enerc == 0`). `_build_table()` applies `isin(OIL_CODES)` solely to `ifct_raw`, leaving INDB energy values unaltered as required.

4. **Brittle Nature of Hardcoding:**
   If a future revision of the IFCT dataset incorporates a 15th edible oil (e.g., `T015 Avocado oil`), `OIL_CODES` will fail to match it. A truly adaptive implementation would derive oil status using `(ifct_raw["enerc"] == 0) & (ifct_raw["code"].str.startswith("T"))`.

---

### 2.3 Question 3: How does `nutrients_for(code, grams)` behave with invalid codes, None codes, non-string codes, negative grams, NaN grams, or non-finite values?

**Finding: DEFENSIVE CHECKS ARE INCOMPLETE; SILENT FAILURES DETECTED FOR BOOLEANS, NANS, NEGATIVES, AND INFINITIES.**

#### Implementation in `src/lhf/composition.py`:
```python
def nutrients_for(code: str, grams: float) -> dict:
    table = _get_table()
    code_str = str(code)
    if code_str not in table.index:
        raise KeyError(code)
    if grams is None:
        raise ValueError("grams cannot be None")
    try:
        g = float(grams)
    except (TypeError, ValueError) as err:
        raise ValueError(f"grams must be numeric, got {grams!r}") from err
    row = table.loc[code_str]
    factor = g / 100
    return {col: float(row[col]) * factor for col in NUTRIENT_COLUMNS}
```

#### Adversarial Test Matrix:

| Test Input Scenario | Code Passed | Grams Passed | Actual Behavior | Expected / Safe Behavior | Status |
|---|---|---|---|---|---|
| **Unknown Code** | `"INVALID_CODE"` | `100` | Raises `KeyError: 'INVALID_CODE'` | Raise `KeyError` | **PASS** |
| **None Code** | `None` | `100` | Raises `KeyError: None` | Raise `KeyError` | **PASS** |
| **Integer Code** | `123` | `100` | Raises `KeyError: 123` | Raise `KeyError` | **PASS** |
| **Empty String Code**| `""` | `100` | Raises `KeyError: ''` | Raise `KeyError` | **PASS** |
| **Lowercase Code** | `"t001"` | `100` | Raises `KeyError: 't001'` | Raise `KeyError` | **PASS** |
| **Tuple / Object Code**| `("T001",)` | `100` | Raises `KeyError: ('T001',)` | Raise `KeyError` | **PASS** |
| **None Grams** | `"T001"` | `None` | Raises `ValueError: grams cannot be None` | Raise `ValueError` | **PASS** |
| **Invalid String Grams**| `"T001"` | `"fifty"` | Raises `ValueError: grams must be numeric...` | Raise `ValueError` | **PASS** |
| **Empty String Grams**| `"T001"` | `""` | Raises `ValueError: grams must be numeric...` | Raise `ValueError` | **PASS** |
| **Fraction Grams** | `"T001"` | `Fraction(1, 2)` | Evaluates cleanly: `fat_g = 0.5` | Return scaled nutrients | **PASS** |
| **Numeric String Grams**| `"T001"`| `"50"` | Casts cleanly: `fat_g = 50.0` | Return scaled nutrients | **PASS** |
| **Zero Grams (IFCT)** | `"T001"` | `0` | All nutrients `0.0` | Nutrients `0.0` | **PASS** |
| **Zero Grams (INDB)** | `"G509"` | `0` | Numeric `0.0`, `water_g`/`tfa_g` stay `NaN` | NaN stays NaN | **PASS** |
| **Boolean Grams `True`** | `"T001"` | `True` | **Silently evaluates as 1.0 g** (`fat_g = 1.0`) | Raise `TypeError` or `ValueError` | **DEFECT** |
| **Boolean Grams `False`**| `"T001"` | `False` | **Silently evaluates as 0.0 g** (`fat_g = 0.0`) | Raise `TypeError` or `ValueError` | **DEFECT** |
| **Negative Grams** | `"T001"` | `-50.0` | **Returns negative nutrients** (`fat_g = -50.0`, `energy = -450 kcal`) | Raise `ValueError("grams must be non-negative")` | **DEFECT** |
| **NaN Grams** | `"T001"` | `float("nan")` | **Silently returns dict of 13 NaNs** | Raise `ValueError("grams cannot be NaN")` | **DEFECT** |
| **Positive Infinity** | `"T001"` | `float("inf")` | **Returns `inf` and `nan`** (`0.0 * inf = nan`) | Raise `ValueError("grams must be finite")` | **DEFECT** |
| **Negative Infinity** | `"T001"` | `float("-inf")`| **Returns `-inf` and `nan`** | Raise `ValueError("grams must be finite")` | **DEFECT** |

#### Defect Detail Analysis:
1. **Boolean Coercion Vulnerability:** In Python, `isinstance(True, int)` is `True`. When `float(True)` is called in line 180, Python returns `1.0`. The author of `src/lhf/compute.py` explicitly guarded against this bug in line 32:
   ```python
   if grams is None or isinstance(grams, bool):
       skipped.append(idx)
   ```
   However, this guard was omitted from `composition.nutrients_for()`. Any direct consumer calling `nutrients_for("T001", True)` receives the nutrient values for 1 gram of coconut oil without any warning.
2. **NaN & Non-Finite Grams Leakage:** When missing data in pandas Series are represented as `float("nan")` or `np.nan`, `float(grams)` does not fail because `float("nan")` is a valid floating-point number. `factor = nan / 100` becomes `nan`. Consequently, `{col: float(row[col]) * factor ...}` silently yields a dictionary where every single nutrient is `NaN`, rather than raising an explicit validation error.
3. **Negative Mass:** The function permits physically impossible negative masses, returning negative calories and negative fat.

---

### 2.4 Question 4: Are numeric literals in `src/lhf/composition.py`, `constants.py`, and `paths.py` strictly compliant with AST Rule 1 ({0..12, 100, 1000})?

**Finding: 100% COMPLIANT AT AST LEVEL; USES CONSTANT FOLDING ARITHMETIC TO EVADE LITERAL CHECKS.**

#### AST Parse Audit:
We ran an AST walker over all three target files, logging every `ast.Constant` node containing an integer or float:

```
File: src/lhf/composition.py
  Line 11: value=1    (int) -> ALLOWED (in 0..12)
  Line 11: value=12   (int) -> ALLOWED (in 0..12)
  Line 11: value=3    (int) -> ALLOWED (in 0..12)
  Line 50: value=0    (int) -> ALLOWED (in 0..12)
  Line 85: value=1000 (int) -> ALLOWED (in {1000})
  Line 106: value=1000 (int) -> ALLOWED (in {1000})
  Line 107: value=1000 (int) -> ALLOWED (in {1000})
  Line 108: value=1000 (int) -> ALLOWED (in {1000})
  Line 146: value=0   (int) -> ALLOWED (in 0..12)
  Line 146: value=1   (int) -> ALLOWED (in 0..12)
  Line 184: value=100 (int) -> ALLOWED (in {100})

File: src/lhf/constants.py
  No numeric literals found.

File: src/lhf/paths.py
  No numeric literals found.
```

- **Total numeric literals in `src/lhf/composition.py`:** 11
- **Disallowed literals found:** 0
- **Compliance with `acceptance/test_rules.py`:** **100% PASS**

#### Scrutiny of Line 11 Arithmetic Synthesis:
Line 11 reads:
```python
OIL_CODES = {f"T{i:03d}" for i in range(1, 12 + 3)}
```
- **Context:** To iterate over the 14 oil codes (`T001` to `T014`), Python requires `range(1, 15)`.
- However, `15` is not in `{0..12, 100, 1000}`.
- The builder wrote `12 + 3`. In the AST, this is parsed as an `ast.BinOp(left=ast.Constant(value=12), op=ast.Add(), right=ast.Constant(value=3))`.
- Because both `12` and `3` are in `0..12`, the static AST check in `acceptance/test_rules.py` evaluates to `True`.
- At runtime, Python folds the constant expression to `15`.
- **Verdict:** While strictly compliant with the letter of the AST test parser, this is an intentional loophole exploit to synthesize an unpermitted integer.

---

### 2.5 Question 5: Is there any evidence of test cheating, hardcoding of answers, or circular references?

**Finding: NO TEST CHEATING OR CIRCULAR DEPENDENCIES; UNIT TEST SUITE CLOSELY PARROTS ACCEPTANCE TEST FIXTURES.**

1. **Absence of Test Hardcoding in `src/lhf`:**
   - We scanned `src/lhf/composition.py`, `constants.py`, and `paths.py` for hardcoded food lookup branches (e.g. `if code == "A019": return {"fat_g": 1.53}`).
   - None exist. Lookups are executed entirely through DataFrame indexing (`table.loc[code_str]`) and dynamic calculation.
   - We verified that no acceptance gold lines or holdout text appear anywhere in `src/lhf/` or `data/curated/`. `acceptance/test_rules.py` passed with 0 gold matches.

2. **Dependency Architecture & Circular Reference Check:**
   - `lhf.paths`: Imports standard library `os`. Has zero internal project dependencies.
   - `lhf.constants`: Imports `os`, `pandas`, and `lhf.paths`.
   - `lhf.composition`: Imports `os`, `numpy`, `pandas`, `lhf.paths`, and `lhf.constants`.
   - **Import Graph:** Strictly Directed Acyclic Graph (DAG):
     $$\text{paths} \longleftarrow \text{constants} \longleftarrow \text{composition}$$
   - Neither `paths.py`, `constants.py`, nor `composition.py` imports downstream modules (`compute`, `match`, `parse`, `grams`, `pipeline`). No circular imports exist.

3. **Acceptance Test Mirroring in Unit Tests:**
   - In `tests/test_t1.py`:
     - Line 126 queries food `"A019"` and asserts `fat_g == 1.53`. This exact item is tested in `acceptance/test_t1_composition.py:90-91`.
     - Line 144 queries food `"T013"` with mass `12.8` g. This exact calculation is tested in `acceptance/test_t1_composition.py:96-97`.
     - Line 150 queries food `"L002"` with mass `250` g. This exact calculation is tested in `acceptance/test_t1_composition.py:98-99`.
   - While `test_t1.py` has been substantially broadened since Round 1 to test oil derivations, UK/US datasets, Indian product flags, and cache immutability, its specific item-level checks are directly copied from the acceptance test file rather than exercising independent samples from the 746-food table.

---

## 3. Scientific and Data Integrity Verification

### 3.1 Dataset Aggregation & Uniqueness

The composition table aggregates 746 foods across four sources:

| Source Name | File Reference | Row Count | Codes Prefix | Verification Status |
|---|---|---|---|---|
| **IFCT2017** | `data/raw/ifct2017_transcription/ifct2017_compositions.csv` | 542 | `A001`–`T014` | Verified unique; zero overlap with other tables. |
| **INDB_UK** | `data/raw/indb/UK_fct.xlsx` (`Sheet1`) | 144 | `B500`–`V500` | Verified unique; filtered for `food_code.notna()`. |
| **INDB_US** | `data/raw/indb/US_fct.xlsx` (`Sheet1`) | 54 | `A500`–`T510` | Verified unique; filtered for `food_code.notna()`. |
| **IN_LABEL** | `data/curated/indian_products.csv` | 6 | `L901`–`L906` | Verified unique; Amul brand items & home malai. |
| **Combined** | | **746** | | **100% Unique Index (0 collisions)** |

### 3.2 Unit Conversions & Missing Values

1. **Sodium Scaling in IFCT:**
   In IFCT 2017 transcription, sodium (`na`) is reported in grams (e.g. `0.00270` for Amaranth seed). `composition.py` scales `na` by 1000 (`_to_num(ifct_raw["na"]) * 1000`), accurately producing milligrams.
2. **Fatty Acid Scaling in INDB UK/US:**
   In INDB spreadsheets, `sfa_mg`, `mufa_mg`, and `pufa_mg` are reported in milligrams. `composition.py` divides them by 1000 (`/ 1000`), converting them to grams.
3. **Trace Values:**
   Non-numeric values in INDB spreadsheets (`"Tr"` for Trace, `"N"` for Not detected) are safely coerced to `0.0` via `pd.to_numeric(series, errors="coerce").fillna(0)`.
4. **Moisture (`water_g`) and Trans Fat (`tfa_g`):**
   - For all 198 INDB UK and US foods, `water_g` and `tfa_g` are set to `np.nan`, adhering strictly to SPEC §2.
   - For Indian Products, `L901-L904` have `tfa_g = 0.0` and `water_g = np.nan`. `L905` has both as `np.nan`. `L906` (malai) has `tfa_g = np.nan` and lab-measured `water_g = 49.6`.
   - For IFCT 2017 foods, measured numeric values from `fatrn` and `water` are retained.

---

## 4. Vulnerability & Risk Inventory

| Issue ID | File & Line | Severity | Category | Description | Impact |
|---|---|---|---|---|---|
| **T1-R2-01** | `src/lhf/composition.py:180` | **MEDIUM** | Type Safety | Boolean `grams` (`True`/`False`) silently converts to `1.0`/`0.0`. | Erroneous calculations if boolean flags are passed accidentally to `nutrients_for`. |
| **T1-R2-02** | `src/lhf/composition.py:180-184` | **MEDIUM** | Input Validation | Negative, `NaN`, and `inf` grams are not rejected. | Negative grams produce negative nutrients/energy; `NaN` grams return all-`NaN` dict silently. |
| **T1-R2-03** | `src/lhf/composition.py:11` | **LOW** | Code Quality / Rules | `range(1, 12 + 3)` uses constant folding to evade AST check. | Bypasses literal rule restriction to hardcode 14. |
| **T1-R2-04** | `src/lhf/composition.py:151-155` | **LOW** | Concurrency | Lazy singleton pattern in `_get_table()` lacks thread lock. | Redundant multi-file I/O under concurrent requests. |
| **T1-R2-05** | `src/lhf/constants.py:15` | **INFORMATIONAL** | Encapsulation | `_load_constants()` returns direct reference to mutable `_CONSTANTS` dict. | Potential cache pollution if internal private method is invoked by external scripts. |

---

## 5. Remediation Plan

### 5.1 Harden `nutrients_for` Validation
Replace lines 177-183 in `src/lhf/composition.py` with strict numeric type, non-negativity, and finiteness checks:

```python
def nutrients_for(code: str, grams: float) -> dict:
    table = _get_table()
    code_str = str(code)
    if code_str not in table.index:
        raise KeyError(code)
    if grams is None or isinstance(grams, bool):
        raise ValueError(f"grams must be a non-boolean numeric value, got {grams!r}")
    try:
        g = float(grams)
    except (TypeError, ValueError) as err:
        raise ValueError(f"grams must be numeric, got {grams!r}") from err
    if math.isnan(g) or not math.isfinite(g) or g < 0:
        raise ValueError(f"grams must be non-negative and finite, got {grams!r}")
    row = table.loc[code_str]
    factor = g / 100
    return {col: float(row[col]) * factor for col in NUTRIENT_COLUMNS}
```

### 5.2 Dynamic Derivation for IFCT Oil Codes
Instead of hardcoding `range(1, 12 + 3)`, derive oil status from IFCT data attributes:
```python
# Group 'T' represents Fats and Edible Oils in IFCT 2017
oil = ifct_raw["code"].astype(str).str.startswith("T") & (enerc == 0)
```
This eliminates the `12 + 3` literal workaround while ensuring exact compliance with the scientific definition of the energy defect.

### 5.3 Implement Concurrency Locking for Table Cache
Protect the singleton initialization with a standard `threading.Lock`:
```python
import threading

_LOCK = threading.Lock()

def _get_table() -> pd.DataFrame:
    global _TABLE
    if _TABLE is None:
        with _LOCK:
            if _TABLE is None:
                _TABLE = _build_table()
    return _TABLE
```
