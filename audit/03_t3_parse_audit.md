# Adversarial Code and Data Audit: Task T3 (Ingredient Line Parser)

**Auditor:** Adversarial Code & Data Auditor (Red Teamer)  
**Date:** 2026-11-10  
**Target Files:**
- `src/lhf/parse.py`  
**Associated Test Files:**
- `tests/test_t3.py`
- `acceptance/test_t3_parse.py`
- `acceptance/gold/gold_public.json`  
**Reference Holdout Dataset:**
- `~/subjects/CGAS/lhf_holdout/gold_holdout.json`  
**Specification Reference:** `docs/SPEC.md` §4 (T3: parsing one ingredient line), `docs/SPEC.md` §1 (Package layout & Integrity rules), `AGENTS.md`

---

## 1. Executive Summary & Verdict

### **Verdict: MAJOR FLAWS**

The implementation of Task T3 in `src/lhf/parse.py` successfully passes the local unit tests (`tests/test_t3.py`) and achieves 100% accuracy on the public acceptance benchmark (`acceptance/gold/gold_public.json`). Furthermore, static AST analysis confirms **strict compliance with Rule 1** (no invented numbers; only literals 0–12, 100, and 1000 appear).

However, deep adversarial analysis, probe testing with real-world culinary lines, and evaluation against the unseen reference holdout dataset (`gold_holdout.json`) reveal that the module suffers from **major algorithmic defects, regex blunders, overfitting to public test fixtures, and silent nutrient exclusion vulnerabilities**:

1. **Failure on Reference Holdout (`gold_holdout.json` G058):** The parser drops from 100% on public gold to 97.2% on holdout due to line G058 (`2 &amp; ½ cups pureed tomatoes  (from 4 medium tomatoes)`). While `html.unescape` is invoked, `NUM_ATOM` lacks support for `&` or `and` between whole numbers and fractions. The parser parses `qty: 2.0`, defaults `unit: 'piece'`, and dumps `& ½ cups pureed tomatoes` into the ingredient name. In real recipes (`recipes_phase1.jsonl`), this causes `1 &amp; ½ tablespoons oil` to drop to `unit: 'piece'`, causing `grams_for` to fail as `UNQUANTIFIABLE` and **completely omitting cooking oil and its fat/calorie budget from the recipe**.
2. **Devanagari Vowel Sign (Matra) `\b` Bug (6 of 11 Hindi Unit Synonyms Broken):** In Python's built-in `re` module, Devanagari dependent vowel signs (matras: `ी`, `ा`, `े`, etc.) are category `Mn`/`Mc` and classified as `\W` (non-word). Blindly appending `\b` to patterns causes every unit synonym ending in a matra (`मिली`, `किग्रा`, `सेमी`, `टुकड़ा`, `टुकड़े`, `चुटकी`) to **fail to match whenever followed by whitespace or punctuation**. For example, `1 किग्रा आलू` parses as `unit: 'piece'`, `stated_g: None`, and `name: 'किग्रा आलू'`.
3. **Inch Symbol (`"`) Broken by `\b`:** The canonical synonym `"` for inches (`("inch", re.compile(r'^(?:inches|inch|\"|इंच)\b', re.I))`) never matches when followed by whitespace because `"` is punctuation (`\W`). `1" ginger` parses as `unit: 'piece'` and `name: '" ginger'`.
4. **Overly Broad Water Heuristic Leading to Silent Fat & Calorie Erasure:** `_is_plain_water` classifies any line matching `\b(?:water|ice(?:\s+cubes?)?|पानी|बर्फ)\b` as `status: WATER` (unless preceded by rose/kewra/coconut/rice/dal). Consequently, **`1 cup ice cream`**, **`1 cup water chestnuts`**, **`1 cup tamarind water`**, and **`1 cup ice apple`** are classified as `WATER` and discarded by `pipeline.py` (`exclusion_reason: WATER`), completely deleting significant dietary fat and sugar from nutritional sums!
5. **Direct Spec Violation on `dash` Without Number:** SPEC §4 explicitly mandates: *"pinch" or "dash" with no number means qty 1.* `parse.py` contains the comment `# Check pinch / dash at start without number`, but line 173 implements regex matching *only for pinch*. `dash of pepper` is discarded as `UNQUANTIFIED`.
6. **Direct Spec Violation on Leaf Rule (`"5 leaves mint"`):** SPEC §4 states: *leaf: leaf, leaves, only when the name is something else (e.g. "5 leaves mint")*. The builder wrote a hardcoded hack (`if re.search(r"\b(bay|curry|methi|fenugreek|coriander|cilantro|mint)\b", s.lower()): unit = "piece"`) that directly turns `"5 leaves mint"` into `unit: 'piece'` and `name: 'leaves mint'`.
7. **Spurious Inversion of Spaced Hyphen Mixed Numbers:** `m_mix` enforces strict absence of whitespace around hyphens. Input `1 - 1/2 cups` fails `m_mix` and falls into `RANGE_PAT`, computing a range from 1 to 0.5 with midpoint `0.75` (halving the intended quantity).
8. **Range Truncation on Hyphenated Mixed Numbers:** `m_mix` is checked *before* `RANGE_PAT`. A line like `1-1/2 to 2 cups flour` is immediately truncated at `1-1/2`, yielding `qty: 1.5, unit: 'piece', name: 'to 2 cups flour'`.
9. **Overfitting to Public Line G137:** Regex `mb = re.search(r"\b(small|medium|large|big)?\s*(bunches|bunch)\b", rem, re.I)` searches anywhere in `rem` specifically to catch G137 (`1 Mint Leaves (Pudina) small bunch, chopped`). As a side effect, `2 tomatoes for a bunch of people` sets `unit: 'bunch'` and mangles name to `'tomatoes for a of people'`.
10. **Unhandled `ZeroDivisionError` & Acceptance Invariant Violation on Zero Qty:** `_parse_num_val` does not check denominator zero (`1/0 tsp salt` crashes with uncaught `ZeroDivisionError`). Furthermore, `0 tsp salt` returns `status: QUANTIFIED`, `qty: 0.0`, violating the core invariant that quantified lines must have `qty > 0`.

