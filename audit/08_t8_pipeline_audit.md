# Adversarial Audit Report: Task T8 (Recipe Pipeline & CLI)

**Audit Target:** Task T8 — Recipe Pipeline & CLI  
**Auditor:** Adversarial Code and Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Files:**
- `src/lhf/pipeline.py`
- `src/lhf/cli.py`
- `tests/test_t8.py`
- `acceptance/test_t8_pipeline.py`
- `data/curated/constants.csv`
- `data/curated/classes.csv`
- `docs/SPEC.md` §9, §1

---

## 1. Executive Summary & Verdict

### **Verdict: MAJOR FLAWS**

The pipeline implementation in `src/lhf/pipeline.py` and CLI in `src/lhf/cli.py` pass the existing happy-path acceptance suite (`acceptance/test_t8_pipeline.py`) on the 71 curated sample recipes. Furthermore, **NO cheating, NO hardcoded answers**, and **NO unauthorized numeric literals** were found (all numeric literals in code are strictly within `{0..12, 100, 1000}`, and constant thresholds `SPICE_LINE_MAX_G`, `RECIPE_MASS_MIN_G`, and `RECIPE_MASS_MAX_G` are sourced dynamically from `data/curated/constants.csv`).

However, adversarial stress testing and code analysis uncovered multiple **MAJOR FLAWS** that compromise system stability and scientific integrity:
1. **Unhandled Crashes on Valid Input Shapes (`lines: null` and `servings: "0"`):**
   - If a JSON recipe contains `"lines": null`, `recipe.get("lines", [])` returns `None`, crashing `analyse_recipe` with an uncaught `TypeError: 'NoneType' object is not iterable`.
   - If a recipe specifies `"servings": "0"` (or non-numeric strings), `bool("0")` evaluates to `True`, triggering an unhandled `ZeroDivisionError: float division by zero` during per-serving calculations.
2. **Negative Servings Nutrient Corruption:**
   - If `servings` is negative (e.g., `-2` or `"-2"`), `if not servings:` evaluates to `False`. The engine calculates negative nutrients and negative footprint daily limits with no `NO_SERVINGS` warning.
3. **Scientific Defect: Water Leakage into Food Mass (K505 / Hindi "pani"):**
   - Lines with Hindi/transliterated water (e.g., `"1 cup pani"`) parse as `status: "QUANTIFIED"`, match code `K505` ("Water, distilled"), and are assigned class `WATER` in `data/curated/classes.csv`. Because `pipeline.py` only checks `parsed.status == "WATER"` and never inspects `classes_for(code)`, 240 g of water is marked `included: True`, inflating `included_mass_g` and violating SPEC §0/§9.
4. **False Positive `SALT_UNQUANTIFIED` Warnings via Substring Matching:**
   - An ad-hoc heuristic (`"salt" in name.lower() or "namak" in name.lower()`) flags ingredients like `"salted butter to grease"` or `"salted peanuts"` as unquantified salt lines, generating false `SALT_UNQUANTIFIED` warnings.
5. **Architectural Drift / Code Duplication of `sum_nutrients`:**
   - Rather than calling `lhf.compute.sum_nutrients` (built and validated in T2), `pipeline.py` re-implements nutrient summing inline.
6. **Coverage Defect: Failure to Capture Cooking Fats in `unquantified_fat_lines`:**
   - Common unquantified cooking fat phrases like `"oil for deep frying"`, `"butter for greasing"`, and `"ghee to smear"` fail to match food codes because preparation suffixes are not stripped, silently dropping them from `unquantified_fat_lines`.

---

## 2. Integrity Rules Audit

### Rule 1: No Invented Numbers
- **AST Scan of `src/lhf/pipeline.py`:**
  - Literals detected: `0` (lines 179-183, line 130), `1` (line 189), `0.0` (lines 211, 221, 225).
  - All values belong to the allowed set `{0..12, 100, 1000}`.
