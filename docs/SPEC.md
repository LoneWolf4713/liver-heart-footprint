# SPEC: Phase 1 core engine (architect-authored, protected)

This file defines exactly what Phase 1 builds. Builder sessions implement it; acceptance tests in `acceptance/` check it. If code and this spec disagree, the spec wins. If the spec is silent, choose the simplest option and write the choice in a note (`python3 build.py note --file note.txt`).

## 0. What Phase 1 delivers, in plain English
Given a real recipe (title, servings, ingredient lines as written on the web), the engine:
1. reads each ingredient line into a structured form (quantity, unit, name);
2. finds the matching food in Indian/UK/US composition tables;
3. converts the quantity to grams using a cited measures table, never a guess;
4. adds up nutrients;
5. expresses the per-serving amounts as a share of daily limits (ICMR-NIN 2024 / WHO) and of the average Indian intake (NSO 2025).

Every number in the output traces to a source row. Lines that cannot be handled are excluded with a reason, never silently dropped or defaulted.

Not in Phase 1 (later phases): frying oil uptake, trans fat, "salt to taste" imputation, swaps, atlas, web app, chatbot, recipe fetching from the web.

## 1. Package layout
Python package `lhf` in `src/lhf/`. Run with `PYTHONPATH=src`. Python: `/home/prtyksh/subjects/cgas_env/bin/python` (3.12). Allowed third-party libraries: pandas, numpy, openpyxl. Nothing else.

| Module | Task | Public functions |
|---|---|---|
| `lhf/paths.py`, `lhf/constants.py`, `lhf/composition.py` | T1 | see §2 |
| `lhf/compute.py` | T2 | `sum_nutrients` |
| `lhf/parse.py` | T3 | `parse_line` |
| `lhf/match.py` (+ `data/curated/aliases.csv`) | T4 | `match_name` |
| `lhf/grams.py` | T5 | `grams_for` |
| `lhf/classify.py` | T6 | `classes_for`, `class_totals` |
| `lhf/footprint.py` | T7 | `footprint` |
| `lhf/pipeline.py`, `lhf/cli.py` | T8 | `analyse_recipe`; CLI |
| `experiments/phase1_validation/` | T9 | `run.py` -> `results.json`, `REPORT.md` |

Numeric-literal rule (checked by a test on every task): `src/lhf/*.py` may contain no numeric literals except the values 0-12, 100 and 1000 (0.0 counts as 0; 0.5 is refused). Every other number comes from `data/curated/*.csv` (`constants.csv`, `measures.csv`, `baselines.csv`, `classes.csv`). Fractions in the parser are written as `Fraction(1, 2)` or `1 / 2`.

## 2. T1: constants and composition table
`lhf/paths.py`: `REPO` (repo root, computed from `__file__`), `DATA_RAW`, `DATA_CURATED`.

`lhf/constants.py`: `get(id) -> float` reads `data/curated/constants.csv` (columns id,value,unit,source); unknown id raises `KeyError`.

`lhf/composition.py`:
- `load_table() -> pandas.DataFrame`, cached, indexed by `code` (str). Columns:
  `name, source, energy_kj, energy_kcal, fat_g, sfa_g, mufa_g, pufa_g, tfa_g, carb_g, freesugar_g, fibre_g, protein_g, sodium_mg, water_g, energy_flag`.
  All values per 100 g edible portion.
- Sources, combined into one table (no code appears twice):
  - `IFCT2017`: `data/raw/ifct2017_transcription/ifct2017_compositions.csv`, 542 rows. Column map:
    - `enerc`→energy_kj
    - `fatce`→fat_g
    - `fasat`→sfa_g
    - `fams`→mufa_g
    - `fapu`→pufa_g
    - `fatrn`→tfa_g
    - `choavldf`→carb_g
    - `fsugar`→freesugar_g
    - `fibtg`→fibre_g
    - `protcnt`→protein_g
    - `na`×1000→sodium_mg
    - `water`→water_g

    energy_kcal = energy_kj / KJ_PER_KCAL.
  - `INDB_UK`: `data/raw/indb/UK_fct.xlsx` sheet `Sheet1` (144 rows).
  - `INDB_US`: `data/raw/indb/US_fct.xlsx` sheet `Sheet1` (54 rows).

    Both INDB sheets use the column names directly. sfa/mufa/pufa are mg in the source, so divide by 1000. water_g and tfa_g are not in these sheets, so they are NaN.
