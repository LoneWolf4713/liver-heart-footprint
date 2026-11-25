# Adversarial Audit Report: Task T7 (Daily-Budget Footprint)

**Audit Target:** Task T7 — Daily-budget footprint  
**Auditor:** Adversarial Code and Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Files:**
- `src/lhf/footprint.py`
- `tests/test_t7.py`
- `acceptance/test_t7_footprint.py`
- `data/curated/baselines.csv`
- `data/curated/constants.csv`
- `docs/SPEC.md` §8, §1

---

## 1. Executive Summary & Verdict

### **Verdict: MINOR ISSUES**

The implementation of `src/lhf/footprint.py` conforms closely to the mathematical specifications in `docs/SPEC.md` §8. There is **NO cheating**, **NO hardcoded test answers**, and **NO invented constants or numeric literals** (Rule 1 is fully respected: all numeric literals in code are within `{0..12, 100, 1000}`, and energy/fat conversion constants are dynamically resolved from `baselines.csv` and `constants.csv`).

However, two significant behavioral defects were identified under adversarial probing:
1. **Silent Fallback on Invalid Parameters (Setting & Risk):** Any unrecognized setting (e.g., `setting="suburban"`) silently falls back to `"urban"`, and any unrecognized risk profile (e.g., `risk="high"`) silently falls back to `"general"` without raising an error. Simultaneously, the returned `reference` metadata preserves the unvalidated string, resulting in self-contradictory outputs (e.g., `reference["setting"] = "suburban"`, but calculations and context use `NSO_CALORIES_URBAN` and `NSO_FAT_URBAN`).
2. **Silent Zero-Imputation for Missing/NaN Nutrient Values:** When `per_serving` contains `None`, `NaN`, or missing nutrient keys, `footprint()` coerces them to `0.0`, computing `0.0` amount, `0.0%` of limit, and `0.0%` energy. For nutritional and cardiometabolic risk evaluation, reporting an unmeasured nutrient as `0.0 g` (and `0%` of daily budget) is a dangerous false negative, violating the spirit of AGENTS.md Rule 2 (No silent defaults for missing data).

---

## 2. Integrity Rules Audit

### Rule 1: No Invented Numbers
- **AST Scan of `src/lhf/footprint.py`:**
  - Literals detected: `0`, `0.0`, `100`.
  - Prohibited numeric literals (e.g., `0.5`, `4.0`, `9.0`, `2240`): **0 found**.
  - All constants are retrieved dynamically:
    - `constants.get("FAT_KCAL_PER_G")`
    - `constants.get("SODIUM_MG_PER_G_SALT")`
    - `get_baseline("LIMIT_TOTAL_FAT_PCT")`
    - `get_baseline("LIMIT_SFA_GENERAL")` / `get_baseline("LIMIT_SFA_CARDIOMETABOLIC")`
    - `get_baseline("LIMIT_ADDED_SUGAR_GRAMS")`
    - `get_baseline("LIMIT_SALT_GRAMS")`
    - `get_baseline("NSO_CALORIES_URBAN")` / `get_baseline("NSO_CALORIES_RURAL")`
- **Sugar / Carbohydrate Calorie Constant Verification:**
  - SPEC §8 explicitly mandates: *"Sugar and carbs have no constant yet, so their pct_energy is None. Do not invent a constant."*
  - In `src/lhf/footprint.py` lines 107-113:
    ```python
    if k in ("fat_g", "sfa_g"):
        if e_energy > 0:
            pct_energy = amount * fat_kcal_factor / e_energy * 100
        else:
            pct_energy = None
    else:
        pct_energy = None
    ```
  - `pct_energy` for `added_sugar_g` and `refined_carb_g` is strictly `None`. The builder did not invent `4.0 kcal/g`.
  - **Status:** **PASS**

### Rule 2: No Silent Defaults & Missing Data Handling
- **Missing / NaN Nutrient Handling:**
  - In `src/lhf/footprint.py` lines 95-99:
    ```python
    for k in axes_keys:
        raw_val = per_serving.get(k, 0.0)
        if raw_val is None or (isinstance(raw_val, float) and math.isnan(raw_val)):
            amount = 0.0
        else:
            amount = float(raw_val)
    ```
  - If a nutrient is missing from `per_serving`, or is passed as `None` or `NaN`, it is silently converted to `0.0`.
  - This causes `pct_of_limit` to become `0.0` and `pct_energy` to become `0.0`.
  - In `tests/test_t7.py` lines 121-125, the builder explicitly codified this behavior:
    ```python
    def test_footprint_missing_keys_or_nan(self):
        ps = {"energy_kcal": float("nan"), "fat_g": None}
        res = footprint(ps)
        self.assertEqual(res["axes"]["energy_kcal"]["amount"], 0.0)
        self.assertEqual(res["axes"]["fat_g"]["amount"], 0.0)
    ```
  - **Adversarial Critique:** In food composition analysis, `NaN` / `None` indicates unknown or unmeasured content. Presenting an unknown saturated fat or sodium value as `0.0 g` (0% of daily limit) communicates safety when the actual value is unknown. When `raw_val` is `None` or `NaN`, the axis should report `amount: None`, `pct_of_limit: None`, and `pct_energy: None`.
  - **Status:** **DEFECT / SILENT DEFAULT**

