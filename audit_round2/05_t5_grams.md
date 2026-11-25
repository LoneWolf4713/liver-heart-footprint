# Round 2 Adversarial Audit Report: Task T5 (Household Measures to Grams)

**Audit Target:** Task T5 — Household Measures to Grams Conversion (`lhf.grams`)  
**Auditor:** Auditor 5 — Round 2 Adversarial Red Team Auditor  
**Date:** 2026-11-11  
**Operating Principle:** GUILTY UNTIL PROVEN INNOCENT  
**Target Files Scrutinized:**
- `src/lhf/grams.py`
- `data/curated/measures.csv`
- `data/curated/measures_README.md`
- `data/curated/constants.csv`
- `acceptance/test_t5_grams.py`
- `tests/test_t5.py`
- `src/lhf/pipeline.py` (downstream consumer)
- `docs/SPEC.md` §6, §1
- `AGENTS.md` (Integrity Rules 1–6)

---

## 1. Executive Summary & Verdict

### **Verdict: CLEAN**

Following comprehensive adversarial stress testing, boundary condition probing, negative fuzzing, AST analysis, and verification of Round 1 defect remediation, Task T5 (`lhf.grams.grams_for`) is rated **CLEAN**.

The critical defects identified in Round 1—specifically the type-brittleness crash on non-string food codes (DEF-C7), the downstream NaN leakage hole (DEF-D10), and the shallow unit test coverage—have been **fully and rigorously remediated**.

Key highlights of the audited implementation:
1. **Defensive Normalization Across All Inputs (DEF-C7 Remediated):** `grams_for` and `_get_density` sanitize `code` using `if isinstance(code, str): code = code.strip().upper(); if not code: code = None; else: code = None`. Non-string inputs (`None`, `int`, `float`, `bool`, `list`, `dict`, `object()`) are safely handled without throwing `TypeError` or `IndexError`.
2. **Strict Waterfall Fidelity:** Rules 1 through 9 are executed in the exact priority order mandated by `docs/SPEC.md` §6. Stated mass strictly preempts stated volume; stated volume strictly preempts household parsing; unmapped/non-food codes are fenced from household lookup rules; code-level measurements preempt group-level measurements; pinch/dash fallback operates strictly as documented.
3. **Plugging the NaN / Boolean Vulnerability (DEF-D10 Remediated):** `math.isnan()` and `isinstance(..., bool)` guards are placed at every entry point (`stated_g`, `stated_ml`, and `qty`). Passing `NaN` or booleans immediately yields `grams: None`, `basis: "UNQUANTIFIABLE"`, preventing NaN contamination in downstream nutrient accumulators.
4. **AST Rule 1 Compliance:** An Abstract Syntax Tree traversal of `src/lhf/grams.py` revealed exactly 12 numeric constant nodes, consisting only of the integers `0`, `1`, and `1000`. All are strictly within the permitted set `{0..12, 100, 1000}`. Zero numeric literals were invented. `PINCH_FRACTION_OF_TSP` (0.25) is dynamically loaded from `constants.csv`.
5. **Zero Test Gaming & Full Data Integrity:** In `measures.csv`, all 243 data rows are structurally valid, code references match NIN/FDC composition tables with 100% referential integrity, and all 45 group measures and 5 mass unit measures are fully reachable.

---

## 2. Rigorous Answers to Mandated Audit Questions

### Question 1: Conversion Rule Implementation & Precedence Order (Rules 1 to 9)
**Does `grams_for` properly implement all conversion rules (rules 1 through 9) in the exact documented precedence order?**

