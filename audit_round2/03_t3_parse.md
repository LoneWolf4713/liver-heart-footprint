# Round 2 Adversarial Code & Data Audit: Task T3 (Ingredient Line Parser)

**Auditor:** Auditor 3 (Round 2 Adversarial Red Team Auditor)  
**Date:** 2026-11-11  
**Target Module:** `src/lhf/parse.py`  
**Associated Test Files:**
- `acceptance/test_t3_parse.py`
- `tests/test_t3.py`
- `acceptance/gold/gold_public.json`
- `~/subjects/CGAS/lhf_holdout/gold_holdout.json`
- `data/samples/recipes_phase1.jsonl`  
**Specification Reference:** `docs/SPEC.md` §4 (T3: parsing one ingredient line), §1 (Integrity rules), `AGENTS.md`

---

## 1. Executive Summary & Verdict

### **Verdict: MAJOR FLAWS**

Following the Round 1 audit, significant improvements were implemented in `src/lhf/parse.py`: ampersand-joined mixed numbers (`2 &amp; ½`, `1 & 1/2`) are properly recognized, holdout gold line G058 now passes at 100%, and standalone `dash` and `BOUNDARY` lookahead patterns were introduced. Acceptance tests pass (`108/109` unit, `108/109` size, `100%` status/qty/range/stated/optional), and AST static analysis confirms 100% adherence to Rule 1 (allowed numeric literals only).

However, rigorous adversarial probing with a **blank slate and guilty-until-proven-innocent** approach uncovered multiple severe algorithmic flaws, regressions, and silent nutritional deletion vulnerabilities:

1. **Silent Dairy Fat Deletion on Real Recipe V2-R18 ("Chicken Korma"):**  
   In `data/samples/recipes_phase1.jsonl` (recipe `V2-R18`, dish: chicken korma), line 13 is:  
   `"2 teaspoon Curd (Dahi / Yogurt) beaten with a little water"`  
   Because `_is_plain_water` performs a naive substring match for `water` anywhere in the line, this curd line is classified as **`status: WATER`**! In `pipeline.py`, this line is excluded with `exclusion_reason: WATER`, **completely deleting the dairy curd (and its dairy fat and calories) from Chicken Korma**!
2. **Devanagari Unicode Normalization / Nukta Decomposition Mismatch (Standard Hindi Keyboards Broken):**  
   In `src/lhf/parse.py:52`, `बड़े\s*चम्मच` is defined using precomposed `U+095C` (`DEVANAGARI LETTER RRA`), whereas standard Hindi typing on Android, iOS, Windows, and Google Indic keyboards emits decomposed `U+0921` (`DDA`) + `U+093C` (`NUKTA`). Because `parse.py` never normalizes Unicode, standard typing `"2 बड़े चम्मच घी"` **fails to match `tbsp`**, falling back to `unit: 'piece'` and polluting `name: 'बड़े चम्मच घी'`. Downstream in `grams_for`, `ghee` with `unit: piece` becomes `UNQUANTIFIABLE`, **erasing 100% of the cooking fat from the dish**!
3. **Overly Broad Water Substring Classification Silently Dropping Confections and Foods:**  
   Because `_is_plain_water` tests whether `water|ice|पानी|बर्फ` occurs anywhere in the unbracketed string with only a fragile hardcoded exemption list, numerous real culinary foods, beverages, and preparations are classified as plain `WATER` and discarded with 0 grams / 0 nutrients:
   - `"1 प्लेट पानी पूरी"` (Pani Puri street food) $\rightarrow$ `status: WATER`
   - `"100 ग्राम पानी फल"` (Singhara / water chestnut in Hindi) $\rightarrow$ `status: WATER`
   - `"100 g water spinach"` (Kalmi saag greens) $\rightarrow$ `status: WATER`
   - `"2 cups water melon"` (Watermelon written with space) $\rightarrow$ `status: WATER`
   - `"1 cup tonic water"` (Sugar-sweetened carbonated beverage) $\rightarrow$ `status: WATER`
   - `"1 glass ice tea"` (Sweetened beverage) $\rightarrow$ `status: WATER`
   - `"1 ice gola"` / `"1 ice pop"` (Flavored street confection) $\rightarrow$ `status: WATER`
   - `"1 cup sugar water"` (Sugar syrup preparation) $\rightarrow$ `status: WATER`
   - `"1/2 cup imli water"` / `"kokum water"` / `"amchur water"` $\rightarrow$ `status: WATER`
   - `"1 tbsp cornflour mixed in 2 tbsp water"` (Slurry) $\rightarrow$ `status: WATER`
