# Round 2 Adversarial Code & Data Audit: Task T4 (Ingredient Name Matcher & Alias Table)

**Auditor:** Auditor 4 (Round 2 Adversarial Red Team Auditor)  
**Date:** 2026-11-11  
**Target Files:**
- `src/lhf/match.py`
- `data/curated/aliases.csv`
- `acceptance/test_t4_match.py`
- `tests/test_t4.py`  
**Specification References:** `docs/SPEC.md` §5 (T4: matching a name to a food code), §1 (Integrity rules), `AGENTS.md`

---

## 1. Executive Summary & Verdict

### **Verdict: MAJOR FLAWS**

Following Round 1, acceptance checks for Task T4 pass completely (`acceptance/test_t4_match.py` achieves 112/112 = 100.0% on gold, zero invalid codes on 1,204 sample quantified lines, and `acceptance/test_rules.py` passes AST literal checks). AST verification confirms `src/lhf/match.py` strictly complies with Rule 1 ({0..12, 100, 1000}), and no whole gold lines appear in `aliases.csv` or `match.py`.

However, when approached with a **blank slate and the principle of GUILTY UNTIL PROVEN INNOCENT**, rigorous adversarial probing reveals that the passing test score is an illusion created by testing exclusively happy-path samples and gold lines tailored directly to `aliases.csv`. Underneath the surface, `match.py` and `aliases.csv` harbor severe algorithmic flaws, dangerous priority hijackings, broken plural stemmers, and silent nutritional distortion bugs:

1. **Catastrophic Frying Suffix Hijacking (Food Items Transformed into Cooking Oil):**  
   In `src/lhf/match.py:221-222`, `_check_priority_variant` checks whether any variant contains frying phrases (`"for deep frying"`, `"to deep fry"`, `"for frying"`, `"to fry"`, `"deep fry"`, `"deep frying"`). Because the uncleaned raw name is tested first and the check does **not** verify the presence of the word "oil" or cooking fat, **ANY food item with a frying instruction is mapped directly to 100% Sunflower Oil (`T508`)**:
   - `"onions to fry"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"fish for deep frying"` / `"fish to fry"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"potatoes for frying"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"papads to fry"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"batter for deep frying"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"egg to fry"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"bread to fry"` $\rightarrow$ `T508` (Sunflower Oil)
   - `"tofu to fry"` $\rightarrow$ `T508` (Sunflower Oil)  
   In a recipe calling for "2 large onions to fry" or "500 g fish for deep frying", the vegetable or meat is completely erased and counted as 500 grams of pure vegetable cooking oil, completely destroying lipid, cardiovascular, and hepatic risk calculations!

2. **Chicken Priority Over-matching Spices, Eggs, and Vegan Items:**  
   In `src/lhf/match.py:156-158`, any variant containing `"chicken"` (except if the full line has `"stock"` or `"cube"`) maps directly to `N500` (UK Whole Chicken). As a result:
   - `"chicken masala"` / `"chicken curry masala"` $\rightarrow$ `N500` (Spice mix treated as poultry meat!)
   - `"chicken egg"` / `"chicken eggs"` $\rightarrow$ `N500` (Poultry meat instead of egg `M001`!)
   - `"vegan chicken"` / `"plant-based chicken"` $\rightarrow$ `N500` (Soy/pea protein treated as real poultry meat!)

3. **Butter Priority Over-matching Non-Dairy and Grocery Items:**  
   In `src/lhf/match.py:184`, matching `vl.startswith("butter ")` or `vl.endswith(" butter")` causes widespread false-positive dairy fat attribution:
   - `"butter beans"` / `"butter bean"` (Phaseolus lunatus legume!) $\rightarrow$ `L904` (Amul Salted Dairy Butter with 80% saturated fat!)
   - `"butter fruit"` (Avocado in South India!) $\rightarrow$ `L904` (Dairy Butter!)
   - `"butter paper"` (Greaseproof parchment paper!) $\rightarrow$ `L904` (Dairy Butter!)
   - `"butter milk"` (Spaced spelling of buttermilk) $\rightarrow$ `L904` (Butter) instead of `L521` (Buttermilk)!
   - `"butter cookie"` / `"butter biscuit"` / `"butter naan"` $\rightarrow$ `L904` (Pure Dairy Butter!)
   - `"cocoa butter"`, `"shea butter"`, `"cashew butter"`, `"sunflower butter"` $\rightarrow$ `L904`!

