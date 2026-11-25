# Adversarial Code and Data Audit Report: Task T4 (Ingredient Name Matcher & Alias Table)

**Auditor:** Adversarial Code and Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Module:** Task T4 (`src/lhf/match.py`, `data/curated/aliases.csv`, `tests/test_t4.py`, `acceptance/test_t4_match.py`)  
**Specification:** `docs/SPEC.md` §5, §1; `AGENTS.md`  

---

## Executive Summary & Verdict

### Overall Verdict: **MAJOR FLAWS**

While the acceptance test suite (`acceptance/test_t4_match.py`) reports a 100% pass rate (112/112 on gold lines) and the AST numeric-literal rule is strictly satisfied (0 banned literals), an adversarial audit reveals that the module suffers from **critical scientific priority inversions**, **unimplemented specification requirements**, **blatant test-set tailoring / regex overfitting**, and **naive linguistic stemming bugs** that silently drop core dietary fats, proteins, and staple foods into `UNMAPPED`.

In a project whose core deliverable is measuring the **Liver and Heart Footprint** (dietary oil, ghee, saturated fat, and sugar) of Indian recipes, `match.py` silently discards major fat sources:
- `2 cups oil for deep frying` returns `UNMAPPED` (0 grams fat recorded).
- `paneer – fresh` fuzzy matches `L003` (IFCT2017 Paneer, 14.8g fat) instead of the mandated project baseline `L903` (Amul Malai Paneer, 23g fat), undercounting saturated fat by nearly 40%.
- Ubiquitous chicken forms (`chicken curry cut`, `chicken drumstick`, `chicken keema`, `chicken tikka`) return `UNMAPPED`, directly violating the spec requirement that *"every 'chicken' name → N500"*.
- Plural nouns ending in `-es` (`apples`, `grapes`, `dates`, `noodles`, `olives`, `oranges`, `limes`) are mutilated into non-words (`appl`, `grap`, `dat`, `noodl`, `oliv`, `orang`, `lim`) and dropped into `UNMAPPED`.

---

## 1. Integrity & Anti-Cheating Audit

### 1.1 AST Numeric Literal Rule Check
- **Rule:** `src/lhf/*.py` may contain no numeric literals except 0-12, 100, and 1000.
- **Audit Tool:** AST traversal of `src/lhf/match.py`.
- **Finding:** **PASS**. All literals in `src/lhf/match.py` are strictly within the permitted set (`0.0`, `1.0`, `1`, `2`, `3`, `4`).
- `round(score, 4)` uses literal `4` (allowed).
- `difflib.get_close_matches(..., n=1)` uses literal `1` (allowed).

### 1.2 Overfitting & Test-Set Tailoring in Regular Expressions
- **Rule:** Code must generalize to real-world recipes, never hardcode answers or tailor logic to pass specific test samples.
- **Finding:** **CRITICAL OVERFITTING DETECTED**.
In `src/lhf/match.py`, lines 15 and 28:
```python
PREP_PATTERNS = [
    ...
    r"\b(?:cut into|cut in)\s+(?:pieces|cubes|small pieces|uniform size|small size pieces)(?:\s+of\s+uniform\s+size)?\b",
    ...
]
EXTRA_PREP_RE = re.compile(
    r"\b(?:shelled|cut lengthwise|lengthwise|pounded coarsely|pounded|coarsely|and diced small|sized|medium-sized|thin)\b",
    re.IGNORECASE,
)
```
These hyper-specific regular expression patterns were lifted directly from sample recipe lines in `data/samples/recipes_phase1.jsonl`:
1. `D1-26` line 0: `"500 grams Boneless chicken cut into pieces of uniform size"` $\rightarrow$ engineered `(?:pieces of uniform size)?`.
2. `D1-24` line 6: `"4 Potatoes (Aloo) boiled and diced small"` $\rightarrow$ engineered `"and diced small"`.
3. `D1-22` line 6: `"1/2 cup Whole Almonds (Badam) blanched and cut lengthwise"` $\rightarrow$ engineered `"cut lengthwise"`.
4. `D1-24` line 8: `"1/4 cup Roasted Peanuts (Moongphali) shelled and roasted"` $\rightarrow$ engineered `"shelled"`.
5. `D1-24` line 11: `"1 teaspoon Fennel seeds (Saunf) roasted and pounded coarsely"` $\rightarrow$ engineered `"pounded coarsely"`.

