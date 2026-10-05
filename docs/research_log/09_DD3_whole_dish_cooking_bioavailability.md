# 09 Deep Dive 3: Whole-dish health reasoning + cooking transformation (2026-09-29)
Legend: [V] verified from source read | [S] secondary | [B] blog | [U] unverified / inference
Scope decision: the nutrition/bioactive half (cooked-dish composition + bioavailability) is the strong lead; the FLAVOR half (cooking-aware pairing) is secondary.

## 1. Problem reality
- [V] The host lab says health evidence exists per ingredient but "must logically be assessed for the complete dish" (Bagler & Goel, npj Syst Biol Appl 2024) and that recipes as unordered ingredient lists miss quantity, processing and cooking transformation.
- [V] Lab's own recipe-nutrition method (Kalra, Batra, Diwan, Bagler 2020, arXiv 2004.12286): dish nutrition = SUM of raw ingredient values from USDA-SR after NER + Jaccard string matching. Authors state: "more accurate results would be obtained if nutritional yield due to cooking is taken into account, but there is no such consolidated resource for yield values". Validated ONLY on calories: mean error 36.42 kcal/serving vs AllRecipes third-party values on 2,482 recipes with 100% ingredient mapping. Ingredient-to-USDA matching accuracy 71.6% on the 5,000 most frequent ingredient+state strings; USDA lacks Indian ingredients (their example: garam masala not present).
- [V] Indian Nutrient Databank (INDB; Vijayakumar et al., Anuvaad Solutions, Gates Foundation-funded, 2024, PMC11277795; open access + code): 1,095 raw foods (IFCT 2017: 528; IFCT 2004: 369; rest UK/USDA) and 1,014 recipes (Delhi University manuals + 148 blog recipes), values per 100 g and per serving, 40+ nutrients incl. vitamin K1/K2, MUFA, carotenoids.
  COOKING handled only as a SENSITIVITY analysis: USDA Retention Factors Release 6 (2007), ONE factor per food based on the most common Indian cooking method, matched for only 42.62% of ingredients; differences "small" (largest losses vitamin C, potassium, phosphorus); NO yield-factor correction (listed as a next step); authors: cooked-sample analysis "would be more accurate but is cost-prohibitive".
  Not modelled: bioavailability, matrix/combination effects, fat-assisted absorption, phytate, fermentation, cookware.
- [V] USDA Table of Nutrient Retention Factors, Release 6 (2007): ~290 foods, 16 vitamins, 8 minerals; standard practice = recipe calculation with ingredient weights x yield x retention. Dated and US-centric.
- [V] Phenol-Explorer: >37,000 data points from 638 papers; retention factors for 155 foods x 139 polyphenols x 35 processes; PK data on 380 metabolites (cooking + metabolism exist for polyphenols).
- [V] Bioavailability mechanics are quantifiable: phytate:mineral molar ratio thresholds (Phy:Zn <15, Phy:Fe <1 for adequate absorption); in maize, soaking + germination + fermentation cut Phy:Zn 40.76 -> 7.77 (-81%) (Frontiers Nutr 2024, Nsabimana et al.). Phytate-rich cereals/legumes are staples in India.
- [V] Ayurveda tie-in with experimental data (PMC12900709, INFOGEST digestion + Caco-2): buttermilk (Takra, an "anupana" adjuvant) raised estimated bioavailable iron from cooked green gram (8.30 -> 25.78 mg/kg), calcium (300.31 -> 698.68), zinc (17.26 -> 21.32). Authors caution: in-vitro uptake is not whole-body absorption. => the Ayurvedic idea that food combinations change nutrient availability is testable and partially supported; also shows that dish-combination effects are large, not marginal.
- [V] Need context (from DD1 consensus): India micronutrient deficiencies vit D 61%, iron 54%, B12 53%, folate 37%; deficiencies almost double 6->12 months on GLP-1 therapy. Absorbable nutrient per small portion is what matters for GLP-1 users, not raw label content.
- [V] Meal-level absorption algorithms exist by title: Armah et al. "A complete diet-based algorithm for predicting nonheme iron absorption in adults" (J Nutr 2013); Hallberg & Hulthen "Prediction of dietary iron absorption: an algorithm..." (AJCN 2000). Full text blocked; validity/limits not read. [U] whether any implementation covers Indian dishes.
- VERDICT on problem: REAL and documented as an open limitation by both flagship Indian resources. The clinical demand link comes through DD1 (small-volume nutrient adequacy) and India's deficiency burden.

## 2. Prior-art kill-check
- Recipe-level nutrient calculators with retention factors: exist (USDA NNDB approach, INDB sensitivity analysis) but partial, static (one factor per food), US/one-method assumptions.
- Meal-level iron absorption algorithms: exist (Hallberg/Armah) but generic, not dish/process-aware for Indian preparations [U].
- Cooking-aware flavor pairing: searches surfaced only more pairing analyses (Northeast India sub-cuisines 2022; FlavorDiffusion 2025 pairing/chemical-interaction prediction; "Food Pairing Unveiled" 2024) and an in-vivo flavor-release study of pairings (2026). None cooking-aware in the snippets [U, weak evidence].
- Not found: an open, probabilistic, process-aware engine mapping Indian recipes -> cooked-dish composition AND bioavailable nutrients with uncertainty. [U: 3 of 5 key ScienceDirect/ResearchGate sources blocked; snippet-level check only.]
- Lab overlap: their estimator is raw-sum; no cooking/bioavailability layer visible. Risk: an unpublished CoSyLab extension [U].