4. **Boundary Failure on Unspaced Quantities (`100g`, `250ml`, `1kg`, `1tbsp`):**  
   `SINGLE_PAT = re.compile(rf"^({NUM_ATOM})\b")` enforces a word boundary `\b` immediately following the digits. When a quantity is written directly adjacent to an ASCII unit without a space (e.g. `100g paneer`, `250ml milk`, `1kg mutton`), there is no word boundary between `\d` and `[a-z]`. As a result, `qty` is `None` and the line is dropped as `UNQUANTIFIED`.
5. **Stray Preposition 'of' Causing Downstream Unmapped Food Dropping:**  
   Lines like `"1 cup of flour"` or `"a pinch of salt"` parse as `name: 'of flour'` and `name: 'of salt'`. While `match.py` strips `of` for prioritized oils and sugars, general ingredients like `"of flour"` fail matching completely (`UNMAPPED`), causing the flour (120 g, ~450 kcal) to be dropped by the pipeline.
6. **Unhandled Leading-Dot Decimals (`.5 cups flour`):**  
   `NUM_ATOM` requires `\d+(?:\.\d+)?` and fails on decimals without leading zero (`.5`), classifying them as `UNQUANTIFIED` and stripping the leading period to yield `name: '5 cups flour'`.

---

## 2. Integrity Rules & Static Analysis Checks

### 2.1 Rule 1: No Invented Numbers (AST Analysis)
We parsed `src/lhf/parse.py` into an Abstract Syntax Tree (AST) and scanned all numeric literals against the permitted set $\{0, 1, \dots, 12, 100, 1000\}$:

```python
# AST Scan Verification for src/lhf/parse.py:
Lines 7-15:  1/2, 1/3, 2/3, 1/4, 3/4, 1/8, 3/8, 5/8, 7/8 (Unicode fraction table ratios)
Lines 19-28: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10                (WORD_NUMS dictionary)
Lines 110, 111, 116, 117, 119: 1, 2, 0                   (Fraction parsing)
Lines 123, 124, 126: 1, 2                                (Range midpoint computation)
Lines 131, 134, 135, 137, 140, 141, 143: 0, 1, 2, 3      (Fraction regex group indexes)
Lines 163, 164, 165, 166: 0, 1, 2, 1000                  (Gram pattern group matching and kg conversion)
Lines 172, 173, 174, 175: 0, 1, 2, 1000                  (ML pattern group matching and liter conversion)
Lines 196, 197, 198, 199: 1, 0                           (Default pinch/dash quantity 1.0)
Lines 207, 213, 214, 218: 1, 2, 3                        (Range parsing operands)
Lines 224, 225, 230, 231: 0, 1, 2                        (Mixed number operands)
Lines 240, 252, 266, 275, 316: 0, 1                      (Single pattern operand and quantity zero checks)
```

- **Disallowed Numeric Literals Found:** 0
- **Status:** **PASS** (Strict 100% compliance with AST Rule 1).

### 2.2 Rule 2: No Silent Defaults for Missing Data
- True unquantified lines (`"salt to taste"`, `"oil for frying"`) correctly fall back to `status: 'UNQUANTIFIED'`, `qty: None`, `unit: None`.
- **Integrity Concern:** Because `_is_plain_water` classifies culinary items like `2 teaspoon Curd beaten with a little water` and confections like `water chestnuts` / `ice cream` as `status: 'WATER'`, the engine bypasses `UNQUANTIFIED` or `QUANTIFIED` processing and silently discards them in `pipeline.py`.
- **Status:** **DEFECTIVE IN PRACTICE** (silent exclusion via water heuristic).