### Rule 3: No Cheating or Hardcoding Test Answers
- **Acceptance Test Integrity:**
  - `acceptance/test_t7_footprint.py` recalculates all limits from ground truth CSV tables across all 4 setting/risk permutations and compares against `footprint()`.
  - `src/lhf/footprint.py` contains no conditional branches checking for test inputs or golden values.
  - **Status:** **PASS**

### Rule 4: Correct Scientific Behavior & Units
- **Mathematical Formulations:**
  - Reference Energy $E$:
    - Urban: $2240\text{ kcal}$ (NSO HCES 2022-24)
    - Rural: $2212\text{ kcal}$ (NSO HCES 2022-24)
  - Fat Limit: $\frac{30}{100} \times E / 9.0 = 74.67\text{ g}$ (Urban) or $73.73\text{ g}$ (Rural).
  - SFA Limit:
    - General: $\frac{10}{100} \times E / 9.0 = 24.89\text{ g}$ (Urban) or $24.58\text{ g}$ (Rural).
    - Cardiometabolic: $\frac{7}{100} \times E / 9.0 = 17.42\text{ g}$ (Urban) or $17.20\text{ g}$ (Rural).
  - Added Sugar Limit: $25.0\text{ g}$ (ICMR-NIN DGI 2024 Guideline 7).
  - Sodium Limit: $5.0\text{ g salt} \times 393.4\text{ mg Na/g NaCl} = 1967.0\text{ mg Na}$.
  - Refined Carbohydrate: Limit is `None`, `pct_of_limit` is `None`.
  - Context indicators:
    - Urban: `NSO_FAT_URBAN` ($70.0\text{ g/day}$) and `INDIAB_SFA_NATIONAL` ($8.9\%E$).
    - Rural: `NSO_FAT_RURAL` ($59.8\text{ g/day}$) and `INDIAB_SFA_NATIONAL` ($8.9\%E$).
  - **Status:** **PASS**

---

## 3. Dynamic Parameter Checks & Edge-Case Probing

A dedicated probe script was executed to stress-test parameter handling and mathematical boundaries.

### 3.1. Setting Parameter Analysis
```python
setting_norm = str(setting).lower() if setting else "urban"
is_rural = setting_norm == "rural"
ekey = "NSO_CALORIES_RURAL" if is_rural else "NSO_CALORIES_URBAN"
fat_context_key = "NSO_FAT_RURAL" if is_rural else "NSO_FAT_URBAN"
```
- **Valid Inputs:**
  - `setting="urban"` -> Uses `NSO_CALORIES_URBAN` ($2240\text{ kcal}$) and `NSO_FAT_URBAN` ($70.0\text{ g}$). (Correct)
  - `setting="rural"` -> Uses `NSO_CALORIES_RURAL` ($2212\text{ kcal}$) and `NSO_FAT_RURAL` ($59.8\text{ g}$). (Correct)
  - Case-insensitive matching (`"Rural"`, `"URBAN"`) works as expected.
- **Adversarial / Invalid Inputs:**
  - Passing `setting="suburban"`, `setting="unknown"`, `setting=123`, or `setting="other"`:
    - Evaluates `is_rural = False`.
    - Silently uses `NSO_CALORIES_URBAN` ($2240\text{ kcal}$) and `NSO_FAT_URBAN` ($70.0\text{ g}$).
    - Sets `reference["setting"] = "suburban"` (or whatever was passed).
    - **Issue:** Does not raise `ValueError`. Emits a contradictory dictionary where `reference["setting"] == "suburban"` but `reference["energy_metric"] == "NSO_CALORIES_URBAN"`.

### 3.2. Risk Parameter Analysis
```python
risk_norm = str(risk).lower() if risk else "general"
is_cardiometabolic = risk_norm == "cardiometabolic"
skey = "LIMIT_SFA_CARDIOMETABOLIC" if is_cardiometabolic else "LIMIT_SFA_GENERAL"
```
- **Valid Inputs:**
  - `risk="general"` -> SFA limit 10% ($24.89\text{ g}$). (Correct)
  - `risk="cardiometabolic"` -> SFA limit 7% ($17.42\text{ g}$). (Correct)
- **Adversarial / Invalid Inputs:**
  - Passing `risk="high"`, `risk="cardiac"`, or `risk="severe"`:
    - Evaluates `is_cardiometabolic = False`.
    - Silently uses `LIMIT_SFA_GENERAL` (10% limit).
    - Sets `reference["risk"] = "high"`.
    - **Clinical Risk:** A user specifying `risk="high"` expects a stricter cardiometabolic ceiling (7%), but the engine silently applies the more relaxed general ceiling (10%) without warning or error.

