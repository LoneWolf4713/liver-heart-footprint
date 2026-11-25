# Adversarial Code and Data Audit: Task T1 (Constants & Food Composition Table)

**Auditor:** Adversarial Code & Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Files:**
- `src/lhf/__init__.py`
- `src/lhf/paths.py`
- `src/lhf/constants.py`
- `src/lhf/composition.py`  
**Associated Test Files:**
- `tests/test_t1.py`
- `acceptance/test_t1_composition.py`  
**Specification Reference:** `docs/SPEC.md` §2 (T1: constants and composition table), `docs/SPEC.md` §1 (Package layout & Integrity rules), `AGENTS.md`

---

## 1. Executive Summary & Verdict

### **Verdict: MINOR ISSUES**

The implementation of Task T1 in `src/lhf/paths.py`, `src/lhf/constants.py`, and `src/lhf/composition.py` is scientifically accurate, adheres strictly to the project integrity rules, and correctly reproduces the unified 746-food composition table across all four primary datasets (IFCT 2017 transcription, INDB UK, INDB US, and curated Indian Products). All 16 table columns, exact unit conversions, and missing-value semantics are respected.

Static analysis confirms **0 violations** of the numeric literal rule (AST check verifies only allowed literals `0`, `100`, `1000` appear). No cheating, hardcoded test fixtures, network calls, or unauthorized imports were detected.

However, deep adversarial probing revealed four notable issues:
1. **Cache Mutation Vulnerability (Cache Pollution):** `composition.load_table()` returns the raw mutable module-level singleton `_TABLE`. Any caller mutating the returned `DataFrame` in-place (e.g. dropping rows, adding columns, modifying values) permanently corrupts the global composition table across the entire Python process.
2. **Brittle Heuristic for Energy Defect Fix:** `_build_table()` identifies the 14 oil/fat rows using `ifct_raw["code"].astype(str).str.startswith("T0")`. While currently matching all 14 rows in IFCT 2017, this is a brittle heuristic directly copied from `acceptance/test_t1_composition.py:64` rather than an explicit check against `T001` through `T014` or group classification.
3. **Superficial Unit Test Suite:** `tests/test_t1.py` is an uncritical 36-line test file containing only 4 assertions. It checks only a single constant (`KJ_PER_KCAL`), a single food entry (`T001`), and a single nutrient calculation (`fat_g` for `T013`), leaving UK/US datasets, unit conversions, missing-value coercion, and error handling entirely unprobed in local unit tests.
4. **Undocumented Propagation of `None` in `nutrients_for`:** Calling `composition.nutrients_for(code, None)` does not raise a `TypeError` or `ValueError`; instead it calculates `factor = float("nan")` and returns a dict with all 13 nutrient values set to `NaN`.

---

## 2. Integrity Rules & Static Analysis Checks

### 2.1 Rule 1: No Invented Numbers (AST Analysis)
We parsed all target source files (`paths.py`, `constants.py`, `composition.py`) into Abstract Syntax Trees (ASTs) to audit every numeric constant against the allowed set $\{0, 1, 2, \dots, 12, 100, 1000\}$:

```python
# AST Scan Results for src/lhf/composition.py:
Line 47:  0       # fillna(0) for missing nutrient values (Allowed)
Line 82:  1000    # sodium conversion factor from IFCT g to mg (Allowed)
Line 103: 1000    # sfa conversion factor from INDB mg to g (Allowed)
Line 104: 1000    # mufa conversion factor from INDB mg to g (Allowed)
Line 105: 1000    # pufa conversion factor from INDB mg to g (Allowed)
Line 171: 100     # per-100g denominator in nutrients_for (Allowed)
```

- **Numeric Literals Found in `src/lhf/composition.py`:** 6
- **Numeric Literals Found in `src/lhf/constants.py`:** 0
- **Numeric Literals Found in `src/lhf/paths.py`:** 0
- **Disallowed Literals Found:** 0
- **Status:** **PASS** (100% compliant with Rule 1). All scientific constants (`KJ_PER_KCAL`, `FAT_KJ_PER_G`, `FAT_KCAL_PER_G`) are loaded dynamically from `data/curated/constants.csv`.