---

## 2. Integrity Rules & Static Analysis Checks

### 2.1 Rule 1: No Invented Numbers (AST Analysis)
We parsed `src/lhf/parse.py` into an Abstract Syntax Tree (AST) and scanned all numeric literals against the allowed set $\{0, 1, \dots, 12, 100, 1000\}$:

```python
# AST Scan Results for src/lhf/parse.py:
Lines 7-15:  1/2, 1/3, 2/3, 1/4, 3/4, 1/8, 3/8, 5/8, 7/8 (Fractions written with ints 1-8)
Lines 19-28: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10                (WORD_NUMS dictionary values)
Line 118:    2                                            (Range midpoint divisor)
Line 152:    1000                                         (kg to g conversion factor)
Line 161:    1000                                         (liter to ml conversion factor)
Line 181:    1                                            (pinch default qty)
Line 209:    2                                            (Range midpoint divisor)
```

- **Disallowed Numeric Literals Found:** 0
- **Status:** **PASS** (100% compliant with Rule 1).

### 2.2 Rule 2: No Silent Defaults for Missing Data
- Lines where no quantity is recognized fall back to `status: 'UNQUANTIFIED'`, `qty: None`, `unit: None`.
- However, as detailed in Section 3.4, high-calorie foods like **ice cream** and culinary ingredients like **water chestnuts** are silently converted to `status: 'WATER'`, which the pipeline then silently drops.
- **Status:** **DEFECTIVE IN PRACTICE** (silent exclusion via water classification).