- Missing values: for every nutrient except `tfa_g` and `water_g`, a missing value (NaN, "N", "Tr", "NA", blank) becomes 0, exactly as INDB.do does. `tfa_g` and `water_g` stay NaN, meaning unknown.
- Energy defect fix: in the IFCT transcription, the 14 fats and oils (codes T001-T014) have energy 0. For these rows:
  - energy_kj = fat_g × FAT_KJ_PER_G and energy_kcal = fat_g × FAT_KCAL_PER_G;
  - energy_flag = "FAT_ENERGY_DERIVED".

  All other rows have an empty energy_flag.
- `get(code) -> dict` returns one row as a dict, plus `code`. An unknown code raises `KeyError`.
- `nutrients_for(code, grams) -> dict`: each nutrient × grams / 100. Keys are the nutrient columns; NaN stays NaN.

## 3. T2: summing
`lhf/compute.py`:
- `NUTRIENTS`: a tuple of the 12 nutrient column names above.
- `sum_nutrients(items) -> dict`, where `items` is a list of dicts `{"code": str, "grams": float or None}`. It returns:
  - `{"total_g": Σ grams of items with grams, "totals": {nutrient: Σ}, "per_100g": {nutrient: Σ / total_g × 100}}`;
  - `"skipped": [indexes of items with grams None or code not in table]`.

  For `tfa_g` and `water_g`, the total is NaN if any included item has NaN. Report `"unknown_tfa_items"` and `"unknown_water_items"` as lists of indexes.
- The acceptance test reproduces INDB's 1,014 published dishes. It converts INDB's own ingredient units with INDB's own rules (inside the test), then calls `sum_nutrients`.

## 4. T3: parsing one ingredient line
`lhf/parse.py`: `parse_line(text: str) -> dict` with exactly these keys:

| key | type | meaning |
|---|---|---|
| raw | str | the input, unchanged |
| status | str | QUANTIFIED, UNQUANTIFIED or WATER |
| qty | float or None | the main quantity; midpoint for ranges |
| qty_min, qty_max | float or None | range ends (equal to qty when not a range) |
| unit | str or None | canonical unit (list below) |
| size | str or None | small, medium or large |
| stated_g | float or None | grams written anywhere in the line (e.g. "(60 grams)", "or 40 grams", "/300 grams", "400 g"); kg→×1000; first one wins; a range takes the midpoint |
| stated_ml | float or None | millilitres written anywhere in the line (ml, l); same rules; only when no stated_g |
| optional | bool | the line says "optional" |
| name | str | the ingredient name, lower case, without quantity, unit, size words or bracketed notes |

**Canonical units** (synonyms, case-insensitive, singular or plural):

| unit | synonyms |
|---|---|
| tsp | teaspoon, tsp, टी स्पून, छोटा चम्मच |
| tbsp | tablespoon, tbsp, tbs, टेबल स्पून, बड़ा चम्मच |
| cup | cups, C, कप |
| g | g, gm, gms, gram, grams, ग्राम |
| kg | kg, kilogram |
| mg | mg |
| ml | ml, millilitre, milliliter |
| l | l, litre, liter |
| oz | oz, ounce |
| lb | lb, lbs, pound |
| pinch | pinch, a pinch, generous pinch |
| dash | dash |
| piece | nos, no, number, whole, piece, pieces, pod, pods, bag; also a count with no unit word, e.g. "2 onions" |
| clove | clove, cloves, only when followed or preceded by garlic; "8 Garlic pods" is also clove |
| inch | inch, inches, " |
| cm | cm |
| sprig | sprig, sprigs |
| stick | stick, sticks |
| strand | strand, strands |
| leaf | leaf, leaves, only when the name is something else (e.g. "5 leaves mint") |
| bunch | bunch |
| cube | cube |
| slice | slice |
| floret | floret, florets |
| ball | ball |
| blade | blade |
| pat | pat |

Spice cloves ("4 cloves", "6 Cloves (Laung)") are unit piece, name cloves.

**Quantities:** digits, decimals, "1/2", unicode fractions (½ ¼ ¾ ⅓ ⅔ ⅛), mixed numbers ("1½", "1 1/2", "2 &amp; ½" means 2.5; decode HTML entities first). Ranges: "1-2", "1 to 2", "½ to ¾", "10-12"; qty is the midpoint. But "2-1/2" and "1-1/2" are mixed numbers (2.5, 1.5), not ranges. "pinch" or "dash" with no number means qty 1.

**Size:** small, medium, large ("big" → large; "medium-sized" → medium). Take it only from the word right after the quantity, or right after the unit. Size notes elsewhere, e.g. "(or 1 large onion)" or "(Indian bay leaf), medium sized", are ignored. For mass/volume units (g, kg, mg, oz, lb, ml, l) the size is None ("350 g Large King Prawns" → size None).

