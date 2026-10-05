# 37 VALIDATION HANDOFF v2: does ingredient-sum nutrition match lab-measured cooked dishes?
Fresh session instructions. Supersedes 34. Previous attempts failed: one HARDCODED results (file 31), one had broken parsing (file 36: 143/174 ingredients unmapped and counted as 0 g fat, "¼ tsp turmeric" read as 100 g, invented DEFAULT_* values instead of INDB). Read research_log/36_AUDIT_of_validation.md before starting.

## 0. Goal and honesty rules
Question: for non-fried Indian/South Asian dishes, does fat estimated by summing a real recipe's ingredients (Indian food composition data) agree with laboratory-measured fat of the same dish?
- Every number must trace to a saved file: recipe URL + ingredient line, INDB food code + row, or lab source + food code/page. No hardcoded arrays, no synthetic data, no invented defaults.
- "NOT AVAILABLE" or "INCONCLUSIVE" are acceptable results. A wrong number is not.
- Web search only via the Stealth Search MCP. Downloads via Python requests, ≤1 req/s, respect robots.txt, no anti-bot bypass; skip blocked sites.
- Work in research_log/validation_v2/. Write notes.md as you go. Final report research_log/38_VALIDATION_RESULT_v2.md, generated from results.json.

## 1. Ground truth (lab-measured, cooked, non-fried)
A) UK CoFID 2021: research_log/data/CoFID_2021.xlsx.
   - Read the "1.1 Notes" sheet to learn how the reference column (F, "Main data references") and footnotes (G) distinguish ANALYSED foods from RECIPE-CALCULATED foods. Keep only analysed rows; record the evidence for each decision.
   - Candidate South Asian dishes: lentil/dal dishes, chick pea/chana curry, vegetable "bhaji" (sabzi) dishes, palak/saag, chicken curries, korma, tikka masala, biryani/pilau.
   - Take fat (g/100 g), water (g/100 g) and energy (kcal/100 g) from sheet "1.3 Proximates".
B) safefood 2015 (research_log/data/safefood_text.txt): chicken tikka masala, korma, jalfrezi, pilau rice, plain naan. Values are per portion with portion weight; convert to per 100 g. There is no water value, so use the energy-based metric below.
C) Chen, Gilbert & Khokhar 2009 (zenodo.org/records/10043766), if the full text is accessible: aloo palak, chicken bhuna, Bombay aloo, Bengali chicken curry, prawn bhuna, zarda, rasmalai (analysed values).
Target: 6–10 dishes with clean ground truth. Save ground_truth.csv (dish, source, code/page, fat, water, energy, setting: home/takeaway/retail, evidence_of_analysis).

## 2. Recipes
- For each dish, fetch 3–5 real recipes from polite sites: indianhealthyrecipes.com, hebbarskitchen.com, archanaskitchen.com, cookwithmanali.com, pipingpotcurry.com, ranveerbrar.com. Use schema.org JSON-LD recipeIngredient, and recipeYield if present.
- Check the title matches the dish (log mismatches; never use them).
- Save recipes.csv (dish, url, fetch_date, title, yield, raw ingredient lines).

## 3. Parsing (this is where the last run failed; do it carefully)
For EVERY ingredient line produce: name, quantity (number), unit, grams, status ∈ {QUANTIFIED, NOT_QUANTIFIED, EXCLUDED_WATER}.
- Use YOU (the model) to parse each line into JSON, with deterministic conversion afterwards. Handle unicode fractions (½ ¼ ¾ ⅓ ⅔), mixed numbers ("1½"), ranges (use midpoint, also keep min/max), parentheses with grams ("1½ lbs (700 grams)" → 700 g; prefer stated grams).
- Conversion table (cite in notes): tsp 5 ml, tbsp 15 ml, cup 240 ml (sensitivity 200 ml), pinch 0.3 g. Densities: oil 0.92, ghee 0.91, melted butter 0.91, cream 1.0, yogurt 1.03, milk 1.03 g/ml; ground spices ~2.5 g/tsp; salt 6 g/tsp; sugar 4.2 g/tsp. Piece weights from INDB Units.xlsx (research_log/data/indb_repo/Units.xlsx) or a cited source (onion, tomato, chilli, garlic clove, cashew ≈ 1.5 g each).
- NOT_QUANTIFIED ("to taste", "as required", "for garnish"): oil/ghee/butter "as required" → record separately and report results with and without a 1 tbsp assumption. Salt/spices to taste → negligible for fat.
- Water/stock added: EXCLUDED_WATER (not in the dry-matter calculation; see section 5).
- SANITY TESTS (must pass; otherwise fix before computing):
  - no single spice or condiment > 30 g;
  - main ingredient grams equal what the line says (e.g., 700 g chicken);
  - total non-water ingredient mass per recipe between 200 g and 5,000 g;
  - zero lines silently defaulted to 100 g.
  Print a table of the 10 largest lines per recipe for a visual check.

## 4. Mapping to nutrient data
- Map each ingredient to INDB (research_log/data/indb_repo; identify the sheet with per-100 g fat, SFA, energy and water/moisture if present) using exact/alias match first, then fuzzy match, then your judgement. Record the food code and name.
- Allowed fallbacks only: IFCT-based INDB rows, then UK CoFID raw-ingredient rows, then USDA FoodData Central (cite the FDC id). NO invented values.
- Required coverage: ≥95% of ingredient MASS mapped. Report unmapped lines explicitly. Unmapped lines are excluded from both numerator and denominator, with a mass-share warning.
- Save per_ingredient.csv: dish, url, line, grams, code, source, fat/100 g, water/100 g, kcal/100 g, fat_g, water_g, kcal.

## 5. Comparison metrics (avoid the water-loss guess)
Water added and evaporated is unknown, so compare on bases that do not depend on it:
- **M1, fat per 100 g DRY MATTER.** Recipe: Σfat / Σ(ingredient mass − ingredient water) × 100. Lab: fat / (100 − water) × 100 (CoFID; Chen if water given).
- **M2, fat as % of energy.** Recipe: (Σfat × 9) / Σkcal × 100. Lab: (fat × 9) / kcal × 100. This works for safefood too.
- **M3 (secondary), fat per 100 g as eaten,** with a moisture band, for reference only.
Per dish: the recipe range (min–max across recipes and the oil-as-required sensitivity), the median, and whether the lab value falls inside the range. Overall: coverage (dishes with lab value inside range) and median ratio (recipe median / lab) for M1 and M2.

## 6. Interpretation guide (write it honestly)
- Ratio ~0.8–1.25 with decent coverage → ingredient sums are a reasonable basis.
- Ratio clearly < 0.8 for takeaway dishes but ~1 for homemade dishes → restaurant food is richer than web home recipes (a real finding, supports the home-vs-restaurant setting in the app).
- Low coverage everywhere → report it plainly with likely causes.
- Always separate home-style ground truth (CoFID homemade, Chen) from takeaway (safefood, CoFID takeaway).

## 7. Final report (38_VALIDATION_RESULT_v2.md, built from results.json)
1. 5-line plain summary.
2. Table per dish: ground truth source + setting, n recipes, M1 lab vs recipe range/median, M2 lab vs recipe range/median, inside? (yes/no).
3. Overall coverage and median ratios (M1, M2), split by home vs takeaway.
4. Parsing/mapping QA: % mass mapped, sanity tests passed, excluded lines with reasons.
5. Limitations.
Then tell the user the 5-line summary in chat.