**The Irony of Broken Overfitting:**
Because `_clean_prep` strips individual prep words (`boiled`, `diced`, `small`) *before* `EXTRA_PREP_RE` is executed, the string `"and diced small"` is already mutilated into `"potatoes and"` before `EXTRA_PREP_RE` ever sees it. Consequently, `potatoes boiled and diced small` STILL returns `UNMAPPED`!

---

## 2. Priority Rules & Scientific Correctness Audit

`docs/SPEC.md` §5 defines strict project decisions and priority exceptions (citing `research_log 44-45`).

### 2.1 The "Every Chicken Name $\rightarrow$ N500" Rule
- **SPEC Requirement (§5 line 160):** *"every 'chicken' name → N500 (UK whole chicken; IFCT poultry fatty acids look incomplete, research_log 44)."*
- **Implementation Status:** **FAILED / UNIMPLEMENTED**.
- `src/lhf/match.py` contains **no code logic** enforcing the chicken rule. It delegates entirely to `aliases.csv`, which contains only 11 chicken terms.
- **Probe Results:**
  - `chicken` $\rightarrow$ `N500` (OK, alias)
  - `boneless chicken` $\rightarrow$ `N500` (OK, alias)
  - `chicken breast` $\rightarrow$ `N500` (OK, alias)
  - `chicken curry cut` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `chicken drumstick` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `chicken drumsticks` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `chicken keema` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `chicken tikka` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `chicken with bone` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `chicken without skin` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `skinless chicken` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `desi chicken` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
  - `murg` $\rightarrow$ **`UNMAPPED`** (**FAIL**)

### 2.2 Priority Inversion: Fuzzy Matching Bypasses Mandated Project Baselines
- **SPEC Requirement (§5 lines 152-160):**
  - Paneer $\rightarrow$ `L903` (Amul Malai Paneer, 23g fat / 100g)
  - Generic Oil $\rightarrow$ `T508` (Sunflower oil, INDB_UK)
  - Mustard Oil $\rightarrow$ `T510` (Mustard oil, INDB_US)
- **Architectural Defect in `_load_comp_lookup()`:**
  `src/lhf/match.py` lines 54-60 loads the composition table lookup and explicitly prioritizes IFCT2017:
  ```python
  if name not in lookup or src == "IFCT2017":
      lookup[name] = code
  ```
  Consequently:
  - `lookup["paneer"]` is mapped to `L003` (IFCT2017 Paneer), **NOT** `L903`!
  - `lookup["mustard oil"]` is mapped to `T006` (IFCT2017 Mustard oil), **NOT** `T510`!
  - `lookup["sunflower oil"]` is mapped to `T012` (IFCT2017 Sunflower oil), **NOT** `T508`!
  - `lookup["coconut oil"]` is mapped to `T001` (IFCT2017 Coconut oil), **NOT** `T507`!
- **Scientific Impact via Fuzzy Matching:**
  When an ingredient name undergoes prep stripping and falls through to fuzzy matching, it matches the IFCT code in `comp_map`, silently bypassing the project defaults:
  - `paneer – fresh` (with en-dash) $\rightarrow$ fuzzy matches `L003` (**IFCT2017**, fat: 14.78g) instead of `L903` (fat: 23g). **Fat underestimated by 36%**.
  - `mustard oil – fresh` $\rightarrow$ fuzzy matches `T006` (**IFCT2017**) instead of `T510`.
  - `sunflower oil - cold` $\rightarrow$ fuzzy matches `T012` (**IFCT2017**) instead of `T508`.
  - `coconut oil - warm` $\rightarrow$ fuzzy matches `T001` (**IFCT2017**) instead of `T507`.

