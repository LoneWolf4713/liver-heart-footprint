# 22 Refined concept: "Liver footprint of Indian food" (2026-09-29)
User decisions: Indian niche is the justified advantage (mirrors the lab's own Indian focus); NO Instagram; YouTube (API) optional; primary input = recipe text or recipe WEBSITE link (scrape, as in Assignment 1) -> NER / small LLM -> quantities -> compare sat fat, sugar, unsat fat etc. -> liver good/bad; place the dish in the context of an AVERAGE INDIAN DAY (Kurkure example: 500 kcal/100 g is "under 2000" but large in a day's context); healthier SUBSTITUTIONS using the lab's flavour-compound data; must be clearly COMPUTATIONAL GASTRONOMY, not a biology project.

## Grounding numbers found this round (all [V] unless marked)
Average Indian day:
- NSO "Nutritional Intake in India" (HCES Aug 2022-Jul 2024; released 2 Jul 2025): per capita/day 2023-24 rural 2,212 kcal (adjusted 2,191), urban 2,240 kcal; protein ~62 g rural / ~63 g urban; fat ~60 g rural / ~70 g urban; state/sector/expenditure-class tables; top 5% urban 3,092 kcal vs bottom 5% 1,696.
- ICMR-INDIAB-21 (Anjana et al., Nat Med 31:3813, 2025; n=18,090 dietary sub-sample of 121,077; 36 states/UTs): 62% energy from carbohydrate; added sugar >5%E in 21 states/UTs; total fat 21.6%E (NE) to 27.9%E (West); SATURATED FAT 8.9%E nationally (North 11.2%E, NE 7.4%E); MUFA 6.1%E; PUFA 5.3-9.1%E; most states exceed SFA <7%E (ICMR) and many exceed <10%E; state values in Extended Data Tables 2 and 4. Authors: added sugar UNDER-estimated because mithai, street food, bakeries, juices (unregulated sector) carry no labels.
Limits (ICMR-NIN DGI 2024): added sugar <5%E, i.e. 25-30 g/day; salt >5 g/day (sodium >2 g) = high; total fat <=30%E; HFSS = >15% energy from added oils/fats (ghee, butter, oil); Table 15.2 HFSS categories per 100 g; reference day uses ~25 g oil (child diet example) [copyright: cite, do not reproduce tables in a product without NIN permission].
Liver evidence:
- Luukkonen et al., Diabetes Care 2018 (PMC7082640): +1,000 kcal/day x 3 wk; saturated fat -> largest intrahepatic TG rise (lipolysis), insulin resistance, ceramides; simple sugars -> rise via de novo lipogenesis; unsaturated fat -> smallest rise.
- Phenome India 2026: obesity (energy surplus) = predominant driver of MASLD in India.
- Spices not implicated; curcumin trials show improved markers.
Cooking/frying:
- Chen, Gilbert, Khokhar 2009: puri fat uptake up to 18.4 g/100 g; water loss up to 24%.
- Jain, Passi & Selvamurthy, J Food Sci Technol 61:2185 (2024): poori, bread pakora, mathri, chips, fries: total fat 22.5% (1st frying cycle) -> 27.4% (32nd cycle, dry basis); SFA ~5% -> ~15%; TFA 0.05% -> 0.89% with oil REUSE (street-food relevance).
Substitution prior art: hobby app "rezipi" (Jaccard over a 131-ingredient/121-compound FlavorDB subset, no nutrition); generic LLM/RAG substitution surveys. Health-aware + flavour-preserving + Indian-authenticity substitution: not found.
Liver apps (from 21): Liverly, Liver Nutrition App = Western/Mediterranean; not recipe-science, not Indian.

## The concept
Framing (CG): The lab computed the CARBON footprint of recipes ("Cultural context shapes the carbon footprints of recipes", SustainableFoodDB). We compute the LIVER footprint of Indian recipes: recipe -> ingredients x quantities x cooking processes -> liver-relevant nutrient load -> placed against a person's day. Same computational object (recipe), different impact axis.