### 2.3 Rule 3: No Hardcoded Test Answers or Test Gaming
- `acceptance/test_rules.py` passed with 0 occurrences of full gold line strings.
- **However, test gaming via overfitted regexes was detected:**
  * Line 283: `mb = re.search(r"\b(small|medium|large|big)?\s*(bunches|bunch)\b", rem, re.I)` was injected specifically to pass line G137 in `gold_public.json`.
  * Line 269: `if re.search(r"\b(bay|curry|methi|fenugreek|coriander|cilantro|mint)\b", s.lower()): unit = "piece"` was hardcoded to satisfy G002 and G115 (`1 bay leaf`), directly breaking general parsing of leaf units.
- **Status:** **SUSPICIOUS / OVERFITTED**

---

## 3. Detailed Technical Breakdown of Vulnerabilities & Flaws

### 3.1 Flaw 1: Holdout Failure on Ampersand Mixed Numbers (`&amp;` / `&` / `and`)
**Location:** `src/lhf/parse.py:31-37, 188-220`

#### Specification Requirement (SPEC §4)
> *"Quantities: digits, decimals, '1/2', unicode fractions (½ ¼ ¾ ⅓ ⅔ ⅛), mixed numbers ('1½', '1 1/2', '2 &amp; ½' means 2.5; decode HTML entities first)."*

#### Root Cause Analysis
In `src/lhf/parse.py`:
```python
NUM_ATOM = (
    r"(?:\d+\s*-\s*\d+/\d+|\d+\s*-\s*[½⅓⅔¼¾⅛⅜⅝⅞]|\d+\s+\d+/\d+|\d+\s*[½⅓⅔¼¾⅛⅜⅝⅞]|"
    r"[½⅓⅔¼¾⅛⅜⅝⅞]|\d+/\d+|\d+(?:\.\d+)?)"
)
```
Although `s = html.unescape(text)` converts `&amp;` to `&`, `NUM_ATOM` only permits whitespace or hyphens between the whole number and fraction. It has **no provision for `&` or `and`**.

When evaluating G058 (`2 &amp; ½ cups pureed tomatoes  (from 4 medium tomatoes)`):
1. `s_clean` becomes `2 & ½ cups pureed tomatoes`.
2. `SINGLE_PAT.match(s_clean)` matches only `2`.
3. `qty` becomes `2.0`.
4. `rem` becomes `& ½ cups pureed tomatoes`.
5. No unit regex matches starting with `&`. Unit defaults to `piece`.
6. `name` becomes `& ½ cups pureed tomatoes`.

#### Holdout Test Evaluation Output
```
FAIL [G058]: "2 &amp; ½ cups pureed tomatoes  (from 4 medium tomatoes)"
    - qty (got 2.0, exp 2.5)
    - range (got min=2.0, max=2.0, exp 2.5, 2.5)
    - unit (got piece, exp cup)
    Parsed: {'raw': '2 &amp; ½ cups pureed tomatoes  (from 4 medium tomatoes)', 
             'status': 'QUANTIFIED', 'qty': 2.0, 'qty_min': 2.0, 'qty_max': 2.0, 
             'unit': 'piece', 'size': None, 'stated_g': None, 'stated_ml': None, 
             'optional': False, 'name': '& ½ cups pureed tomatoes'}
```

#### Real Recipe Impact (`data/samples/recipes_phase1.jsonl`)
In real recipe `D1-29`:
`1 &amp; ½ tablespoons oil (use any oil of choice, I used avocado oil)`
- `qty` parses as `1.0` (loss of 0.5 tbsp).
- `unit` parses as `'piece'`.
- When passed to `grams_for(1.0, 'piece', None, None, None, 'T508')`, the basis is `UNQUANTIFIABLE` because cooking oil has no measure for `piece`.
- **Impact:** 1.5 tablespoons (20.7 g, ~180 kcal, 20 g fat) of oil is completely dropped from the dish!

---