#### Contract Analysis (`docs/SPEC.md` §6)
The specification defines an ordered 9-rule waterfall where the first matching rule must be applied:
1. `stated_g is not None` → grams = `stated_g`, basis `STATED_MASS`.
2. `stated_ml is not None` → grams = `stated_ml × density`, basis `STATED_VOLUME`. Density resolved from (code, "ml") → (code[0], "ml") → 1.0 with flag `DENSITY_ASSUMED_1`.
3. `qty is None or unit is None` → None, basis `UNQUANTIFIABLE`.
4. `unit in (g, kg, mg, oz, lb)` → `qty × any row`, basis `MASS_UNIT`.
5. `unit in (ml, l)` → `qty × (1000 if l) × density`, basis `VOLUME_UNIT`.
*(Gate: When code is None or UNMAPPED/NON_FOOD, only rules 1–5 can apply).*
6. Code rows for `(code, unit)`, basis `CODE_MEASURE`:
   - Exact size match;
   - Otherwise blank size row;
   - Otherwise "medium" row with flag `SIZE_ASSUMED_MEDIUM` (no size given) or `SIZE_SUBSTITUTED` (different size given).
7. Group row for `(code[0], unit)`, basis `GROUP_MEASURE`.
8. Unit `pinch` or `dash` with no row found in rules 6–7 → `qty × PINCH_FRACTION_OF_TSP × tsp_weight`, flag `PINCH_AS_QUARTER_TSP`. Basis is the basis of the tsp row (`CODE_MEASURE` or `GROUP_MEASURE`).
9. Otherwise → None, basis `UNQUANTIFIABLE`. **Never invent a default.**

#### Code Audit & Precedence Verification
Examining `src/lhf/grams.py`:
- **Lines 109–119 (Rule 1):** `if stated_g is not None:` executes first. If valid, immediately returns `STATED_MASS`.
- **Lines 121–132 (Rule 2):** `if stated_ml is not None:` executes second. Calls `_get_density(code)`. If valid, immediately returns `STATED_VOLUME`.
- **Lines 154–156 (Rule 3):** `if qty is None or unit is None:` returns `UNQUANTIFIABLE`.
- **Lines 170–172 (Rule 4):** `if unit in any_measures:` looks up `measures.csv` any rows (`g`, `kg`, `mg`, `oz`, `lb`) and returns `MASS_UNIT`.
- **Lines 174–178 (Rule 5):** `if unit in ("ml", "l"):` applies density scaling and returns `VOLUME_UNIT`.
- **Lines 181–182 (Gate):** `if not code or code in ("UNMAPPED", "NON_FOOD"): return UNQUANTIFIABLE`. Correctly blocks unmapped foods from attempting household measure extrapolation.
- **Lines 185–188 (Rule 6):** `_resolve_code_measure` executes code row lookup with size fallback waterfall.
- **Lines 191–193 (Rule 7):** `grp = code[0]`; `if (grp, unit) in group_measures:` returns `GROUP_MEASURE`.
- **Lines 196–213 (Rule 8):** `if unit in ("pinch", "dash"):` queries code tsp, then group tsp, applies `PINCH_FRACTION_OF_TSP`, and attaches `PINCH_AS_QUARTER_TSP`.
- **Line 216 (Rule 9):** Final fallback returns `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}`.