### 2.2 Rule 2: No Silent Defaults for Missing Data
- Checked whether missing values are silently defaulted to standard serving sizes (e.g. 100 g) or assumed ingredients:
  - `constants.get(id_)` raises `KeyError(id_)` on unknown IDs.
  - `composition.get(code)` raises `KeyError(code)` on unknown food codes.
  - `composition.nutrients_for(code, grams)` raises `KeyError(code)` on unknown food codes.
  - Trans fat (`tfa_g`) and moisture (`water_g`) are strictly kept as `NaN` (unknown), never coerced to 0.0 or estimated.
  - Other nutrients are coerced to `0.0` strictly per INDB convention (`INDB.do`) as specified in SPEC §2.
- **Status:** **PASS**

### 2.3 Rule 3: No Hardcoded Test Answers or Cheating
- Examined code for string literals matching recipe lines, test dishes, or hardcoded lookup dictionaries.
- Neither `constants.py` nor `composition.py` contains hardcoded food codes, nutrients, or results.
- `acceptance/test_rules.py` passed with 0 gold line occurrences in source code.
- **Status:** **PASS**

### 2.4 Rule 4: Data and Legal Rules
- No network libraries (`urllib`, `requests`, `httpx`, `aiohttp`, `socket`) imported.
- No subprocess calls or randomness (`random`, `secrets`) introduced.
- Raw files read strictly from local directories via `lhf.paths`.
- **Status:** **PASS**

---

## 3. Data Source Auditing & Contract Verification

### 3.1 Constants Reader (`src/lhf/constants.py`)
`lhf/constants.py` exports `get(id_) -> float`.
- **Source:** `data/curated/constants.csv` (9 records: `KJ_PER_KCAL`, `FAT_KJ_PER_G`, `FAT_KCAL_PER_G`, `SODIUM_MG_PER_G_SALT`, `PINCH_FRACTION_OF_TSP`, `SPICE_LINE_MAX_G`, `RECIPE_MASS_MIN_G`, `RECIPE_MASS_MAX_G`, `FUZZY_MATCH_CUTOFF`).
- **Data Types:** All loaded values are explicitly cast to `float`.
- **Key Validation:** Non-existent keys raise `KeyError`. Non-string keys (e.g. `None`, `123`, `4.5`) safely raise `KeyError`.

### 3.2 Composition Table Composition (`src/lhf/composition.py`)
`composition.load_table()` builds and returns a unified `pd.DataFrame` containing exactly 746 foods:

| Source | File Path | Rows | Specific Mappings & Transformations |
|---|---|---|---|
| **IFCT2017** | `data/raw/ifct2017_transcription/ifct2017_compositions.csv` | 542 | `na * 1000` -> `sodium_mg`; `enerc / KJ_PER_KCAL` -> `energy_kcal`; `fatrn` -> `tfa_g`; `water` -> `water_g`. T001-T014 energy defect fix applied. |
| **INDB_UK** | `data/raw/indb/UK_fct.xlsx` (`Sheet1`) | 144 | `sfa_mg / 1000` -> `sfa_g`; `mufa_mg / 1000` -> `mufa_g`; `pufa_mg / 1000` -> `pufa_g`; `tfa_g` = `NaN`; `water_g` = `NaN`; `energy_flag` = `""`. |
| **INDB_US** | `data/raw/indb/US_fct.xlsx` (`Sheet1`) | 54 | Same as INDB UK. |
| **IN_LABEL** | `data/curated/indian_products.csv` | 6 | Read with unified columns; `energy_flag` kept as `LABEL` (L901-L904) or `DERIVED_ENERGY` (L905-L906); `tfa_g` and `water_g` empty fields stay `NaN`. |
| **Total** | | **746** | Index is `code` (string), 100% unique. |

### 3.3 Column Schema & Dtypes
Table schema consists of 16 columns matching SPEC §2:
- **Metadata Columns (3):** `name` (str), `source` (str), `energy_flag` (str)
- **Nutrient Columns (13):** `energy_kj`, `energy_kcal`, `fat_g`, `sfa_g`, `mufa_g`, `pufa_g`, `tfa_g`, `carb_g`, `freesugar_g`, `fibre_g`, `protein_g`, `sodium_mg`, `water_g` (all `float64`).