### 3.2 Flaw 2: Devanagari Matra Word-Boundary (`\b`) Bug Breaking Hindi Units
**Location:** `src/lhf/parse.py:40, 44, 49-76`

#### Root Cause Analysis
In Python's standard `re` module, a word character `\w` is defined as characters with Unicode categories `Ll, Lu, Lt, Lo, Lm, Nd, Pc`.
Devanagari dependent vowel signs (matras: `ी` U+0940, `ा` U+093E, `े` U+0947, `ु` U+0941) are classified as category `Mn` (Mark, nonspacing) or `Mc` (Mark, spacing combining). **They are NOT word characters (`\W`) in Python `re`!**

A word boundary `\b` requires a transition between `\w` and `\W`. In a string like `"मिली पानी"`:
- The character before the space is `ी` (`\W`).
- The space itself is ` ` (`\W`).
- Because both are `\W`, there is **no word boundary** between `मिली` and the space!

Consequently, `re.compile(r"^(?:...|मिली)\b")` **NEVER matches `मिली` followed by a space!**

#### Affected Unit Definitions & Probes
| Unit | Broken Pattern in `UNIT_DEFS` | Test Input | Expected Unit | Actual Unit | Actual Name |
|---|---|---|---|---|---|
| `ml` | `मिली\b` | `500 मिली दूध` | `ml` | `piece` | `मिली दूध` |
| `kg` | `किग्रा\b` | `2 किग्रा आलू` | `kg` | `piece` | `किग्रा आलू` |
| `cm` | `सेमी\b` | `2 सेमी अदरक` | `cm` | `piece` | `सेमी अदरक` |
| `piece` | `टुकड़ा\b` | `1 टुकड़ा अदरक` | `piece` | `piece` | `टुकड़ा अदरक` |
| `piece` | `टुकड़े\b` | `2 टुकड़े दालचीनी` | `piece` | `piece` | `टुकड़े दालचीनी` |
| `pinch` | `चुटकी\b` | `1 चुटकी नमक` | `pinch` | `piece` | `चुटकी नमक` |

Additionally, this bug breaks `GRAM_PAT` (`किग्रा\b`) and `ML_PAT` (`मिली\b`):
- `1 किग्रा आलू` -> `stated_g: None` (missed 1000 g stated mass!).
- `500 मिली दूध` -> `stated_ml: None` (missed 500 ml stated volume!).

---

### 3.3 Flaw 3: Inch Double-Quote (`"`) Regex Failure
**Location:** `src/lhf/parse.py:62`

#### Specification Requirement (SPEC §4)
> `inch: inch, inches, "`

#### Root Cause Analysis
Line 62 defines:
```python
("inch", re.compile(r'^(?:inches|inch|\"|इंच)\b', re.I))
```
The double quote character `"` is punctuation (`\W`). When followed by a space (e.g. `1" ginger`), both `"` and ` ` are `\W`. The `\b` word boundary check fails.

#### Probe Results
```python
parse_line('1" ginger')
# Expected: unit='inch', name='ginger'
# Actual:   unit='piece', name='" ginger'

parse_line('2" Cinnamon (Dalchini)') # (From data/samples/recipes_phase1.jsonl)
# Expected: unit='inch', name='cinnamon'
# Actual:   unit='piece', name='" cinnamon'
```
The unit defaults to `piece` and a stray quote corrupts the ingredient name.

---

### 3.4 Flaw 4: Overly Broad Water Detection Erasing High-Calorie Foods
**Location:** `src/lhf/parse.py:90-96`

#### Specification Requirement (SPEC §4)
> *"WATER when the ingredient is plain water or ice (any quantity)."*

#### Root Cause Analysis
In `src/lhf/parse.py`:
```python
def _is_plain_water(s_no_brackets: str) -> bool:
    low = s_no_brackets.lower().strip()
    if re.search(r"\b(?:rose|kewra|coconut|rice|dal)\s+water\b", low):
        return False
    if re.search(r"\bmilk\s+or\s+water\b", low):
        return False
    return bool(re.search(r"\b(?:water|ice(?:\s+cubes?)?|पानी|बर्फ)\b", low))
```
The regex tests whether the word `water` or `ice` occurs anywhere in the unbracketed line, with only a tiny hardcoded exception list.

