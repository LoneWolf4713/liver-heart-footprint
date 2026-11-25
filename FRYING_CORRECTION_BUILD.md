# Frying Correction Module — Build Instructions

**For:** Automated agent (cheaper model)
**Project root:** `/home/prtyksh/subjects/CGAS/liver-heart-footprint/`
**Python:** `/home/prtyksh/subjects/cgas_env/bin/python`
**PYTHONPATH for all runs:** `src/`

Always run python as:
```bash
cd /home/prtyksh/subjects/CGAS/liver-heart-footprint
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python <script>
```

---

## 1. The Problem (Read This Carefully)

The engine (`src/lhf/pipeline.py`) processes recipe ingredient lines one by one and sums their nutrients. For a fried dish like samosa, a recipe may write:

```
500 ml oil for deep frying
```

The engine:
1. Parses this as `qty=500, unit=ml, name="oil for deep frying"`
2. Matches the name to `T508` (sunflower oil, density ~0.92) → **460g of oil**
3. Sunflower oil is ~100g fat per 100g → adds **~460g of fat** to totals
4. Divided by 4 servings → **115g fat per serving** from frying oil alone

This is physically impossible. A samosa absorbs about **7–17g fat per 100g** of finished food (lab measured). The stated 500ml is the *frying bath* — the oil you fill the pan with — not what gets eaten.

**The fix:** When the engine detects a "frying bath" ingredient (large quantity of oil with a "for deep frying" / "to fry" phrase), it should:
1. **Exclude** that oil from the nutrient calculation (mark it as `FRYING_BATH`)
2. **Substitute** the absorbed fat using lab-measured values from `data/curated/fried_foods_lab.csv`

---

## 2. What Already Exists (Do NOT Modify These)

### 2a. `data/curated/fried_foods_lab.csv`
Lab-measured fat content of Indian fried foods. Already fully populated with 60+ entries from Gupta 2016, UK CoFID 2021, Joshee 2019, Jain 2024, etc.

Key columns you will use:
```
item          — dish name (e.g. "Samosa", "Onion Pakora / Bhaji", "Puri")
category      — dish type: "stuffed pastry", "battered fritter", "flat dough",
                            "crisp namkeen", "syrup-soaked sweet", "other"
setting       — "street", "home", "restaurant-takeaway", "retail-packaged", "lab-controlled"
fat_g_100g    — lab-measured fat in grams per 100g of finished fried food (KEY VALUE)
SFA_pct_of_fat — saturated fat as % of total fat (use this to split SFA from fat)
```

### 2b. `src/lhf/pipeline.py` → `analyse_recipe(recipe, setting, risk)`
The main pipeline function. Returns a dict with:
```python
{
    "recipe": {...},
    "lines": [
        {
            "index": 0,
            "raw": "500 ml oil for deep frying",
            "parsed": {"status": "QUANTIFIED", "qty": 500.0, "unit": "ml", "name": "oil for deep frying"},
            "match": {"code": "T508", "method": "alias", "score": 1.0},
            "grams": 460.0,
            "included": True,          # currently True — this is the bug
            "exclusion_reason": None,
            "classes": ["COOKING_OIL"],
            "nutrients": {...},
        },
        ...
    ],
    "coverage": {"included_mass_g": ..., "excluded_by_reason": {...}, ...},
    "totals": {"energy_kcal": ..., "fat_g": ..., "sfa_g": ..., ...},
    "per_serving": {"fat_g": ..., "sfa_g": ..., ...},
    "footprint": {"axes": {...}},
    "warnings": [...]
}
```

### 2c. `src/lhf/classify.py` → `classes_for(code)`
Returns the class list for a food code. `classes_for("T508")` returns `["COOKING_OIL"]`.

### 2d. `src/lhf/footprint.py` → `footprint(per_serving, setting, risk)`
Recomputes the footprint bars from a `per_serving` dict. You will call this after correction.

### 2e. `src/lhf/compute.py` → `sum_nutrients(items)`
Where `items = [{"code": "T508", "grams": 460.0}, ...]`. Returns `{"totals": {...}}`.