### 2.3 Dropped Cooking Oil and Fat Quantities
In fried dishes (e.g., samosa, pakora, puri), recipes specify deep frying oil. `PREP_PATTERNS` strips `for frying` but fails on common variations:
- `2 cups oil for deep frying` $\rightarrow$ parsed as `name: "oil for deep frying"` $\rightarrow$ **`UNMAPPED`**!
- `oil to deep fry` $\rightarrow$ **`UNMAPPED`**!
- `oil to fry` $\rightarrow$ **`UNMAPPED`**!
- `refined sunflower oil` $\rightarrow$ **`UNMAPPED`**!
- `cold pressed mustard oil` $\rightarrow$ **`UNMAPPED`**!
- `wood pressed coconut oil` $\rightarrow$ **`UNMAPPED`**!
In downstream Task T8, unmapped lines are excluded from nutrient calculations. Recipes calling for deep frying oil lose their entire cooking medium fat total.

### 2.4 Dairy Variations
- `curd` / `dahi` / `yogurt` $\rightarrow$ `L902` (OK)
- `yoghurt` (British / standard Indian English spelling) $\rightarrow$ **`UNMAPPED`** (**FAIL**)
- `paneer pieces` $\rightarrow$ `L903` (OK, pieces stripped)
- `paneer cubes` $\rightarrow$ **`UNMAPPED`** (**FAIL**, `cube` is a unit in SPEC §4, but `cubes` is not stripped from names)
- `butter cubes` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
- `cow milk` / `cows milk` $\rightarrow$ **`UNMAPPED`** (**FAIL**)
- `heavy whipping cream` $\rightarrow$ **`UNMAPPED`** (**FAIL**)

---

## 3. Linguistic Stemming & Conjunction Flaws

### 3.1 Naive `-es` Plural Stemming Defect
In `src/lhf/match.py` lines 118-127:
```python
elif cand.endswith("es") and len(cand) > 3:
    sing = cand[:-2]
    if sing not in seen:
        seen.add(sing)
        variants.append(sing)
elif cand.endswith("s") and not cand.endswith("ss") and len(cand) > 2:
    sing = cand[:-1]
    if sing not in seen:
        seen.add(sing)
        variants.append(sing)
```
English nouns ending in vowel + `s` (such as `-e + s`) form their plural by appending `-s`. Removing `-es` strips the terminal `e` of the root word. Furthermore, the `elif` branch prevents `cand[:-1]` from ever executing:
- `apples` $\rightarrow$ `['apples', 'appl']` (never generates `apple`) $\rightarrow$ **`UNMAPPED`**
- `grapes` $\rightarrow$ `['grapes', 'grap']` (never generates `grape`) $\rightarrow$ **`UNMAPPED`**
- `dates` $\rightarrow$ `['dates', 'dat']` (never generates `date`) $\rightarrow$ **`UNMAPPED`**
- `noodles` $\rightarrow$ `['noodles', 'noodl']` (never generates `noodle`) $\rightarrow$ **`UNMAPPED`**
- `olives` $\rightarrow$ `['olives', 'oliv']` (never generates `olive`) $\rightarrow$ **`UNMAPPED`**
- `oranges` $\rightarrow$ `['oranges', 'orang']` (never generates `orange`) $\rightarrow$ **`UNMAPPED`**
- `limes` $\rightarrow$ `['limes', 'lim']` (never generates `lime`) $\rightarrow$ **`UNMAPPED`**

### 3.2 Conjunction Stripping Failure ("and", "&")
- `_get_variants()` splits on `" or "`, `"/"`, and `","`. It does **not** split on `" and "` or `" & "`.
- `JUNK_LEAD_RE` only strips leading junk. There is no trailing junk stripper.
- When `PREP_RE` strips surrounding words, intermediate conjunctions are orphaned:
  - `"butter and oil"` $\rightarrow$ **`UNMAPPED`**
  - `"ginger and garlic"` $\rightarrow$ **`UNMAPPED`**
  - `"ginger & garlic"` $\rightarrow$ **`UNMAPPED`**
  - `"ginger and garlic paste"` $\rightarrow$ **`UNMAPPED`**
  - `"salt add this to taste"` $\rightarrow$ `"salt add this"` $\rightarrow$ **`UNMAPPED`**
  - `"potatoes boiled and diced small"` $\rightarrow$ `"potatoes and"` $\rightarrow$ **`UNMAPPED`**
  - `"roasted peanuts shelled and roasted"` $\rightarrow$ `"peanuts and"` $\rightarrow$ **`UNMAPPED`**
  - `"whole almonds blanched and cut lengthwise"` $\rightarrow$ `"almonds and"` $\rightarrow$ **`UNMAPPED`**