### 3.4 Missing-Value Implementation Verification
Adversarial check of missing-value handling across all 746 rows:
- **Non-tfa/water columns (11 nutrients):** Scanned all 746 rows across all 11 columns for `NaN`. Found **0 NaNs**. Non-numeric representations in source files (e.g. `"N"`, `"Tr"` in `UK_fct.xlsx`) are cleanly coerced to `0.0` via `_to_num(series)`.
- **Trans fat (`tfa_g`):**
  - IFCT2017: 0 NaNs (all 542 rows have measured numeric `fatrn`).
  - INDB_UK: 144 / 144 are `NaN`.
  - INDB_US: 54 / 54 are `NaN`.
  - IN_LABEL: 2 / 6 are `NaN` (L905, L906); 4 / 6 are `0.0` (L901-L904).
- **Moisture (`water_g`):**
  - IFCT2017: 0 NaNs (all 542 rows have measured numeric `water`).
  - INDB_UK: 144 / 144 are `NaN`.
  - INDB_US: 54 / 54 are `NaN`.
  - IN_LABEL: 5 / 6 are `NaN` (L901-L905); 1 / 6 is `49.6` (L906).

### 3.5 IFCT Energy Defect Fix Audit
In IFCT 2017 raw transcription, the 14 edible oils and fats (`T001` through `T014`) have `enerc = 0`.
- Verified that exactly codes `T001` through `T014` have `energy_flag == "FAT_ENERGY_DERIVED"`.
- Verified that for all 14 rows:
  - `energy_kj == fat_g * constants.get("FAT_KJ_PER_G")` ($fat \times 37$)
  - `energy_kcal == fat_g * constants.get("FAT_KCAL_PER_G")` ($fat \times 9$)
- Verified that **0 non-oil IFCT rows** have `FAT_ENERGY_DERIVED`.
- Verified that all non-oil IFCT rows compute `energy_kcal == enerc / constants.get("KJ_PER_KCAL")`.

---

## 4. Adversarial Probing & Edge-Case Vulnerabilities

We executed dynamic adversarial probing scripts to test failure modes, type boundaries, cache integrity, and calculation precision.

### 4.1 Probe 1: Cache Mutation & Singleton Corruption (Vulnerability)
- **Test:** Retrieve table via `t1 = composition.load_table()`, perform in-place mutation (`t1.drop(t1.index, inplace=True)` or modify a nutrient cell `t1.loc['T001', 'fat_g'] = 999999.0`), and inspect `t2 = composition.load_table()`.
- **Result:** **FAILED**. `t2` reflected the corrupted state (`len(t2) == 0` or `t2.loc['T001', 'fat_g'] == 999999.0`).
- **Mechanism:** `load_table()` returns the direct reference to the module-level global `_TABLE`. Because pandas `DataFrame` is mutable, any downstream consumer that mutates the DataFrame in-place corrupts the shared dataset for all other modules in the running process.
- **Severity:** **MINOR**. In the current Phase 1 codebase, modules treat `load_table()` as read-only. However, in shared environments or multi-step analysis pipelines, this represents a classic mutable global state defect.

### 4.2 Probe 2: Brittle Oil Detection Heuristic
- **Test:** Inspect `_build_table()` line 62:
  ```python
  oil = ifct_raw["code"].astype(str).str.startswith("T0")
  ```
- **Analysis:** This heuristic assumes every code starting with `"T0"` is one of the 14 fats/oils. While valid for the current static transcription of IFCT 2017 (which contains only `T001`-`T014`), it mirrors `acceptance/test_t1_composition.py:64` rather than implementing the specification contract:
  > "in the IFCT transcription, the 14 fats and oils (codes T001-T014) have energy 0."
  If a future update to IFCT introduces codes like `T015` or `T020`, or if food codes are restructured, this rule will silently apply the 100% fat energy derivation to non-pure-oil items.

### 4.3 Probe 3: `composition.nutrients_for(code, grams)` Edge Cases
We tested `nutrients_for` against unexpected, invalid, and boundary inputs:
- `grams = 0`: Evaluates cleanly. Nutrients with values become `0.0`. For UK/US foods where `water_g` is `NaN`, `NaN * 0.0` correctly evaluates to `NaN` under IEEE 754 floating point arithmetic.
- `grams = -50`: Returns negative nutrient values (e.g. `fat_g = -0.6`).
- `grams = None`: Returns a dictionary where **all 13 nutrient values are `NaN`**. The function does not raise an exception because line 171 computes:
  ```python
  factor = float(grams) / 100 if grams is not None else float("nan")
  ```
  While `lhf.compute` filters `grams is None` upstream, this behavior in `nutrients_for` is implicit and undocumented.
