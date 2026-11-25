# UNMAPPED Audit — Full INDB Run
**Handoff instructions for execution by an automated agent.**  
**Save all outputs into `/home/prtyksh/subjects/CGAS/liver-heart-footprint/demo/`.**

---

## Context

This is the **Liver and Heart Footprint** project (`src/lhf`). The engine parses Indian recipe ingredient lines and maps them to a nutritional composition database. When an ingredient name cannot be matched to any known food code, it gets marked `UNMAPPED` and is silently dropped from the nutrient calculation.

We need to know: **across all 1,014 INDB recipes, what is currently UNMAPPED, and is there a pattern?**

This audit will determine whether replacing `difflib` fuzzy matching (Step 7 in `lhf.match`) with a semantic embedding model (MiniLM-L6-V2) is justified.

---

## Environment

```
Project root:   /home/prtyksh/subjects/CGAS/liver-heart-footprint/
Python:         /home/prtyksh/subjects/cgas_env/bin/python
PYTHONPATH:     src/   (must be set for all runs)
INDB recipes:  data/raw/indb/recipes.xlsx
Servings data: data/raw/indb/recipes_servingsize.xlsx
Output dir:    demo/
```

Always run python as:
```bash
cd /home/prtyksh/subjects/CGAS/liver-heart-footprint
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python <script>
```

---

## Task 1 — Build a Script: `demo/run_indb_audit.py`

Create this script at `demo/run_indb_audit.py`. It must do the following:

### 1a. Load all 1,014 INDB recipes from the Excel file

The file `data/raw/indb/recipes.xlsx` has these columns:
```
recipe_code, recipe_name, ingredient_name_org, amount, unit, food_code, food_name
```

The file `data/raw/indb/recipes_servingsize.xlsx` has:
```
recipe_code, recipe_name, no_of_servings
```

**Build recipe dicts** in the format the `analyse_recipe()` function expects:
```python
{
    "id": recipe_code,          # e.g. "ASC001"
    "dish": recipe_name,        # e.g. "Hot tea (Garam Chai)"
    "servings": no_of_servings, # float from recipes_servingsize.xlsx, default to 4 if missing/NaN
    "lines": [
        "50 ml milk",
        "2 tsp sugar",
        "1.5 tsp tea leaves",
        ...
    ]
}
```

**To build `lines`:** For each ingredient row, combine `amount` + `unit` + `ingredient_name_org` into a string like `"{amount} {unit} {ingredient_name_org}"`. If `amount` is NaN, just use `ingredient_name_org` alone (it will be UNQUANTIFIED). If `unit` is NaN or empty, just use `"{amount} {ingredient_name_org}"`.

Group rows by `recipe_code` to build each recipe's `lines` list.

### 1b. Run `analyse_recipe()` on every recipe

```python
from lhf.pipeline import analyse_recipe

result = analyse_recipe(recipe_dict, setting="urban", risk="general")
```

Catch exceptions per recipe (some recipes may have malformed data) — log the error but continue.

### 1c. Collect the UNMAPPED data

For every processed recipe, scan `result["lines"]`. For each line where `exclusion_reason == "UNMAPPED"`:
- Record: `recipe_code`, `recipe_name`, `raw_line`, `parsed_name` (from `line["parsed"]["name"]`), `match_method` (from `line["match"]["method"]` if present), `match_score` (from `line["match"]["score"]` if present)

Also record for every recipe:
- `lines_total`, `lines_included`, `lines_unmapped` count, `lines_unquantified` count
- `included_mass_g`
- Whether `MASS_IMPLAUSIBLE` warning is in `result["warnings"]`

### 1d. Save raw results

Save two files:
1. `demo/indb_audit_unmapped.csv` — one row per UNMAPPED ingredient line, columns: `recipe_code`, `recipe_name`, `raw_line`, `parsed_name`
2. `demo/indb_audit_coverage.csv` — one row per recipe, columns: `recipe_code`, `recipe_name`, `lines_total`, `lines_included`, `lines_unmapped`, `lines_unquantified`, `included_mass_g`, `mass_implausible`

