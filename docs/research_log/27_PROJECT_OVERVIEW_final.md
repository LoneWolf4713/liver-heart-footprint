# 27 PROJECT OVERVIEW (final, after tests + audit) — 2026-09-30
Verdict (after 25 test report + 26 audit): the idea is SOUND -> PROCEED (GO-WITH-CHANGES). T2/T3/T5 numbers from file 25 must not be quoted until redone.

## One line
Paste any Indian recipe link -> the app shows how heavy it is on the liver, what is causing it, and the smallest change that makes it lighter; plus a research study of the "liver footprint" of Indian cuisine. (Lab computed the CARBON footprint of recipes; we compute the LIVER footprint.)

## Problem (verified numbers)
- MASLD: 38.9% of Indian adults (Phenome India, Lancet SEA 2026); 27.4% of young non-obese South Indians (JCEH 2025).
- Dietary drivers: saturated fat (ghee, butter, cream, vanaspati, palm oil), added sugar, refined carbs (maida), deep-fried food, excess calories (Luukkonen 2018; guidelines). Spices NOT implicated (curcumin improves markers).
- Average Indian already exceeds limits: SFA 8.9%E nationally, 11.2%E in North (limit <7%E); added sugar >5%E in 21 states (ICMR-INDIAB, Nat Med 2025). NSO 2025: ~2,212-2,240 kcal/day, fat 60-70 g.
- Existing liver apps (Liverly, Liver Nutrition App) are Western; reel->recipe->nutrition apps exist (Nutrola etc.) but not Indian and not liver/cuisine science.

## User flow
Paste link -> ingredients + quantities read -> per serving: % of daily SFA, added sugar, refined carbs, energy, salt budgets -> shown against the average person in your region's existing day (the "Kurkure" point) -> "why" explanation traced to ingredients + citations -> swaps with load reduction shown.

## Features
- Link reader: schema.org Recipe JSON-LD (84% of tested pages), small-LLM fallback.
- Quantity normaliser: tbsp/cup/katori/count units -> grams; defaults for "salt to taste".
- Nutrient mapping: INDB/IFCT first, USDA/RecipeDB2 fallback.
- Frying model: oil actually absorbed by samosa/puri/pakora (no recipe states it; 9/10 websites, 0/18 YouTube videos).
- Liver budget bars with regional baseline pre-filled.
- "Why" explanations with citations.
- Swap suggester: same culinary role + appears in real Indian recipes of that dish (RecipeDB2 co-occurrence) + lower load. (FlavorDB dropped for fats/sugar: too sparse; usable only for aromatics.)
- Day builder; street-food mode (oil-reuse toggle: SFA ~x3, Jain & Passi 2024); "Is it the masala?" breakdown.
- Optional later: YouTube links via official Data API descriptions only. No Instagram.

## Research questions (the computational-gastronomy science)
1. Liver footprint of Indian cuisine by region/dish; contribution analysis (Jain & Bagler-style) of which ingredients drive it.
2. Dietetic textbook recipes (INDB) vs popular web recipes: how much heavier is what people cook from blogs? (NOT "change over time": Wayback too thin.)
3. Hidden load of unlabelled foods (mithai, street snacks, bakery).
4. How much load can be removed while staying authentic.

## Data
Have (open / downloaded / verified): INDB (1,014 recipes w/ grams, Indian nutrients, units) in research_log/data/indb_repo; popular recipe websites (robots.txt permits); NSO + ICMR-INDIAB baselines; ICMR-NIN 2024 limits; liver evidence; lab-measured fried-food fat (Chen 2009, safefood 2015, UK CoFID 2021 in data/, Jain 2024); CulinaryDB; FlavorDB scrape (data/flavordb_repo).
Ask the professor: RecipeDB2 bulk (Indian recipes w/ quantities, processes, state), lab's recipe NER model, lab's ingredient->nutrient mapping.

## Missing / weak (to fix)
1. Frying-model validation: ~8 lab-measured fried dishes; first attempt circular -> redo with source split (fit on some, test on others), include mathri.
2. Parser accuracy unmeasured: ~100 hand-labelled lines by the two students (~1 hour).
3. Score weights: order evidence-based (SFA > added sugar > refined carbs/energy > unsaturated), exact weights are choices -> sensitivity analysis; never a diagnosis; show budget bars rather than a single 0-100 score until justified.
4. Non-veg coverage: add 1-2 non-veg sources; fix wrong-dish URL matches.
5. Swap validation: real recipe URLs for each healthier variant.
6. RQ2 caveat stated honestly (textbook vs web, not time).
Rule: no Cloudflare-bypass/impersonation scraping; polite collection only.

## Build order
1 link reader + normaliser + nutrient mapping -> 2 frying model (validated) -> 3 budget bars + explanations with regional baseline -> 4 swap panel -> 5 research analyses on RecipeDB2 + INDB.
Next action proposed: redo T3 (frying-model validation) here.

## Discussion 2026-09-30 (user review of features)
- User: link reader can use a small LLM; normaliser, mapping, budget bars, explanations, day builder = fine/trivial. CORE = frying model + swap suggester. Street-food mode = same recipe home vs street estimate. "Is it the masala?" = optional extra.
- User questioned why we need RecipeDB2, the lab NER model, and the lab mapping. Answer (corrected): NONE are required for the app.
  * RecipeDB2: not needed for the app; helpful for the research questions and the swap engine's authenticity statistics (scale, 34-state labels). Plan A = scrape our own Indian recipe corpus (Assignment-1 skills, polite); RecipeDB2 = optional upgrade / professor-fit.
  * Lab NER: not needed (JSON-LD already splits ingredient lines; regex + small LLM parses qty/unit/name). Optional baseline to compare our parser against.
  * Lab mapping: not needed; we build our own string -> INDB mapping (alias dictionary + fuzzy/embedding match + manual check of the most frequent ~300 ingredient strings). The lab's mapping targets USDA anyway.
- Frying model = calibrated literature model (not new physics): category-based oil-uptake ranges + mass balance (moisture loss replaced partly by oil) + oil-reuse scenario; parameters from literature; validated leave-one-source-out on lab-measured fried foods; more lab values to be searched.
- Swap engine = hotspot detection -> role-based candidates (curated role table) -> authenticity from recipe corpus (substitute/lower quantity actually used in real recipes of the same dish) -> "cook it like the lightest 25% of real recipes" quantity rule -> rank by load cut x authenticity.

## Status 2026-09-30
User: building starts in ~1 month, after the professor + TA vet the idea. Now = dry-run feasibility of every component on real data (80% on parsing/mapping is acceptable; LLMs/local models will help later). Handoff written: 29_DRYRUN_HANDOFF_INSTRUCTIONS.md (integrity protocol added because 25 misreported values).

## Feasibility verdict for idea submission (2026-09-30, after audit 31)
User only needs to know if the app can be built (no numbers for the pitch). Verdict: YES, buildable. Proven on real data: link reader, quantity parsing (~80%, 95% on fat/sugar lines), INDB mapping (~97%), fried-food lab data exists (61 verified rows). Remaining items (frying-range accuracy, ingredient-sum vs measured cooked fat, swap-rule effectiveness) affect ACCURACY/QUALITY, not whether the app works; to be tested during the build phase. Recommendation: submit the idea.