- `grams = float("nan")`: All nutrients evaluate to `NaN`.
- `grams = "100"`: Casts string to float and returns valid scaled nutrients.
- `grams = "abc"`: Correctly raises `ValueError: could not convert string to float: 'abc'`.
- `code = 901` (int): Raises `KeyError: 901` (does not auto-map to `"L901"`).
- `code = None`: Raises `KeyError: None`.
- `code = "ZZZ999"`: Raises `KeyError: 'ZZZ999'`.

### 4.4 Probe 4: `composition.get(code)` Dictionary Mutation
- **Test:** Call `r = composition.get("T001")`, mutate `r["fat_g"] = 999999.0`, and call `r2 = composition.get("T001")`.
- **Result:** **PASS**. `r2["fat_g"]` remained `100.0`. `row.to_dict()` creates a shallow dictionary copy, insulating subsequent `get()` calls from dict mutations.

### 4.5 Probe 5: `constants.get(id_)` Robustness
- **Test:** Probe `constants.get()` with invalid types: `None`, `123`, `4.5`, `""`, `("tuple",)`.
- **Result:** **PASS**. All raise `KeyError`.
- **Test:** Verify return types of all 9 registered constants.
- **Result:** **PASS**. All 9 return instances of `float`.

---

## 5. Detailed Vulnerability Inventory

| ID | File & Line | Severity | Description | Impact |
|---|---|---|---|---|
| **T1-1** | `src/lhf/composition.py:148-152` | **MINOR** | `load_table()` returns mutable global `_TABLE` without `.copy()`. | Process-wide cache corruption if caller mutates DataFrame in-place. |
| **T1-2** | `src/lhf/composition.py:62` | **MINOR** | Oil filter uses heuristic `.str.startswith("T0")` mirroring acceptance test rather than checking exact set `T001-T014`. | Brittle; could misclassify future IFCT `T0*` food codes. |
| **T1-3** | `tests/test_t1.py:1-36` | **MINOR** | Superficial test suite: only 4 assertions in 36 lines; fails to test INDB UK/US, IN_LABEL, unit conversions, or missing-value handling. | Builder relied entirely on acceptance tests; zero regression coverage for 90% of T1 functionality. |
| **T1-4** | `src/lhf/composition.py:171` | **INFORMATIONAL** | `nutrients_for(code, None)` silently returns a dict of `NaN`s instead of raising `TypeError` or `ValueError`. | Undocumented implicit behavior relying on float NaN arithmetic. |

---

## 6. Recommendations for Remediation

### 6.1 Prevent Cache Mutation in `load_table()`
Return a copy or mark the dataframe as read-only to prevent cache pollution:
```python
def load_table() -> pd.DataFrame:
    global _TABLE
    if _TABLE is None:
        _TABLE = _build_table()
    return _TABLE.copy()
```

### 6.2 Make Oil Code Matching Explicit
Replace the `startswith("T0")` heuristic with explicit set membership matching SPEC §2:
```python
OIL_CODES = {f"T{i:03d}" for i in range(1, 15)}
oil = ifct_raw["code"].astype(str).isin(OIL_CODES)
```

### 6.3 Expand Unit Tests in `tests/test_t1.py`
Add comprehensive unit tests covering:
1. INDB UK and INDB US food parsing and unit scaling (mg to g).
2. IN_LABEL parsing and `energy_flag` retention (`LABEL`, `DERIVED_ENERGY`).
3. Verification that `water_g` and `tfa_g` remain `NaN` on UK/US items.
4. Error checking on `constants.get()` and `composition.get()` with invalid types (`None`, ints).
5. Verification of `nutrients_for` scaling with `0`, `float`, and `Fraction` inputs.

---

## 7. Audit Conclusion & Final Sign-Off

The Task T1 implementation is **sound, honest, and scientifically compliant**. The builder did not cheat, did not hardcode values, did not invent constants, and faithfully transcribed all source composition tables. The identified issues do not compromise the integrity of the calculated footprints in Phase 1, but represent software engineering weaknesses (cache mutability and token unit testing) that should be hardened.

**Final Audit Verdict:** **MINOR ISSUES**