**Status:**
- WATER when the ingredient is plain water or ice (any quantity).
- UNQUANTIFIED when no quantity can be read ("salt as required", "Milk or water to knead", "Tamarind Chutney").
- Otherwise QUANTIFIED. Words like "adjust to taste" after a real quantity do NOT make a line UNQUANTIFIED.

## 5. T4: matching a name to a food code
`lhf/match.py`: `match_name(name: str) -> dict` with keys:
- `code`: a code from the composition table, "UNMAPPED" or "NON_FOOD";
- `method`: "alias", "exact", "fuzzy" or "none";
- `score`: 0-1.

Rules:
- Use `data/curated/aliases.csv` (columns alias,code,note), which the T4 builder creates. Aliases cover Indian names, Hindi in Devanagari, and common English variants (e.g. maida→A018, besan→A504, jeera→G025, hing→G019, kasuri methi→C020, toor dal→B021, curd→L520).
- Then exact or fuzzy matching against composition names. Use stdlib `difflib` only, with cutoff = constant FUZZY_MATCH_CUTOFF.
- Then UNMAPPED. Non-food items (charcoal) give NON_FOOD.
- **Priority:** prefer IFCT2017 codes. Exception: for fats and oils, prefer the INDB_UK codes T5xx (INDB itself does this).
- Every alias code must exist in the composition table.
- Aliases must be general names. They must never be whole ingredient lines copied from a test file (a test checks this).

## 6. T5: grams
`lhf/grams.py`: `grams_for(qty, unit, size, stated_g, stated_ml, code) -> dict` with keys `grams` (float or None), `basis` (str) and `flags` (list of str). It uses `data/curated/measures.csv` (read `data/curated/measures_README.md`).