- **AST Scan of `src/lhf/cli.py`:**
  - Literals detected: `0` (line 31), `1` (line 28), `2` (lines 22, 30).
  - All values belong to `{0..12, 100, 1000}`.
- **Constants Resolution:**
  - `spice_max = constants.get("SPICE_LINE_MAX_G")` (line 235) -> resolved to 30.0 g.
  - `mass_min = constants.get("RECIPE_MASS_MIN_G")` (line 240) -> resolved to 200.0 g.
  - `mass_max = constants.get("RECIPE_MASS_MAX_G")` (line 241) -> resolved to 5000.0 g.
- **Status:** **PASS**

### Rule 2: No Silent Defaults for Missing Data
- Missing quantities are classified as `UNQUANTIFIED` without guessing defaults (e.g., no default 100 g or 1 tsp).
- Unquantifiable units or missing grams return `UNQUANTIFIABLE` with `grams: None`.
- **Status:** **PASS**

### Rule 3: No Cheating or Hardcoding Test Answers
- Neither `src/lhf/pipeline.py` nor `src/lhf/cli.py` contains hardcoded recipe IDs, gold text strings, or acceptance test conditionals.
- `acceptance/test_rules.py` confirmed 0 occurrences of gold test lines.
- **Status:** **PASS**

### Rule 4: Correct Scientific Behavior & Units
- Nutrient summing across included items properly respects unit weights (edible portion per 100 g scaled by `grams / 100`).
- Saturated fatty acids, sodium, and energy limits strictly follow the baselines and constants architecture.
- **Defects:**
  - Water leakage for `K505` violates water exclusion rules.
  - Negative servings violate non-negativity constraints in dietary science.
- **Status:** **DEFECT / MAJOR FLAW**

---

## 3. Line Inclusion & Exclusion Reasons Waterfall Analysis

SPEC §9 prescribes:
> "A line is included if status is QUANTIFIED, the code is a real composition code, and grams > 0. Otherwise it is excluded with exactly one reason: WATER, UNQUANTIFIED, UNMAPPED, NON_FOOD or UNQUANTIFIABLE."

### Waterfall Evaluation Table

| Case | Parsed Status | Code | Grams | Expected Status / Reason | Implemented Status / Reason | Spec Compliant? |
|---|---|---|---|---|---|---|
| Standard food line | `QUANTIFIED` | `A001` (Rice) | 100.0 | Included (`exclusion_reason: None`) | Included (`exclusion_reason: None`) | YES |
| Water line | `WATER` | N/A | None | Excluded (`WATER`) | Excluded (`WATER`) | YES |
| Unquantified line | `UNQUANTIFIED` | Any | None | Excluded (`UNQUANTIFIED`) | Excluded (`UNQUANTIFIED`) | YES |
| Non-food line | `QUANTIFIED` | `NON_FOOD` | None | Excluded (`NON_FOOD`) | Excluded (`NON_FOOD`) | YES |
| Unmapped ingredient | `QUANTIFIED` | `UNMAPPED` | None | Excluded (`UNMAPPED`) | Excluded (`UNMAPPED`) | YES |
| Code not in composition table | `QUANTIFIED` | `INVALID_CODE`| None | Excluded (`UNMAPPED`) | Excluded (`UNMAPPED`) | YES |
| Unquantifiable unit | `QUANTIFIED` | `G001` | None | Excluded (`UNQUANTIFIABLE`) | Excluded (`UNQUANTIFIABLE`) | YES |
| Zero / Negative grams | `QUANTIFIED` | `G001` | 0.0 or <0 | Excluded (`UNQUANTIFIABLE`) | Excluded (`UNQUANTIFIABLE`) | YES |
| Water in Hindi ("1 cup pani") | `QUANTIFIED` | `K505` | 240.0 | Excluded (`WATER`) | **Included (`None`)** | **NO (LEAK)** |