#### Boundary Precedence Probes (Adversarial Script Output)
```python
# Probe: Rule 1 vs Rule 2 conflict (both stated_g and stated_ml supplied)
grams_for(qty=1, unit="cup", size="medium", stated_g=100.0, stated_ml=200.0, code="A504")
# Output: {'grams': 100.0, 'basis': 'STATED_MASS', 'flags': []} -> PASS (Rule 1 strictly wins)

# Probe: Rule 1 vs Rule 4 conflict (stated_g supplied with unit='g')
grams_for(qty=50, unit="g", size=None, stated_g=100.0, stated_ml=None, code="A504")
# Output: {'grams': 100.0, 'basis': 'STATED_MASS', 'flags': []} -> PASS (Rule 1 strictly wins)

# Probe: Rule 2 vs Rule 3 conflict (stated_ml supplied with qty=None, unit=None)
grams_for(qty=None, unit=None, size=None, stated_g=None, stated_ml=100.0, code="T508")
# Output: {'grams': 92.0, 'basis': 'STATED_VOLUME', 'flags': []} -> PASS (Rule 2 strictly wins)

# Probe: Rule 3 vs Rule 4 conflict (qty=None with unit='g')
grams_for(qty=None, unit="g", size=None, stated_g=None, stated_ml=None, code="A504")
# Output: {'grams': None, 'basis': 'UNQUANTIFIABLE', 'flags': []} -> PASS (Rule 3 strictly wins)

# Probe: Rule 6 vs Rule 7 conflict (Code row vs Group row for T508 tsp)
# Code T508 tsp = 5.0 g; Group T tsp = 4.0 g
grams_for(qty=1, unit="tsp", size=None, stated_g=None, stated_ml=None, code="T508")
# Output: {'grams': 5.0, 'basis': 'CODE_MEASURE', 'flags': []} -> PASS (Rule 6 strictly wins)

# Probe: Rule 6 vs Rule 8 conflict (Dash with existing code row: G528 salt dash = 0.4 g)
grams_for(qty=1, unit="dash", size=None, stated_g=None, stated_ml=None, code="G528")
# Output: {'grams': 0.4, 'basis': 'CODE_MEASURE', 'flags': []} -> PASS (Code row dash used without pinch flag)

# Probe: Rule 8 Code tsp vs Group tsp (Turmeric G033 has code tsp 3.0 g; Group G has tsp 2.0 g)
grams_for(qty=1, unit="pinch", size=None, stated_g=None, stated_ml=None, code="G033")
# Output: {'grams': 0.75, 'basis': 'CODE_MEASURE', 'flags': ['PINCH_AS_QUARTER_TSP']} -> PASS (Uses code tsp)

# Probe: Rule 8 Group tsp fallback (Hing G019 has no code tsp; Group G has tsp 2.0 g)
grams_for(qty=1, unit="pinch", size=None, stated_g=None, stated_ml=None, code="G019")
# Output: {'grams': 0.5, 'basis': 'GROUP_MEASURE', 'flags': ['PINCH_AS_QUARTER_TSP']} -> PASS (Uses group tsp)
```
**Verdict:** **PASS (Flawless Precedence Order)**.

---

### Question 2: Non-String `code` Handling (Defensive Architecture)
**How does `grams_for` handle non-string `code` inputs (e.g. `None`, integers, floats)? Does it crash or handle them defensively?**

#### Implementation Verification (Fix for DEF-C7)
In Round 1, passing `code=123` crashed inside `_get_density` and Rule 7 with `TypeError: 'int' object is not subscriptable` because `code[0]` was called on un-sanitized non-string types.

In the current implementation:
```python
# src/lhf/grams.py lines 101-106
if isinstance(code, str):
    code = code.strip().upper()
    if not code:
        code = None
else:
    code = None
```
And inside `_get_density`:
```python
# src/lhf/grams.py lines 48-53
if not isinstance(code, str):
    code = None
else:
    code = code.strip().upper()
    if not code:
        code = None
```

#### Adversarial Fuzzing Matrix
We subjected `grams_for` to a comprehensive matrix of non-string and malformed codes across various rule contexts:

| Test Input (`code`) | Operation Context | Expected Behavior | Observed Result | Status |
|---|---|---|---|---|
| `None` | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `123` (int) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `0` (int) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `3.14` (float) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `float("nan")` | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `True` (bool) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `False` (bool) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `["A504"]` (list) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `{"code": "A504"}` | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `object()` | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `123` (int) | `qty=100, unit="g"` (Rule 4) | `MASS_UNIT`, `100.0` grams | `{"grams": 100.0, "basis": "MASS_UNIT", "flags": []}` | PASS |
| `None` | `stated_ml=100` (Rule 2) | `STATED_VOLUME`, `100.0` grams | `{"grams": 100.0, "basis": "STATED_VOLUME", "flags": ["DENSITY_ASSUMED_1"]}` | PASS |
| `123` (int) | `stated_ml=100` (Rule 2) | `STATED_VOLUME`, `100.0` grams | `{"grams": 100.0, "basis": "STATED_VOLUME", "flags": ["DENSITY_ASSUMED_1"]}` | PASS |
| `""` (empty str) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `"   "` (spaces) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `"\x00"` (null byte) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |
| `"🍛"` (emoji) | `qty=1, unit="cup"` | `UNQUANTIFIABLE`, `None` grams | `{"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}` | PASS |