4. **Broken Plural Stemmer Invaliding Core Culinary Staples:**  
   In `src/lhf/match.py:122-126`, the `-ies` rule unconditionally converts `-ies` to `-y`:
   - `"chillies"` $\rightarrow$ stems to `"chilly"`. Because `aliases.csv` only contains `"chilli"` and `"chili"`, **`"chillies"` returns `UNMAPPED`!** Every standard Indian recipe calling for "4 chillies" or "chopped chillies" fails to map completely!
   - `"cookies"` $\rightarrow$ stems to `"cooky"`, never reaching the `-es` rule for `"cookie"`.
   - The stemmer has no rule for irregular plural `leaves` $\rightarrow$ `leaf`. As a result, singular `"curry leaf"` and `"mint leaf"` return **`UNMAPPED`**!

5. **Truncated Pseudoword Over-stemming:**  
   In `src/lhf/match.py:127-135`, words ending in `es` generate `s1 = cand[:-2]` before `s2 = cand[:-1]`. For standard English plurals ending in `e + s`, this blindly generates truncated pseudowords:
   - `"apples"` $\rightarrow$ `["apples", "appl", "apple"]`
   - `"grapes"` $\rightarrow$ `["grapes", "grap", "grape"]`
   - `"dates"` $\rightarrow$ `["dates", "dat", "date"]`
   - `"cloves"` $\rightarrow$ `["cloves", "clov", "clove"]`
   - `"olives"` $\rightarrow$ `["olives", "oliv", "olive"]`
   - `"spices"` $\rightarrow$ `["spices", "spic", "spice"]`

6. **Preparation Stripping Inverting Nutritional Classifications:**  
   `PREP_PATTERNS` strips `"refined"` and `"puree"`. Because alias matches on stripped variants run before exact composition matches:
   - `"refined wheat flour"` (MAIDA, `A018`) has `"refined"` stripped to `"wheat flour"`, which hits `A019` (Whole Wheat Atta) in `aliases.csv`! **Maida is misclassified as Whole Wheat Atta!**
   - `"tomato puree"` (Exact match for INDB_UK `X504 -> Tomato puree`) has `"puree"` stripped to `"tomato"`, hitting `D075` (raw fresh tomato) in `aliases.csv`!
   - 20 official composition table entries cannot match themselves because prep stripping intercepts them with different aliases (e.g. `B017` Dry Peas $\rightarrow$ `D061` Fresh Peas, `M004` Boiled Egg $\rightarrow$ `M001` Raw Egg, `H006` Dry Coconut $\rightarrow$ `H007` Fresh Coconut).

7. **Dirty Curation Artifacts in `data/curated/aliases.csv`:**  
   Scrutiny of all 4,112 rows revealed OCR artifacts and broken keys:
   - Question-mark keys: `'?. indu'`, `'?. motte'`, `'bafelu ?. indu'`, `'beyisida ?. motte'`, `'?. mas'`, `'?. mamsa'` (6 corrupted NIN raw transcription artifacts).
   - Trailing punctuation: `'emu mamsam.'`, `'guinea kodi mamsam.'`, `'turkey kaallu.'` (contain trailing periods, so user inputs like `"emu mamsam"` fail to match and return `UNMAPPED`).
   - Backticks instead of apostrophes: `'horse`s ear'`, `'bishop`s weed'`, `'hardenberg`s anchovy'`, `'morgan`s cod'`, `'spot-finned bull`s eye'`. Normal typing `"bishop's weed"` returns `UNMAPPED`!

---

## 2. Mission, Scope & Audit Methodology

### 2.1 Scope of Examination
- **Core Engine:** `src/lhf/match.py` (`_load_aliases`, `_load_comp_lookup`, `_clean_prep`, `_get_variants`, `_check_priority_variant`, `match_name`).
- **Data Table:** `data/curated/aliases.csv` (4,112 rows, columns: `alias`, `code`, `note`).
- **Test Harnesses:** `acceptance/test_t4_match.py`, `acceptance/test_rules.py`, `tests/test_t4.py`.
- **Reference Datasets:** `data/samples/recipes_phase1.jsonl`, `acceptance/gold/`, `data/curated/composition.csv`.

### 2.2 Adversarial Methodology
In accordance with AGENTS.md integrity rules, the audit was executed with zero code edits, using automated Python probe scripts to test edge cases, Unicode scripts, ReDoS vulnerability, AST rule compliance, and semantic correctness.

---

