# 20 New idea round WITH DATA GATE (2026-09-29)
User ask: >=4 genuinely good ideas; real-world problems/frustrations of restaurants, customers, cooks; data gate enforced (ground truth verified, open, sized) BEFORE scoring. No fieldwork; no scraping of apps; no manual copying of platform data.

## Data verified this round
- [V] Food.com Recipes & Interactions (Shuyang Li, 2019; Kaggle + mirrors): ~180k-230k recipes (ingredients, steps, techniques) + ~700k-1.1M user interactions with RATING and REVIEW TEXT, 18 years, ~0.9 GB. Public research dataset.
- [V] NYC DOHMH Restaurant Inspection Results (NYC Open Data, updated 25 Sep 2026): ~295k violation rows, 31 cols incl. CUISINE DESCRIPTION, violation code + full text, critical flag, score, grade, dates, geo. Open licence.
- [V] UK Food Hygiene Rating Scheme open data (companion; component hygiene/structural/management scores).
- [V] Yelp Open Dataset: businesses (categories incl. Indian), reviews with text + date + stars, users; licence = educational/academic use (no redistribution).
- [V] RecipeDB2 (Aug 2026) + CulinaryDB + INDB for recipe structure, processes, ingredients (from 15/19).
- [V] FDA 2017-18 retail risk-factor study (via RapidEye 2026 summary): improper holding time/temperature out of compliance in 94.4% full-service restaurants; NYC 2025: 25,054 inspections, only 3.5% zero violations.

## Prior-art checks this round
- Allergens from dish names/menus: DONE (Brahimi, Int J Inf Technol 2025, menu -> recipe search -> allergen-free recommendation, 87-90%; JAIC 2026 multilabel allergen detection from 15,823 recipes, SVM F1 ~0.87-0.99). -> DROPPED.
- Recipe-review mining: student topic-modelling projects (e.g., 6k Allrecipes reviews, KeyBERT/LDA); Druck & Pang 2012 (ACL) mined recipe refinements from reviews; Fatemi et al. 2023 learned ingredient substitutions from Recipe1M comments. NOT found: linking complaint TYPE to recipe COMPOSITION deviations + measuring which fixes/substitutions WORK (outcome-aware).
- Inspections: cuisine-level dashboards common (Power BI, GitHub); sushi-rice risk-factor study (IFPTI 2023). NOT found: linking the COOKING PROCESSES a cuisine relies on (from recipe corpora) to the violation TYPES its restaurants receive.
- Consistency/delivery complaints vs dish structure: searches blocked -> UNKNOWN (treat as open but unverified).

## IDEAS (all pass the data gate)
### I1 "Kitchen Doctor": why home recipes fail, and which fixes actually work
Frustration: cooks follow a recipe and it comes out too salty/dry/bland/runny; recipe writers and AI recipe generators do not know which of their recipes will fail.
Question (science): Are failure complaints ("too salty", "dry", "didn't set", "bland", "too sweet") predictable from how a recipe's composition deviates from its dish family's norm (salt %, liquid:flour, fat %, sugar %, time/temp)? And which crowd fixes/substitutions raise the reviewer's rating (outcome-aware), vs which are folklore?
Ground truth: 700k+ Food.com reviews with ratings + text (complaints and self-reported modifications) linked to exact ingredient lists/steps.
AI necessary: complaint + modification extraction from free text (small LLM/NER), dish-family norms learned from 180k recipes, predictive + causal-ish (matched) analysis of fix outcomes.
Deliverables: (1) complaint/fix-annotated review corpus (open); (2) "failure map": which compositional deviations drive which complaints, per dish family; (3) fix-effectiveness table (which substitutions/tweaks raise ratings, with matched comparisons); (4) Recipe checker: paste a recipe -> likely complaints + evidence-backed fixes (also usable to audit LLM-generated recipes).
Valuable either way: yes (if complaints are NOT predictable from composition, that says failures are technique/skill-driven, itself useful).
Risks: US-centric recipes (Indian subset exists but smaller); review self-selection; quantity parsing effort. Rarity: HIGH vs classmates (they build recommenders/chatbots).
Prof fit: recipes as data, ingredient ratios, NER (his LREC-COLING work), RecipeDB2 norms; answers the lab's own "quantities matter" limitation.

### I2 "Hazard fingerprint of cuisines": do the cooking processes a cuisine depends on predict its food-safety violations?
Frustration: restaurants fail inspections and diners get sick; improper holding is the #1 risk factor (94% of full-service restaurants out of compliance, FDA). Inspectors (and FSSAI's new risk-based inspections, Apr 2026) lack a way to know WHICH process risks to prioritise for WHICH kitchen type.
Question (science + food microbiology): Map each cuisine's typical processes (from recipe corpora: cooked rice held warm, cold garnishes/raw herbs, fermented batters, marination, large-batch gravies, reheating, cooling) to hazard classes (B. cereus, C. perfringens, Listeria, etc.), then test whether cuisines' process profiles predict the TYPES of violations their restaurants receive in NYC (and UK FHRS), controlling for size, borough, inspection history.
Ground truth: ~295k NYC violation records with cuisine + violation text; UK FHRS.
AI necessary: process extraction from recipe text (NER of techniques/holding/cooling), violation-text classification into hazard classes, hierarchical models with controls.
Deliverables: (1) cuisine process-profile dataset (from RecipeDB2/CulinaryDB); (2) process->hazard map grounded in microbiology literature; (3) statistical test + effect sizes on NYC data; (4) risk-prioritisation checklist/tool per menu (enter menu -> highest-risk processes to control).
Valuable either way: yes (a null result says violations are about management, not cuisine, which counters stereotyping).
Risks: ETHICS: must not stigmatise ethnic cuisines -> frame at PROCESS level, report controls, avoid ranking cuisines as "dirty"; cuisine label is owner-reported; recipe corpora describe home recipes, not restaurant practice.
Bio leverage: HIGH (microbiology). Rarity: HIGH. Prof fit: medium-high (recipe processes = his data; new health dimension).

