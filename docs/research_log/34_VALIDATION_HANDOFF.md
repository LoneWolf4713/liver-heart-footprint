# 34 HANDOFF: one validation check (fresh session)
Question: do ingredient-sum estimates from real web recipes match LAB-MEASURED fat in cooked (non-fried) South Asian dishes?
Read first: research_log/LIVER_FOOTPRINT_PROJECT.md, research_log/31_AUDIT_of_dryrun_report.md (previous sessions FABRICATED this exact test by hardcoding numbers; do not repeat).

## Hard rules
- NO hardcoded or synthetic numbers. Every value must come from a saved file: fetched recipe (URL + fetch date), INDB row (food code), or lab table row (source + code/page).
- Web search only via Stealth Search MCP; downloads via Python requests; <=1 req/s; respect robots.txt; no anti-bot bypass; skip blocked sites.
- If data is missing, write "NOT AVAILABLE" and move on. A failed or inconclusive result is acceptable; an invented one is not.
- Output folder: research_log/validation/ with code, CSVs, results.json, notes.md. Final: research_log/35_VALIDATION_RESULT.md written from results.json.

## Steps
1. Ground truth. Collect LAB-ANALYSED fat (g/100 g as eaten) for non-fried cooked South Asian dishes:
   - UK CoFID 2021: research_log/data/CoFID_2021.xlsx, sheet "1.3 Proximates". Use only rows whose reference column (F) / footnote (G) indicates ANALYSED, not recipe-calculated. Record food code and name exactly.
   - safefood 2015: research_log/data/safefood_text.txt (chicken tikka masala, korma, jalfrezi, rice, naan).
   - Chen, Gilbert & Khokhar 2009 (zenodo.org/records/10043766) if accessible.
   Target 6-10 dishes (e.g., dal/lentil curry, chana, aloo gobi / vegetable curry, palak, tikka masala, korma).
2. Recipes. For each dish, fetch 3 real web recipes from polite sites (indianhealthyrecipes.com, hebbarskitchen.com, archanaskitchen.com, cookwithmanali.com, pipingpotcurry.com). Verify the title matches the dish. Save URL + ingredient lines.
3. Compute. Parse quantities to grams (tsp 5 ml, tbsp 15 ml, cup 240 ml; oil 0.92 g/ml; ghee 0.91; INDB Units.xlsx piece weights). Map each ingredient to an INDB food code (research_log/data/indb_repo). Total fat = sum(grams × fat/100 g). Save a per-ingredient table.
4. Cooked weight. Fat/100 g needs the cooked weight. Use raw total weight (incl. water) × (1 − moisture loss), with moisture loss 0%, 10%, 20% as a stated sensitivity band (no single assumed value).
5. Compare. Per dish: measured fat vs the min-max of the 3 recipes (across the moisture band). Metrics: coverage (measured inside the band), median ratio (estimated/measured), and a list of failures with reasons.
6. Report plainly: n dishes, n recipes, coverage, median ratio, caveats (UK takeaway vs Indian home recipes; restaurant fat is often higher). Tell the user the result in 5 lines.