**Verdict:** **PASS (Completely Resilient)**.

---

### Question 3: Handling of Missing, Zero, Negative, and NaN Quantities
**How does `grams_for` handle missing, zero, negative, or `NaN` parsed quantities?**

#### Comprehensive Numeric Probe Suite
We tested all three numeric parameters (`stated_g`, `stated_ml`, and `qty`) across boundary values:

```
Input Type           | stated_g Result                  | stated_ml Result (density=1.0)    | qty Result (unit="cup", A504 92g)
---------------------------------------------------------------------------------------------------------------------------
None (missing)       | Falls to Rule 2/3                | Falls to Rule 3                   | UNQUANTIFIABLE, grams=None
0 (zero int)         | STATED_MASS, grams=0.0           | STATED_VOLUME, grams=0.0          | CODE_MEASURE, grams=0.0
0.0 (zero float)     | STATED_MASS, grams=0.0           | STATED_VOLUME, grams=0.0          | CODE_MEASURE, grams=0.0
-5 (negative int)    | STATED_MASS, grams=-5.0          | STATED_VOLUME, grams=-5.0         | CODE_MEASURE, grams=-460.0
-5.0 (neg float)     | STATED_MASS, grams=-5.0          | STATED_VOLUME, grams=-5.0         | CODE_MEASURE, grams=-460.0
float("nan")         | UNQUANTIFIABLE, grams=None       | UNQUANTIFIABLE, grams=None        | UNQUANTIFIABLE, grams=None
True (bool)          | UNQUANTIFIABLE, grams=None       | UNQUANTIFIABLE, grams=None        | UNQUANTIFIABLE, grams=None
False (bool)         | UNQUANTIFIABLE, grams=None       | UNQUANTIFIABLE, grams=None        | UNQUANTIFIABLE, grams=None
"10" (numeric str)   | STATED_MASS, grams=10.0          | STATED_VOLUME, grams=10.0         | CODE_MEASURE, grams=920.0
"abc" (invalid str)  | UNQUANTIFIABLE, grams=None       | UNQUANTIFIABLE, grams=None        | UNQUANTIFIABLE, grams=None
[10] (list)          | UNQUANTIFIABLE, grams=None       | UNQUANTIFIABLE, grams=None        | UNQUANTIFIABLE, grams=None
{"a": 1} (dict)      | UNQUANTIFIABLE, grams=None       | UNQUANTIFIABLE, grams=None        | UNQUANTIFIABLE, grams=None
```

#### Detailed Observations:
1. **NaN Immunity:** `math.isnan()` is checked on `stated_g` (line 114), `stated_ml` (line 126), and `qty` (line 162). If any parsed quantity is NaN, execution halts with `grams: None, basis: "UNQUANTIFIABLE"`.
2. **Boolean Trap Prevention:** In Python, `isinstance(True, int)` is `True`. Naive conversion `float(True)` yields `1.0`. `grams.py` contains explicit boolean guards:
   ```python
   if isinstance(stated_g, bool): return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
   if isinstance(stated_ml, bool): return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
   if isinstance(qty, bool): return {"grams": None, "basis": "UNQUANTIFIABLE", "flags": []}
   ```