### 2f. Demo output for reference (a correctly processed non-fried recipe):
```
demo/paneer_butter_masala.out.json  — per_serving fat: 22.75g (correct, no frying)
demo/dal_makhani.out.json
demo/chicken_biryani.out.json
```
**These must produce identical output after your changes.** They are your regression baseline.

---

## 3. What You Must Build

### 3a. New file: `src/lhf/frying.py`

This module does two things:
1. **Detects** frying bath lines in a processed pipeline result
2. **Corrects** the nutrient totals using lab-measured fat values

#### Full spec for `src/lhf/frying.py`:

```python
"""
Frying correction module.

Detects deep-frying bath oil lines and replaces the stated oil mass with
lab-measured absorbed fat from data/curated/fried_foods_lab.csv.

A "frying bath" line is an ingredient line that:
  (a) has class COOKING_OIL or HYDROGENATED_FAT, AND
  (b) its raw_line contains a frying phrase (see FRYING_PHRASES below), AND
  (c) its grams value exceeds FRYING_BATH_MIN_G (50g)

If frying bath lines are detected in a recipe result, this module:
  1. Removes their nutrient contribution from totals
  2. Looks up the dish name in fried_foods_lab.csv to get lab fat_g_100g
  3. Estimates absorbed fat = (non-oil included mass / 100) * lab_fat_g_100g
  4. Estimates absorbed SFA = absorbed_fat * (SFA_pct_of_fat / 100)
  5. Adds the absorbed fat/SFA back to totals
  6. Re-derives per_serving and footprint
  7. Returns the corrected result dict with a FRYING_CORRECTED warning added
"""
```

#### Constants to define at the top of the module:
```python
FRYING_PHRASES = [
    "for deep frying", "to deep fry", "for frying", "to fry",
    "deep fry", "deep frying", "for deep-frying", "to deep-fry",
]

FRYING_BATH_MIN_G = 50.0  # grams — below this, treat as sautéing oil (not a bath)

# Default fat per 100g by dish category if no exact match found in lab data
CATEGORY_DEFAULTS = {
    "stuffed pastry": 15.0,     # samosa, kachori
    "battered fritter": 17.0,   # pakora, bhaji, vada
    "flat dough": 20.0,         # puri, bhatura, paratha
    "crisp namkeen": 25.0,      # mathri, sev, chakri, namakpara
    "syrup-soaked sweet": 15.0, # gulab jamun, jalebi
    "other": 15.0,              # aloo tikki, etc.
    "default": 15.0,            # fallback
}

# Default SFA % of fat by category (used if SFA_pct_of_fat is missing in lab data)
CATEGORY_SFA_PCT = {
    "stuffed pastry": 42.0,
    "battered fritter": 38.0,
    "flat dough": 36.0,
    "crisp namkeen": 42.0,
    "syrup-soaked sweet": 55.0,
    "other": 40.0,
    "default": 40.0,
}
```

#### Functions to implement:

**Function 1: `_load_lab_data() -> list[dict]`**
- Loads `data/curated/fried_foods_lab.csv` using csv.DictReader
- Returns list of dicts, one per row
- Caches result in a module-level variable (like other modules do)
- Path: use `from lhf.paths import DATA_CURATED` and `os.path.join(DATA_CURATED, "fried_foods_lab.csv")`
- Parse `fat_g_100g` as float; skip rows where it is empty or non-numeric
- Parse `SFA_pct_of_fat` as float; use None if empty

**Function 2: `_detect_frying_bath_lines(lines: list) -> list[dict]`**
- Iterates over `lines` from the pipeline result
- Returns the subset of lines that qualify as frying bath:
  - `line["included"] == True` (currently included in totals)
  - `line.get("classes")` contains `"COOKING_OIL"` or `"HYDROGENATED_FAT"`
  - `line["raw"].lower()` contains any string from `FRYING_PHRASES`
  - `line["grams"] >= FRYING_BATH_MIN_G`