### Detailed Defect: Water Leakage into Food Mass
In `src/lhf/pipeline.py` (lines 44-57 vs lines 83-162):
```python
        if status == "WATER":
            lines_out.append({ ... "exclusion_reason": "WATER" ... })
        elif status == "QUANTIFIED":
            name = parsed.get("name", "")
            m = match_name(name)
            code = m.get("code")
            ...
            g_res = grams_for(...)
            ...
            lines_out.append({ "included": True, "exclusion_reason": None, ... })
```
If a line like `"1 cup pani"` is passed:
1. `parse_line` returns `status: "QUANTIFIED"`, `name: "pani"`.
2. `match_name("pani")` maps to `K505` ("Water, distilled").
3. `classes_for("K505")` returns `["WATER"]` (per `data/curated/classes.csv`).
4. `pipeline.py` checks `code == "NON_FOOD"` and `code == "UNMAPPED"`. It does **not** check if `"WATER" in classes_for(code)`.
5. It computes 240.0 g and marks `included: True`.
6. `coverage["included_mass_g"]` is incremented by 240.0 g.
This violates the fundamental Phase 1 rule: water must be excluded from recipe mass and nutrient footprints.

---

## 4. Warnings & Sanity Checks Audit

SPEC §9 defines 4 warning categories:
1. `SPICE_OVER_LIMIT`: Any included line whose code has class `SPICE` in `classes.csv` and whose grams exceed `SPICE_LINE_MAX_G`.
2. `MASS_IMPLAUSIBLE`: Included mass outside `RECIPE_MASS_MIN_G` to `RECIPE_MASS_MAX_G`.
3. `NO_SERVINGS`: Servings not specified.
4. `SALT_UNQUANTIFIED`: A salt line that is `UNQUANTIFIED`.

### Audit Findings by Warning Category

#### 1. `SPICE_OVER_LIMIT` (Lines 235-239)
- **Implementation:**
  ```python
  spice_max = constants.get("SPICE_LINE_MAX_G")
  for l in inc_items:
      if "SPICE" in l["classes"] and l["grams"] > spice_max:
          warnings.append(f"SPICE_OVER_LIMIT: line '{l['raw']}' exceeds {spice_max} g ({l['grams']} g)")
  ```
- **Finding:** Correctly verifies class `SPICE` and compares against `SPICE_LINE_MAX_G` (30 g). Multiple excessive lines generate individual warnings.

#### 2. `MASS_IMPLAUSIBLE` (Lines 240-243)
- **Implementation:**
  ```python
  mass_min = constants.get("RECIPE_MASS_MIN_G")
  mass_max = constants.get("RECIPE_MASS_MAX_G")
  if not (mass_min <= included_mass <= mass_max):
      warnings.append(f"MASS_IMPLAUSIBLE: included mass {included_mass} g outside range {mass_min}-{mass_max} g")
  ```
- **Finding:** Correctly applies inclusive range check `[200.0, 5000.0]`. When no lines are included (`included_mass = 0.0`), the warning triggers as expected.

#### 3. `NO_SERVINGS` & Servings Validation (Lines 245-257)
- **Implementation:**
  ```python
  servings = recipe.get("servings")
  if not servings:
      warnings.append("NO_SERVINGS: servings not specified in recipe")
      per_serving = None
      fp = None
  else:
      servings_val = float(servings)
      per_serving = {
          k: (v / servings_val if v is not None and not math.isnan(v) else None)
          for k, v in totals.items()
      }
      fp = footprint(per_serving, setting=setting, risk=risk)
  ```
- **Flaws Identified:**
  - **Fatal Division by Zero:** When `servings = "0"` (string zero), `bool("0")` is `True`. Line 251 sets `servings_val = 0.0`, and line 253 crashes with `ZeroDivisionError: float division by zero`.
  - **Type Conversion Crash:** When `servings = "four"`, line 251 crashes with `ValueError: could not convert string to float: 'four'`.
  - **Negative Servings Corruption:** When `servings = -2`, `bool(-2)` is `True`. Line 251 sets `servings_val = -2.0`, resulting in negative nutrients and negative footprint bars without issuing `NO_SERVINGS`.