3. **Zero and Negative Gram Handling (Pipeline Harmonization):**
   - In `grams_for`, a quantity of `0` or negative yields arithmetic mass `0.0` or negative.
   - Downstream in `src/lhf/pipeline.py` (lines 147–160):
     ```python
     if g is None or g <= 0:
         lines_out.append({
             ...,
             "grams": None,
             "grams_basis": g_basis,
             "grams_flags": g_flags,
             "included": False,
             "exclusion_reason": "UNQUANTIFIABLE",
             ...
         })
     ```
   - Zero and negative grams are immediately excluded as `UNQUANTIFIABLE` by the pipeline and never enter `compute.sum_nutrients`. This architecture strictly satisfies SPEC §9: *"A line is included if status is QUANTIFIED, the code is a real composition code, and grams > 0."*
4. **Infinite Quantities (`float("inf")`):**
   - If an external caller bypasses `parse_line` and directly injects `qty = float("inf")`, `grams_for` returns `grams: inf`. Downstream in `pipeline.py`, `inf <= 0` is `False`, so the pipeline includes the line, but catches it with the `MASS_IMPLAUSIBLE` warning. In normal pipeline operation, `parse_line` rejects `"inf"` as `UNQUANTIFIED`.

**Verdict:** **PASS (Clean & Sound)**.

---

### Question 4: Pinch and Dash Resolution via `constants.csv`
**Are pinches and dashes properly resolved using `PINCH_FRACTION_OF_TSP` from `constants.csv`?**

#### Implementation Audit
Rule 8 implementation in `src/lhf/grams.py`:
```python
# Lines 196-213
if unit in ("pinch", "dash"):
    tsp_chosen, _ = _resolve_code_measure(code, "tsp", None)
    tsp_grams = None
    tsp_basis = None
    if tsp_chosen is not None:
        tsp_grams = tsp_chosen["grams"]
        tsp_basis = "CODE_MEASURE"
    elif (grp, "tsp") in group_measures:
        tsp_grams = group_measures[(grp, "tsp")]
        tsp_basis = "GROUP_MEASURE"

    if tsp_grams is not None:
        pinch_frac = constants.get("PINCH_FRACTION_OF_TSP")
        return {
            "grams": qty_val * pinch_frac * tsp_grams,
            "basis": tsp_basis,
            "flags": ["PINCH_AS_QUARTER_TSP"],
        }
```

#### Verification Checks:
1. **Dynamic Constant Loading:** The code calls `constants.get("PINCH_FRACTION_OF_TSP")`. In `data/curated/constants.csv`, this row is defined as:
   ```csv
   PINCH_FRACTION_OF_TSP,0.25,tsp per pinch or dash,"INDB Units.xlsx: 'Spice powders 1 sprinkle/pinch = 0.25 tsp' and '1 dash = 0.25 tsp'"
   ```
   No literal `0.25` is hardcoded in `grams.py`.
2. **Code Tsp vs Group Tsp Priority:**
   - If the code has a specific tsp row (e.g. Turmeric `G033` = 3.0 g), it computes `qty × 0.25 × 3.0 = 0.75 g`, basis `CODE_MEASURE`, flags `["PINCH_AS_QUARTER_TSP"]`.
   - If the code has no tsp row, but its group does (e.g. Hing `G019`, group `G` tsp = 2.0 g), it computes `qty × 0.25 × 2.0 = 0.5 g`, basis `GROUP_MEASURE`, flags `["PINCH_AS_QUARTER_TSP"]`.
3. **Specific Dash Code Rows Preempt Rule 8:**
   - Table salt (`G528`) has a specific code row for `dash`: 0.4 g.
   - When `grams_for(1, "dash", None, None, None, "G528")` is invoked, Rule 6 matches first:
     ```python
     {'grams': 0.4, 'basis': 'CODE_MEASURE', 'flags': []}
     ```
   - It correctly returns `0.4 g`, basis `CODE_MEASURE`, and does NOT apply the quarter-tsp fallback flag.
