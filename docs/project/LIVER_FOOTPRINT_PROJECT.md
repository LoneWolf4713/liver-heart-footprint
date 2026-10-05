# Liver and Heart Footprint of Indian Recipes
### BIO544 Computational Gastronomy mini-project (IIIT-Delhi, Prof. Ganesh Bagler, Monsoon 2026)
Complete project document. Compiled 2026-09-30 from the research log (files 15-33 in `research_log/`). Updated 2026-09-30: added the Heart profile and the grounded conversational assistant (file 33).

---

## 1. One-line summary
Paste any Indian recipe link (or just ask in plain language) and the app tells you how heavy that dish is on your **liver and heart**, what exactly is causing it, and the smallest authentic change that makes it lighter. It is backed by a research study of the cardiometabolic footprint of Indian cuisine.

Liver remains the lead story. Heart is a second profile on the same engine.

The professor's lab computed the **carbon footprint** of recipes. We compute the **liver footprint**: recipe → ingredients × quantities × cooking processes → liver-relevant nutrient load → placed in the context of an average Indian's day.

---

## 2. The problem (verified evidence)
| Fact | Source |
|---|---|
| Fatty liver (MASLD) affects **38.9%** of Indian adults (age-adjusted; crude 47.8%) | Phenome India cohort, Lancet Regional Health SE Asia 2026 |
| **27.4%** of young South Indian adults with BMI < 30 and no alcohol use have MASLD | Nair et al., J Clin Exp Hepatol 2025 (n = 2,373) |
| Obesity / energy surplus is the main driver of MASLD in India | Phenome India 2026 |
| Saturated fat raises liver fat the most; sugar raises it via fat-making in the liver; unsaturated fat the least | Luukkonen et al., Diabetes Care 2018 (overfeeding RCT) |
| Clinical diet advice targets fried foods, oil/saturated fat, sugar, refined carbs (maida, white rice), alcohol | Hospital/clinical guidance |
| **Spices are not the culprit**; curcumin (turmeric) improved liver markers in trials | Meta-analyses of curcumin RCTs |
| Average Indian eats ~2,212 (rural) / 2,240 (urban) kcal/day, fat ~60 / 70 g, protein ~62 / 63 g | NSO "Nutritional Intake in India" (HCES 2022-24, July 2025) |
| Saturated fat = **8.9% of energy nationally, 11.2% in North India** (recommended < 7%); added sugar > 5% of energy in 21 states; 62% of energy from carbohydrate | ICMR-INDIAB-21, Nature Medicine 2025 (n = 18,090) |
| Added sugar in mithai, street food, bakeries is uncounted because they carry no labels | ICMR-INDIAB-21 authors |
| Limits: added sugar 25-30 g/day; salt < 5 g; total fat ≤ 30% energy; HFSS = > 15% of energy from added oil/fat | ICMR-NIN Dietary Guidelines for Indians 2024 |
| Cardiovascular disease causes ~**28%** of deaths in India | Sci Rep 2023 (citing GBD) |
| Dietary risks caused **38.5%** of India's cardiovascular deaths in 2021; fastest-rising: sugary drinks, processed meat, **high sodium**, low whole grains, trans fat | Zinzuvadia et al., JACC 2025 (GBD analysis) |
| Mean salt intake **~8 g/day** (men 8.9, women 7.1) vs 5 g limit | National NCD Monitoring Survey, Sci Rep 2023 |
| India has no trans-fat database, so trans fat intake is uncaptured | ICMR-INDIAB-21 authors |

**Why it matters in daily life:** people cannot tell from a recipe how much it adds to their liver burden. A dish can look "under 2,000 kcal" but still use most of a day's saturated-fat budget (the Kurkure example: ~500 kcal/100 g is small against 2,000 kcal, but large in the context of a full day's food).

**Existing apps and the gap:**
- Reel/link → recipe → nutrition apps exist (Nutrola, Honeydew, Peel, ReciMe, Flavorish, RecipeBro), but they are generic and Western.
- Liver apps exist (Liverly, Liver Nutrition App), also Western/Mediterranean.
- None is built for Indian recipes, none models Indian frying, none uses the Indian day baseline, and none does cuisine-level science.