#### 4. `SALT_UNQUANTIFIED` (Lines 67-68, 258-259)
- **Implementation:**
  ```python
  if "SALT" in unq_classes or "salt" in name.lower() or "namak" in name.lower():
      has_unquantified_salt = True
  ```
- **Flaw Identified (False Positives):**
  - Checking `or "salt" in name.lower()` triggers false positive warnings on ingredients that contain "salt" as a substring or preparation descriptor, e.g.:
    - `"salted butter to grease"` -> flagged as `SALT_UNQUANTIFIED`.
    - `"salted peanuts to serve"` -> flagged as `SALT_UNQUANTIFIED`.
  - Under SPEC §9, the rule states *"a salt line that is UNQUANTIFIED"*. The cited definition of a salt line is an item matching class `SALT` (codes `G528` and `G540` in `data/curated/classes.csv`). The crude substring matching creates unwarranted warnings.

---

## 5. Coverage & Reconciliation Audit

### Structure and Reconciliation
- `coverage` output matches SPEC §9:
  ```json
  {
    "lines_total": 5,
    "lines_included": 1,
    "excluded_by_reason": {
      "WATER": 1,
      "UNQUANTIFIED": 1,
      "UNMAPPED": 1,
      "NON_FOOD": 1,
      "UNQUANTIFIABLE": 0
    },
    "included_mass_g": 30.0,
    "unquantified_fat_lines": []
  }
  ```
- Reconciliation check:
  $$\sum \text{excluded\_by\_reason} = \text{lines\_total} - \text{lines\_included}$$
  This equality holds across all test cases.

### Flaw in `unquantified_fat_lines`
SPEC §9 requires:
> `"unquantified_fat_lines":[raw lines of UNQUANTIFIED lines whose name matches a COOKING_OIL/DAIRY_FAT/HYDROGENATED_FAT code]`

In `pipeline.py` (lines 60-65):
```python
name = parsed.get("name", "")
unq_m = match_name(name)
unq_code = unq_m.get("code")
unq_classes = classes_for(unq_code) if unq_code and unq_code not in ("UNMAPPED", "NON_FOOD") else []
if any(c in ("COOKING_OIL", "DAIRY_FAT", "HYDROGENATED_FAT") for c in unq_classes):
    unquantified_fat_lines.append(raw)
```
When real recipe lines have preparation phrases attached to unquantified fats:
- `"oil for deep frying"` -> `parsed["name"]` is `'oil for deep frying'`.
- `"butter for greasing"` -> `parsed["name"]` is `'butter for greasing'`.
- `"ghee to smear"` -> `parsed["name"]` is `'ghee to smear'`.
Because `match_name` cannot match these strings (returns `UNMAPPED`), `unq_classes` is empty, and the line is **omitted** from `unquantified_fat_lines`. This distorts fat coverage tracking.

---

## 6. CLI Robustness & Error Handling Audit

SPEC §9 requires:
> "`lhf/cli.py`: `PYTHONPATH=src python -m lhf.cli RECIPE.json [--setting urban|rural] [--risk general|cardiometabolic]` prints the JSON to stdout and exits 0. It exits 2 with a message on stderr for an unreadable file."

### CLI Testing Matrix

| Scenario | Command | Expected Exit | Actual Exit | Stderr Message | Spec Compliant? |
|---|---|---|---|---|---|
| Valid recipe JSON | `python -m lhf.cli valid.json` | 0 | 0 | Empty | YES |
| Setting rural / Risk cardio | `python -m lhf.cli valid.json --setting rural --risk cardiometabolic` | 0 | 0 | Empty | YES |
| Missing file | `python -m lhf.cli missing.json` | 2 | 2 | `Error: unable to read recipe file 'missing.json': [Errno 2] ...` | YES |
| Invalid JSON syntax | `python -m lhf.cli malformed.json` | 2 | 2 | `Error: unable to read recipe file '...': Expecting ...` | YES |
| Invalid setting argument | `python -m lhf.cli valid.json --setting invalid` | 2 | 2 | `usage: cli.py ... invalid choice` | YES |
| Internal crash (`lines: null`) | `python -m lhf.cli null_lines.json` | 1 | 1 | `Error analysing recipe: 'NoneType' object is not iterable` | DEFECT |
| Internal crash (`servings: "0"`) | `python -m lhf.cli zero_serv.json` | 1 | 1 | `Error analysing recipe: float division by zero` | DEFECT |