4. **Fallback When Neither Code Nor Group Has Tsp:**
   - For an ingredient in food group `F` (Fruits, which has no tsp measure in `measures.csv`), `grams_for(1, "pinch", None, None, None, "F999")` cleanly returns `grams: None`, basis `UNQUANTIFIABLE`, without inventing a default.

**Verdict:** **PASS (Strictly Adherent to Scientific Contracts)**.

---

### Question 5: Numeric Literals & AST Rule 1 Compliance
**Are numeric literals in `src/lhf/grams.py` strictly compliant with AST Rule 1 ({0..12, 100, 1000})?**

#### Static AST Traversal
We parsed `src/lhf/grams.py` into an Abstract Syntax Tree using Python's standard `ast` library and enumerated all `ast.Constant` numeric nodes:

```python
import ast

tree = ast.parse(open("src/lhf/grams.py").read())
constants_found = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float) and not isinstance(node.value, bool):
            constants_found.append((node.lineno, node.value, type(node.value).__name__))
```

#### Traversal Results:
```
Index | Line | Value | Type | Context Description
-------------------------------------------------------------------------
1     | 58   | 0     | int  | Tuple index for code_measures[(code, 'ml')][0]
2     | 59   | 0     | int  | String index for len(code) > 0 check
3     | 59   | 0     | int  | String index for code[0] group extraction
4     | 60   | 0     | int  | String index for code[0] group extraction
5     | 61   | 1     | int  | Fallback density return (1.0)
6     | 136  | 0     | int  | List index for unit[0]
7     | 136  | 0     | int  | len(unit) > 0 check
8     | 145  | 0     | int  | List index for size[0]
9     | 145  | 0     | int  | len(size) > 0 check
10    | 175  | 1000  | int  | Liter to milliliter multiplier (mult = 1000 if unit == "l" else 1)
11    | 175  | 1     | int  | Fallback multiplier for milliliter (1)
12    | 191  | 0     | int  | String index for grp = code[0] group extraction
```

- **Total Numeric Literals Found:** 12
- **Unique Numeric Values:** `{0, 1, 1000}`
- **Permitted Set:** `{0..12, 100, 1000}`
- **Disallowed Numeric Literals:** **0**
- **Test Enforcement:** Verified by running `PYTHONPATH=src python3 acceptance/test_rules.py` (Rule 1 passes across all source files).

**Verdict:** **PASS (100% Compliant)**.

---

## 3. Data Integrity & Reachability Audit (`measures.csv`)

We audited `data/curated/measures.csv` (243 rows, protected architect table):
1. **Referential Integrity of Food Codes:**
   - All semicolon-delimited food codes in `measures.csv` were verified against `lhf.composition.load_table()`.
   - **0 unmapped or missing codes** were found.
2. **Duplicate Key Check:**
   - `(code, unit, size)` uniqueness: 0 duplicates.
   - `(group, unit)` uniqueness: 0 duplicates.
   - `any` unit uniqueness: 0 duplicates.
3. **Group Measures Reachability:**
   - In Round 1, Auditor 1 noted that `acceptance/test_t5_grams.py` Part A omitted reachability checks for `group` measures.
   - We authored an exhaustive reachability probe testing all 45 group rows in `measures.csv` by querying synthetic codes `f"{grp}9999"`.
   - **Result:** **45 / 45 group rows (100.0%) are fully reachable and return their exact cited values**.
4. **Grams Value Validity:**
   - All 243 rows have strictly positive, finite float values (`grams > 0`). Zero NaNs, negatives, or zeroes exist in the table.

---

## 4. Test Suite Quality & Gaming Detection

### 4.1 Acceptance Test Verification (`acceptance/test_t5_grams.py`)
Running `PYTHONPATH=src python3 acceptance/test_t5_grams.py`:
- **Part A (Reachability):** 411 code-level keys tested and confirmed.
- **Part B (Gold Line Validation):** 106 / 106 gold lines exact (100.0% agreement, exceeding the 97% requirement).
- **Part C (Edge Cases):** 14 policy edge cases tested, including besan cup, hing tsp/pinch, salt dash, onion size substitution, mint unquantifiable, milk liter, and unknown density.