## 3. Rigorous Answers to Mandated Audit Questions

### Question 1: Does `data/curated/aliases.csv` contain any slashes (`/`), overly long entries (>40 chars), digits, or duplicate keys?

**Audit Findings:**
- **Slashes (`/`):** **0 found.** Zero rows contain `/` in the `alias` column.
- **Overly Long Entries (>40 chars):** **0 found.** The longest alias is exactly 40 characters (`'whole wheat flour bread with added bran'`).
- **Digits in Aliases:** **0 found.** Zero rows contain numeric digits (`0-9`).
- **Duplicate Keys:** **0 found.** Across all 4,112 rows, every lowercase stripped alias is unique. NFC vs NFD unicode normalization checks also confirmed 0 collisions.
- **Valid Composition Codes:** All 4,112 codes exist in `composition.load_table().index` or are `SPECIAL` (`{"UNMAPPED", "NON_FOOD"}`).

**However, Red-Team Deep Inspection Uncovered 27 Corrupted / Dead Data Rows in `aliases.csv`:**
1. **Unresolved OCR / Transcription Question Marks (6 rows):**
   ```csv
   ?. indu,M014,IFCT G Egg, quial, whole, raw
   ?. motte,M014,IFCT Kan Egg, quial, whole, raw
   bafelu ?. indu,M015,IFCT G Egg, quial, whole, boiled
   beyisida ?. motte,M015,IFCT Kan Egg, quial, whole, boiled
   ?. mas,N015,IFCT G Quail, meat, skinless
   ?. mamsa,N015,IFCT Kan Quail, meat, skinless
   ```
   These entries originated from uncleaned raw transcription tables where National Institute of Nutrition (NIN) transcribers used `?.` to denote missing regional language designations.
2. **Trailing Periods Breaking User Matching (5 rows):**
   ```csv
   emu mamsam.,N012,IFCT Tel Emu, meat, skinless
   guinea kodi mamsam.,N013,IFCT Tel Guinea fowl, meat, with skin
   turkey kaallu.,N016,IFCT Tel Turkey, leg, with skin
   ```
   Because `_get_variants` strips trailing punctuation from recipe lines, any recipe line containing `"emu mamsam"` or `"turkey kaallu"` produces variant `"emu mamsam"`, which **fails** exact key lookup against `"emu mamsam."`, returning `UNMAPPED`!
3. **Backticks Instead of Apostrophes (5 rows):**
   ```csv
   bishop`s weed,G029,IFCT E Omum
   horse`s ear,C027,IFCT E Pak Choi leaves
   hardenberg`s anchovy,P003,IFCT E Anchovy
   morgan`s cod,P042,IFCT E Nalla bontha
   spot-finned bull`s eye,P066,IFCT E Red snapper, small
   ```
   Standard typing (`"bishop's weed"`) returns `UNMAPPED` because the alias contains an ASCII backtick (`` ` ``) rather than an apostrophe (`'`).
4. **Dead Language Prefixes (11 rows):**
   Entries like `'tam. apple pazham'`, `'mar. vatana'`, `'u. alu'`, `'h. arhar dal'`, `'p. imli patte'`, `'tel. batani'`. These language prefixes never appear in real culinary text.

---

### Question 2: Does `match_name` enforce programmatic domain priorities (e.g., chicken dishes mapping to boneless chicken `N500`, frying oil mapping to `T508`, dairy baselines)?

**Audit Findings:**
The programmatic domain priority function `_check_priority_variant` is implemented, but its logic contains catastrophic over-matching, missing exclusions, and architectural flaws:

#### 2.1 The Frying Suffix Catastrophe
Lines 220-222 of `src/lhf/match.py`:
```python
oil_phrases = ("for deep frying", "to deep fry", "for frying", "to fry", "deep fry", "deep frying")
if any(p in vl for p in oil_phrases):
    return "T508"
```
Because `p in vl` does not require the presence of the word `"oil"`, and `variants[0]` is the uncleaned input string:
- `"onions to fry"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`
- `"fish to fry"` / `"fish for deep frying"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`
- `"potatoes for frying"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`
- `"papads to fry"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`
- `"batter for deep frying"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`
- `"egg to fry"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`
- `"tofu to fry"` $\rightarrow$ `{'code': 'T508', 'method': 'alias', 'score': 1.0}`

Any non-chicken ingredient that includes preparation instructions for frying is converted into 100% vegetable oil!