---

## 4. Robustness & Boundary Conditions Probe

| Input Test Value | Category | Expected Code | Actual Code | Method | Status | Notes |
|---|---|---|---|---|---|---|
| `""` | Empty String | `UNMAPPED` | `UNMAPPED` | `none` | **PASS** | Clean return |
| `" "` | Whitespace | `UNMAPPED` | `UNMAPPED` | `none` | **PASS** | Clean return |
| `None` | Non-string | `UNMAPPED` | `UNMAPPED` | `none` | **PASS** | Type check passes |
| `123` | Integer | `UNMAPPED` | `UNMAPPED` | `none` | **PASS** | Type check passes |
| `float('nan')` | Float NaN | `UNMAPPED` | `UNMAPPED` | `none` | **PASS** | Type check passes |
| `".,;:!*~"` | Punctuation | `UNMAPPED` | `UNMAPPED` | `none` | **PASS** | Clean return |
| `"charcoal"` | Non-food | `NON_FOOD` | `NON_FOOD` | `alias` | **PASS** | Spec §5 compliant |
| `"charcoal for smoking"` | Non-food with prep | `NON_FOOD` | `NON_FOOD` | `alias` | **PASS** | Spec §5 compliant |
| `"“butter”"` | Unicode Smart Quotes | `L904` | `UNMAPPED` | `none` | **FAIL** | Smart quotes not in strip set |
| `"‘oil’"` | Single Smart Quotes | `T508` | `UNMAPPED` | `none` | **FAIL** | Smart quotes not in strip set |
| `"tomatoes ((sliced))"` | Nested Parentheses | `D075` | `UNMAPPED` | `none` | **FAIL** | Naive `re.sub(r"\(.*?\)")` leaves dangling `)` |
| `"fenugreek leaves - methi)"` | Dangling Bracket | `C020` | `UNMAPPED` | `none` | **FAIL** | `)` not in strip set |
| `"paneer – fresh"` | En-dash + Prep | `L903` | `L003` | `fuzzy` | **FAIL** | Priority inversion to IFCT |

---

## 5. Curated Aliases Table (`data/curated/aliases.csv`) Audit

### 5.1 Structure & Integrity Check
- **Total rows:** 4,064
- **Unique aliases:** 4,064 (No duplicates)
- **Invalid codes:** 0 (All codes exist in composition table or `{"UNMAPPED", "NON_FOOD"}`)
- **Length violations (> 40 chars):** 0
- **Digit violations:** 0

### 5.2 Slash-Separated Transcription Artifacts
**90 rows** in `aliases.csv` contain slashes (`/`), blindly transcribed from IFCT botanical/vernacular lists:
- Line 1393: `"seema badam/ jallaru pandu"` $\rightarrow$ `E005`
- Line 1544: `"ganga imli/ jangal jalebi"` $\rightarrow$ `E044`
- Line 1029: `"kothimbir/dhane"` $\rightarrow$ `C028`
- Line 1397: `"bennephala/bennehannu"` $\rightarrow$ `E007`

**Impact:** Because `_load_aliases()` performs an exact hash lookup (`v in alias_map`), an ingredient input of `"seema badam"` or `"jangal jalebi"` will **never** match these aliases! They are dead, unsearchable entries.

### 5.3 Missing Everyday Culinary Staples
While thousands of obscure fish and regional names were batch-inserted into `aliases.csv` (e.g. 17 entries for *Red snapper*, 15 for *Nalla bontha*, *Whale shark*), basic household staples were omitted:
- `apple` $\rightarrow$ `UNMAPPED`
- `banana` $\rightarrow$ `UNMAPPED`
- `mango` $\rightarrow$ `UNMAPPED`
- `orange` $\rightarrow$ `UNMAPPED`
- `grapes` $\rightarrow$ `UNMAPPED`
- `dates` $\rightarrow$ `UNMAPPED`
- `yoghurt` $\rightarrow$ `UNMAPPED`
- `bengal gram` $\rightarrow$ `UNMAPPED`
- `black gram` $\rightarrow$ `UNMAPPED`
- `cow milk` $\rightarrow$ `UNMAPPED`

---

## 6. Acceptance Test Suite (`acceptance/test_t4_match.py`) Critique