#### Probe Results: Non-Water Foods Classified as WATER
```python
>>> parse_line("1 cup ice cream")["status"]
'WATER'
>>> parse_line("1 scoop vanilla ice cream")["status"]
'WATER'
>>> parse_line("100 g water chestnuts")["status"]
'WATER'
>>> parse_line("1 cup tamarind water")["status"]
'WATER'
>>> parse_line("1 cup ice apple")["status"]
'WATER'
>>> parse_line("1 cup water cress")["status"]
'WATER'
```

#### Downstream Nutritional Impact
In `src/lhf/pipeline.py:44-54`:
```python
if status == "WATER":
    items.append({
        "line_index": i, "raw": raw, "name": name, "code": "WATER",
        "grams": None, "basis": "WATER", "nutrients": {}, "exclusion_reason": "WATER",
    })
```
Any item with status `WATER` is **excluded from nutrient summation**. If a recipe calls for `1 cup ice cream`, it contributes **0 calories, 0 g fat, 0 g sugar**, leading to gross underestimation of the cardiometabolic footprint!

---

### 3.5 Flaw 5: Missing `dash` Quantity Default Rule
**Location:** `src/lhf/parse.py:172-187`

#### Specification Requirement (SPEC §4)
> *"pinch" or "dash" with no number means qty 1.*

#### Root Cause Analysis
The developer authored line 172:
```python
# Check pinch / dash at start without number
m_pinch = re.match(r"^(?:generous\s+pinch|a\s+pinch|pinch|चुटकी\s*भर|चुटकी)\b", s_clean, re.I)
```
The word `dash` is completely missing from the regex pattern!

#### Probe Results
```python
parse_line("dash pepper")
# Expected: status='QUANTIFIED', qty=1.0, unit='dash', name='pepper'
# Actual:   status='UNQUANTIFIED', qty=None, unit=None, name='dash pepper'

parse_line("a dash hot sauce")
# Expected: status='QUANTIFIED', qty=1.0, unit='dash', name='hot sauce'
# Actual:   status='UNQUANTIFIED', qty=None, unit=None, name='a dash hot sauce'
```

---

### 3.6 Flaw 6: Mixed Numbers vs Ranges Operator Precedence & Spacing Bugs
**Location:** `src/lhf/parse.py:103-118, 188-212`

#### Issue A: Spaced Hyphens Inverting Mixed Numbers into Ranges
Lines 103 and 189 use `^(\d+)-(\d+/\d+|[½...])\b` without `\s*`.
When a mixed number has spaces around the hyphen (`1 - 1/2 cups` or `2 - 1/2 cups`):
- `m_mix` fails.
- `RANGE_PAT` (`^({NUM_ATOM})\s*(?:to|–|—|-)\s*({NUM_ATOM})\b`) matches `1` and `1/2` as a range!
- `qty` is calculated as $(1.0 + 0.5) / 2 = \mathbf{0.75}$ instead of $\mathbf{1.5}$!
- `2 - 1/2 cups` calculates as $(2.0 + 0.5) / 2 = \mathbf{1.25}$ instead of $\mathbf{2.5}$!

#### Issue B: Ranges Starting with Hyphenated Mixed Numbers Truncated
In `parse_line`, `m_mix` is checked *before* `RANGE_PAT`:
```python
parse_line("1-1/2 to 2 cups flour")
# Expected: qty=1.75, qty_min=1.5, qty_max=2.0, unit='cup', name='flour'
# Actual:   qty=1.5,  qty_min=1.5, qty_max=1.5, unit='piece', name='to 2 cups flour'
```
`m_mix` matches `1-1/2` and immediately stops, discarding the rest of the range and corrupting the ingredient name.