## 3. Data
- [V] INDB (open, code on GitHub) = ready benchmark of 1,014 Indian recipes with ingredient grams; IFCT 2017/2004 raw values; RecipeDB Indian subset via professor; UK FCT/USDA fallback.
- [V] Phenol-Explorer retention + PK tables; USDA retention factors; Book-of-Yields-style yield tables (cited by the lab).
- [U] Ground truth for COOKED Indian dishes: scattered raw-vs-cooked studies (e.g., Kerala tribal foods raw vs cooked, Indian cooking-method reviews, cookware studies); no consolidated cooked-dish analytical set. Would need to curate ~100-300 measured points from the literature (labour, but feasible). In-vitro digestion (INFOGEST/Caco-2) datasets small.
- [U] Oil absorption/yield for Indian frying and tadka; cookware effects (iron kadhai raising iron content): literature review snippets say traditional cookware does not leach toxic elements; quantitative iron-transfer data not read.
- We have bioscience skills but no wet lab; validation must be literature back-testing + expert review.

## 4. Candidate technical framings (untested)
 H1 "Dish as process": represent each recipe as a small executable program (ingredients with quantities -> unit operations: soak, ferment, sprout, boil/pressure-cook, temper in fat, fry, combine with acid/dairy) with mass-balance and nutrient-state; propagate distributions (not point values) for yield, retention, leaching.
 H2 Bioavailability layer: rule/mechanism-based modifiers (phytate:mineral ratios, enhancers like ascorbic acid/organic acids, inhibitors like tannins in chai/polyphenols, fat for carotenoids, protein digestibility/DIAAS mixing across dal+cereal) computing absorbable iron/zinc/calcium/protein per dish and per combination (dal+rice, dal+curd/buttermilk, tea timing).
 H3 Hybrid learning: physics/biochemistry-informed forward model + small learned residual/calibration fitted to literature measurements; report calibrated uncertainty; active-learning list of "which measurements would shrink uncertainty most" (useful to the lab and a real contribution).
 H4 Combination search: find dish/plate combinations maximising bioavailable micronutrients per unit volume/energy under cuisine authenticity constraints (connects to DD1 F2/F3).
 H5 Cooking-aware flavor: predict flavor-compound changes by process to recompute pairing scores (secondary; heavy on chemistry data I did not find).
 Where AI is necessary: (a) NER/parsing of free-text methods (temper, pressure-cook 3 whistles, ferment overnight) into unit operations; (b) learned residual calibration on sparse data; (c) uncertainty-aware ranking; deterministic mechanistic core keeps outputs auditable.
 Honest caveat: much of H2 is nutrition-science rules already in the literature; the contribution is integration + uncertainty + Indian process coverage + open engine, not a new learning paradigm. It is "intentional engineering", not BERT-level novelty of method.

## 5. Local-AI justification
- Small local model parses recipe methods offline; deterministic engine computes. Privacy relevance lower here than in DD1/DD2; benefit mainly offline/regional-language use in kitchens and clinics. Modest.

## 6. Validation route
- Back-test predicted cooked/raw ratios against curated literature measurements (MAE, calibration of predictive intervals); compare vs INDB (raw sum), INDB+USDA-retention, and the lab's USDA-SR summation.
- Bioavailability: compare predicted relative changes with in-vitro digestion results (e.g., buttermilk-green gram) and published absorption-study directions; report direction accuracy + magnitude error separately.
- Expert review (dietitian/food scientist) of 20-30 dish audits; chef sanity check ("does the process representation match how this is cooked?").
- Limits: no wet-lab ground truth; predictions are estimates with intervals, not measurements.

## 7. Symposium fit
- Good: "what does your dal-chawal / tadka / fermented batter actually deliver?" is tangible for chefs; Ayurveda anupana angle is on the symposium's recurring themes; extends the lab's own nutrition estimator (natural collaboration hook, but also overlap risk).

## 8. Bio leverage
- Very high: digestion physiology, mineral chemistry, enzymology (phytase), absorption inhibitors/enhancers, protein digestibility.

## Score (rubric from 06_roadmap)
| Criterion | Max | Score | Note |
|---|---|---|---|
| Real problem + evidence | 25 | 19 | gap admitted by lab + INDB; demand via deficiency burden and DD1 |
| Novelty confirmed | 25 | 17 | verified gap in both flagship resources; pieces exist in food science; integration for Indian dishes not found (check partly blocked) |
| Technical originality | 20 | 16 | process-representation + uncertainty propagation + hybrid calibration = intentional engineering; not a new learning paradigm |
| Data + validation feasibility | 15 | 9 | INDB/IFCT/RecipeDB good; cooked ground truth must be curated; no wet lab |
| Symposium / chef relevance | 10 | 8 | |
| Bio leverage | 5 | 5 | |
| TOTAL | 100 | 74 | |
VERDICT: GO as the CORE ENGINE. Best score so far (DD1 69, DD2 59, DD3 74). DD3 supplies the technical substance that DD1 lacked; DD1 supplies the urgent use case and audience; DD2 becomes an optional safety/exposure layer (e.g., vitamin K1 per day is already in INDB).
What would change my mind: (a) a fetched, confirmed existing open engine doing process-aware Indian dish bioavailability -> KILL/downgrade; (b) unable to curate enough cooked-vs-raw Indian measurements for a fair back-test -> downgrade; (c) CoSyLab already building the same extension -> reposition as collaboration/extension.

## Tool notes
- fetch on arXiv PDF: worked cleanly (page-structured, no truncation for a 6-page paper).
- get_toc + read_section on PMC works well for prose (INDB methods returned in full).
- ScienceDirect/ResearchGate blocked again (Armah/Hallberg algorithm papers, Kalra ResearchGate copy). arXiv/PMC/Europe PMC are the reliable sources.
- batch_search returned "All 3 sources inaccessible" for the Armah/Hallberg query because all hits were ScienceDirect/ResearchGate (genuine block).