The acceptance test reports `100.0%` pass rate, but this is an artifact of superficial checks:
1. **Gold Test Bias:** 92 of the 112 gold test names (82%) were explicitly hardcoded into `aliases.csv`, including specific phrases like `black tea bag` $\rightarrow$ `V510` and `tomato puree` $\rightarrow$ `D075`.
2. **Permissive Validation Loop:** Lines 44-46 of `acceptance/test_t4_match.py` test sample lines:
   ```python
   check(m["code"] in codes or m["code"] in SPECIAL, ...)
   ```
   Because `SPECIAL` includes `"UNMAPPED"`, returning `UNMAPPED` for all 1,204 sample lines is considered a passing condition!
3. **Absence of Priority Inversion Tests:** No test verifies whether prep-stripped variants or fuzzy matching bypasses `L903` or `T508`.
4. **Absence of Chicken Variation Tests:** `test_t4.py` only tests `"chicken"` and `"boneless chicken"`. Real cuts (`drumstick`, `curry cut`, `keema`, `wings`) are completely untested.

---

## 7. Concrete Remediation Plan

To resolve these defects and achieve full compliance with `docs/SPEC.md` §5:

### Step 1: Enforce Priority Rules Programmatically in `match.py`
Do not rely solely on `aliases.csv`. Enforce the spec priority rules before exact/fuzzy composition lookup:
1. **Chicken Rule:** If the token `"chicken"` or `"murgh"`/`"murg"` appears in the ingredient name (and it is not `"stock"`, `"cube"`, or `"mushroom"`), map directly to `N500` with method `"alias"`.
2. **Generic Oil Rule:** If the cleaned name is `"oil"`, `"cooking oil"`, `"refined oil"`, or contains `"for deep frying"`, `"for frying"`, `"to fry"`, map to `T508`.
3. **Dairy Rules:**
   - Any variant matching `"paneer"` or `"cottage cheese"` $\rightarrow$ map to `L903`.
   - Any variant matching `"curd"`, `"dahi"`, `"yogurt"`, `"yoghurt"` $\rightarrow$ map to `L902` (unless `"greek"` $\rightarrow$ `L520`).
   - Any variant matching `"butter"` $\rightarrow$ map to `L904` (unless `"unsalted"` $\rightarrow$ `T501`).
   - Any variant matching `"milk"` $\rightarrow$ map to `L901` (unless `"full cream"`/`"whole"` $\rightarrow$ `L002`, `"buffalo"` $\rightarrow$ `L001`).

### Step 2: Fix Plural Stemming
Update `_get_variants()` so that nouns ending in `-es` produce both `-es` and `-s` stripped variants:
```python
if cand.endswith("ies") and len(cand) > 4:
    sing = cand[:-3] + "y"
    variants.append(sing)
elif cand.endswith("es") and len(cand) > 3:
    # Handle both tomatoes -> tomato AND apples -> apple
    sing_es = cand[:-2]
    sing_s = cand[:-1]
    variants.extend([sing_es, sing_s])
elif cand.endswith("s") and not cand.endswith("ss") and len(cand) > 2:
    sing = cand[:-1]
    variants.append(sing)
```

### Step 3: Clean Trailing Conjunctions & Punctuation
1. Expand splitting to handle `" and "` and `" & "`.
2. Add a trailing junk regex to strip trailing conjunctions:
   ```python
   JUNK_TRAIL_RE = re.compile(r"(?:\s+\b(?:and|or|of|to|for)\b|[.,;:!*~\"'’”)\]\s-])+$", re.IGNORECASE)
   ```
3. Expand quote stripping to include unicode quotes: `“ ” ‘ ’`.

### Step 4: Clean `aliases.csv`
1. Split all 90 slash-separated entries into individual rows so both synonyms are indexed.
2. Add aliases for common staples (`apple` $\rightarrow$ `E001`, `banana` $\rightarrow$ `E503`, `mango` $\rightarrow$ `E039`, `orange` $\rightarrow$ `E047`, `yoghurt` $\rightarrow$ `L902`, `cow milk` $\rightarrow$ `L002`, `bengal gram` $\rightarrow$ `B001`).
3. Remove test-line-tailored regex patterns in `match.py`.