**Function 3: `_lookup_lab_fat(dish_name: str) -> tuple[float, float, str]`**
Returns `(fat_g_100g, sfa_pct_of_fat, match_description)`.

Logic:
1. Normalize `dish_name`: lowercase, strip punctuation
2. Load lab data
3. Try **exact substring match**: check if any lab `item` name (lowercased) is a substring of `dish_name` or vice versa
4. If multiple matches, prefer `setting == "home"` over `"street"` over `"restaurant-takeaway"`; then take the median `fat_g_100g` across matching rows
5. If no match, try **word overlap**: split both into words, find the lab row with the most words in common with `dish_name`; threshold = at least 1 content word match (ignore "and", "or", "with", "in", "of", "the", "a")
6. If still no match, determine category from dish_name:
   - Contains "samosa" or "kachori" → "stuffed pastry"
   - Contains "pakora" or "pakoda" or "bhaji" or "fritter" or "bonda" or "vada" or "batter" → "battered fritter"
   - Contains "puri" or "poori" or "bhatura" or "bhature" or "paratha" → "flat dough"
   - Contains "mathri" or "namakpara" or "sev" or "chakri" or "bhujia" or "chivda" or "chewda" or "murukku" or "papad" → "crisp namkeen"
   - Contains "gulab jamun" or "jalebi" or "ladoo" or "boondi" → "syrup-soaked sweet"
   - Default → "default"
   - Return `(CATEGORY_DEFAULTS[category], CATEGORY_SFA_PCT[category], f"category_default:{category}")`
7. For the matched rows, compute:
   - `fat_g_100g` = median of matched rows' `fat_g_100g` values
   - `sfa_pct_of_fat` = median of non-None `SFA_pct_of_fat` values from matched rows; if all None, use `CATEGORY_SFA_PCT["default"]`
   - `match_description` = `f"lab_match:{matched_items_joined}"`
8. Return `(fat_g_100g, sfa_pct_of_fat, match_description)`

**Function 4: `correct_frying(result: dict, setting: str = "urban", risk: str = "general") -> dict`**
Main entry point. Takes a full pipeline result dict, returns a (possibly corrected) result dict.