Apply the first rule that matches:
1. stated_g is not None → grams = stated_g, basis STATED_MASS.
2. stated_ml is not None → grams = stated_ml × density, basis STATED_VOLUME. Density is the measures row for (code, "ml"); otherwise the group row (code's first letter, "ml"); otherwise 1.0 with flag DENSITY_ASSUMED_1.
3. qty is None or unit is None → None, basis UNQUANTIFIABLE.
4. unit in g, kg, mg, oz, lb → qty × the `any` row, basis MASS_UNIT.
5. unit in ml, l → qty × (1000 if l) × density as in rule 2, basis VOLUME_UNIT.
6. Code rows for (code, unit), basis CODE_MEASURE:
   - if a row's size equals the requested size, use it;
   - otherwise use a row with blank size;
   - otherwise use the "medium" row, with flag SIZE_ASSUMED_MEDIUM when no size was given or SIZE_SUBSTITUTED when a different size was given.
7. Group row for (first letter of code, unit), basis GROUP_MEASURE.
8. unit pinch or dash with no row found in rules 6-7 → qty × PINCH_FRACTION_OF_TSP × (the tsp weight found by rules 6-7 for this code), with flag PINCH_AS_QUARTER_TSP. The basis is the one of the tsp row used (CODE_MEASURE or GROUP_MEASURE).
9. Otherwise → None, basis UNQUANTIFIABLE. **Never invent a default.**

When code is None or UNMAPPED/NON_FOOD, only rules 1-5 can apply.

## 7. T6: food classes
`lhf/classify.py` uses `data/curated/classes.csv` (code,class,note):
- `classes_for(code) -> list[str]`.
- `class_totals(items) -> dict`. Items are dicts with code, grams and `nutrients` (from `composition.nutrients_for`). It returns:
  - `added_sugar_g` = Σ over ADDED_SUGAR items of grams × min(freesugar_g per 100 g, 100) / 100 (UK values above 100 g/100 g are capped at the item's mass);
  - `refined_carb_g` = Σ carb_g of REFINED_GRAIN items;
  - `salt_g` = Σ grams of SALT items;
  - `fat_by_class_g` = {class: Σ fat_g} for COOKING_OIL, HYDROGENATED_FAT, DAIRY_FAT, and OTHER for everything else.

## 8. T7: footprint (daily budget bars)
`lhf/footprint.py`: `footprint(per_serving: dict, setting: str = "urban", risk: str = "general") -> dict`.

Input keys: energy_kcal, fat_g, sfa_g, added_sugar_g, sodium_mg, refined_carb_g. All values are read from `data/curated/baselines.csv` (metric_id → value) and `constants.csv`:
- Reference energy E: NSO_CALORIES_URBAN, or NSO_CALORIES_RURAL when setting="rural".
- Limits:
  - fat = LIMIT_TOTAL_FAT_PCT/100 × E / FAT_KCAL_PER_G;
  - sfa = LIMIT_SFA_GENERAL/100 × E / FAT_KCAL_PER_G, or LIMIT_SFA_CARDIOMETABOLIC when risk="cardiometabolic";
  - added_sugar = LIMIT_ADDED_SUGAR_GRAMS;
  - sodium = LIMIT_SALT_GRAMS × SODIUM_MG_PER_G_SALT;
  - energy = E;
  - refined_carb has no limit, so pct None.
- Output: `{"axes": {axis: {"amount", "unit", "limit", "pct_of_limit", "pct_energy", "limit_sources": [metric ids/constant ids]}}, "reference": {...}, "context": {metric_id: value}}`. Axis keys are the six input keys.
  - pct_of_limit = amount / limit × 100.
  - pct_energy (fat, sfa, added_sugar, refined_carb) = amount × kcal-per-gram / E × 100, using FAT_KCAL_PER_G for fat/sfa. Sugar and carbs have no constant yet, so their pct_energy is None. Do not invent a constant.
  - `context`: `{metric_id: value}` for the national average intake rows: NSO_FAT_URBAN or NSO_FAT_RURAL (g/day, matching the setting) and INDIAB_SFA_NATIONAL (%E).

## 9. T8: pipeline and command line
`lhf/pipeline.py`: `analyse_recipe(recipe: dict, setting="urban", risk="general") -> dict`. The input has the same shape as a line of `data/samples/recipes_phase1.jsonl`: id, url, dish, servings (int or None), lines (list of str).

For every line, in order:
1. parse it;
2. if the status is QUANTIFIED, match the name;
3. compute grams.

A line is **included** if status is QUANTIFIED, the code is a real composition code, and grams > 0. Otherwise it is excluded with exactly one reason: WATER, UNQUANTIFIED, UNMAPPED, NON_FOOD or UNQUANTIFIABLE.

Output (JSON-serialisable; NaN becomes None):
```
{"recipe": {"id","url","dish","servings"},
 "lines": [{"index","raw","parsed":{...T3 dict...},"match":{...}|None,"grams","grams_basis","grams_flags","included","exclusion_reason","classes","nutrients"|None}],
 "coverage": {"lines_total","lines_included","excluded_by_reason":{reason:n},"included_mass_g",
              "unquantified_fat_lines":[raw lines of UNQUANTIFIED lines whose name matches a COOKING_OIL/DAIRY_FAT/HYDROGENATED_FAT code]},
 "totals": {nutrient: value, ..., "added_sugar_g","refined_carb_g","salt_g"},
 "per_serving": {...same keys...} | None,
 "footprint": footprint(per_serving) | None,
 "warnings": [str]}
```
- Warnings (texts start with these codes):
  - `SPICE_OVER_LIMIT`: any included line whose code has class SPICE in classes.csv and whose grams exceed SPICE_LINE_MAX_G;
  - `MASS_IMPLAUSIBLE`: included mass outside RECIPE_MASS_MIN_G to RECIPE_MASS_MAX_G;
  - `NO_SERVINGS`;
  - `SALT_UNQUANTIFIED`: a salt line that is UNQUANTIFIED, meaning sodium is a lower bound.
- `lhf/cli.py`: `PYTHONPATH=src python -m lhf.cli RECIPE.json [--setting urban|rural] [--risk general|cardiometabolic]` prints the JSON to stdout and exits 0. It exits 2 with a message on stderr for an unreadable file.

## 10. T9: validation against lab-analysed dishes (procedure check, not a target)
`experiments/phase1_validation/run.py`:
1. Run `analyse_recipe` on every `validation_v2` recipe (ids starting `V2-`) in `data/samples/recipes_phase1.jsonl`.
2. Join each recipe to `data/curated/validation_ground_truth.csv` by `dish`. A dish may have several lab rows; keep each pair.
3. Compute M2 = fat energy share, as fat_g × FAT_KCAL_PER_G / energy_kcal × 100:
   - for the recipe from `totals`;
   - for the lab row from its fat and energy_kcal.
4. Compute ratio = recipe / lab.
5. Write `results.json` with:
   - `pairs`: dish, recipe_id, lab code, setting, recipe_M2, lab_M2, ratio, lines_included, lines_total;
   - `summary`: n_pairs, median ratio overall, and median ratio by setting (home/takeaway/retail).
6. Generate `REPORT.md` from `results.json` (a template filled by code) with the sections: Summary, Per-dish table, By setting, Coverage, Limitations.

Every number in REPORT.md must appear in results.json. There is no pass mark on the ratio: an honest result is the deliverable.