---

### 3.7 Flaw 7: Spec-Violating Leaf/Leaves Logic
**Location:** `src/lhf/parse.py:268-274`

#### Specification Requirement (SPEC §4)
> `leaf: leaf, leaves, only when the name is something else (e.g. "5 leaves mint")`

#### Root Cause Analysis
Lines 268-274 state:
```python
elif u_name == "leaf":
    if re.search(r"\b(bay|curry|methi|fenugreek|coriander|cilantro|mint)\b", s.lower()):
        unit = "piece"
        rem = u_str + " " + rem
    else:
        unit = "leaf"
```
The developer intended to handle lines like `1 bay leaf`, but in `1 bay leaf`, `bay` precedes `leaf`, so `u_name` is never `leaf` in the first place! The only time `u_name == "leaf"` triggers is when `rem` begins with `leaf` or `leaves`.
Because `mint`, `curry`, `coriander`, and `methi` are in the regex, any line matching the spec's exact example fails:

```python
parse_line("5 leaves mint")
# Spec §4 Expected: unit='leaf',  name='mint'
# Actual:           unit='piece', name='leaves mint'

parse_line("10 leaves basil") # (basil is not in the hardcoded list)
# Actual:           unit='leaf',  name='basil'
```

---

### 3.8 Flaw 8: Overfitting to Public Line G137 Corrupting Ordinary Words
**Location:** `src/lhf/parse.py:283-294`

In `acceptance/gold/gold_public.json`, line G137 is:
`"1 Mint Leaves (Pudina) small bunch, chopped"` (qty: 1, unit: bunch, size: small, name_any: ['mint']).

To force G137 to pass, the builder added line 283:
```python
mb = re.search(r"\b(small|medium|large|big)?\s*(bunches|bunch)\b", rem, re.I)
if mb:
    unit = "bunch"
    ...
    rem = (rem[:mb.start()] + " " + rem[mb.end():]).strip()
```
This regex searches for `bunch` **anywhere** in `rem`. When tested on culinary descriptions:
```python
parse_line("2 tomatoes for a bunch of people")
# Expected: unit='piece', name='tomatoes for a bunch of people'
# Actual:   unit='bunch', name='tomatoes for a of people'
```

---

### 3.9 Flaw 9: Unhandled ZeroDivisionError & Acceptance Invariant Violation
**Location:** `src/lhf/parse.py:127-129, 301-307`

1. **ZeroDivisionError:**
   In `_parse_num_val`:
   ```python
   m = re.match(r"^(\d+)\s*/\s*(\d+)$", s)
   if m:
       return float(m.group(1)) / float(m.group(2))
   ```
   No guard checks whether `float(m.group(2)) == 0`.
   `parse_line("1/0 tsp salt")` crashes with unhandled `ZeroDivisionError: float division by zero`.

2. **Acceptance Invariant Violation on Zero Quantity:**
   `acceptance/test_t3_parse.py:50` enforces:
   ```python
   if p["status"] == "QUANTIFIED":
       check(p["qty"] is not None and p["qty"] > 0, f"QUANTIFIED needs qty > 0: {l[:50]!r}")
   ```
   For input `"0 tsp salt"`, `qty` is parsed as `0.0`. Line 304 checks `elif qty is None: status = "UNQUANTIFIED"`. Because `0.0 is not None`, `status` is set to `QUANTIFIED`, directly violating `qty > 0`.

---

### 3.10 Flaw 10: Punctuation Boundary Bug on `no.` Dropping Size
**Location:** `src/lhf/parse.py:75, 248-257`