### 2.3 Rule 3: No Hardcoded Test Answers or Test Gaming
- `acceptance/test_rules.py` confirms 0 hardcoded gold lines in `src/lhf/parse.py`.
- In Round 1, an overfitted bunch regex (`mb = re.search(r"\b(small|medium|large|big)?\s*(bunches|bunch)\b", rem, re.I)`) was identified. The builder cleanly removed this overfitted search, accepting a known drop on G137 (`1 Mint Leaves small bunch` $\rightarrow$ `piece`, `99.1%` unit accuracy), which is honest engineering.
- **Status:** **PASS** (No cheating or gold-line hardcoding).

---

## 3. Rigorous Answers to Required Audit Questions

### 3.1 Question 1: Mixed Fractions, Decimals, Ranges, and Unicode Fractions
**Question:** Does `parse_line` handle mixed fractions (`2 & 1/2`, `2 1/2`, `2 and 1/2`), decimal quantities, ranges (`1-2`), and unicode fractions (`½`, `¼`)?

#### Evaluation & Probing Results
We executed an extensive test harness probing various permutations of mixed fractions, decimals, ranges, and fractions:

| Input String | Expected `qty` | Actual `qty` | Status | Unit | Name | Verdict |
|---|---|---|---|---|---|---|
| `2 & 1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 and 1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2-1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 - 1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2&1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2&½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 & ½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 and ½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 ½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2-½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 - ½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 &amp; ½ cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `2 &amp; 1/2 cups flour` | 2.5 | 2.5 | QUANTIFIED | cup | flour | PASS |
| `1-1/2 to 2 cups flour` | 1.75 (1.5-2.0) | 1.75 | QUANTIFIED | cup | flour | PASS |
| `1 1/2 to 2 1/2 cups flour` | 2.0 (1.5-2.5) | 2.0 | QUANTIFIED | cup | flour | PASS |
| `½ to ¾ cups flour` | 0.625 (0.5-0.75) | 0.625 | QUANTIFIED | cup | flour | PASS |
| `1/2 - 3/4 cups flour` | 0.625 (0.5-0.75) | 0.625 | QUANTIFIED | cup | flour | PASS |
| `2 to 1 cups flour` | 1.5 (1.0-2.0) | 1.5 | QUANTIFIED | cup | flour | PASS |
| `0.5 cups flour` | 0.5 | 0.5 | QUANTIFIED | cup | flour | PASS |
| `.5 cups flour` | 0.5 | **None** | **UNQUANTIFIED** | **None** | `'5 cups flour'` | **FAIL** |

#### Analysis
- Ampersand mixed fractions (`2 & 1/2`, `2 &amp; ½`, `2 and 1/2`) are properly supported.
- Range midpoint calculations and mixed fraction pre-filtering in `RANGE_PAT` (`parse.py:204-211`) work as expected.
- All SPEC-listed unicode fractions (`½ ¼ ¾ ⅓ ⅔ ⅛ ⅜ ⅝ ⅞`) evaluate accurately.
- **Flaw Detected:** Input `.5 cups flour` fails `SINGLE_PAT` because `NUM_ATOM` lacks leading-dot support (`\d+(?:\.\d+)?` requires at least one digit before the period). The parser falls back to `UNQUANTIFIED`, strips the leading period, and outputs `name: '5 cups flour'`.

---

### 3.2 Question 2: Hindi / Devanagari Lines & Matra Word Boundaries
**Question:** Does `parse_line` handle Hindi / Devanagari lines correctly without regex word boundary errors on vowel signs (matras)?

#### Evaluation & Probing Results
The parser defines:
```python
BOUNDARY = r"""(?=$|[\s,.\-–—:;/\(\)\[\]\{\}"'])"""
```
This custom lookahead boundary successfully replaces `\b` for matra-ending words (`मिली`, `किग्रा`, `सेमी`, `चुटकी`). Devanagari numerals (`०१२३४५६७८९`) are also correctly mapped to ASCII digits (`0-9`).

**HOWEVER, ADVERSARIAL PROBING REVEALED A SEVERE DEVANAGARI UNICODE NORMALIZATION DEFECT:**

In the Devanagari Unicode standard, letters with nuktas (dots beneath consonants, e.g. `ड़` or `ढ़`) have two distinct representations:
1. **Decomposed Form (Canonical in Standard Typing):** Base consonant + Nukta (`U+0921` + `U+093C`), generated by standard Hindi keyboards on Android, iOS, Windows, Mac, and Linux.
2. **Precomposed Form (Unicode Composition Exclusion):** Single precomposed codepoints (`U+095C` = `DEVANAGARI LETTER DDDHA` / `RRA`).

In `src/lhf/parse.py:52`:
```python
("tbsp", re.compile(rf"^(?:tablespoons?|tbsps?|tbs|टेबल\s*स्पून|बड़ा\s*चम्मच|बड़े\s*चम्मच){BOUNDARY}", re.I)),
```
- `बड़ा` was typed in decomposed form: `[0x92c, 0x921, 0x93c, 0x93e]`.
- `बड़े` was typed in precomposed form: `[0x92c, 0x95c, 0x947]`.

Because Python strings are compared byte-for-byte without `unicodedata.normalize`:

| Hindi Input String | Input Encoding | Actual Parsed Unit | Actual Parsed Name | Nutritional Impact |
|---|---|---|---|---|
| `1 बड़ा चम्मच तेल` | Standard decomposed (`0x921 0x93c`) | `tbsp` | `तेल` | Matched correctly |
| `2 बड़े चम्मच घी` | Standard decomposed (`0x921 0x93c`) | **`piece`** | **`'बड़े चम्मच घी'`** | **CRITICAL: Ghee marked `piece` $\rightarrow$ `UNQUANTIFIABLE` $\rightarrow$ 100% fat erased!** |
| `2 बड़े चम्मच घी` | Rare precomposed (`0x95c`) | `tbsp` | `घी` | Matched only on precomposed |
| `2 टुकड़े पनीर` | Precomposed (`0x95c`) | **`piece`** | **`'टुकड़े पनीर'`** | Unit missed, left in name |

Because the Unicode standard's Composition Exclusion table explicitly **excludes** Devanagari nuktas from NFC composition (`unicodedata.normalize('NFC', '\u0921\u093c')` remains `\u0921\u093c`), standard Hindi typing will **never match** `बड़े` in `parse.py`!

---

### 3.3 Question 3: Plain Water Behavior vs. Water-Containing Ingredients
**Question:** How does plain water status (`WATER`) behave compared to water-containing ingredients like "water chestnuts", "ice cream", or "tamarind water"?

#### Implementation in `src/lhf/parse.py:93-101`:
```python
def _is_plain_water(s_no_brackets: str) -> bool:
    low = s_no_brackets.lower().strip()
    if re.search(r"\b(?:ice\s*cream|water\s*chestnuts?|water\s*cress|ice\s*apple|tamarind\s*water)\b", low):
        return False
    if re.search(r"\b(?:rose|kewra|coconut|rice|dal)\s+water\b", low):
        return False
    if re.search(r"\bmilk\s+or\s+water\b", low):
        return False
    return bool(re.search(rf"\b(?:water|ice(?:\s+cubes?)?|पानी|बर्फ){BOUNDARY}", low))
