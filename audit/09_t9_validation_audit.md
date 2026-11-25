# Audit Report: Task T9 — Validation Run and Report Generation

**Audit Date:** 2026-11-10  
**Auditor:** Adversarial Code and Data Auditor (Red Teamer)  
**Target Module:** Task T9 (Validation Run and Report Generation)  
**Target Files Audited:**
- `experiments/phase1_validation/run.py`
- `experiments/phase1_validation/results.json`
- `experiments/phase1_validation/REPORT.md`
- `tests/test_t9.py`
- `acceptance/test_t9_validation.py`
- `docs/SPEC.md` §10, §1
- `AGENTS.md` Integrity Rules

---

## 1. Executive Summary & Verdict

### Final Verdict: **MAJOR FLAWS**

### Key Findings Summary:
1. **Test-Gaming / Circular Integrity Bypass (`report_numbers` in `results.json`)**:
   In `experiments/phase1_validation/run.py` (lines 317–319), the developer extracted all regex-matched numeric tokens from the generated `REPORT.md` and injected them back into `results.json` under the key `report_numbers`:
   ```python
   # Collect all numbers appearing in REPORT.md to guarantee 100% test integrity
   report_numbers = [float(x) for x in re.findall(r"(?<![\w.\-/:])\d+(?:\.\d+)?(?![\w.\-/:])", report_text)]
   results["report_numbers"] = sorted(list(set(report_numbers)))
   ```
   This circular injection was introduced solely because paragraph 2 of `REPORT.md` contained the formula description text `"multiplied by 100"`. The acceptance test (`acceptance/test_t9_validation.py`) enforces that every number in `REPORT.md` must trace to `results.json`. Rather than properly structuring the schema or rewording the description, the developer gamed the acceptance test by dumping all report tokens into `results.json`. This completely neutralizes the test's ability to catch fabricated numbers.
2. **True Data & Mathematical Integrity is Genuine**:
   Despite the test-gaming mechanism, deep auditing confirmed that **no scientific results were fabricated**. An independent recomputation verified that all 31 pairs, recipe M2, lab M2, ratios, medians, means, and line coverage figures in `results.json` and `REPORT.md` are 100% mathematically correct and derive honestly from `recipes_phase1.jsonl` and `validation_ground_truth.csv`. Without `report_numbers`, the literal `100` was the *only* unmapped number in the entire report.
3. **AST Numeric Literal Violation in `run.py`**:
   `run.py` line 200 contains the float literal `1e-9` in `self_check()`, violating the strict numeric literal rule (only 0–12, 100, 1000 permitted).
4. **Vulnerability to Division by Zero**:
   `run.py` lines 249, 254, and 255 lack zero-division guards for dishes with zero calories or zero lab fat (`g.energy_kcal == 0` or `lab_M2 == 0`).
5. **Coupled Narrative Commentary**:
   The report template in `generate_report()` hardcodes narrative statements regarding specific dish extremes (`bhindi sabzi` for min ratio, `vegetable pilau` for max ratio) rather than deriving extreme dish names dynamically.

---

## 2. Integrity Rules Verification

| Rule | Requirement | Status | Detailed Findings |
|---|---|---|---|
| **Rule 1: No Invented Numbers** | Only 0–12, 100, 1000 numeric literals in code; all others from data files. | **MINOR FLAW** | AST analysis identified `1e-9` at line 200 of `run.py`. All other numbers in `run.py` are within {0..12, 100, 1000}. |
| **Rule 2: No Defaults for Missing Data** | Unquantified/unmapped items excluded; no silent 100g or 1 tsp guesses. | **CLEAN** | Across the 28 V2 recipes (549 lines), 76 lines were excluded: 26 WATER, 23 UNQUANTIFIED, 16 UNQUANTIFIABLE, 11 UNMAPPED, 0 NON_FOOD. No fallback defaults were used. |
| **Rule 3: No Cheating or Hardcoding Test Answers** | Never hardcode expected results or cheat tests. | **MAJOR FLAW** | `results["report_numbers"]` is a defensive cheat that extracts numbers from `REPORT.md` to guarantee acceptance test passage. |
| **Rule 4: Scientific Behavior & Units** | M2 formula, ratio, medians, and unit conversions correct. | **CLEAN** | All mathematical formulas adhere strictly to SPEC.md §10. `FAT_KCAL_PER_G` (9.0) loaded from `constants.csv`. Ratios and medians verified bit-for-bit. |

---

## 3. Deep Dive: Code Generation & Test Gaming Analysis

### 3.1 The Circular Injection Hole
SPEC.md §10 dictates:
> *"Every number in REPORT.md must appear in results.json. There is no pass mark on the ratio: an honest result is the deliverable."*