### 4.2 Unit Test Verification (`tests/test_t5.py`)
`tests/test_t5.py` contains 12 comprehensive unit tests spanning 226 lines:
- `test_rule1_stated_mass`
- `test_rule2_stated_volume`
- `test_rule3_missing_qty_or_unit`
- `test_rule4_mass_units`
- `test_rule5_volume_units`
- `test_rule6_code_measure_and_sizes`
- `test_rule7_group_measure`
- `test_rule8_pinch_and_dash`
- `test_rule9_otherwise_unquantifiable`
- `test_non_string_code_types` (DEF-C7 test)
- `test_nan_and_invalid_values` (DEF-D10 test)
- `test_group_measures_reachability` (Groups T, L, K, E, G reachability)

### 4.3 Code Coverage
Using `sys.settrace` dynamic line execution tracking across `tests/test_t5.py` and `acceptance/test_t5_grams.py`:
- **Executable Lines:** 166
- **Executed Lines:** 153
- **Statement Coverage:** **92.17%**
- Unexecuted lines are strictly `else:` clauses and branch fallbacks for multi-token inputs.

### 4.4 Gaming & Hardcoding Check
- No gold recipe lines appear in `src/lhf/grams.py`.
- No food codes (`A504`, `G019`, `T508`, etc.) appear as literals in `src/lhf/grams.py`.
- All conversions derive dynamically from `data/curated/measures.csv` and `data/curated/constants.csv`.

---

## 5. Remediation Status of Round 1 Findings

| Defect / Observation | Round 1 Status | Round 2 Audit Verification | Current Status |
|---|---|---|---|
| **DEF-C7: Non-string `code` crash (`TypeError`)** | Critical Bug | Lines 48–53 and 101–106 now defensively normalize `code` via `isinstance(code, str)`. Fuzzed with 15+ non-string types. Zero exceptions raised. | **RESOLVED** |
| **DEF-D10: NaN leakage through `grams_for`** | High Vulnerability | `math.isnan()` checks added to `stated_g`, `stated_ml`, and `qty_val`. NaNs immediately return `UNQUANTIFIABLE`. | **RESOLVED** |
| **Boolean-as-integer trap (`float(True) == 1.0`)** | Hidden Vulnerability | Explicit `isinstance(..., bool)` checks added for all numeric inputs. Booleans return `UNQUANTIFIABLE`. | **RESOLVED** |
| **Acceptance test omission of group measures** | Test Gap | `tests/test_t5.py` added `test_group_measures_reachability`; our probe confirmed 45/45 group rows reachable. | **RESOLVED** |
| **Shallow unit test coverage** | Quality Defect | `tests/test_t5.py` expanded from 9 happy-path tests to 12 in-depth unit tests (226 lines). | **RESOLVED** |

---

## 6. Recommendations & Minor Observations

1. **Infinity Guard (`math.isinf`) [Minor Observation]:**
   While `math.isnan()` is thoroughly checked, `math.isinf()` is not explicitly checked in `grams.py`. If `qty = float("inf")` is passed directly by an external API caller, `grams_for` returns `grams: inf`. Adding `not math.isfinite(val)` alongside `math.isnan(val)` would provide defense-in-depth against malicious API inputs.
2. **Acceptance Test Enhancement [Maintenance]:**
   In `acceptance/test_t5_grams.py` Part A, an explicit branch for `elif r["match_type"] == "group":` could be added to formally assert reachability of all 45 group measures during acceptance test runs.

---

## 7. Conclusion

Task T5 (`lhf.grams`) is in outstanding condition. The module is scientifically sound, strictly adheres to the project's zero-guesswork integrity principles, exhibits 100% adherence to documented rule precedence, and has fully remediated all defects identified in earlier sessions.

**Final Verdict: CLEAN**