The CLI correctly adheres to the exit code 0 / exit code 2 contract for file I/O errors and argument parsing. The failures on exit code 1 stem from unhandled input validation bugs in `pipeline.py`.

---

## 7. Adversarial Stress Probes & Failure Modes

The following test script demonstrates each defect identified:

```python
from lhf.pipeline import analyse_recipe
import json

# Probe 1: Servings Edge Cases
for s in [0, "0", -2, "-2", "four", None]:
    try:
        r = {"id": "TEST", "dish": "test", "servings": s, "lines": ["100 g rice"]}
        res = analyse_recipe(r)
        ps_energy = res["per_serving"]["energy_kcal"] if res["per_serving"] else None
        print(f"servings={s!r:6} -> OK: per_serving={ps_energy}, warnings={res['warnings']}")
    except Exception as e:
        print(f"servings={s!r:6} -> CRASH: {type(e).__name__}: {e}")

# Probe 2: lines: null Edge Case
try:
    r = {"id": "TEST", "dish": "test", "servings": 2, "lines": None}
    res = analyse_recipe(r)
    print("lines=None -> OK")
except Exception as e:
    print(f"lines=None -> CRASH: {type(e).__name__}: {e}")

# Probe 3: Salt False Positive Warnings
for line in ["salted butter to grease", "salted peanuts to serve", "1 pinch salt"]:
    r = {"id": "TEST", "dish": "test", "servings": 2, "lines": [line]}
    res = analyse_recipe(r)
    print(f"line={line!r:28} -> warnings={res['warnings']}")

# Probe 4: Water Leak via K505
for line in ["1 cup water", "1 cup pani"]:
    r = {"id": "TEST", "dish": "test", "servings": 2, "lines": [line]}
    res = analyse_recipe(r)
    l0 = res["lines"][0]
    print(f"line={line!r:15} -> included={l0['included']}, reason={l0['exclusion_reason']}, mass={res['coverage']['included_mass_g']}")
```

### Probe Execution Output

```
servings=0      -> OK: per_serving=None, warnings=['MASS_IMPLAUSIBLE: included mass 100.0 g outside range 200.0-5000.0 g', 'NO_SERVINGS: servings not specified in recipe']
servings='0'    -> CRASH: ZeroDivisionError: float division by zero
servings=-2     -> OK: per_serving=-175.7887189292543, warnings=['MASS_IMPLAUSIBLE: included mass 100.0 g outside range 200.0-5000.0 g']
servings='-2'   -> OK: per_serving=-175.7887189292543, warnings=['MASS_IMPLAUSIBLE: included mass 100.0 g outside range 200.0-5000.0 g']
servings='four' -> CRASH: ValueError: could not convert string to float: 'four'
servings=None   -> OK: per_serving=None, warnings=['MASS_IMPLAUSIBLE: included mass 100.0 g outside range 200.0-5000.0 g', 'NO_SERVINGS: servings not specified in recipe']

lines=None -> CRASH: TypeError: 'NoneType' object is not iterable

line='salted butter to grease'    -> warnings=['MASS_IMPLAUSIBLE: included mass 0 g outside range 200.0-5000.0 g', 'SALT_UNQUANTIFIED: recipe contains unquantified salt line (sodium is a lower bound)']
line='salted peanuts to serve'    -> warnings=['MASS_IMPLAUSIBLE: included mass 0 g outside range 200.0-5000.0 g', 'SALT_UNQUANTIFIED: recipe contains unquantified salt line (sodium is a lower bound)']
line='1 pinch salt'               -> warnings=['MASS_IMPLAUSIBLE: included mass 1.5 g outside range 200.0-5000.0 g']

line='1 cup water'   -> included=False, reason=WATER, mass=0.0
line='1 cup pani'    -> included=True, reason=None, mass=240.0
```