### 3.3. Zero Division & Extreme Inputs
- **Zero Energy Limit:**
  - If $E = 0$ in baselines:
    - Fat limit calculation: $0.0$.
    - Lines 102 and 108 guard against division by zero using `if lim is not None and lim > 0:` and `if e_energy > 0:`.
    - Result: `pct_of_limit = None`, `pct_energy = None`. No unhandled exception.
- **Negative Nutrient Values:**
  - If `per_serving = {"energy_kcal": -100, "fat_g": -10}`:
    - Returns negative percentages (`pct_of_limit = -13.39%`, `pct_energy = -4.02%`).
    - No lower-bound assertion or warning is triggered.
- **Type Handling:**
  - `per_serving = None` returns `None` (matches SPEC §9).
  - String numbers (e.g. `{"energy_kcal": "450"}`) are successfully cast via `float(raw_val)`.
  - Non-numeric strings (e.g. `{"energy_kcal": "abc"}`) raise `ValueError`.
  - Non-dict inputs (e.g. `[]`, `"invalid"`, `123`) raise `AttributeError: '<type>' object has no attribute 'get'`.

### 3.4. Citation & Source Traceability
All IDs in `limit_sources` were verified against `data/curated/baselines.csv` and `data/curated/constants.csv`:
- `energy_kcal`: `["NSO_CALORIES_URBAN"]` or `["NSO_CALORIES_RURAL"]` (in `baselines.csv`)
- `fat_g`: `["LIMIT_TOTAL_FAT_PCT", ekey, "FAT_KCAL_PER_G"]` (in `baselines.csv` and `constants.csv`)
- `sfa_g`: `[skey, ekey, "FAT_KCAL_PER_G"]` (in `baselines.csv` and `constants.csv`)
- `added_sugar_g`: `["LIMIT_ADDED_SUGAR_GRAMS"]` (in `baselines.csv`)
- `sodium_mg`: `["LIMIT_SALT_GRAMS", "SODIUM_MG_PER_G_SALT"]` (in `baselines.csv` and `constants.csv`)
- `refined_carb_g`: `[]` (explicit empty list for unconstrained nutrient)

---

## 4. Line-by-Line Code Findings in `src/lhf/footprint.py`

| Lines | Code Snippet | Issue Description | Severity |
|---|---|---|---|
| **44–47** | `setting_norm = str(setting).lower() if setting else "urban"`<br>`is_rural = setting_norm == "rural"`<br>`ekey = "NSO_CALORIES_RURAL" if is_rural else "NSO_CALORIES_URBAN"` | Unrecognized setting values silently default to urban instead of raising `ValueError`. | **Medium** |
| **49–51** | `risk_norm = str(risk).lower() if risk else "general"`<br>`is_cardiometabolic = risk_norm == "cardiometabolic"`<br>`skey = "LIMIT_SFA_CARDIOMETABOLIC" if is_cardiometabolic else "LIMIT_SFA_GENERAL"` | Unrecognized risk values silently default to general instead of raising `ValueError`. High-risk labels silently get general limits. | **Medium** |
| **95–99** | `raw_val = per_serving.get(k, 0.0)`<br>`if raw_val is None or (isinstance(raw_val, float) and math.isnan(raw_val)):`<br>`    amount = 0.0` | Missing or NaN nutrient values are coerced to `0.0`, presenting unknown nutrients as 0 g intake and 0% budget consumption. | **Medium** |
| **124–129** | `reference = {"setting": setting, "risk": risk, ...}` | Outputs the unvalidated caller-supplied setting/risk strings while internal calculation used default fallback. | **Low** |

---

## 5. Recommendations for Remediation

1. **Parameter Validation:**
   Enforce strict validation for `setting` and `risk` parameters:
   ```python
   ALLOWED_SETTINGS = {"urban", "rural"}
   ALLOWED_RISKS = {"general", "cardiometabolic"}

   setting_norm = str(setting).lower() if setting else "urban"
   if setting_norm not in ALLOWED_SETTINGS:
       raise ValueError(f"Invalid setting '{setting}'. Must be one of {ALLOWED_SETTINGS}")

   risk_norm = str(risk).lower() if risk else "general"
   if risk_norm not in ALLOWED_RISKS:
       raise ValueError(f"Invalid risk '{risk}'. Must be one of {ALLOWED_RISKS}")
   ```
2. **Honest Missing-Value Representation:**
   Do not convert `None` or `NaN` nutrient amounts to `0.0`. If a nutrient value is missing from `per_serving`, record `amount: None`, `pct_of_limit: None`, and `pct_energy: None`:
   ```python
   raw_val = per_serving.get(k)
   if raw_val is None or (isinstance(raw_val, float) and math.isnan(raw_val)):
       amount = None
       pct_of_limit = None
       pct_energy = None
   else:
       amount = float(raw_val)
       # proceed with percentage calculation
   ```
3. **Type and Boundary Checks:**
   Add a type check for `per_serving` (`if not isinstance(per_serving, dict): return None` or raise `TypeError`), and issue a warning or reject negative nutrient amounts.