#### 2.2 Chicken Priority Over-matching Spices and Eggs
Lines 156-158 of `src/lhf/match.py`:
```python
if any(w in vl for w in ("chicken", "murgh", "murg", "चिकन")):
    if not any(w in fnl for w in ("stock", "cube")):
        return "N500"
```
- In Indian cooking, `"chicken masala"` / `"chicken curry masala"` is a dry spice blend (coriander, cumin, chilli, cardamom, cinnamon) containing 0% chicken. `match_name("chicken masala")` returns `N500` (UK Whole Chicken)!
- `"chicken egg"` and `"chicken eggs"` return `N500` (Chicken Meat) instead of `M001` (Hen's Egg)!
- `"vegan chicken"` and `"plant-based chicken"` return `N500`!

#### 2.3 Dairy Baselines & False Positives
- **Butter (`L904`):**
  Lines 184-185 check `vl == k or vl.startswith(k + " ") or vl.endswith(" " + k)`.
  This flags non-dairy items as salted dairy butter:
  - `"butter beans"` / `"butter bean"` (Legume) $\rightarrow$ `L904` (Butter)!
  - `"butter fruit"` (South Indian name for Avocado) $\rightarrow$ `L904` (Butter)!
  - `"butter paper"` (Parchment) $\rightarrow$ `L904` (Butter)!
  - `"butter milk"` (With space) $\rightarrow$ `L904` (Butter) instead of `L521` (Buttermilk)!
  - `"cocoa butter"`, `"shea butter"`, `"cashew butter"` $\rightarrow$ `L904`!
- **Cream (`L905`):**
  - `"cream of tartar"` (Potassium bitartrate, chemical leavener) $\rightarrow$ `L905` (Fresh Dairy Cream)!
  - `"cream cheese"` $\rightarrow$ `L905`!
  - `"cashew cream"` / `"soy cream"` $\rightarrow$ `L905`!
- **Ghee (`T013`):**
  Line 161 checks `vl == "ghee" or "clarified butter" in vl`.
  Exact match requirement causes common Indian variants to fail:
  - `"pure ghee"`, `"cow ghee"`, `"buffalo ghee"`, `"homemade ghee"` $\rightarrow$ **`UNMAPPED`**!
  - Yet `"cow clarified butter"` matches `T013`!
- **Cooking Oils Hijacking:**
  `named_oils` omits Safflower oil and Cottonseed oil:
  - Safflower oil has its own code `T009` (IFCT2017) in the composition table. Because `"safflower"` is omitted from `named_oils`, `match_name("safflower oil")` returns `T508` (Sunflower oil), violating SPEC §5!
  - Cottonseed oil has its own code `T003` (IFCT2017). `match_name("cottonseed oil")` returns `T508`!
  - Non-culinary oils: `"engine oil"`, `"mineral oil"`, `"castor oil"` all map to `T508`!

---

### Question 3: How does plural stemming behave (e.g., `apples`, `grapes`, `dates`, `potatoes`)? Does it over-stem or under-stem?

**Audit Findings:**
The plural stemmer in `src/lhf/match.py:121-141` exhibits both severe **under-stemming** (failing to match valid plurals) and **over-stemming** (generating corrupt truncated non-words):

1. **Catastrophic Failure on `"chillies"` (Core Staple Dropped):**
   ```python
   if cand.endswith("ies") and len(cand) > 4:
       sing = cand[:-3] + "y"
   ```
   For `"chillies"`, the stemmer removes `-ies` and adds `y`, producing `"chilly"`.
   Neither `"chillies"` nor `"chilly"` exists in `aliases.csv` (which stores `"chilli"` with an `i`, or `"green chillies"` / `"red chillies"`).
   As a direct consequence:
   ```python
   match_name("chillies")  # -> {'code': 'UNMAPPED', 'method': 'none', 'score': 0.0}
   ```
   A recipe calling for `"4 chillies"` or `"chopped chillies"` returns `UNMAPPED`!

2. **Failure on `-ies` Nouns with `-e` Base:**
   `"cookies"` ends in `-ies`, so branch 1 converts it to `"cooky"`. Branch 2 (`elif cand.endswith("es")`) is skipped, so `"cookie"` is never produced. `match_name("cookies")` $\rightarrow$ `UNMAPPED`.

3. **Truncated Pseudoword Over-stemming on `-es` Words:**
   ```python
   elif cand.endswith("es") and len(cand) > 3:
       s1 = cand[:-2]  # tomatoes -> tomato
       ...
       s2 = cand[:-1]  # apples -> apple, grapes -> grape
   ```
   Because `s1` (`cand[:-2]`) is unconditionally generated and prepended to `variants` before `s2`:
   - `"apples"` $\rightarrow$ generates `s1 = "appl"`, then `s2 = "apple"`.
   - `"grapes"` $\rightarrow$ generates `s1 = "grap"`, then `s2 = "grape"`.
   - `"dates"` $\rightarrow$ generates `s1 = "dat"`, then `s2 = "date"`.
   - `"cloves"` $\rightarrow$ generates `s1 = "clov"`, then `s2 = "clove"`.
   - `"olives"` $\rightarrow$ generates `s1 = "oliv"`, then `s2 = "olive"`.
   - `"spices"` $\rightarrow$ generates `s1 = "spic"`, then `s2 = "spice"`.
   - `"molasses"` $\rightarrow$ generates `s1 = "molass"`, then `s2 = "molasse"`.
   While `apple`, `grape`, `date`, `potato` happen to match because both singular and plural were hardcoded into `aliases.csv`, generating non-word roots (`appl`, `grap`, `dat`, `clov`, `oliv`, `spic`) is linguistically incorrect and pollutes the variant pipeline.

4. **Irregular Plurals Fails (`leaves` $\rightarrow$ `leaf`):**
   The stemmer has no rule for `ves` $\rightarrow$ `f`.
   - `"leaves"` generates `s1 = "leav"` and `s2 = "leave"`. It never generates `"leaf"`.
   - Because `aliases.csv` contains `"curry leaves"` and `"mint leaves"` but not the singular forms:
     - `match_name("curry leaf")` $\rightarrow$ **`UNMAPPED`**!
     - `match_name("mint leaf")` $\rightarrow$ **`UNMAPPED`**!

5. **Over-stemming Non-Plural Latin/Greek Nouns:**
   Branch 3 (`elif cand.endswith("s") and not cand.endswith("ss") and len(cand) > 2`) strips `s`:
   - `"asparagus"` $\rightarrow$ `"asparagu"`
   - `"hummus"` $\rightarrow$ `"hummu"`
   - `"couscous"` $\rightarrow$ `"couscou"`
   - `"lentils"` $\rightarrow$ stems to `"lentil"`, which is **`UNMAPPED`**!

---

### Question 4: How are preparation prefixes and suffixes handled?

**Audit Findings:**
Preparation terms are handled via `PREP_RE`, `EXTRA_PREP_RE`, and `JUNK_LEAD_RE` / `JUNK_TRAIL_RE`. However, the order in which variants are generated and matched causes severe **classification inversions**:

1. **Maida Inverted to Whole Wheat Atta (`refined wheat flour` $\rightarrow$ `A019`):**  
   In `src/lhf/match.py:20`, `PREP_PATTERNS` strips `"refined"`.
   When the user inputs `"refined wheat flour"` (which is the exact English definition of Maida, IFCT `A018`):
   - `_get_variants` strips `"refined"`, producing variant `"wheat flour"`.
   - In `aliases.csv`, `"wheat flour"` is mapped to `A019` (Whole wheat atta).
   - `match_name` tests all variants against `aliases.csv`.
   - Result: `match_name("refined wheat flour")` returns `A019` (Whole Wheat Atta)!
   **Refined white flour (Maida) is mathematically classified as 100% whole grain fiber-rich Atta!**

2. **Tomato Puree Inverted to Raw Tomato (`tomato puree` $\rightarrow$ `D075`):**  
   In `src/lhf/match.py:14`, `PREP_PATTERNS` strips `"puree"`.
   In INDB_UK, code `X504` is literally named `"Tomato puree"`.
   When `"tomato puree"` is passed:
   - Variant 0 is `"tomato puree"` (not in `aliases.csv`).
   - Variant 1 is `"tomato"` (which exists in `aliases.csv` mapped to `D075` raw tomato).
   - Because alias matching checks all variants before exact composition matching:
   - `match_name("tomato puree")` returns `D075` (Raw fresh tomato) instead of `X504` (Tomato puree)!

3. **20 Composition Items Cannot Match Themselves:**  
   Adversarial testing iterating over all entries in `composition.load_table()` revealed that 20 official composition items fail self-matching because prep stripping intercepts them:
   - `B017` (*Peas, dry*) $\rightarrow$ matched to `D061` (*Peas, fresh*)!
   - `H006` (*Coconut, kernel, dry*) $\rightarrow$ matched to `H007` (*Coconut, kernel, fresh*)!
   - `M004` (*Egg, poultry, whole, boiled*) $\rightarrow$ matched to `M001` (*Egg, poultry, whole, raw*)!
   - `E514` (*DRIED MANGO*) $\rightarrow$ matched to `E039` (*Mango, ripe, kesar*)!
   - `B505` (*Peanuts, dry roasted*) $\rightarrow$ matched to `H012` (*Ground nut*)!
   - `L510` (*Milk, skimmed, dried, fortified*) $\rightarrow$ matched to `L901` (*Milk, toned*)!

4. **Missing Preparation Modifiers Dropping Real Lines:**  
   In `data/samples/recipes_phase1.jsonl`, real recipe lines failed matching because common modifiers were omitted from `PREP_RE`:
   - `"shelled"`: `"roasted peanuts shelled and roasted"` $\rightarrow$ `UNMAPPED`
   - `"beaten"`: `"thick curd beaten"` $\rightarrow$ `UNMAPPED`
   - `"stalk"`: `"stalk coriander leaves finely chopped"` $\rightarrow$ `UNMAPPED`
   - `"handful"`: `"handful fresh coriander leaves, finely chopped"` $\rightarrow$ `UNMAPPED`
   - `"add this to taste"`: `"salt add this to taste"` $\rightarrow$ `UNMAPPED`

---

### Question 5: Are numeric literals in `src/lhf/match.py` strictly compliant with AST Rule 1 ({0..12, 100, 1000})?

**Audit Findings:**
**PASSED.** An automated AST walk of `src/lhf/match.py` inspected every numeric constant:
- Total numeric literals found: 17
- Values observed:
  - `0.0` (Lines 233, 270)
  - `1.0` (Lines 244, 249, 254, 267)
  - `0` (Line 261)
  - `1` (Lines 91, 132, 137, 259)
  - `2` (Lines 128, 136)
  - `3` (Lines 123, 127)
  - `4` (Lines 122, 263)
- Every numeric literal is an element of `set(range(0, 13)) | {100, 1000}`.
- Cutoff constant `FUZZY_MATCH_CUTOFF` (0.85) is loaded dynamically via `constants.get("FUZZY_MATCH_CUTOFF")`, avoiding numeric hardcoding.
- Rule 1 violations: **0**.

---

### Question 6: Does any whole gold test line text appear in `aliases.csv` or `match.py` (Rule 4 check)?

**Audit Findings:**
**PASSED.**
- All 120 lines from `acceptance/gold/` were scanned against `src/lhf/match.py` and `data/curated/aliases.csv`.
- Zero whole gold lines ($\ge 12$ chars) appear in `src/lhf/match.py` or `data/curated/aliases.csv`.
- Cross-referencing against `data/samples/recipes_phase1.jsonl` confirmed only two trivial lines match sample lines: `'oil'` and `'salt'`, which are legitimate ingredient names.

**Critical Red-Team Observation on Test-Gaming:**  
While no full lines were copied, **111 out of 112 gold test lines matched via `method: "alias"`**, and 1 matched `method: "none"` (expected UNMAPPED). Exactly **0 lines matched via `"exact"`** and **0 lines matched via `"fuzzy"`**.
This demonstrates that `aliases.csv` was meticulously handcrafted to cover 100% of the public gold test set, while leaving ordinary variants (like `"chillies"`, `"curry leaf"`, `"refined wheat flour"`) completely unhandled.

---

## 4. Comprehensive Adversarial Probes & Evidence

| Probe Input | Expected Food / Behavior | Actual Match Output | Root Cause / Impact | Severity |
|---|---|---|---|---|
| `"onions to fry"` | Onion (`G017`) | `T508` (Sunflower Oil) | Frying phrase hijacking in `_check_priority_variant` | **CRITICAL** |
| `"fish for deep frying"` | Fish (`P003` / `P042`) | `T508` (Sunflower Oil) | Frying phrase hijacking; converts 500g fish into 500g oil | **CRITICAL** |
| `"potatoes for frying"` | Potato (`F006`) | `T508` (Sunflower Oil) | Frying phrase hijacking | **CRITICAL** |
| `"papads to fry"` | Papad / pulse | `T508` (Sunflower Oil) | Frying phrase hijacking | **CRITICAL** |
| `"chicken masala"` | Spice mix (`G523`) | `N500` (UK Whole Chicken) | Chicken priority rule intercepts spice powder | **HIGH** |
| `"chicken eggs"` | Eggs (`M001`) | `N500` (UK Whole Chicken) | Chicken priority rule intercepts eggs | **HIGH** |
| `"butter beans"` | Legume (`D050`) | `L904` (Amul Salted Butter) | Butter prefix match flags pulse as 80% dairy fat | **HIGH** |
| `"butter fruit"` | Avocado | `L904` (Amul Salted Butter) | Butter prefix match flags avocado as dairy butter | **HIGH** |
| `"butter paper"` | Non-food kitchen supply | `L904` (Amul Salted Butter) | Non-food paper mapped to dairy butter | **HIGH** |
| `"butter milk"` | Buttermilk (`L521`) | `L904` (Amul Salted Butter) | Spaced spelling escapes exclusion, maps to butter | **HIGH** |
| `"chillies"` | Chilli (`G516` / `G008`) | `UNMAPPED` | Plural stemmer converts `-ies` to `-y` (`chilly`), missing alias | **HIGH** |
| `"refined wheat flour"` | Maida (`A018`) | `A019` (Whole Wheat Atta) | Prep regex strips "refined", hits "wheat flour" alias | **HIGH** |
| `"tomato puree"` | Tomato Puree (`X504`) | `D075` (Raw fresh tomato) | Prep regex strips "puree", hits raw tomato alias | **HIGH** |
| `"curry leaf"` | Curry leaves (`G010`) | `UNMAPPED` | Stemmer does not handle `leaves` $\rightarrow$ `leaf` | **MEDIUM** |
| `"mint leaf"` | Mint leaves (`G016`) | `UNMAPPED` | Stemmer does not handle `leaves` $\rightarrow$ `leaf` | **MEDIUM** |
| `"safflower oil"` | Safflower oil (`T009`) | `T508` (Sunflower Oil) | `named_oils` omits safflower; SPEC §5 IFCT priority violated | **MEDIUM** |
| `"cottonseed oil"` | Cotton seed oil (`T003`) | `T508` (Sunflower Oil) | `named_oils` omits cottonseed; SPEC §5 IFCT priority violated | **MEDIUM** |
| `"pure ghee"` | Ghee (`T013`) | `UNMAPPED` | `vl == "ghee"` exact string equality fails on common qualifiers | **MEDIUM** |
| `"cream of tartar"` | Leavening agent | `L905` (Fresh Dairy Cream) | Cream suffix match flags tartaric acid as dairy cream | **MEDIUM** |
| `"ginger and garlic"` | Ginger (`G014`) & Garlic | `UNMAPPED` | Variant splitter splits on "or", "/", "," but not "and" | **MEDIUM** |
| `"cous cous"` / `"paw paw"` | Couscous / Papaya | `['cous']`, `['paw']` | Blind deduplication splits legitimate doubled words | **LOW** |
| `"bishop's weed"` | Omum (`G029`) | `UNMAPPED` | Alias stored with backtick ``bishop`s weed`` | **LOW** |
| `"emu mamsam"` | Emu meat (`N012`) | `UNMAPPED` | Alias stored with trailing period `emu mamsam.` | **LOW** |

---

## 5. Downstream Impact Analysis

The vulnerabilities in `lhf.match` propagate directly through the core pipeline:
1. **Distortion of Gram Conversions (T5):**  
   When `"onions to fry"` or `"fish for deep frying"` maps to `T508`, `grams_for` treats them as liquid vegetable oil rather than solid vegetables or meat. If the unit is `"tbsp"`, a density of 0.92 g/ml is applied; if the unit is `"piece"` (e.g. "2 onions to fry"), it fails as `UNQUANTIFIABLE`, erasing the ingredient entirely!
2. **False Classification Signals (T6):**  
   `classify_recipe` relies on mapped codes to calculate lipid indices and identify major culinary culprits (oil, butter, ghee, cream, chicken, maida).
   - A vegetarian recipe with `"onions to fry"` receives an inflated cooking oil count (`T508`).
   - A vegan recipe containing `"butter beans"` receives an immediate dairy-fat flag (`L904`).
   - A vegetarian curry with `"chicken masala"` receives a poultry meat flag (`N500`).
   - A recipe using `"refined wheat flour"` (Maida, glycemic risk) is incorrectly scored as whole grain Atta (`A019`), evading maida penalties!
3. **Footprint Computation Invalidation (T7 & T8):**  
   Footprint scores (hepatic steatosis and coronary heart disease risk points) depend on saturated fat (SFA) and free sugars. Mapping `"butter beans"` to `L904` injects 80g fat / 50g SFA per 100g, massively over-scoring heart and liver risk points for a healthy legume! Conversely, dropping `"chillies"` (UNMAPPED) triggers unnecessary recipe exclusion under high unmapped thresholds.

---

## 6. Actionable Recommendations for Remediation

### 6.1 Fix Frying Suffix Hijacking in `src/lhf/match.py`
Require the word `"oil"`, `"tel"`, or fat terms when matching frying phrases, and ensure prep cleaning runs before priority checks:
```python
# BEFORE:
oil_phrases = ("for deep frying", "to deep fry", "for frying", "to fry", "deep fry", "deep frying")
if any(p in vl for p in oil_phrases):
    return "T508"

# AFTER:
oil_phrases = ("for deep frying", "to deep fry", "for frying", "to fry", "deep fry", "deep frying")
if any(p in vl for p in oil_phrases) and any(w in vl for w in ("oil", "tel", "fat")):
    return "T508"
```

### 6.2 Fix Chicken Priority Over-matching
Add explicit exclusions for masala, spices, seasonings, eggs, and vegan substitutes:
```python
# BEFORE:
if any(w in vl for w in ("chicken", "murgh", "murg", "चिकन")):
    if not any(w in fnl for w in ("stock", "cube")):
        return "N500"

# AFTER:
if any(w in vl for w in ("chicken", "murgh", "murg", "चिकन")):
    exclusions = ("stock", "cube", "masala", "curry powder", "spice", "seasoning", "egg", "vegan", "plant-based")
    if not any(w in fnl for w in exclusions):
        return "N500"
```

### 6.3 Fix Butter and Cream False Positives
Exclude legumes, fruits, paper, and confectionery from butter and cream matches:
```python
# Butter exclusions:
butter_exclusions = (
    "buttermilk", "chaas", "peanut butter", "almond butter", "apple butter",
    "butterfish", "butter bean", "butter beans", "butter fruit", "butter paper",
    "butter cookie", "butter biscuit", "cocoa butter", "shea butter", "cashew butter"
)
# Cream exclusions:
cream_exclusions = (
    "ice cream", "sour cream", "coconut cream", "cream of tartar",
    "tartar cream", "cream cheese", "cashew cream", "soy cream"
)
```

### 6.4 Fix Plural Stemmer for `"chillies"` and Irregular Plurals
```python
# Handle chillies -> chilli
if cand.endswith("ies") and len(cand) > 4:
    if cand == "chillies":
        variants.append("chilli")
        variants.append("chili")
    elif cand == "cookies":
        variants.append("cookie")
    else:
        sing = cand[:-3] + "y"
        variants.append(sing)

# Handle leaves -> leaf
if cand.endswith("leaves"):
    variants.append(cand[:-3] + "f")  # curry leaves -> curry leaf
elif cand.endswith("leaf"):
    variants.append(cand[:-1] + "ves")  # curry leaf -> curry leaves
```

### 6.5 Reorder Variant Matching to Prevent Preparation Inversions
Check exact composition name matches on the unstripped variant **before** checking alias matches on prep-stripped variants:
```python
# Priority:
# 1. Domain priority checks on exact raw variants
# 2. Exact match of raw unstripped variants against comp_map
# 3. Alias match of raw unstripped variants
# 4. Alias match of prep-cleaned variants
# 5. Exact match of prep-cleaned variants against comp_map
# 6. Fuzzy match
```

### 6.6 Clean Dirty Entries in `data/curated/aliases.csv`
- Replace backtick `` ` `` with apostrophe `'` in 5 rows (`bishop's weed`, `horse's ear`, etc.).
- Strip trailing dots `.` in 3 rows (`emu mamsam`, `guinea kodi mamsam`, `turkey kaallu`).
- Delete or clean the 6 OCR artifact rows containing `?.`.
- Add missing Indian staples: `"chillies" -> G516`, `"curry leaf" -> G010`, `"mint leaf" -> G016`, `"daal" -> B021`, `"refined wheat flour" -> A018`.
- Include `"safflower oil" -> T009` and `"cottonseed oil" -> T003` in `named_oils`.

---

**Report Completion Verification:**  
- Target file written: `audit_round2/04_t4_match.md`
- Integrity rules verified: Zero code modifications made; all findings backed by reproducible Python probe executions.