Pipeline:
A. Input: recipe text, recipe website URL (scraper as in Assignment 1), YouTube URL (official Data API description). Parse with recipe NER (lab's LREC-COLING 2024 model) or small LLM with a strict JSON schema -> ingredient, quantity, unit, state, process (fry/tadka/bhuna/boil).
B. Ingredient -> nutrients: INDB (IFCT-based Indian ingredients incl. SFA/MUFA/PUFA, free sugar, fibre) first; RecipeDB2/USDA fallback; INDB unit conversions (katori, tbsp, "1 medium onion"); rules for ADDED sugar (sugar, jaggery, honey, syrups, condensed milk) and ADDED fat (oil, ghee, butter, cream, vanaspati).
C. Cooking adjustments: deep-fry oil uptake ranges (Chen 2009; Jain & Passi 2024), tadka/bhuna oil counted in full, oil-REUSE toggle (SFA x~3, TFA up), yield/water loss.
D. Day context ("Liver Budget"): per-serving load shown as % of daily budgets: energy (reference ~2,000 kcal; user adjustable), SFA (<7%E ICMR; <10%E general), added sugar (25 g), added-fat share (HFSS rule >15%E), refined carbs (maida, white rice), salt (5 g); protective: fibre, pulses, vegetables, unsaturated oils. Pre-filled BASELINE = what the average person in your region already eats (NSO kcal/fat; INDIAB regional SFA%, added sugar) -> "remaining headroom" (e.g., average North Indian already at 11.2%E SFA before this dish).
E. Liver Load Index (transparent): weighted sum of budget fractions; weights ordered by evidence (SFA > added sugar/fructose > refined starch/energy surplus > unsaturated fat); every point traceable to an ingredient + a citation; sensitivity analysis over weights. NOT a diagnosis.
F. Swaps: candidates must (1) fill the same culinary role (fat for fat, dairy for dairy); (2) preserve flavour: FlavorDB shared-molecule similarity (food-pairing machinery); (3) be culturally real: co-occur in real Indian recipes of the same dish family (RecipeDB2 co-occurrence = authenticity); (4) cut liver load. Rank on these. Validation: the cuisine itself (held-out real recipe variants that already use the swap, e.g., curd instead of cream, mustard oil instead of ghee).

Research questions (the "science" half):
RQ1 Liver footprint of Indian cuisine by region/dish family (RecipeDB2 34 states; INDB 1,014 recipes) + contribution analysis (Jain & Bagler style): which ingredients drive load? Tests the "masala" belief: expected drivers = cooking fats, cream/khoya, sugar, maida; spices ~0.
RQ2 Drift: traditional (INDB textbook recipes 2007/2011; older TarlaDalal in CulinaryDB) vs today's popular web/YouTube recipes of the SAME dishes: heavier? [data dry-run needed: share of modern recipes with real quantities]
RQ3 Hidden load of unlabelled foods (mithai, street snacks, bakery) that INDIAB says escape added-sugar labelling; oil-reuse scenarios.
RQ4 How much load can be removed while staying authentic (load vs authenticity trade-off curve).
"Regional atlas" = simply a map of Indian states coloured by the average liver footprint of that state's recipes + top driving ingredients, shown next to INDIAB state SFA%/sugar (descriptive, not causal).

Features: day builder (add meals, see budgets fill; regional baseline pre-filled); "why" explanations with citations; swap slider; street-food mode with oil-reuse toggle; "is it the masala?" breakdown; Hinglish recipe parsing; optional packaged-label photo mode (OCR -> same budget view; Open Food Facts India lookup).

Data asks:
- From the lab: RecipeDB2 bulk (Indian recipes with quantities, processes, state), FlavorDB bulk, recipe NER model/code, their ingredient->nutrient mapping.
- Open: INDB (GitHub), CulinaryDB, USDA FDC, NSO report tables, INDIAB Extended Data tables, DGI 2024 (cite), Luukkonen 2018, Jain & Passi 2024, Chen 2009, Open Food Facts India (optional).
- Collected by us (legal): recipe websites (as Assignment 1, respect robots.txt); YouTube Data API.

Limits: estimates not diagnosis; FlavorDB has presence not concentration; cooking factors are literature ranges; weights are modelling choices (report sensitivity); no individual outcome validation.
CG relevance: uses all five course data pillars (recipes, flavour, nutrition, health, cuisine patterns) + course methods (NER, contribution analysis, culinary fingerprints/co-occurrence); mirrors lab's carbon-footprint and nutrition-estimation work; answers lab's stated open items (health "for the complete dish", quantities, cooking transformation) and symposium theme "tweak my recipe for better health".
EOF
echo ok
## Decision (user, 2026-09-29): prototype input = WEBSITE LINK only (YouTube later). Target ~5 most popular Indian recipe sites.
## Website dry-run [V, fetched 2026-09-29]
- Hebbar's Kitchen (4,577 posts; veg only): paneer butter masala -> ALL fats/sugar quantified (2 tbsp + 2 tsp oil, 1 tsp + 1 tbsp butter, 2 tbsp cream, 1 tsp sugar, 1 tsp salt); issues: count units ("20 cubes paneer", "2 onion"), servings not visible in text dump.
- VegRecipesOfIndia (veg only): dal makhani -> grams for many items (140 g urad, 40 g rajma, 200 g tomato), 3 tbsp butter; issues: RANGES ("1/4 to 1/3 cup light cream 25-30% fat"), "salt as required", optional garnish cream.
- Hebbar's samosa: deep-frying oil NOT quantified ("heat the oil in a kadhai and deep-fry"); recipe card not visible in markdown fetch (structured card likely JSON-LD/JS) -> deep-fry oil must be MODELLED (uptake ranges).
- Tarla Dalal: 4,000+ veg recipes; pages already show "calories per serving" (calculated) -> usable as a pipeline sanity check (not ground truth).
- indianhealthyrecipes.com URL guess 404 (site exists; URL wrong) - not tested.
- robots.txt: hebbarskitchen and vegrecipesofindia allow recipe pages (disallow only wp-admin, search, comments); sitemaps published -> polite crawling permitted.
- schema.org Recipe/recipeIngredient used on 10K-100K domains (Google, Aug 2026) -> generic JSON-LD extraction for "any link", LLM fallback when absent.

## Loopholes identified (red team of the concept)
L1 Deep-fry oil unquantified -> oil-uptake model from literature ranges (Chen 2009 puri 18.4 g/100 g; Jain & Passi 2024 fried foods 22.5-27.4% fat dry basis; safefood/CoFID lab-analysed bhaji/pakora/samosa) -> report ranges.
L2 Portion/servings ambiguity; count units; ranges; "to taste" -> unit->gram table (INDB units + defaults), carry min/max uncertainty, per-100 g AND per-serving views.
L3 Recipe as written != what is eaten (restaurant/street heavier; home cooks deviate) -> score "the recipe", separate street-food mode.
L4 RQ2 CONFOUND: INDB baseline = home-science TEXTBOOK recipes (nutrition-minded, likely leaner by design) vs blogs (often "restaurant style") -> may measure textbook-vs-blog, not traditional-vs-modern. Mitigation: multiple baselines + Wayback Machine snapshots of the SAME recipe URLs over time (true longitudinal); match dish-by-dish; tag "restaurant style" recipes. No causal claim about MASLD.
L5 Score validity: weights are modelling choices; no outcome data -> sensitivity analysis; agreement with ICMR HFSS categories / other nutrient-profile scores (construct validity); optional blind dietitian ranking.
L6 Ingredient mapping errors (lab's 2020 matcher 71.6%; RecipeDB2 BERT F1 87.9) -> INDB-first for Indian items; measure mapping accuracy on a labelled sample.
L7 Nutrient DB nuances: added vs intrinsic sugar; ghee/vanaspati/analogue paneer (palm-oil based -> higher SFA) -> explicit rules; analogue-paneer toggle links to adulteration news.
L8 FlavorDB limits for swaps: presence not concentration; raw profiles; COVERAGE of Indian fats (ghee, vanaspati, mustard oil, khoya, paneer, cream) UNVERIFIED -> must check.
L9 Site-selection bias: top Google-ranked sites (Hebbar's, VRoI, Tarla Dalal) are largely VEGETARIAN, urban, English -> include non-veg sources for RQ1/RQ2.
L10 Legal/ethical: robots OK; store extracted facts + source URL, do not republish prose; rate-limit; not medical advice; no brand shaming.
L11 Competition: Liverly/Liver Nutrition App could add Indian food; lab could add health scores to RecipeDB2 -> edge = India baseline + cooking model + cuisine-level science + authentic swaps.

## Test plan
T1 Extraction coverage: 5 sites x 20 recipes -> % with JSON-LD; % with quantified oil/ghee/butter/cream/sugar; % deep-fried with unquantified oil.
T2 Parsing + unit->gram + ingredient->INDB mapping accuracy on ~100 hand-labelled ingredient lines.
T3 Fried-food fat validation: our estimates vs lab-measured values (Chen 2009 puri; safefood bhaji/pakora; UK CoFID analysed items; Jain & Passi 2024).
T4 FlavorDB coverage of Indian cooking fats/dairy + swap back-test on held-out real recipe variants (curd for cream, mustard oil for ghee).
T5 Score: sensitivity to weights; agreement with ICMR HFSS categories; sanity vs Tarla Dalal calories.
T6 RQ2 feasibility: count Wayback snapshots for popular recipe URLs (same URL, earlier version) + baseline confound check.