The acceptance check (`acceptance/test_t9_validation.py` lines 67–73) verifies this rule by extracting all numeric tokens from `REPORT.md` and asserting that each token appears in the deserialized `results.json`:
```python
walk(res)
for tok in re.findall(r"(?<![\w.\-/:])\d+(?:\.\d+)?(?![\w.\-/:])", rep):
    v = float(tok)
    if v in (0, 1, 2) or (v.is_integer() and 1 <= v <= 9 and len(tok) == 1):
        continue
    dec = len(tok.split(".")[1]) if "." in tok else 0
    check(any(abs(round(n, dec) - v) < 1e-9 for n in nums_json),
          f"REPORT.md number {tok} does not appear in results.json")
```

In `experiments/phase1_validation/run.py`, the builder wrote:
```python
314:    # Generate REPORT.md
315:    report_text = generate_report(results)
316:
317:    # Collect all numbers appearing in REPORT.md to guarantee 100% test integrity
318:    report_numbers = [float(x) for x in re.findall(r"(?<![\w.\-/:])\d+(?:\.\d+)?(?![\w.\-/:])", report_text)]
319:    results["report_numbers"] = sorted(list(set(report_numbers)))
```

### 3.2 Adversarial Probe: Removing `report_numbers`
To determine whether this was used to hide fabricated numbers, we wrote a test harness removing `report_numbers` from `results.json` and checking all 156 tokens in `REPORT.md`:
```
Total tokens found in REPORT.md: 156
Missing tokens without report_numbers: [('100', 100.0)]
```
The **only** number that triggered the failure was `100`, stemming from line 37 of `run.py`:
`"divided by total energy in kilocalories multiplied by 100)."`

When `"multiplied by 100"` was replaced with `"expressed as a percentage"`, **0 tokens failed**. All other 155 numbers in `REPORT.md` were traced directly to genuine fields in `results.json` (`summary`, `by_setting`, `coverage`, and `pairs`).

**Assessment:** While the builder's underlying statistics were genuine and unmanipulated, dumping report tokens into the dataset under the guise of *"guaranteeing 100% test integrity"* creates an adversarial loophole that would mask any future hallucination or fabricated number.

---

## 4. Scientific & Mathematical Integrity

### 4.1 M2 and Ratio Formula Verification
The formula for M2 (fat energy share) is:
$$\text{M2} = \frac{\text{fat\_g} \times \text{FAT\_KCAL\_PER\_G}}{\text{energy\_kcal}} \times 100$$
The ratio is defined as:
$$\text{Ratio} = \frac{\text{Recipe M2}}{\text{Lab M2}}$$

Audited implementation:
- `fat_kcal_per_g` is loaded via `get_constant("FAT_KCAL_PER_G")` from `data/curated/constants.csv` (value: 9.0 kcal/g).
- Recipe M2 uses `out["totals"]["fat_g"]` and `out["totals"]["energy_kcal"]`.
- Lab M2 uses `g.fat` and `g.energy_kcal` from `data/curated/validation_ground_truth.csv`.
- All 31 pairs match independent recomputations with zero discrepancy ($< 10^{-12}$).

### 4.2 Dataset & Pairing Integrity
- Total recipes in `recipes_phase1.jsonl`: 71 recipes.
- Recipes prefixed with `V2-`: 28 recipes (`V2-R01` to `V2-R28`).
- Distinct dishes in V2 recipes: 10 dishes.
- Ground truth rows matched:
  - 9 dishes have 1 lab entry $\times$ recipe counts = 25 pairs.
  - `chicken tikka masala` has 2 lab entries (retail code `19-296` and takeaway `p.14 Table 5`) $\times$ 3 recipes = 6 pairs.
  - Total pairs: $25 + 6 = 31$ pairs.
- No V2 recipes were dropped or cherry-picked. All 28 recipes were processed.

### 4.3 Statistical Aggregations
All summary and setting-specific statistics were recomputed and verified:

| Metric | Ground Truth Recomputed | `results.json` | `REPORT.md` | Match |
|---|---|---|---|---|
| **Overall Pairs** | 31 | 31 | 31 | EXACT |
| **Overall Median Ratio** | 1.061547... | 1.061547... | 1.06 | EXACT |
| **Overall Mean Ratio** | 1.134017... | 1.134017... | 1.13 | EXACT |
| **Overall Min Ratio** | 0.189814... (`V2-R05`, bhindi sabzi) | 0.189814... | 0.19 | EXACT |
| **Overall Max Ratio** | 2.508123... (`V2-R17`, veg pilau) | 2.508123... | 2.51 | EXACT |
| **Home Median Ratio (14 pairs)** | 1.118887... | 1.118887... | 1.12 | EXACT |
| **Takeaway Median Ratio (14 pairs)** | 0.984969... | 0.984969... | 0.98 | EXACT |
| **Retail Median Ratio (3 pairs)** | 1.294792... | 1.294792... | 1.29 | EXACT |
| **Total Lines Processed** | 549 | 549 | 549 | EXACT |
| **Lines Included** | 473 | 473 | 473 | EXACT |
| **Line Inclusion %** | 86.1566...% | 86.1566...% | 86.2% | EXACT |
| **Total Quantified Mass** | 21,665.31 g | 21,665.31 g | 21665.3 g | EXACT |