### I3 "Complaint physics": which dishes disappoint diners, and why (dish-level review mining linked to cooking structure)
Frustration: restaurants get "soggy on delivery", "not like last time", "too spicy/bland", "oily" complaints and don't know which menu items cause them; customers can't predict which dishes travel/hold well.
Question: Do dish properties derived from recipes (deep-fried/crisp, gravy-based, bread, rice, number of steps/ingredients = complexity, chili load) predict specific complaint types in reviews (sogginess after delivery/takeout, inconsistency, oiliness, spice mismatch)?
Ground truth: Yelp Open Dataset reviews (text + stars + dates; delivery/takeout attributes), dish mentions extracted from text; Indian restaurants as focus plus other cuisines for contrast.
AI necessary: dish-mention NER in reviews, aspect-based complaint classification, linking dish names to recipe structure (RecipeDB2).
Deliverables: (1) dish-complaint atlas; (2) model: dish structure -> complaint risk; (3) "travels well?" and "consistency risk" scores for menu items; (4) menu-design tool for cloud kitchens.
Risks: dish-to-review attribution noise (a review mentions several dishes); Yelp = US/Canada cities only; licence academic-only. Prior art UNVERIFIED (searches blocked) -> must re-check.
Rarity: HIGH. Prof fit: medium.

### I4 "When tomato hits Rs 100": data-driven substitutes for tomato in Indian gravies
Frustration: every price spike (tomato +31% YoY Jun 2026; ~Rs 200/kg in 2023) restaurants and households scramble; advice is anecdotal.
Question: What functional roles does tomato play in Indian gravies (sourness, umami, colour, body, aroma) and which cheaper ingredient combinations reproduce that role profile? Ground truth = the cuisine itself: regional versions of the same dish types that already use no tomato (tamarind, kokum, curd, amchur, onion-heavy bases) in RecipeDB2/INDB; hold them out and test whether the model recovers them.
AI necessary: learned ingredient role embeddings from co-occurrence + FlavorDB + nutrient composition; constrained substitution search.
Deliverables: (1) role-profile dataset for Indian gravy ingredients; (2) substitution model + held-out-recipe back-test; (3) price-aware recommender using DoCA daily prices (open) with backtest over 2023/2026 spikes; (4) chef-facing substitution cards.
Valuable either way: yes (quantifies which roles are replaceable vs not).
Risks: no tasting validation (back-test on real recipes only); generic substitution prior art exists (novelty = function + price + Indian regional recovery).
Rarity: HIGH. Prof fit: HIGH (FlavorDB, recipes, Indian cuisine). India relevance: HIGHEST of the four.

## Comparison (data gate PASSED for all four)
| | I1 Kitchen Doctor | I2 Hazard fingerprint | I3 Complaint physics | I4 Tomato-shock |
|---|---|---|---|---|
| Ground truth | 700k+ reviews w/ text + exact recipes | 295k violations w/ cuisine + text | Yelp reviews (academic licence) | held-out regional recipes + open prices |
| Real frustration | home cooks, recipe writers, AI recipes | restaurants, diners, inspectors | restaurants, delivery customers | restaurants, households (India) |
| Science inside | recipe composition -> failure | process microbiology -> violations | dish structure -> complaints | functional roles of ingredients |
| Main risk | US-centric | ethics framing, confounders | attribution noise, prior art unchecked | no taste validation |
| India relevance | medium | medium (FSSAI risk-based inspections) | low-medium | very high |

## USER FEEDBACK on round 20 (2026-09-29)
- I1-I3 "good" but NOT India-specific; kept as FALLBACK pool (if nothing better, select from these).
- I4 tomato-shock REJECTED: no way to verify our substitution "was true" -> no basis in reality.
- Core complaint: ideas are out of touch with ground realities Indians face.
- NEW RULES: (1) problem must be one Indians really face (news headlines, Reddit, daily life); (2) evidence benchmark = at least ~100 complaints/mentions; (3) India-centric.
- USER'S OWN IDEA to evaluate: Instagram/YouTube reel recipes (masalas, curry masala, street food) are heavy in masala; traditional recipes used less; India has a fatty-liver epidemic; doctors tell fatty-liver patients to avoid heavy-spice food. App: paste reel link -> get recipe (caption or transcript via speech-to-text) -> LLM extracts ingredients -> health score / masala heaviness / impact for conditions like fatty liver. Also: WHY do doctors say avoid spices?