Print progress every 100 recipes processed.

---

## Task 2 — Analyze the Results and Write a Summary

After the script runs successfully, write a **second script** `demo/analyze_audit.py` that reads the two CSVs and generates `demo/UNMAPPED_AUDIT_SUMMARY.md`.

The summary must answer these specific questions:

### Q1. Overall Coverage
- How many of the 1,014 recipes ran without error?
- What is the overall UNMAPPED rate? (`total UNMAPPED lines / total lines across all recipes`)
- What is the median UNMAPPED count per recipe?
- How many recipes have zero UNMAPPED lines?
- How many recipes have >20% of their lines UNMAPPED?

### Q2. The UNMAPPED Ingredient Frequency Table
- Count how many times each unique `parsed_name` appears as UNMAPPED across all recipes.
- Show the **top 40 most-frequently UNMAPPED ingredient names**, with their count and what fraction of total UNMAPPED occurrences they represent.
- This is the key table — it shows exactly what the matcher is failing on.

### Q3. Pattern Classification
Manually classify the top 40 UNMAPPED names into categories:
- **Hindi/transliterated** — names that are clearly Indian-language (e.g., `hari mirch`, `kala namak`, `amchur`)
- **Compound/prep phrases** — names with prep words still attached (e.g., `finely chopped ginger`, `roasted cumin powder`)  
- **Genuine gaps** — ingredients that exist as real foods but have no alias (e.g., `kokum`, `raw banana`)
- **Noise** — non-food text, instructions scraped as ingredients

For each category, state the count of items in the top 40 that fall into it.

### Q4. The difflib vs Semantic Embedding Question
Based on the top 40:
- Which failures would a **character-level fuzzy match (difflib) already fix** if the cutoff were lower? (i.e., close English spellings)
- Which failures would **only a semantic embedding model fix**? (i.e., Hindi ↔ English, synonyms with no character overlap)
- Which failures **neither method can fix** without adding more aliases? (completely novel ingredients)

### Q5. Mass-Implausible Recipes
- How many recipes triggered `MASS_IMPLAUSIBLE`?
- List the top 10 worst (lowest `included_mass_g`) with their recipe names.

### Q6. Verdict
Based on all of the above, state clearly:
- Is there a compelling case to add MiniLM semantic embeddings to Step 7 of `lhf.match`?
- Or is the UNMAPPED failure rate low enough that the current difflib + aliases approach is sufficient?
- What is the single highest-value action to reduce the UNMAPPED rate?

---

## Task 3 — Execute Both Scripts and Confirm Outputs

Run both scripts in order:

```bash
cd /home/prtyksh/subjects/CGAS/liver-heart-footprint
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python demo/run_indb_audit.py
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python demo/analyze_audit.py
```

After running, confirm:
- [ ] `demo/indb_audit_unmapped.csv` exists and has rows
- [ ] `demo/indb_audit_coverage.csv` exists and has ~1014 rows
- [ ] `demo/UNMAPPED_AUDIT_SUMMARY.md` exists and answers all 6 questions above

If any script errors out, fix the error and re-run. Do not stop until all three files exist.

---

## What NOT to Do

- Do not modify anything in `src/lhf/` — the engine is read-only for this task.
- Do not use `lhf.cli` (the CLI is for single recipes). Call `analyse_recipe()` directly in Python.
- Do not invent or fabricate numbers. All numbers in the summary must come from the actual CSV outputs.
- Do not summarize away the top-40 UNMAPPED table — it must appear in full in the markdown.

---

## Final Deliverable

When done, the following files must exist:
```
demo/run_indb_audit.py          ← the audit runner
demo/analyze_audit.py           ← the analysis script
demo/indb_audit_unmapped.csv    ← raw UNMAPPED rows
demo/indb_audit_coverage.csv    ← per-recipe coverage stats
demo/UNMAPPED_AUDIT_SUMMARY.md  ← the markdown summary answering Q1–Q6
```

The `UNMAPPED_AUDIT_SUMMARY.md` is the primary artifact we will read to make the architecture decision.