---

## 8. Line-by-Line Code Citations & Root Causes

1. **`src/lhf/pipeline.py:32`**:
   ```python
   lines_raw = recipe.get("lines", [])
   ```
   *Root Cause:* When key `"lines"` exists in dictionary with value `None`, `.get("lines", [])` returns `None`. Must use `recipe.get("lines") or []`.

2. **`src/lhf/pipeline.py:246-253`**:
   ```python
   servings = recipe.get("servings")
   if not servings:
       warnings.append("NO_SERVINGS: servings not specified in recipe")
       per_serving = None
       fp = None
   else:
       servings_val = float(servings)
       per_serving = {
           k: (v / servings_val if v is not None and not math.isnan(v) else None)
           for k, v in totals.items()
       }
   ```
   *Root Cause:* Truthiness check `if not servings:` does not validate non-zero numeric values. `float("0")` causes `ZeroDivisionError`, `float("four")` raises `ValueError`, and `-2` bypasses checks to generate negative nutrition.

3. **`src/lhf/pipeline.py:67`**:
   ```python
   if "SALT" in unq_classes or "salt" in name.lower() or "namak" in name.lower():
       has_unquantified_salt = True
   ```
   *Root Cause:* Heuristic substring match flags any food with "salt" in the name (e.g., "salted butter", "salted cashews"). Must restrict to `"SALT" in unq_classes`.

4. **`src/lhf/pipeline.py:128-144`**:
   ```python
   c_list = classes_for(code)
   if g is None or g <= 0:
       ...
   else:
       ...
       lines_out.append(line_dict)
       inc_items.append(line_dict)
   ```
   *Root Cause:* Missing check for `if "WATER" in c_list:` or `code == "K505"`. Any water item that escapes parser regex gets treated as quantifiable food.

---

## 9. Recommendations for Remediation

1. **Robust Servings Parsing & Validation:**
   Replace lines 245-256 with:
   ```python
   servings = recipe.get("servings")
   servings_val = None
   if servings is not None:
       try:
           s_num = float(servings)
           if s_num > 0:
               servings_val = s_num
       except (ValueError, TypeError):
           servings_val = None

   if servings_val is None:
       warnings.append("NO_SERVINGS: servings not specified in recipe")
       per_serving = None
       fp = None
   else:
       per_serving = {
           k: (v / servings_val if v is not None and not math.isnan(v) else None)
           for k, v in totals.items()
       }
       fp = footprint(per_serving, setting=setting, risk=risk)
   ```

2. **Defensive Line Iteration:**
   Change line 32 to:
   ```python
   lines_raw = recipe.get("lines") or []
   ```

3. **Exclude Matched Water Items:**
   In the quantified line processing block, check if matched code is water:
   ```python
   c_list = classes_for(code)
   if "WATER" in c_list or code == "K505":
       lines_out.append({
           "index": idx,
           "raw": raw,
           "parsed": parsed,
           "match": m,
           "grams": None,
           "grams_basis": None,
           "grams_flags": [],
           "included": False,
           "exclusion_reason": "WATER",
           "classes": c_list,
           "nutrients": None,
       })
   elif g is None or g <= 0:
       ...
   ```

4. **Principled Salt Warning:**
   Remove naive substring matching on line 67:
   ```python
   if "SALT" in unq_classes:
       has_unquantified_salt = True
   ```

5. **Reuse `lhf.compute.sum_nutrients`:**
   Refactor lines 201-226 to delegate nutrient calculation to `lhf.compute.sum_nutrients(inc_items)` to eliminate code duplication and adhere to package modularity.