In `UNIT_DEFS:75`:
`("piece", re.compile(r"^(?:...|nos?\.?|...)\b", re.I))`
Because `\.?` is followed by `\b`, when `no.` is followed by a space, `no.` cannot match because there is no word boundary between `.` and ` `. The regex matches only `no`, leaving `. ` in `rem`.
Subsequent size matching fails:
```python
parse_line("1 no. large onion")
# Expected: unit='piece', size='large', name='onion'
# Actual:   unit='piece', size=None,    name='large onion'
```
The size is missed and absorbed into the name.

---

## 4. Benchmark Comparison: Public Gold vs. Holdout Gold

We evaluated `src/lhf/parse.py` across all attributes on both datasets:

| Metric | Acceptance Threshold | Public Gold (`gold_public.json`, 120 lines) | Holdout Gold (`gold_holdout.json`, 40 lines) | Status |
|---|---|---|---|---|
| **status** | $\ge 95\%$ | **120 / 120 (100.0%)** | **40 / 40 (100.0%)** | PASS |
| **optional** | $\ge 90\%$ | **120 / 120 (100.0%)** | **40 / 40 (100.0%)** | PASS |
| **name keyword** | $\ge 90\%$ | **120 / 120 (100.0%)** | **40 / 40 (100.0%)** | PASS |
| **qty** | $\ge 95\%$ | **109 / 109 (100.0%)** | **35 / 36 (97.2%)** | **REGRESSION** |
| **range min/max** | $\ge 95\%$ | **109 / 109 (100.0%)** | **35 / 36 (97.2%)** | **REGRESSION** |
| **unit** | $\ge 90\%$ | **109 / 109 (100.0%)** | **35 / 36 (97.2%)** | **REGRESSION** |
| **size** | $\ge 90\%$ | **109 / 109 (100.0%)** | **36 / 36 (100.0%)** | PASS |
| **stated g/ml** | $\ge 95\%$ | **109 / 109 (100.0%)** | **36 / 36 (100.0%)** | PASS |

### Why Did Public Gold Score 100%?
1. `gold_public.json` contains **zero lines** with `&amp;` or `&` in the quantity.
2. `gold_public.json` contains **zero Hindi lines**.
3. `gold_public.json` contains **zero lines** with `"` for inches.
4. `gold_public.json` contains **zero lines** with `ice cream`, `water chestnuts`, or `dash`.
5. The builder tailored regexes (`mb = re.search(...)` for G137; `re.sub(r"/...|or ...")` for G081/G086) specifically to fit public gold lines without generalizing.

---

## 5. Summary Table of Key Issues

| ID | Issue Description | Severity | Spec Section | Direct Consequence |
|---|---|---|---|---|
| **ISSUE-1** | `NUM_ATOM` lacks `&` / `and` fraction support | **MAJOR** | SPEC §4 | Fails G058 holdout; drops 1.5 tbsp cooking oil to `UNQUANTIFIABLE` in recipe D1-29. |
| **ISSUE-2** | Devanagari vowel signs (`\W`) followed by `\b` | **MAJOR** | SPEC §4 | 6 canonical Hindi synonyms (`मिली`, `किग्रा`, `सेमी`, `टुकड़ा`, `टुकड़े`, `चुटकी`) completely broken. |
| **ISSUE-3** | Double quote `"` inch unit followed by `\b` | **MAJOR** | SPEC §4 | `1" ginger` -> `unit: 'piece'`, name corrupted with `"`. |
| **ISSUE-4** | False positive in `_is_plain_water` | **MAJOR** | SPEC §4 | `1 cup ice cream` and `water chestnuts` marked `WATER` and dropped from calories/fat. |
| **ISSUE-5** | `dash` omitted from standalone quantity rule | **MINOR** | SPEC §4 | `dash pepper` marked `UNQUANTIFIED`. |
| **ISSUE-6** | Spaced hyphens invert mixed numbers into ranges | **MODERATE** | SPEC §4 | `1 - 1/2 cups` parsed as 0.75 instead of 1.5. |
| **ISSUE-7** | `m_mix` evaluated before `RANGE_PAT` | **MODERATE** | SPEC §4 | `1-1/2 to 2 cups` truncated to 1.5, unit='piece'. |
| **ISSUE-8** | Leaf unit heuristic breaks spec example | **MODERATE** | SPEC §4 | `"5 leaves mint"` parsed as `unit: 'piece'`, `name: 'leaves mint'`. |
| **ISSUE-9** | Arbitrary `bunch` regex search across string | **MODERATE** | SPEC §4 | Overfitted to G137; corrupts phrases containing "bunch". |
| **ISSUE-10**| ZeroDivisionError and `0 qty` QUANTIFIED status | **MINOR** | SPEC §4 / Acceptance | `1/0` crashes; `0 tsp salt` violates acceptance invariant. |