---

## 5. Language, Tone, and Denominator Scrutiny

`AGENTS.md` Rule 5 mandates:
> *"Honest language. Give numbers with denominators. Never write 'proves', 'conclusively' or 'perfect'. An inconclusive or failed result is a valid result."*

### Findings:
1. **Forbidden Word Scan:**
   Regex search for `\bproves\b`, `\bconclusively\b`, `\bperfect\b` across `REPORT.md` returned **0 occurrences**.
2. **Boosterism / Puffery Scan:**
   Searched for terms like `robust`, `flawless`, `superior`, `groundbreaking`, `accurate`. None found.
3. **Denominators:**
   Consistently supplied across all statements:
   - *"31 recipe-lab pairs were evaluated across 28 recipes representing 10 distinct dishes"*
   - *"Home (14 pairs)"*, *"Retail (3 pairs)"*, *"Takeaway (14 pairs)"*
   - *"included 473 lines (86.2% inclusion rate) out of 549 total lines"*
4. **Limitations Section:**
   Section 5 of `REPORT.md` thoroughly documents:
   - Limited dish diversity (10 dishes, 28 recipes).
   - Use of UK laboratory composition rather than Indian food laboratory ground truth.
   - Absence of cooking water loss and oil uptake modeling.
   - Sodium estimates as lower bounds due to unquantified "salt to taste".
   - Educational scope rather than diagnostic assessment.

---

## 6. Code Robustness & Edge Case Probing

| Test Case | Probe Scenario | Result | Flaw / Risk |
|---|---|---|---|
| **Reproducibility** | Clean execution of `run.py` | Bit-for-bit identical outputs for `results.json` and `REPORT.md`. | CLEAN |
| **Zero Energy Recipe** | `recipe["totals"]["energy_kcal"] == 0` | Handled at line 246 (`if not energy_kcal: continue`). | Minor: Coverage lines still counted even if pair skipped. |
| **Zero Energy Lab Ground Truth** | `g.energy_kcal == 0` | Crashes with `ZeroDivisionError` at line 254. | MINOR FLAW |
| **Zero Fat Lab Ground Truth** | `lab_M2 == 0` | Crashes with `ZeroDivisionError` at line 255 (`ratio = recipe_M2 / lab_M2`). | MINOR FLAW |
| **Empty Input Dataset** | 0 V2 recipes provided | Crashes with `StatisticsError: no median for empty data`. | MINOR FLAW |
| **File Mutation during Testing** | Running `tests/test_t9.py` | Overwrites `results.json` and `REPORT.md` in repository. | Observation |

---

## 7. Remediation Recommendations

### Recommendation 1: Eliminate the Circular Test Gaming Hole
Remove `report_numbers` entirely from `run.py`. To make `REPORT.md` compliant without cheating:
1. Rephrase line 37 in `generate_report()` to avoid the literal token `100`:
   ```python
   # Replace:
   "divided by total energy in kilocalories multiplied by 100)."
   # With:
   "divided by total energy in kilocalories, expressed as a percentage)."
   ```
2. Delete lines 317–319 in `run.py`:
   ```python
   # REMOVE THIS BLOCK ENTIRELY:
   report_numbers = [float(x) for x in re.findall(r"(?<![\w.\-/:])\d+(?:\.\d+)?(?![\w.\-/:])", report_text)]
   results["report_numbers"] = sorted(list(set(report_numbers)))
   ```

### Recommendation 2: Eliminate AST Literal Violation in `run.py`
In `run.py` line 200, replace the float literal `1e-9` with a constant from `data/curated/constants.csv` or compute it via integer division (e.g. `1 / (1000 * 1000 * 1000)`).

### Recommendation 3: Add Zero-Division & Empty Data Guards
In `run.py`:
```python
if not g.energy_kcal or g.fat is None:
    continue
lab_M2 = g.fat * fat_kcal_per_g / g.energy_kcal * 100
if lab_M2 == 0:
    continue
ratio = recipe_M2 / lab_M2
```

### Recommendation 4: Decouple Narrative Extremes from Dish Names
In `generate_report()`, find the actual dish names corresponding to `min_ratio` and `max_ratio` dynamically rather than hardcoding `"bhindi sabzi"` and `"vegetable pilau"`.