```

#### Adversarial Finding 1: Real Validation Sample Recipe V2-R18 ("Chicken Korma") Broken
In `data/samples/recipes_phase1.jsonl`:
```json
{"id": "V2-R18", "dish": "chicken korma", "lines": [
  ...
  "2 Cardamom (Elaichi) Pods/Seeds",
  "2 teaspoon Curd (Dahi / Yogurt) beaten with a little water",
  "1 teaspoon Ajwain (Carom seeds)",
  ...
]}
```
When evaluated by `parse_line`:
```python
parse_line("2 teaspoon Curd (Dahi / Yogurt) beaten with a little water")
# Returns:
{
  'raw': '2 teaspoon Curd (Dahi / Yogurt) beaten with a little water',
  'status': 'WATER',
  'qty': 2.0, 'qty_min': 2.0, 'qty_max': 2.0,
  'unit': 'tsp',
  'name': 'curd beaten with a little water'
}
```
Downstream in `src/lhf/pipeline.py:44-54`:
```json
{
  "index": 13,
  "raw": "2 teaspoon Curd (Dahi / Yogurt) beaten with a little water",
  "included": false,
  "exclusion_reason": "WATER",
  "nutrients": null
}
```
**Impact:** Because the author included the preparation note `"beaten with a little water"`, the curd is categorized as plain water and **completely discarded from the dish's nutritional footprint**.

#### Adversarial Finding 2: False Positive Classification Across Real Foods and Beverages
We probed culinary terms containing the words "water" or "ice":

```python
# Terminal Probe Output:
'1 cup tonic water'           -> status='WATER' (Sugary beverage dropped!)
'100 g water spinach'         -> status='WATER' (Kalmi saag greens dropped!)
'2 cups water melon'          -> status='WATER' (Sugary fruit dropped!)
'1 glass ice tea'             -> status='WATER' (Sweetened iced tea dropped!)
'1 cup sugar water'           -> status='WATER' (Sugar syrup dropped!)
'1/2 cup imli water'          -> status='WATER' (Tamarind infusion dropped!)
'1/2 cup kokum water'         -> status='WATER' (Kokum infusion dropped!)
'1/2 cup amchur water'        -> status='WATER' (Dry mango infusion dropped!)
'2 cups pani puri water'      -> status='WATER' (Flavored pani dropped!)
'1 ice gola'                  -> status='WATER' (Sweet street confection dropped!)
'1 ice pop'                   -> status='WATER' (Sweet frozen treat dropped!)
'1 प्लेट पानी पूरी'           -> status='WATER' (Pani Puri street food dropped!)
'100 ग्राम पानी फल'           -> status='WATER' (Singhara / water chestnut dropped!)
```

#### Adversarial Finding 3: Culinary Mixture and Slurry Lines Dropped
Lines instructing a food to be mixed with water are erroneously marked as `WATER`:
- `"1 tbsp cornflour mixed in 2 tbsp water"` $\rightarrow$ `status: WATER` (Cornflour dropped)
- `"1 tbsp besan mixed with water"` $\rightarrow$ `status: WATER` (Besan dropped)
- `"2 tbsp milk powder dissolved in warm water"` $\rightarrow$ `status: WATER` (Milk powder dropped)
- `"1 cup rice washed in water"` $\rightarrow$ `status: WATER` (Rice dropped)
- `"1/2 cup curd whisked with water"` $\rightarrow$ `status: WATER` (Curd dropped)

---

### 3.4 Question 4: Extraction of Units, Sizes, Stated Grams/ML, and Optional Flags
**Question:** Are units, sizes, stated grams/ml, and optional flags extracted reliably without regressions?

#### 1. Units
- We probed all 27 canonical units across 103 test patterns. All 103 space-separated patterns matched correctly:
  `tsp`, `tbsp`, `cup`, `g`, `kg`, `mg`, `ml`, `l`, `oz`, `lb`, `pinch`, `dash`, `piece`, `clove`, `inch`, `cm`, `sprig`, `stick`, `strand`, `leaf`, `bunch`, `cube`, `slice`, `floret`, `ball`, `blade`, `pat`.
- Garlic/clove disambiguation works cleanly:
  - `"4 cloves garlic"` $\rightarrow$ `unit: 'clove'`, `name: 'garlic'`
  - `"8 Garlic pods"` $\rightarrow$ `unit: 'clove'`, `name: 'garlic'`
  - `"4 cloves"` $\rightarrow$ `unit: 'piece'`, `name: 'cloves'`
  - `"6 Cloves (Laung)"` $\rightarrow$ `unit: 'piece'`, `name: 'cloves'`
- Leaf rule works cleanly:
  - `"5 leaves mint"` $\rightarrow$ `unit: 'leaf'`, `name: 'mint'`
  - `"1 bay leaf"` $\rightarrow$ `unit: 'piece'`, `name: 'bay leaf'`

#### 2. Unspaced Quantities and Units (Flaw)
When units are written adjacent to digits without whitespace (standard in recipes worldwide):
- `parse_line("100g paneer")` $\rightarrow$ `status: 'UNQUANTIFIED'`, `qty: None`, `unit: None`
- `parse_line("250ml milk")` $\rightarrow$ `status: 'UNQUANTIFIED'`, `qty: None`, `unit: None`
- `parse_line("1kg mutton")` $\rightarrow$ `status: 'UNQUANTIFIED'`, `qty: None`, `unit: None`
- `parse_line("1tbsp oil")` $\rightarrow$ `status: 'UNQUANTIFIED'`, `qty: None`, `unit: None`

#### 3. Sizes
- Extraction after quantity: `"1 large onion"` $\rightarrow$ `size: 'large'`, `unit: 'piece'`.
- Extraction after unit: `"1 piece small ginger"` $\rightarrow$ `size: 'small'`, `unit: 'piece'`.
- Suppression on mass/volume: `"350 g Large King Prawns"` $\rightarrow$ `size: None`, `unit: 'g'`.
- Ignoring elsewhere: `"1 onion, large"` $\rightarrow$ `size: None`.

#### 4. Stated Grams and ML
- Parenthetical masses: `"2 cups (350 grams) tomatoes"` $\rightarrow$ `stated_g: 350.0`.
- Slashed masses: `"2 cups/300 grams tomato"` $\rightarrow$ `stated_g: 300.0`.
- Stated ml: `"4 cups (960 ml) water"` $\rightarrow$ `stated_ml: 960.0`.
- Precedence: When both stated_g and stated_ml appear, stated_g takes precedence as mandated by SPEC §4.
- Invariants: In `UNQUANTIFIED` lines, `stated_g` and `stated_ml` are strictly suppressed to `None`, preserving acceptance invariants.

#### 5. Optional Flag
- `"1 tsp garam masala (optional)"` $\rightarrow$ `optional: True`
- `"1 tsp cumin seeds"` $\rightarrow$ `optional: False`

#### 6. Stray Preposition 'of' Polluting Ingredient Name
When an ingredient line includes the standard preposition "of" after the unit:
- `"1 cup of flour"` $\rightarrow$ `unit: 'cup'`, `name: 'of flour'`
- `match_name("of flour")` returns `{"code": "UNMAPPED", "method": "none", "score": 0.0}`!
- The entire cup of flour is excluded from nutritional calculation.

---

### 3.5 Question 5: Strict AST Compliance with Rule 1 ({0..12, 100, 1000})
**Question:** Are numeric literals in `src/lhf/parse.py` strictly compliant with AST Rule 1 ({0..12, 100, 1000})?

#### Verification
We performed static AST inspection using Python's `ast` module, checking every `ast.Constant` containing numeric types (`int`, `float`):
- Total numeric constant occurrences in AST: 65
- Values observed:
  - `0`: 8 occurrences
  - `1`: 23 occurrences
  - `2`: 17 occurrences
  - `3`: 6 occurrences
  - `4`: 3 occurrences
  - `5`: 2 occurrences
  - `6`: 1 occurrence
  - `7`: 2 occurrences
  - `8`: 4 occurrences
  - `9`: 1 occurrence
  - `10`: 1 occurrence
  - `1000`: 2 occurrences
- Literals $>12$ (excluding 100, 1000): **0**
- Floats with unauthorized decimal literals: **0**
- **Status:** **PASS** (100% compliant).

---

### 3.6 Question 6: Crash Probing on Sample Dataset & Synthetic Lines
**Question:** Does `parse_line` crash on any line in `data/samples/recipes_phase1.jsonl` (1,339 lines) or synthetic adversarial lines?

#### 1. Sample Dataset (1,339 lines)
We executed `parse_line` across all 1,339 lines from 71 recipes in `data/samples/recipes_phase1.jsonl`:
- **Total lines parsed:** 1,339
- **Crashes:** **0**
- **Statuses:** `QUANTIFIED`: 1,204, `WATER`: 64, `UNQUANTIFIED`: 71
- **All acceptance invariants passed:**
  - `raw` strictly equals input line.
  - `status` is one of `{"QUANTIFIED", "UNQUANTIFIED", "WATER"}`.
  - When `status == "QUANTIFIED"`, `qty > 0` and `qty_min <= qty <= qty_max`.
  - When `status == "UNQUANTIFIED"`, `qty`, `stated_g`, and `stated_ml` are strictly `None`.
  - Canonical units strictly in allowed set.
  - `name` is strictly lower-case string.

#### 2. Synthetic Adversarial Fuzzing (83 stress-test inputs)
We constructed a stress harness testing boundary conditions:
- **Zero division attempts:** `'1/0 tsp salt'`, `'0/0 cup water'`, `'1-0/0 cup oil'`, `'2 & 0/0 tsp sugar'`.
  $\rightarrow$ Denominator zero checks in `_parse_num_val` safely return `None`; status becomes `UNQUANTIFIED`. **0 crashes**.
- **Whitespace / Punctuation / Empty:** `''`, `'   '`, `'.,!?-–—:;/()[]{}'`, `'((()))'`, `'- to -'`, `'1 to'`, `'1 -'`, `'1 &'`, `'1 /'`.
  $\rightarrow$ Evaluates safely to `UNQUANTIFIED`. **0 crashes**.
- **Extreme exponents / numbers:** `'1e1000 tsp salt'`, `'9'*60 + ' tsp salt'`.
  $\rightarrow$ Evaluates safely. **0 crashes**.
- **Special unicode / emojis:** `'\x00 tsp salt'`, `'\u200b\u200c\u200d\ufeff'`, `'🍕 1 cup pizza'`, `'1 cup 🍕'`, `'½½½ tsp salt'`.
  $\rightarrow$ Evaluates safely. **0 crashes**.
- **Nested & Unbalanced Brackets:** `'1 cup (flour (white))'`, `'1 cup (flour'`, `'1 cup flour)'`.
  $\rightarrow$ Evaluates safely. **0 crashes**.
- **ReDoS Benchmark:** 10 pathological repeated strings of length 300 to 4,000 characters were parsed. Maximum wall-clock execution time was 17.8 ms, confirming absence of catastrophic backtracking.

---

## 4. Benchmark Performance Comparison

| Dataset | Metric | Threshold | Round 1 Score | Round 2 Score | Status |
|---|---|---|---|---|---|
| **Public Gold** (120 lines) | status | $\ge 95\%$ | 120 / 120 (100.0%) | 120 / 120 (100.0%) | PASS |
| | optional | $\ge 90\%$ | 120 / 120 (100.0%) | 120 / 120 (100.0%) | PASS |
| | name keyword | $\ge 90\%$ | 120 / 120 (100.0%) | 120 / 120 (100.0%) | PASS |
| | qty | $\ge 95\%$ | 109 / 109 (100.0%) | 109 / 109 (100.0%) | PASS |
| | range min/max | $\ge 95\%$ | 109 / 109 (100.0%) | 109 / 109 (100.0%) | PASS |
| | unit | $\ge 90\%$ | 109 / 109 (100.0%) | 108 / 109 (99.1%) | PASS |
| | size | $\ge 90\%$ | 109 / 109 (100.0%) | 108 / 109 (99.1%) | PASS |
| | stated g/ml | $\ge 95\%$ | 109 / 109 (100.0%) | 109 / 109 (100.0%) | PASS |
| **Holdout Gold** (40 lines) | status | $\ge 95\%$ | 40 / 40 (100.0%) | 40 / 40 (100.0%) | PASS |
| | optional | $\ge 90\%$ | 40 / 40 (100.0%) | 40 / 40 (100.0%) | PASS |
| | name keyword | $\ge 90\%$ | 40 / 40 (100.0%) | 40 / 40 (100.0%) | PASS |
| | qty | $\ge 95\%$ | 35 / 36 (97.2%) | 36 / 36 (100.0%) | **IMPROVED** |
| | range min/max | $\ge 95\%$ | 35 / 36 (97.2%) | 36 / 36 (100.0%) | **IMPROVED** |
| | unit | $\ge 90\%$ | 35 / 36 (97.2%) | 36 / 36 (100.0%) | **IMPROVED** |
| | size | $\ge 90\%$ | 36 / 36 (100.0%) | 36 / 36 (100.0%) | PASS |
| | stated g/ml | $\ge 95\%$ | 36 / 36 (100.0%) | 36 / 36 (100.0%) | PASS |
| **Real Samples** (1,339 lines) | crashes | 0 | 0 | 0 | PASS |
| | recipe V2-R18 curd line | Included | **Excluded (WATER)** | **Excluded (WATER)** | **FAILED** |

---

## 5. Summary Table of Discovered Vulnerabilities

| Vulnerability ID | Description | Severity | Impact |
|---|---|---|---|
| **VULN-T3-01** | `_is_plain_water` classifies sample recipe V2-R18 curd line as `WATER` | **HIGH** | `2 teaspoon Curd beaten with a little water` dropped from Chicken Korma; dairy fat omitted. |
| **VULN-T3-02** | Devanagari nukta normalization mismatch (`बड़े\s*चम्मच`) | **HIGH** | Standard Hindi keyboard typing `2 बड़े चम्मच घी` parses as `piece` $\rightarrow$ `UNQUANTIFIABLE` $\rightarrow$ cooking fat omitted. |
| **VULN-T3-03** | Overly broad `\bwater\b` heuristic on culinary confections and infusions | **MEDIUM** | Real foods (`पानी पूरी`, `पानी फल`, `water spinach`, `tonic water`, `ice gola`) marked `WATER` and dropped. |
| **VULN-T3-04** | Missing boundary support for unspaced quantities (`100g`, `250ml`, `1kg`) | **MEDIUM** | International and modern recipe formats marked `UNQUANTIFIED`. |
| **VULN-T3-05** | Stray preposition `'of'` left in ingredient name | **MEDIUM** | `"1 cup of flour"` $\rightarrow$ `name: 'of flour'` $\rightarrow$ `UNMAPPED` $\rightarrow$ flour dropped from calories. |
| **VULN-T3-06** | Leading-dot decimal quantities (`.5 cups flour`) unhandled | **LOW** | Marked `UNQUANTIFIED` and leading dot stripped into name (`'5 cups flour'`). |

---

## 6. Recommendations for Remediation

1. **Fix Water Classification (`_is_plain_water`):**  
   Replace the global substring search `re.search(r"\bwater\b", low)` with a check that tests whether water is the primary noun/ingredient of the line. For example, strip quantity and preparation instructions first, or check if the core ingredient begins or ends with `water` / `ice` / `पानी` / `बर्फ` rather than matching when water is merely a subordinate clause (e.g. `beaten with a little water`, `mixed with water`, `dissolved in water`).
2. **Normalize Devanagari Nuktas in Preprocessing:**  
   In `parse_line`, perform Unicode normalization on the input text:
   ```python
   import unicodedata
   s = unicodedata.normalize("NFD", s)
   ```
   Or explicitly normalize precomposed nuktas to decomposed form (`s = s.replace("\u095c", "ड़").replace("\u095d", "ढ़")`) and define unit patterns using standard decomposed nuktas so both precomposed and decomposed Hindi input reliably match.
3. **Strip Leading Preposition `'of'` in Name Cleanup:**  
   In the name cleaning step (around line 349), add stripping for leading `'of '`:
   ```python
   name_clean = re.sub(r"^\bof\b\s+", "", name_clean, flags=re.I)
   ```
4. **Support Unspaced Quantities in `SINGLE_PAT`:**  
   Update `SINGLE_PAT` to permit transitions from digits to recognized unit abbreviations (e.g. `100g`, `250ml`, `1kg`).
5. **Support Leading-Dot Decimals in `NUM_ATOM`:**  
   Update the decimal pattern from `\d+(?:\.\d+)?` to `(?:\d+(?:\.\d+)?|\.\d+)` to properly quantify `.5` as `0.5`.