```
Algorithm:

1. Detect frying bath lines using _detect_frying_bath_lines(result["lines"])
2. If no frying bath lines found → return result unchanged (no-op)

3. Calculate oil_mass_g = sum of grams for all detected frying bath lines

4. Get the dish name from result["recipe"]["dish"] (or result["recipe"].get("title", ""))

5. Look up lab values: fat_g_100g, sfa_pct_of_fat, match_desc = _lookup_lab_fat(dish_name)

6. Calculate non-oil included mass:
   non_oil_mass_g = sum(
       line["grams"]
       for line in result["lines"]
       if line["included"]
       and line not in frying_bath_lines
   )
   # This is the mass of all non-oil ingredients (the "body" of the dish)

7. If non_oil_mass_g <= 0 → return result unchanged with a warning

8. absorbed_fat_g = (non_oil_mass_g / 100.0) * fat_g_100g
   absorbed_sfa_g = absorbed_fat_g * (sfa_pct_of_fat / 100.0)

9. For each frying bath line, build a subtraction of its nutrient contribution:
   For each frying bath line, we know its current nutrients dict (line["nutrients"]).
   fat_to_remove_g = sum(line["nutrients"]["fat_g"] for bath lines if nutrients exists)
   sfa_to_remove_g = sum(line["nutrients"].get("sfa_g", 0) for bath lines if nutrients exists)
   energy_to_remove_kcal = sum(line["nutrients"].get("energy_kcal", 0) for bath lines)
   
   If nutrients dict is not available for a line, estimate:
   fat_to_remove_g += line["grams"] * 0.995   # sunflower oil is ~99.5% fat
   energy_to_remove_kcal += line["grams"] * 9  # 9 kcal/g fat

10. Build corrected totals (deep copy result["totals"] first):
    corrected_totals = copy of result["totals"]
    corrected_totals["fat_g"] -= fat_to_remove_g
    corrected_totals["fat_g"] += absorbed_fat_g
    corrected_totals["sfa_g"] -= sfa_to_remove_g
    corrected_totals["sfa_g"] += absorbed_sfa_g
    corrected_totals["energy_kcal"] -= energy_to_remove_kcal
    corrected_totals["energy_kcal"] += absorbed_fat_g * 9.0  # fat kcal re-add
    # Clamp to 0 (never negative)
    corrected_totals["fat_g"] = max(0.0, corrected_totals["fat_g"])
    corrected_totals["sfa_g"] = max(0.0, corrected_totals["sfa_g"])
    corrected_totals["energy_kcal"] = max(0.0, corrected_totals["energy_kcal"])

11. Mark the frying bath lines in the result:
    For each frying bath line in result["lines"]:
        line["included"] = False
        line["exclusion_reason"] = "FRYING_BATH"
    # Note: do NOT remove them from the lines list — keep them for auditability

12. Recompute coverage:
    corrected_coverage = copy of result["coverage"]
    corrected_coverage["excluded_by_reason"]["FRYING_BATH"] = len(frying_bath_lines)
    corrected_coverage["included_mass_g"] -= oil_mass_g
    corrected_coverage["lines_included"] -= len(frying_bath_lines)

13. Compute corrected per_serving:
    servings = result["recipe"].get("servings") or 1.0
    servings_val = float(servings)
    corrected_per_serving = {
        k: (v / servings_val if v is not None else None)
        for k, v in corrected_totals.items()
    }

14. Recompute footprint using the imported footprint() function:
    from lhf.footprint import footprint as compute_footprint
    corrected_footprint = compute_footprint(corrected_per_serving, setting=setting, risk=risk)

15. Build warning string:
    warn = (
        f"FRYING_CORRECTED: detected {len(frying_bath_lines)} frying bath line(s) "
        f"({oil_mass_g:.0f}g oil excluded). "
        f"Absorbed fat estimated at {absorbed_fat_g:.1f}g using lab data "
        f"({fat_g_100g}g/100g, match={match_desc}). "
        f"Original stated-oil fat: {fat_to_remove_g:.1f}g."
    )

16. Build and return corrected result dict:
    corrected_result = copy of result (deep copy or rebuild)
    corrected_result["totals"] = corrected_totals
    corrected_result["per_serving"] = corrected_per_serving
    corrected_result["footprint"] = corrected_footprint
    corrected_result["coverage"] = corrected_coverage
    corrected_result["lines"] = result["lines"]  # already mutated in step 11
    corrected_result["warnings"] = result["warnings"] + [warn]
    corrected_result["frying_correction"] = {
        "applied": True,
        "frying_bath_lines_count": len(frying_bath_lines),
        "oil_mass_removed_g": oil_mass_g,
        "absorbed_fat_g": absorbed_fat_g,
        "absorbed_sfa_g": absorbed_sfa_g,
        "fat_g_per_100g_lab": fat_g_100g,
        "sfa_pct_of_fat_lab": sfa_pct_of_fat,
        "lab_match": match_desc,
    }
    return corrected_result
```

---

### 3b. Hook `correct_frying()` into `src/lhf/pipeline.py`

At the **very end** of `analyse_recipe()`, just before `return _clean_nan(result)`, add:

```python
# Frying correction (SPEC addendum: replace stated bath oil with lab-measured absorbed fat)
from lhf.frying import correct_frying
result = correct_frying(result, setting=setting, risk=risk)

return _clean_nan(result)
```

**That is the only change to `pipeline.py`.** Do not touch anything else in that file.

---

### 3c. New file: `demo/samosa_test.json`

Create this test recipe to verify the correction works:

```json
{
    "id": "SAMOSA-TEST-01",
    "dish": "samosa",
    "servings": 8,
    "lines": [
        "2 cups maida",
        "2 tbsp oil",
        "0.5 tsp ajwain",
        "salt to taste",
        "3 medium potatoes, boiled and mashed",
        "1 tsp cumin seeds",
        "0.5 tsp garam masala",
        "1 tsp red chilli powder",
        "2 tbsp fresh coriander leaves, chopped",
        "500 ml oil for deep frying"
    ]
}
```

---

## 4. Tests to Run

### Test 1 — Regression: existing demo recipes must be UNCHANGED

Run all three demo recipes and confirm their `per_serving.fat_g` values match the originals:

```bash
cd /home/prtyksh/subjects/CGAS/liver-heart-footprint
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python -c "
import json
from lhf.pipeline import analyse_recipe

recipes = ['demo/paneer_butter_masala.json', 'demo/dal_makhani.json', 'demo/chicken_biryani.json']
expected_fat = {
    'demo/paneer_butter_masala.json': 22.75,
    'demo/dal_makhani.json': 11.8,
    'demo/chicken_biryani.json': 27.9,
}

for path in recipes:
    with open(path) as f:
        recipe = json.load(f)
    result = analyse_recipe(recipe, setting='urban', risk='general')
    fat = result['per_serving']['fat_g']
    exp = expected_fat[path]
    status = 'PASS' if abs(fat - exp) < 1.0 else 'FAIL'
    print(f'{status}: {path} -> fat={fat:.2f}g (expected ~{exp}g)')
    if 'frying_correction' in result:
        print(f'  WARNING: frying correction was applied but should NOT have been for this recipe')
"
```

**Expected:** All 3 print `PASS`. None should trigger frying correction.

---

### Test 2 — Samosa correction is applied and produces sane numbers

```bash
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python -c "
import json
from lhf.pipeline import analyse_recipe

with open('demo/samosa_test.json') as f:
    recipe = json.load(f)

result = analyse_recipe(recipe, setting='urban', risk='general')

print('=== SAMOSA FRYING CORRECTION TEST ===')
ps = result['per_serving']
print(f'Fat per serving:    {ps[\"fat_g\"]:.2f} g')
print(f'SFA per serving:    {ps[\"sfa_g\"]:.2f} g')
print(f'Energy per serving: {ps[\"energy_kcal\"]:.1f} kcal')

# Check frying_correction block
fc = result.get('frying_correction')
if fc and fc.get('applied'):
    print(f'Frying correction:  APPLIED')
    print(f'  Oil removed:      {fc[\"oil_mass_removed_g\"]:.0f} g')
    print(f'  Absorbed fat:     {fc[\"absorbed_fat_g\"]:.1f} g')
    print(f'  Lab fat/100g:     {fc[\"fat_g_per_100g_lab\"]} g')
    print(f'  Lab match:        {fc[\"lab_match\"]}')
else:
    print('FAIL: frying_correction was NOT applied')

# Sanity checks
assert ps['fat_g'] < 30, f'FAIL: fat per serving {ps[\"fat_g\"]:.1f}g is implausibly high for a samosa'
assert ps['fat_g'] > 2, f'FAIL: fat per serving {ps[\"fat_g\"]:.1f}g is implausibly low'
assert fc is not None and fc['applied'], 'FAIL: correction was not applied'

print()
print('Warnings:')
for w in result['warnings']:
    print(f'  {w}')

# Check that the frying bath line is now excluded
for line in result['lines']:
    if 'for deep frying' in line['raw']:
        status = 'FRYING_BATH (correct)' if line['exclusion_reason'] == 'FRYING_BATH' else f'WRONG: {line[\"exclusion_reason\"]}'
        print(f'Frying bath line status: {status}')
"
```

**Expected output (approximate):**
```
Fat per serving:    ~6–12 g    (NOT 115g)
SFA per serving:    ~2–5 g
Energy per serving: ~180–320 kcal
Frying correction:  APPLIED
  Oil removed:      460 g
  Absorbed fat:     ~15–25 g   (total for 8 servings)
  Lab fat/100g:     ~12–17     (from Joshee/Gupta data)
  Lab match:        lab_match:Samosa
```

