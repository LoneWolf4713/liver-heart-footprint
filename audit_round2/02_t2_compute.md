# Round 2 Adversarial Audit Report: Task T2 (Nutrient Summing & INDB Reproduction)

**Audit Target:** Task T2 — Nutrient Summing and INDB Dish Reproduction (`lhf.compute`)  
**Auditor:** Auditor 2 — Round 2 Adversarial Red Team Auditor  
**Date:** 2026-11-11  
**Operating Principle:** GUILTY UNTIL PROVEN INNOCENT  
**Target Files Scrutinized:**
- `src/lhf/compute.py`
- `acceptance/test_t2_indb.py`
- `tests/test_t2.py`
- `src/lhf/composition.py`
- `data/curated/` (`constants.csv`, `indian_products.csv`)
- `docs/SPEC.md` §3, §2, §1
- `AGENTS.md` (Integrity Rules 1–6)

---

## 1. Executive Summary & Verdict

### **Verdict: CLEAN**

Following rigorous adversarial stress testing, negative fuzzing, AST analysis, floating-point boundary checks, and regression verification against Round 1 findings, Task T2 (`lhf.compute`) is rated **CLEAN**.

The defects and vulnerabilities identified in Round 1—specifically the zero-gram NaN contamination bug (DEF-B9), the negative mass asymmetry bug, and under-assertive unit tests—have been **fully and correctly remediated**. 