---

## 6. Recommendations for Remediation

### 6.1 Fix Ampersand Mixed Numbers in `NUM_ATOM`
Update line 31 of `src/lhf/parse.py` to support `&` and `and`:
```python
NUM_ATOM = (
    r"(?:\d+\s*(?:-|&|and)\s*(?:\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])|"
    r"\d+\s+\d+/\d+|\d+\s*[½⅓⅔¼¾⅛⅜⅝⅞]|"
    r"[½⅓⅔¼¾⅛⅜⅝⅞]|\d+/\d+|\d+(?:\.\d+)?)"
)
```

### 6.2 Fix Word Boundary for Matras, Quotes, and Punctuation
Replace `\b` in unit patterns with an explicit boundary that supports Devanagari matras and punctuation:
```python
# Instead of r"^... \b", use a lookahead for whitespace, end-of-string, or non-alphanumeric punctuation:
BOUNDARY = r"(?=$|[\s,.\-–—:;/\(\)\[\]\{\}])"
```
Ensure `मिली`, `किग्रा`, `सेमी`, `टुकड़ा`, `चुटकी`, and `\"` are followed by `BOUNDARY` rather than `\b`.

### 6.3 Restrict Plain Water Detection
Update `_is_plain_water` to match only standalone water or ice cubes, never compound ingredients:
```python
def _is_plain_water(s_no_brackets: str) -> bool:
    low = s_no_brackets.lower().strip()
    # Explicit exclusions for food items containing 'water' or 'ice'
    if re.search(r"\b(?:ice\s*cream|water\s*chestnut|water\s*cress|ice\s*apple|tamarind\s*water)\b", low):
        return False
    if re.search(r"\b(?:rose|kewra|coconut|rice|dal)\s+water\b", low):
        return False
    if re.search(r"\bmilk\s+or\s+water\b", low):
        return False
    return bool(re.search(r"\b(?:water|ice(?:\s+cubes?)?|पानी|बर्फ)\b", low))
```

### 6.4 Implement `dash` Without Number
Update line 173 to include `dash`:
```python
m_pinch = re.match(r"^(?:generous\s+pinch|a\s+pinch|pinch|चुटकी\s*भर|चुटकी|a\s+dash|dash|dashes)\b", s_clean, re.I)
if m_pinch:
    qty = float(1); qty_min = float(1); qty_max = float(1)
    matched_word = m_pinch.group(0).lower()
    unit = "dash" if "dash" in matched_word else "pinch"
    rem = s_clean[m_pinch.end():].strip()
```

### 6.5 Fix Leaf Logic
Honor SPEC §4: if the unit matched is `leaf` and the remaining string is non-empty, the unit is `leaf`:
```python
elif u_name == "leaf":
    if rem.strip():
        unit = "leaf"
    else:
        unit = "piece"
```

### 6.6 Range Precedence and Division Guards
1. Check `RANGE_PAT` before `m_mix`.
2. Allow optional whitespace around hyphens in `m_mix` (`r"^(\d+)\s*-\s*(\d+/\d+|[½...])"`).
3. Guard against `denominator == 0` in `_parse_num_val`.
4. If `qty <= 0`, set `status = "UNQUANTIFIED"`.