---

### Test 3 — Borderline case: small sautéing oil is NOT corrected

```bash
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python -c "
import json
from lhf.pipeline import analyse_recipe

recipe = {
    'id': 'TEST-SAUTE',
    'dish': 'aloo ki sabzi',
    'servings': 4,
    'lines': [
        '3 medium potatoes, cubed',
        '1 medium onion, chopped',
        '2 tbsp oil for frying',
        '1 tsp cumin seeds',
        '0.5 tsp turmeric',
        'salt to taste'
    ]
}

result = analyse_recipe(recipe, setting='urban', risk='general')
fc = result.get('frying_correction')
if fc and fc.get('applied'):
    print(f'FAIL: correction was applied to sauteing oil (2 tbsp = ~27g, below {50}g threshold)')
else:
    print('PASS: small sauteing oil (2 tbsp) correctly NOT treated as frying bath')
"
```

**Expected:** `PASS`

---

### Test 4 — Unquantified frying line is NOT corrected

```bash
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python -c "
import json
from lhf.pipeline import analyse_recipe

recipe = {
    'id': 'TEST-UNQUANT-FRY',
    'dish': 'samosa',
    'servings': 4,
    'lines': [
        '2 cups maida',
        '3 potatoes boiled',
        'oil for deep frying',
        'salt to taste'
    ]
}

result = analyse_recipe(recipe, setting='urban', risk='general')
fc = result.get('frying_correction')
if fc and fc.get('applied'):
    print('FAIL: unquantified frying line should not trigger correction (it has no grams value)')
else:
    print('PASS: unquantified oil for deep frying correctly NOT treated as frying bath (no grams)')
"
```

**Expected:** `PASS` — the unquantified line has `status=UNQUANTIFIED` so it was never `included=True`, meaning `_detect_frying_bath_lines` will not find it.

---

### Test 5 — Save corrected samosa output to disk

```bash
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python -c "
import json
from lhf.pipeline import analyse_recipe

with open('demo/samosa_test.json') as f:
    recipe = json.load(f)
result = analyse_recipe(recipe, setting='urban', risk='general')
with open('demo/samosa_test.out.json', 'w') as f:
    json.dump(result, f, indent=2)
print('Saved demo/samosa_test.out.json')
"
```

---

## 5. What to Write as Summary

After all tests pass, write a file `demo/FRYING_CORRECTION_RESULTS.md` with:

1. Whether all 4 tests passed or failed (and exact error if failed)
2. The samosa test exact numbers: fat per serving, SFA per serving, energy per serving, lab match used
3. The exact warning string from the samosa result's `warnings` list
4. Confirm that `demo/samosa_test.out.json` exists
5. Confirm that `demo/paneer_butter_masala.out.json` fat per serving is still ~22.75g (unchanged)
6. Any issues encountered during implementation

---

## 6. Constraints

- **Do NOT modify anything in `src/lhf/` except:**
  - `src/lhf/pipeline.py` — add exactly 2 lines at the end of `analyse_recipe()` (the import + the correction call)
  - `src/lhf/frying.py` — create this new file
- **Do NOT re-run the full INDB Atlas** — that takes several minutes and is not needed for this task
- **Do NOT modify `data/curated/fried_foods_lab.csv`** — it is read-only reference data
- **Do NOT modify any existing test files in `acceptance/`** if they exist
- If any existing acceptance tests fail after your changes, that is a bug in your implementation — fix it before finishing

---

## 7. Final Deliverables Checklist

```
[ ] src/lhf/frying.py               — new module, fully implemented
[ ] src/lhf/pipeline.py             — 2-line addition at end of analyse_recipe()
[ ] demo/samosa_test.json           — test recipe input
[ ] demo/samosa_test.out.json       — corrected output (saved by Test 5)
[ ] demo/FRYING_CORRECTION_RESULTS.md  — test summary with all numbers
[ ] All 4 tests PASS
[ ] paneer butter masala, dal makhani, chicken biryani produce same fat numbers as before
```