Key highlights of the audited implementation:
1. **Zero / Negative / NaN Mass Defense (DEF-B9 Remediated):** `sum_nutrients` strictly checks `math.isnan(grams_val) or not math.isfinite(grams_val) or grams_val <= 0`. Zero-gram and negative-gram items are routed immediately to `skipped` and can never contaminate recipe totals or erroneously flag `unknown_water_items` or `unknown_tfa_items` with `NaN`.
2. **Mathematical Soundness & Division-by-Zero Protection:** All per-100g calculations are guarded by `elif total_g > 0: val / total_g * 100` with an explicit `0.0` fallback, mathematically preventing any `ZeroDivisionError` on empty or all-skipped recipes.
3. **AST Rule 1 Compliance:** The source code in `src/lhf/compute.py` contains only numeric literals `0.0`, `0`, and `100` (all within the permitted set `{0..12, 100, 1000}`). No magic numbers or ungrounded values exist.
4. **Zero Test Gaming / Full INDB Reproduction:** The module reproduces 995 real recipes from the Indian Nutrient Database (INDB) with 100.0% agreement across 7 key macro/micronutrients and 97.5% on carbohydrates (surpassing the 95% threshold necessitated by INDB's published retention factors). No dish codes, expected sums, or cheat tables exist in the codebase.

---

## 2. Rigorous Answers to Mandated Audit Questions

### Question 1: Input Type Robustness
**Does `sum_nutrients` cleanly handle empty lists, None items, non-dict elements, generator inputs, and malformed inputs?**

- **Implementation Analysis:**
  Lines 22–45 of `src/lhf/compute.py`:
  ```python
  if items is not None:
      for idx, item in enumerate(items):
          if not isinstance(item, dict):
              skipped.append(idx)
              continue

          code = item.get("code")
          code_str = str(code) if code is not None else ""
          grams = item.get("grams")

          if grams is None or isinstance(grams, bool):
              skipped.append(idx)
              continue

          try:
              grams_val = float(grams)
          except (ValueError, TypeError):
              skipped.append(idx)
              continue

          if math.isnan(grams_val) or not math.isfinite(grams_val) or grams_val <= 0 or code is None or code_str not in table_index:
              skipped.append(idx)
              continue
  ```
- **Adversarial Test Findings:**
  1. **Empty Sequences:**
     - `items = []`: Returns `total_g = 0.0`, all nutrient totals `0.0`, all per-100g `0.0`, `skipped = []`, `unknown_tfa_items = []`, `unknown_water_items = []`.
     - `items = None`: Safely bypasses iteration; returns clean zero-state dict.
     - `items = ()`: Evaluates identically to `[]`.
     - `items = (x for x in [])`: Generator input evaluates cleanly to empty result.
  2. **Non-Dict Elements in List:**
     - Tested `items = [None, 123, "string", [], {}]`.
     - For each non-dict element, `not isinstance(item, dict)` triggers; index is appended to `skipped` and iteration immediately continues.
     - For `{}` (empty dict), `.get("code")` and `.get("grams")` return `None`, correctly appending index to `skipped`.
  3. **Generators & Iterables:**
     - Tested generator expressions: `sum_nutrients(item for item in [item1, item2])`.
     - `enumerate(items)` consumes generator streams with identical numerical precision and skip-index tracking as in-memory lists.
  4. **Malformed Item Dictionaries:**
     - Missing `"grams"`: `grams is None` -> skipped.
     - Missing `"code"`: `code is None` -> skipped.
     - Non-numeric `"grams"` (e.g. `"not_a_number"`, `[100]`, `{}`): `except (ValueError, TypeError)` -> skipped.
     - Python Boolean Trap: In Python, `isinstance(True, int)` is `True` and `float(True) == 1.0`. The code explicitly defends with `if grams is None or isinstance(grams, bool): skipped.append(idx); continue`. Both `True` and `False` are rejected.
     - Unknown / Invalid Codes: Strings not present in `table_index` (including empty string `""`, whitespace `" A019 "`, lowercase `"a019"`, and non-existent codes) trigger `code_str not in table_index` and are cleanly skipped.
- **Verdict:** **PASS (Exceptionally Robust)**.

---

### Question 2: Zero, Negative, NaN, and Infinite Grams (Contamination Defense)
**How does `sum_nutrients` handle items with zero grams, negative grams, NaN grams, or infinity? Can zero-gram items poison totals with NaN (especially for water_g or tfa_g)?**

- **Detailed Analysis of DEF-B9 Fix:**
  In Round 1, an item with `grams = 0.0` for a food with missing water/tfa (such as UK sunflower oil `T508`) would compute `nan * 0.0 = nan` in IEEE 754, poisoning the recipe total `water_g` as `NaN`.
  In the current implementation (Line 42):
  ```python
  if math.isnan(grams_val) or not math.isfinite(grams_val) or grams_val <= 0 or code is None or code_str not in table_index:
      skipped.append(idx)
      continue
  ```
- **Adversarial Probe Suite Results:**
  We executed probes across a variety of pathological numeric values alongside code `T508` (which has `water_g = NaN` and `tfa_g = NaN`):
  | Test Case Item | Input `grams` | Code Under Test | Behavior in `sum_nutrients` | Total Water NaN? |
  |---|---|---|---|---|
  | Zero float | `0.0` | `T508` | Skipped (`idx` in `skipped`); `nutrients_for` not called | **No (Isolated)** |
  | Zero int | `0` | `T508` | Skipped (`idx` in `skipped`); `nutrients_for` not called | **No (Isolated)** |
  | Negative float | `-10.0` | `T508` | Skipped (`grams_val <= 0`) | **No (Isolated)** |
  | Negative zero | `-0.0` | `T508` | Skipped (`-0.0 <= 0` is True) | **No (Isolated)** |
  | IEEE NaN | `float("nan")` | `T508` | Skipped (`math.isnan(grams_val)`) | **No (Isolated)** |
  | Positive Infinity | `float("inf")` | `T508` | Skipped (`not math.isfinite(grams_val)`) | **No (Isolated)** |
  | Negative Infinity | `float("-inf")` | `T508` | Skipped (`not math.isfinite(grams_val)`) | **No (Isolated)** |
  | Valid Positive Mass | `10.0` | `T508` | Included; `idx` added to `unknown_water_items` & `unknown_tfa_items` | **Yes (Properly Propagated)** |

- **Isolation Verification:**
  When a recipe contains `[{"code": "A019", "grams": 100.0}, {"code": "T508", "grams": 0.0}]`:
  - `total_g = 100.0`
  - `skipped = [1]`
  - `unknown_water_items = []`
  - `unknown_tfa_items = []`
  - `totals["water_g"] = 11.1` (NOT NaN)
  - `per_100g["water_g"] = 11.1` (NOT NaN)
  Zero-gram and non-positive items are 100% prevented from poisoning nutrient totals.
- **Verdict:** **PASS (DEF-B9 Verified Completely Resolved)**.

---

### Question 3: Mathematical Soundness & Division-by-Zero Defense
**Are the per-100g calculations mathematically sound and protected against division by zero?**

- **Formula & Scale Factor Verification:**
  Lines 66–75 of `src/lhf/compute.py`:
  ```python
  per_100g = {}
  for k in NUTRIENTS:
      val = totals[k]
      if math.isnan(val):
          per_100g[k] = float("nan")
      elif total_g > 0:
          per_100g[k] = val / total_g * 100
      else:
          per_100g[k] = 0.0
  ```
- **Mathematical Invariant Verification:**
  1. **Scaling Formula:** For any nutrient $N$ with mass $v_i = \text{table}[N]_i \times \frac{g_i}{100}$:
     $$\text{totals}[N] = \sum_i v_i$$
     $$\text{per\_100g}[N] = \frac{\text{totals}[N]}{\text{total\_g}} \times 100 = \frac{\sum_i (\text{table}[N]_i \cdot g_i)}{\sum_i g_i}$$
     This is the exact mass-weighted average nutrient density.
  2. **Zero Mass Fallback:** If `total_g == 0.0` (such as empty inputs or where all ingredients are skipped), `total_g > 0` evaluates to `False`. The code executes `per_100g[k] = 0.0`, eliminating any possibility of `ZeroDivisionError`.
  3. **Linear Consistency between kJ and kcal:**
     We probed whether $\text{totals}[\text{energy\_kcal}] = \text{totals}[\text{energy\_kj}] / \text{KJ\_PER\_KCAL}$.
     Over multi-ingredient recipes, the difference was $1.13 \times 10^{-13}$, verifying machine-precision linearity.
  4. **Subnormal & Extreme Magnitudes:**
     - Micro-masses ($10^{-300}\text{ g}$): `per_100g` scales stably without precision loss.
     - Extreme masses ($10^{300}\text{ g}$): Correctly computed without overflow.
- **Verdict:** **PASS (Mathematically Sound)**.

---

### Question 4: AST Rule 1 Numeric Literal Integrity
**Are numeric literals in `src/lhf/compute.py` strictly compliant with AST Rule 1 ({0..12, 100, 1000})?**

- **Abstract Syntax Tree Audit:**
  We parsed `src/lhf/compute.py` into an AST and scanned every `ast.Constant` node where `isinstance(node.value, (int, float))` and not `bool`:
  ```python
  # All Numeric Literals in src/lhf/compute.py:
  Line 16: Constant(value=0.0)    # total_g = 0.0
  Line 17: Constant(value=0.0)    # totals = {k: 0.0 ...}
  Line 42: Constant(value=0)      # grams_val <= 0
  Line 71: Constant(value=0)      # elif total_g > 0:
  Line 72: Constant(value=100)    # val / total_g * 100
  Line 74: Constant(value=0.0)    # per_100g[k] = 0.0
  ```
- **Compliance Matrix:**
  - Allowed set: $\{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 100, 1000\}$
  - Literals present in file: $\{0.0, 0, 100\}$
  - Disallowed literals: **None (0 violations)**.
  - Acceptance Check: Verified with `acceptance/test_rules.py`:
    `scanned 12 source file(s) -> PASS rules`.
- **Verdict:** **PASS (100% Compliant)**.

---

### Question 5: INDB Reproduction & Anti-Gaming Audit
**Does the code game or bypass the INDB 1,014 dish reproduction test?**

- **Harness & Source Code Scrutiny:**
  - `src/lhf/compute.py` does not import `pandas`, `_common`, `acceptance`, `os`, or any fixture files.
  - No recipe IDs, dish names, or expected totals appear anywhere in `compute.py` or `composition.py`.
  - `sum_nutrients` operates purely on the provided `items` argument; it does not receive or know the recipe code.
- **Reproduction Benchmark Results (`acceptance/test_t2_indb.py`):**
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
- **Analysis of Carbohydrate Agreement (97.5%):**
  - All 7 other tested macro/micronutrients match published values with 100.0% exactness.
  - Carbohydrates diverge slightly (by 0.05–0.4g/100g) in 25 out of 995 dishes (e.g. `ASC251`, `ASC264`, `BFP026`).
  - As confirmed by inspection of `data/raw/indb/INDB.do` (line 651: `label var carb_g "Total carbohydrates (g) per 100g (with retention factor)"`), INDB applied Stata nutrient retention factors to certain cooked carbohydrate sources. The architect explicitly codified a 95% threshold for `carb_g` to accommodate this known source dataset characteristic.
  - The implementation passes without any artificial adjustments or hardcoded compensations.
- **Verdict:** **PASS (Genuine, Ungamed Reproduction)**.

---

## 3. Regression Tracking Against Round 1 Audit Findings

| Finding from Round 1 | Severity | Round 2 Verification | Current Status |
|---|---|---|---|
| **DEF-B9: Zero-gram items with unknown water/tfa contaminate recipe totals** | Minor | Line 42 now filters `grams_val <= 0` and appends to `skipped`. Probed with `T508` at `0.0g`: recipe water total remains finite and correct. | **RESOLVED** |
| **Negative mass asymmetry** (`total_g < 0` produces `per_100g = 0.0` while `totals < 0`) | Minor | Line 42 filters `grams_val <= 0`. Negative gram inputs are treated as invalid/skipped and excluded from both `total_g` and `totals`. | **RESOLVED** |
| **Incomplete unit test suite in `tests/test_t2.py`** | Code Health | `tests/test_t2.py` expanded from 38 lines to 137 lines across 8 test methods, covering all 13 nutrient columns, DEF-B9 isolation, generator inputs, and NaN order independence. | **RESOLVED** |
| **Spec Discrepancy (12 vs 13 nutrient columns)** | Documentation | SPEC §3 text says "12", but SPEC §2 and `composition.NUTRIENT_COLUMNS` define 13. `compute.py` uses all 13. Downstream pipelines depend on all 13 (including `energy_kcal`). | **DOCUMENTED / NON-BLOCKING** |

---

## 4. Minor Residual API Observations (Non-Defects)

During adversarial probing, one minor API edge case was noted:
1. **Passing a Single Dictionary Instead of a List:**
   If a caller erroneously passes a single dictionary `item = {"code": "A019", "grams": 100}` instead of `[{"code": "A019", "grams": 100}]`, `enumerate(item)` iterates over the dictionary keys (`"code"`, `"grams"`). Since string keys are not dictionaries, the loop executes lines 24–26:
   ```python
   if not isinstance(item, dict):
       skipped.append(idx)
       continue
   ```
   This returns `{"total_g": 0.0, "skipped": [0, 1], ...}` rather than raising a `TypeError`. While this is benign and adheres to duck-typing, callers should be mindful that `sum_nutrients` expects a sequence of dictionaries.
2. **DataFrame Copying Overhead in High-Throughput Scenarios:**
   `table = composition.load_table()` in line 13 calls `load_table()`, which performs `_get_table().copy()`. Because `sum_nutrients` only reads `table.index`, copying the 746-row DataFrame on every call adds ~100 µs of overhead. Even with this copy, summing 10,000 items takes only 1.8 seconds.

---

## 5. Final Audit Conclusion

The `lhf.compute` module in `src/lhf/compute.py` is **exceptionally clean, rigorous, mathematically correct, and fully compliant with all architectural integrity constraints**. 

No further code modifications are required for Task T2.