**Origin:** the idea came from the student's own observation (Instagram masala/curry recipes and the fatty-liver epidemic). The premise was corrected: the load comes from oil, ghee, butter, cream, sugar, maida and deep frying, not from spices.

---

## 3. User experience
1. Paste a recipe link (e.g., Hebbar's Kitchen paneer butter masala).
2. The app reads ingredients and quantities.
3. Per serving it shows how much of **today's budget** the dish uses: saturated fat, added sugar, refined carbs, calories, salt.
4. It places the dish against what an average person in your region already eats in a day.
5. It explains **why**: "72% of your saturated-fat budget, mostly from 1 tbsp butter + 2 tbsp cream."
6. It suggests lighter authentic versions and shows the load dropping.

---

## 4. Features
| Feature | What it does | Notes |
|---|---|---|
| **Link reader** | Reads schema.org Recipe structured data; small LLM fallback for other pages | Core input for the prototype = website links. YouTube later via official API descriptions only. **No Instagram.** |
| **Quantity normaliser** | tbsp / cup / katori / "2 onions" → grams; defaults for "salt to taste" | INDB unit table; LLM assist |
| **Ingredient → nutrient mapping** | Links each ingredient to INDB/IFCT (USDA fallback) | Our own alias dictionary + fuzzy match + LLM; we build it ourselves |
| **Frying model** (core) | Estimates oil actually absorbed by fried items (samosa, puri, pakora) | Evidence-based **ranges**, by food type × setting (home / street / restaurant) × oil type |
| **Liver and Heart budget bars** | Dish as % of daily limits, regional baseline pre-filled; two profiles on one engine | Heart adds sodium, trans fat, fat quality (MUFA/PUFA vs SFA), fibre/whole grains/legumes as protective. No single black-box score until weights are justified |
| **Grounded conversational assistant** | Natural-language questions: "why is this bad?", "what if I halve the butter?", "I had a samosa already, can I still eat this?" | Tool-calling agent: every number comes from the engine, never the LLM; cites sources; declines diagnosis/medication questions; can run on a small local model |
| **"Why" explanations** | Every number traced to an ingredient + citation | |
| **Swap suggester** (core) | Lighter authentic versions | See Section 6 |
| **Day builder** | Add all meals; watch budgets fill | |
| **Street-food mode** | Same dish at home vs street (more oil, reused oil, bigger portions) | Reused oil roughly triples saturated fat (Jain et al. 2024); labelled as a scenario |
| **"What's really the culprit?"** (optional) | Shows spices contribute almost nothing | Myth-check feature |
| Packaged-food label mode (optional, later) | Photo of a nutrition label → same budget view | |

---

## 5. The frying model (core component 1)
**Why it is needed:** for gravies, dals, sabzis and sweets, fat and sugar don't disappear during cooking, so **summing the ingredients works**. But fried recipes say "oil for deep frying": that is the oil in the kadhai, not the oil absorbed by the food. The biggest liver number in a samosa is simply not written in the recipe. For example, Tarla Dalal lists a samosa at 256 kcal because it ignores absorbed oil, roughly 60% too low.

**What it is:** not new physics. It assembles what food science knows and calibrates it on lab measurements.
- Mechanism (Dana & Saguy 2006; Ziaiifar 2008): water leaves, oil enters; most uptake happens as the food cools after leaving the fryer; the surface/crust matters; degraded oil raises uptake.
- **Layer 1, category ranges:** battered fritters (pakora, bhaji), flat dough (puri, bhatura), pastry (samosa, mathri, kachori), crisp namkeen, syrup-soaked sweets (jalebi, gulab jamun).
- **Layer 2, mass balance:** fat after frying = fat from ingredients + oil absorbed.
- **Layer 3, oil-reuse scenario:** same fat amount, worse saturated/trans-fat profile (street mode).

**Data (lab-measured fat in fried South Asian foods, 100+ values found):**
| Source | Content |
|---|---|
| Gupta et al. 2016 (PMC4826272) | ~30 Indian street/snack items from villages and an urban slum: samosa 29.6/29.2, kachori 32.0/46.6, bread pakora 47.6/26.4, bhatura 10.0/19.6, pakora 30.6, aloo tikki 27.4, mathri 57.2/38.5, namakpara 35.0, bhujia 39.6, boondi ladoo 14.6 g fat/100 g; with SFA/MUFA/PUFA/TFA % |
| Joshee et al. 2019 (PMC6894861) | 75 samples, 13 towns: gathiya, sev, chakli, puri, samosa, batata vada, medu vada, bhaji, jalebi and more (GC fatty-acid sums, which read lower than total-fat methods; kept separate) |
| UK CoFID 2021 | ~20 fried South Asian items (7 pakora types, samosas, puri, paratha, papad, sev, chevda, gulab jamun) + ~40 cooked sabzis with ghee-vs-oil versions |
| Chen, Gilbert & Khokhar 2009 | 10 South Asian dishes analysed vs calculated; puri fat uptake up to 18.4 g/100 g |
| safefood Ireland 2015 | Lab-analysed Indian takeaway: onion bhaji 16.98, chicken pakora 10.32 g/100 g, plus curries, rice, naan |
| Jain, Passi & Selvamurthy 2024 | Poori, bread pakora, mathri; fat and fat quality vs repeated frying (SFA ~5% → ~15%, trans fat up sharply) |
| Food-science experiments (e.g., Yadav & Rajan 2012 on poori) | Recipe changes vs measured oil content |

**Key finding:** the **same dish varies 3-5×**. Samosa ranges from about 9 g (retail) to about 30 g (street) fat per 100 g, and bread pakora from 18 to 48 g. There is no single "true" samosa value, so the model must output **honest ranges**, not one number. Street food medians are clearly higher than home food.

**Validation plan:** fit ranges on some sources and test on held-out sources (leave-one-source-out). A simple pooled version covered only about half the held-out values, so a street/home/restaurant-stratified model is required and will be tested during the build.

---

## 6. The swap suggester (core component 2)
**Why not use food pairing directly:** food pairing (shared flavour molecules, FlavorDB) tells you which ingredients **go together**, not which can **replace** each other. Teng, Lin & Adamic (2012) showed the co-occurrence network and the substitution network are different; substitutes are functionally equivalent and often healthier. A 2020 knowledge-graph study notes garlic and olive oil co-occur but aren't substitutable. A 2025 review says flavour compatibility cannot be determined by molecular similarity alone. FlavorDB also barely covers Indian fats (ghee = 1 molecule).

**How swaps are generated (data-driven, not from scratch):**
1. **Find hotspots:** which ingredients cause most of the load.
2. **Author-stated substitutions:** Indian recipe pages already say "alternative to cream, you can use curd", "use cashew paste instead of cream", "whole wheat flour instead of maida", "air-fry instead of deep-fry". Mined into an Indian substitution network. These are sparse on everyday dishes, so they're used where available.
3. **Context similarity:** ingredients that fill the same slot in the same dish across many recipes but rarely appear together.
4. **"Cook like the lightest 25% of real recipes":** often the most authentic fix is *less* of the same thing (e.g., butter in dal makhani moved from the median amount to the 25th percentile of real recipes).
5. **Food-pairing fit check (the professor's work, used correctly):** does the substitute go well with the rest of the dish?
6. **Rank** by load removed × authenticity × fit; show the top 3 with updated budget bars.

---

## 6b. Heart profile and conversational assistant (added)
**Heart profile:** same pipeline; different axes and weights.
- **Axes:** saturated fat, **trans fat** (from fried/reused oil and bakery fats; our fried-food lab data includes trans-fat shares), **sodium** (primary axis), fat quality, energy, added sugar.
- **Protective terms:** fibre, whole grains, legumes.
- **Limits:** WHO/ICMR — SFA < 10% of energy (< 7% stricter), trans fat < 1% of energy, salt < 5 g (sodium < 2 g).
- **Scope:** diabetes/glycaemic scoring deliberately NOT added.

**Grounded conversational assistant:** LLMs estimating the nutrition of mixed dishes directly are imprecise, so the assistant is a tool-calling agent over the engine. Its tools are `parse_recipe`, `compute_budget`, `frying_range`, `what_if`, `suggest_swaps` and `day_total`.
- **Evaluation:** numeric faithfulness (stated numbers equal engine outputs), citation correctness, refusal on medical questions.
- **Placement:** part of Deliverable 5.

## 7. Why this is computational gastronomy
| Course data pillar | Role in the project |
|---|---|
| Recipes (NER, quantities, processes) | Parsing any recipe into ingredient / amount / method |
| Nutrition (IFCT/INDB) | Saturated fat, sugar, energy per ingredient |
| Flavour (FlavorDB, food pairing) | Fit check for swaps |
| Health associations | Liver evidence setting the priorities |
| Cuisine patterns (co-occurrence, contribution analysis, culinary fingerprints) | Authentic swaps; which ingredients drive the cuisine's load (same contribution method the course used for spices) |

It extends the lab's own work (carbon footprint of recipes, recipe nutrition estimation, RecipeDB2) and answers open problems the lab has stated: health "for the complete dish", quantities, and cooking transformation. It matches the symposium's recurring question: "Can we tweak my recipe for better health?"

---

## 8. Research questions (the science beyond the app)
1. **Liver and heart footprint of Indian cuisine:** by region and dish type; which ingredients drive it (expected: fats, cream, sugar, maida, salt; spices ≈ 0).
2. **Dietetic textbook recipes vs popular web recipes:** how much heavier is what people cook from blogs than INDB's home-science versions? (Framed honestly as textbook vs web, **not** change over time: historical snapshots were too sparse.)
3. **Hidden load in unlabelled foods:** mithai, street snacks, bakery, including trans fat and sodium (strong data in Gupta et al. 2016).
4. **Load vs authenticity:** how much liver load can be removed while the dish stays recognisably itself.

---

## 9. Data
**Already available (open / downloaded, in `research_log/data/` and `research_log/dryrun/`):**
- INDB (Indian Nutrient Databank): 1,014 Indian recipes with grams, Indian ingredient nutrients (IFCT-based), unit conversions.
- UK CoFID 2021, safefood 2015 report, FlavorDB scrape, CulinaryDB.
- Compiled fried-food lab dataset (`dryrun/D4_frying/fried_foods_lab.csv`, 69 rows; 61 from verified sources).
- Baseline numbers (NSO, ICMR-INDIAB, ICMR-NIN 2024) in `dryrun/D7_baselines/baselines.csv`.
- Recipe websites: 6 polite, open sites with ~15,000 recipe URLs in their sitemaps (hebbarskitchen, archanaskitchen, indianhealthyrecipes, cookwithmanali, pipingpotcurry, ranveerbrar). Tarla Dalal and VegRecipesOfIndia block automated access, so they're excluded (no bypassing).

**Nice to have from the professor (not required):**
- RecipeDB2 bulk (129k recipes, Indian recipes tagged by state): more scale and regional labels for the research questions and swap statistics.
- The lab's recipe NER model (as a baseline for our parser).
- The lab's ingredient-to-nutrient mapping (for comparison; ours maps to INDB).

---

## 10. What has been verified (feasibility)
| Component | Result (on real data) |
|---|---|
| Link reader | 43 real recipe pages read; ~93% of fat/sugar lines in non-fried recipes have usable quantities |
| Quantity normaliser (LLM-assisted) | ~80% of all lines within ±25% grams; **~95% on fat/sugar lines** |
| INDB mapping | ~97% of fat/sugar lines matched correctly or to a nutritional equivalent; ~97% corpus coverage |
| Frying data | 61 verified lab values; strong street vs home difference |
| Frying model (simple pooled ranges) | Covered only ~half of held-out values → stratified model needed |
| Author-stated swaps | Real but sparse (3 of 10 dishes) → combine with quantity-reduction rule |

**Verdict: the app is buildable.** The open items affect accuracy and quality, not whether the app works.

**Integrity note:** two automated test sessions produced unreliable reports (circular gold labels, hardcoded or randomly generated "results"). Those numbers were audited and discarded (log files 26 and 31). Only the results above are trusted.

---

## 11. Open items to test during the build
1. Street/home/restaurant-stratified frying ranges, validated on held-out sources.
2. Ingredient-sum estimates vs lab-measured cooked dishes (CoFID, safefood, Chen 2009), using real recipe URLs.
3. The "lightest 25% of real recipes" swap rule on a real recipe corpus.
4. Human spot-check of 30 parsed lines and 30 mapped lines (files in `dryrun/D2_normaliser/` and `dryrun/D3_mapping/`).
**Rule for all future tests:** every number must trace to a saved source URL or data row. No hardcoded or synthetic data.

---

## 12. Honest limits (what we will not claim)
- It's an **estimate**, never a diagnosis; no individual liver outcome is predicted.
- Fried-food values are **ranges**, because the same dish genuinely varies 3-5×.
- Score weights are modelling choices (priority order is evidence-based: saturated fat > added sugar > refined carbs/energy > unsaturated fat); we show budget bars and test sensitivity.
- Textbook vs web is **not** "change over time".
- FlavorDB is not used to generate fat/sugar swaps (too sparse); only as a fit check.
- A recipe as written is not always what people eat (street/restaurant food is heavier).

---

## 13. Legal and ethical decisions
- **No Instagram, no Zomato/Swiggy data:** Instagram's terms bar automated collection; platform data has no scientific standing.
- YouTube only through the official Data API (descriptions), never media downloads.
- Websites: respect robots.txt, ≤ 1 request/second, no anti-bot bypass, store extracted facts + source URL only, never republish recipe text.
- Not medical advice; no shaming of brands or vendors.

---

## 14. Build order (after professor/TA approval; building starts ~1 month later)
1. Link reader + quantity normaliser + INDB mapping.
2. Frying model (stratified ranges, validated).
3. Liver and Heart budget bars + "why" explanations + regional baseline.
4. Swap suggester.
5. Grounded conversational assistant (on top of the engine).
6. Research analyses (own scraped corpus; RecipeDB2 if the professor shares it).

---

## 15. How we got here (short history)
- **Session 1:** broad research, six deep dives (GLP-1 food, food-drug interactions, cooking/bioavailability, Ayurveda, AI-recipe checking), a 13-idea menu; the session crashed before selection.
- **Session 2:** rounds of ideas: Iron-smart kitchens, Pairing Audit, Red Hexagon (FSSAI warning labels), Menu Truth (restaurant label plausibility), data-gated ideas (Kitchen Doctor, Hazard fingerprint), India problems (adulteration, pesticides). Menu Truth was killed for lack of cooked-dish ground truth, which led to the **data gate** rule. The student's own fatty-liver/masala idea was refined into this project.
- **Fallback projects if needed:** Iron-smart kitchens (grade-safe, scientific), Kitchen Doctor, Hazard fingerprint, India Adulteration Atlas. Full comparison in `research_log/32_ALL_PROJECTS_ANALYSIS.md`.

---

## 16. Key files in `research_log/`
| File | Content |
|---|---|
| 22_liver_footprint_concept.md | First full concept, grounding numbers, loopholes |
| 27_PROJECT_OVERVIEW_final.md | Final overview + feature discussion + verdicts |
| 28_frying_data_and_swap_research.md | Fried-food lab data hunt; why food pairing ≠ substitution |
| 26 / 31 AUDIT files | What was wrong in the automated test reports |
| 32_ALL_PROJECTS_ANALYSIS.md | Every project considered, scores, fit |
| 33_heart_and_chatbot_extension.md | Heart-profile evidence and chatbot design |
| submission/FORM_FIELDS.md, submission/PROPOSAL.md | Google Form answers and professor-facing proposal |
| 23_MASTER_SUMMARY_v2.md | Rules and chronology |
| dryrun/ | Real data and scripts from the dry-run (use only the parts marked genuine in file 31) |

---

## 17. Submission deliverables (as submitted to the Google Form; 2-student group, 5 deliverables)
1. Indian Fried-Food Fat Dataset and Frying Oil-Uptake Model (incl. trans-fat shift under oil reuse).
2. Recipe Cardiometabolic Load Engine (Liver and Heart profiles).
3. Authenticity-Preserving Substitution Engine.
4. Cardiometabolic Footprint Atlas of Indian Cuisine.
5. Web Application with a Grounded Conversational Assistant.
Deadline: Thursday 1 October 2026, 11:59 pm.

---

## 18. Sodium and trans fat: how the gaps are filled (added 2026-10-01)
**The problems:** about 78% of recipe salt lines say "to taste", and INDB has no trans-fat column.

**Sodium:**
- The default for "to taste" is the dish-specific median of salt amounts in recipes that do state salt (about 22% of salt lines are quantified).
- Sodium already in ingredients comes from INDB (papad, pickle, cheese, baking soda, bread).
- Cross-checks:
  - A Delhi study (PMC6482771) found 90% of daily salt comes from home-cooked food and 95% of sodium from salt added while cooking. Contribution by dish type: vegetable 31%, pulse 26%, cereal 23%. South India is similar: pulse 30%, rice 27%, vegetable 17%.
  - National NCD Monitoring Survey: about 8 g salt/day (men 8.9, women 7.1).
  - Lab-measured salt in takeaway dishes (safefood 2015, UK CoFID).
- Sodium is reported as a range and flagged as lower-confidence.

**Trans fat:**
- **Fresh commercial oils and fats:** at most 2% of fat. This is the FSSAI regulatory cap since 2022. The FSSAI PAN-India survey (2021, 6,245 lab samples) found only 3.14% of samples exceeded 2%, mostly vanaspati, shortenings and margarine.
- **Street and reused-oil fried items:** measured values from Gupta 2016 (trans fat up to about 12% of fat in some fresh-fried street items) and Jain 2024 (rise with repeated frying).
- **Snacks:** Joshee 2019, trans fat 0.02–4.4% of fatty acids.
- **Biscuits and bakery:** 0.1–3.2 g/100 g (PMC4571254).
- Trans fat is reported mainly for fried, bakery and sweet foods, and is near zero for most home cooking.

## 19. Validation of ingredient-sum estimates (genuine result, 2026-10-01)
Source: `38_VALIDATION_RESULT_v2.md`, audited in `39_AUDIT_of_validation_v2.md`.

**Setup:**
- 9 dishes, 11 dish-to-lab pairs, 27 real recipes.
- Ground truth: lab-analysed only (UK CoFID rows from Leeds 2007, Aspland & James 1997 and LGC; safefood 2015).
- 99.9% of ingredient mass mapped, using CoFID raw ingredients because the INDB repo lacks the raw IFCT table.

**Results:**
- **On average, the ballpark is right:** median recipe/lab ratio 1.00 (fat per dry matter) and 0.88 (fat as % of energy). There is no systematic bias for home cooking.
- **Per-dish spread is wide:** 0.55–2.8×, because recipes vary in oil and cream.
- **Takeaway food is richer:** recipes under-estimated all 5 takeaway dishes (median 0.77).

**Consequences for the design:** estimates are per recipe (the user's recipe as written), reported as ranges, with an explicit home vs restaurant/street setting. Never claim a single composition for a dish name.

**Data note:** request the IFCT 2017 raw table from NIN or through the professor. CoFID raw ingredients are the fallback.

## 20. Caveats in context (the professor's own work states similar limits)
- **Kalra et al. 2020** (lab nutrition estimation) sums raw ingredients and notes that accounting for cooking yield would improve accuracy, but "there is no such consolidated resource". It was validated on calories only (about 36 kcal/serving error), with about 72% ingredient-matching accuracy.
- **Singh & Bagler 2018:** results "contrary to earlier reports"; "quality and completeness of data is a key factor".
- **Jain, Rakhi & Bagler 2015:** flavour profiles are "limited by the availability of data", and cooking changes to flavour are not accounted for.
- **FlavorDB:** "not an exhaustive repository".
- **Course notes:** the unordered-ingredient recipe model "misses out many critical factors" and is a "first step".

Our caveats answer several of these directly: cooking and frying are modelled, Indian composition data is used, and results are honest ranges.

## 21. Overall assessment (2026-10-01)
**Buildable:** every core component has been checked on real data.

**Strong fit with the course and lab:**
- the carbon-footprint framework applied to liver and heart load;
- an India-specific, current problem;
- rare among classmates;
- five non-trivial deliverables.

**Risks:** over-claiming precision (avoid it by using ranges), and scope for two people (prioritise the engine, frying model and app; then the atlas and swaps).

**Symposium:** not guaranteed, but this is the strongest candidate evaluated.
