# Liver and Heart Footprint of Indian Recipes
## A Computational Gastronomy Framework for Estimating and Reducing the Cardiometabolic Dietary Load of Indian Food

**Course:** BIO544 Computational Gastronomy, Monsoon 2026
**Instructor:** Prof. Ganesh Bagler, IIIT-Delhi
**Group:** Group 45 | Parth Verma [2024407], Pratyaksh Kumar [2024431]

---

## 1. Abstract
Fatty liver disease (MASLD) affects an estimated 38.9% of Indian adults, and cardiovascular disease causes about 28% of deaths in India, with dietary risks accounting for 38.5% of cardiovascular deaths. Their shared dietary drivers (saturated and trans fat, added sugar, refined carbohydrate, sodium, excess energy and deep-fried foods) are embedded in everyday Indian recipes. We introduce the **liver and heart footprint** of a recipe: a transparent, per-serving estimate of the cardiometabolic nutrient load of a dish, reported through a Liver profile and a Heart profile, computed from its ingredients, quantities and cooking process, and expressed against national dietary limits and the average Indian's existing daily intake. Methodologically, this parallels the carbon footprint of recipes: the recipe is the computational object, and the impact axes are hepatic and cardiovascular dietary load. The project delivers:
- an open dataset and model of oil uptake in Indian fried foods;
- a recipe-to-load computation engine grounded in Indian food composition data;
- an authenticity-preserving substitution engine;
- a cuisine-level footprint analysis of Indian food;
- a web application that accepts any recipe link, with a grounded conversational assistant.

## 2. Motivation
**Burden.** Age-adjusted MASLD prevalence in Indian adults is 38.9% (Phenome India cohort, 2026); among young South Indian adults without obesity or alcohol use it is 27.4% (Nair et al., 2025). Obesity and metabolic dysfunction are its predominant drivers in India.

**Cardiovascular burden.** Cardiovascular disease accounts for about 28% of deaths in India. Dietary risks caused 38.5% of cardiovascular deaths in 2021, and the fastest-rising dietary risks since 1990 include sugar-sweetened beverages, high sodium, low whole grains and trans fat (GBD-based analysis, 2025). Mean salt intake is about 8 g/day against a 5 g limit (National NCD Monitoring Survey). Trans fat intake is poorly characterised because India lacks a trans-fat composition database.

**Dietary drivers.** Controlled overfeeding shows saturated fat raises intrahepatic fat the most, simple sugars raise it through de novo lipogenesis, and unsaturated fat the least (Luukkonen et al., 2018). Clinical guidance targets fried foods, saturated fat, added sugar and refined carbohydrates. Spices are not implicated; curcumin trials report improved hepatic markers.

**The Indian baseline is already high.** Saturated fat supplies 8.9% of energy nationally and 11.2% in North India, against a recommended limit below 7%. Added sugar exceeds 5% of energy in 21 states, and 62% of energy comes from carbohydrate (ICMR-INDIAB-21, 2025). Mean intake is about 2,212–2,240 kcal/day with 60–70 g fat (NSO, 2025). Sweets, street foods and bakery items carry no labels, so their load goes uncounted.

**The gap.** A cook or consumer cannot tell how much a given recipe adds to this load. Recipe-level nutrition tools sum raw ingredients, ignore oil absorbed during frying, and are built on Western food composition data. Consumer liver-diet applications target Western and Mediterranean diets. No tool reasons about Indian recipes, Indian cooking processes and the Indian dietary baseline together.

## 3. Objectives
1. Quantify the liver- and heart-relevant load of any Indian recipe per serving, including the oil absorbed in frying and its fat quality.
2. Place that load in the context of national limits (ICMR-NIN 2024) and regional average intake (NSO, ICMR-INDIAB).
3. Explain which ingredients and processes drive the load.
4. Propose lighter versions that remain recognisably authentic, with quantified benefit.
5. Characterise the liver footprint of Indian cuisine at scale.

## 4. Methodology

### 4.1 Recipe representation
A recipe is represented as a set of ingredients with quantities and processes: *(ingredient, quantity, unit, state, process)*. This extends the unordered-ingredient-set representation used in food-pairing studies with the quantity and process information needed for nutritional reasoning.

### 4.2 Recipe ingestion and normalisation
- **Extraction.** schema.org `Recipe` structured data is used where published; a small language model with a constrained output schema handles unstructured pages. Recipe collection follows each site's robots.txt with rate limiting.
- **Unit normalisation.** Quantities are converted to grams using standard volumetric equivalents, Indian household measures (katori, cup, spoon, pieces) and ingredient densities. Unquantified entries ("to taste") receive documented defaults.
- **Ingredient mapping.** Ingredients are mapped to the Indian Nutrient Databank (INDB; IFCT 2017/2004-based, with UK/USDA fallback) through an alias dictionary, fuzzy matching and model-assisted disambiguation. This yields per-100 g energy, total fat, SFA/MUFA/PUFA, sugars and sodium.

### 4.3 Cooking and frying adjustment
- **Non-fried dishes.** For gravies, dals, sabzis and sweets, fat and sugar are conserved through cooking, so the load is the ingredient sum. Moisture loss affects concentration, not per-serving load.
- **Fried dishes.** Recipes specify the frying medium ("oil for deep frying") but not the oil absorbed, which is the dominant load in these dishes.
- **Frying model.** A range model estimates absorbed oil by food category (battered fritters, flat doughs, stuffed pastries, crisp namkeen, syrup-soaked sweets) × preparation setting (home, street, restaurant/takeaway) × frying medium. It is parameterised from laboratory-measured fat content of Indian fried foods (Deliverable 1).
- **Oil reuse.** An oil-reuse scenario captures the shift towards saturated and trans fat reported under repeated frying.
- **Output format.** Because measured fat for the same dish varies several-fold across preparation settings, fried-dish estimates are reported as evidence-based ranges rather than point values.

### 4.4 Cardiometabolic budget and footprint (Liver and Heart profiles)
- **Per-serving load** on six axes: saturated fat, trans fat, added sugar, refined carbohydrate, energy and sodium, each as a percentage of the daily limit. Fat quality (MUFA/PUFA vs SFA) and protective components (fibre, whole grains, legumes) are also reported. Limits are SFA < 7% (and < 10%) of energy, trans fat < 1% of energy, added sugar ≤ 25–30 g, salt < 5 g (sodium < 2 g), and the HFSS criterion of > 15% energy from added fat (ICMR-NIN 2024; WHO).
- **Sodium and trans fat.** These need dedicated data because most recipes write "salt to taste" and Indian composition tables lack trans-fat values.
  - *Sodium* is estimated from the salt quantities stated in other recipes of the same dish, together with ingredient-bound sodium (INDB). It is cross-checked against national evidence that most dietary sodium in India comes from salt added during home cooking, and against measured restaurant/takeaway salt.
  - *Trans fat* is assigned from FSSAI's national trans-fat survey and the regulatory cap for fresh oils and fats, and from measured trans-fat shares in street and fried foods, including the effect of oil reuse.
- **Per-recipe ranges and setting.** Estimates describe the user's recipe as written, not a generic dish. They are reported as ranges, and restaurant/takeaway preparations are modelled as typically richer than home recipes.
- **Two profiles on one engine.** The *Liver profile* weights saturated fat, added sugar, refined carbohydrate and energy surplus most. The *Heart profile* weights saturated and trans fat, sodium and fat quality most.
- **Contextual view.** The same load is shown against the remaining headroom for an average person in the user's region, using NSO intake and ICMR-INDIAB regional macronutrient profiles.
- **Attribution.** Every value is traced to contributing ingredients and processes, with the source of each constant cited.
- **Footprint indices (optional summary).** Per-profile weighted combinations of budget fractions with evidence-ordered weights. For the Liver profile: saturated fat > added sugar > refined carbohydrate/energy > unsaturated fat. For the Heart profile: saturated and trans fat, and sodium, lead. Fibre and pulses act as protective terms. It will be accompanied by a sensitivity analysis over the weights. The per-axis budget remains the primary output.

### 4.5 Grounded conversational assistant
- **Role.** A natural-language interface over the engine (e.g., "why is this dish heavy on my liver?", "what if I halve the butter?", "I already had a samosa today; can I still have this?").
- **Design.** A tool-calling agent: the language model plans and explains, while every quantitative statement comes from engine functions (parse recipe, compute budget, frying range, what-if modification, suggest swaps, day total), with sources cited. This addresses the documented imprecision of language models when estimating the nutrient content of mixed dishes directly.
- **Safeguards.** Diagnosis and medication questions are declined. The assistant can run on a small local model for privacy.
- **Evaluation.** Numeric faithfulness (stated numbers equal engine outputs), citation correctness and appropriate refusal.

### 4.6 Authenticity-preserving substitution
- **Why not flavour similarity alone.** Flavour-compound similarity identifies ingredients that pair well, not ingredients that can replace one another. Substitution therefore combines functional, statistical and flavour evidence.
- **Hotspot detection.** Identify the ingredients contributing most of the load.
- **Candidate generation:**
  - an Indian ingredient-substitution network built from substitutions stated in Indian recipe sources;
  - recipe-context similarity (ingredients occupying the same role in the same dish across recipes but rarely co-occurring);
  - a functional-role table (tempering fat, gravy richness, sweetener, frying technique, flour).
- **Quantity rule.** For each dish, the distribution of each load-driving ingredient across real recipes is estimated, and moving towards the lower quartile ("cook like the lightest quarter of real recipes") is proposed as the most authentic reduction.
- **Fit check.** Shared flavour compounds between the substitute and the remaining ingredients (FlavorDB) are used as a food-pairing compatibility check.
- **Ranking.** Candidates are ranked by load reduction × authenticity (observed frequency in real recipes of the dish) × pairing fit.

### 4.7 Cuisine-level analysis
The engine is applied to a large corpus of Indian recipes to estimate:
- the distribution of liver and heart load across dish categories and regions;
- ingredient contributions to the cuisine's load (a contribution analysis analogous to ingredient contribution in food-pairing studies);
- differences between dietetic textbook recipes (INDB, derived from institutional home-science manuals) and popular web recipes of the same dishes;
- the load (including trans fat and sodium) of unlabelled street snacks and sweets relative to comparable preparations.

## 5. Data sources
| Data | Use |
|---|---|
| Indian Nutrient Databank (INDB): 1,014 Indian recipes, ~1,100 foods; IFCT 2017/2004-based | Nutrient composition, unit conversions, textbook recipe baseline |
| Published analytical studies of Indian fried foods (e.g., Gupta et al. 2016; Joshee et al. 2019; Jain et al. 2024; Chen, Gilbert & Khokhar 2009; safefood 2015) and UK CoFID 2021 analysed South Asian foods | Frying model; validation of cooked-dish estimates |
| Indian recipe websites (publicly accessible pages, collected per robots.txt); RecipeDB2 if made available by CoSyLab | Recipe corpus, quantity distributions, substitution statements |
| FlavorDB | Food-pairing fit of substitutions |
| NSO Nutritional Intake in India (2025); ICMR-INDIAB-21 (2025); ICMR-NIN Dietary Guidelines for Indians (2024) | Daily baselines and limits |
| Hepatology and nutrition literature (e.g., Luukkonen et al. 2018; Phenome India 2026) | Evidence ordering of liver-relevant nutrients |
| Cardiovascular evidence (GBD dietary-risk analyses for India; National NCD Monitoring Survey salt data; WHO fat and sodium guidelines) | Heart-profile axes and limits |
| Sodium sources in Indian diets (household salt-use studies) and FSSAI PAN-India trans-fat survey (2021); published trans-fat measurements of Indian snacks, sweets and bakery products | Sodium estimation for unquantified salt; trans-fat assignment |
| IFCT 2017 raw-ingredient table (NIN, on request) and UK CoFID raw-ingredient data (fallback) | Ingredient composition including water, for dry-matter comparisons |

## 6. Deliverables
| # | Deliverable | Output | Evaluation |
|---|---|---|---|
| 1 | **Indian Fried-Food Fat Dataset and Frying Oil-Uptake Model** | Open curated dataset of laboratory-measured fat and fatty-acid composition of Indian fried foods with provenance; category × setting range model | Leave-one-source-out coverage of held-out measurements; range width; median error |
| 2 | **Recipe Cardiometabolic Load Engine (Liver and Heart profiles)** | Pipeline from recipe to per-serving Liver and Heart budgets with ingredient-level attribution | Extraction, normalisation and mapping accuracy on annotated ingredient lines; agreement with laboratory-analysed cooked South Asian dishes |
| 3 | **Authenticity-Preserving Substitution Engine** | Indian substitution network; ranked swaps with quantified load reduction | Agreement with substitutions stated in recipe sources; load reduction; authenticity (frequency in real recipes); pairing fit |
| 4 | **Cardiometabolic Footprint Atlas of Indian Cuisine** | Cuisine-level analysis and visualisations: liver and heart load by category and region, driver contributions, textbook vs web recipes, unlabelled street foods (incl. trans fat, sodium) | Statistical comparisons with uncertainty; sensitivity to modelling assumptions |
| 5 | **Web Application with a Grounded Conversational Assistant** | Recipe-link input; Liver and Heart budget bars; explanations with citations; home-vs-street estimates; day builder; lighter alternatives; tool-calling assistant answering natural-language questions | End-to-end demonstration; assistant numeric faithfulness, citation correctness, refusal behaviour |

## 7. Relation to computational gastronomy and prior work
- **Computational gastronomy data.** The project operates on the field's core data types (recipes, ingredient composition, flavour profiles and health associations) and uses its core methods: recipe structuring, ingredient mapping, co-occurrence statistics, contribution analysis and food pairing.
- **CoSyLab work.** It extends recipe-level nutrition estimation and the carbon-footprint-of-recipes framework to a new impact axis, adds the cooking transformation (frying) that ingredient sums miss, and evaluates health at the level of the complete dish.
- **Novelty.** An Indian-specific, process-aware, baseline-contextualised liver and heart load estimate for recipes; an agentic interface grounded in computed values; an open dataset of measured fat in Indian fried foods; and a substitution method that separates substitutability from flavour pairing.

## 8. Scope, limitations and ethics
- Outputs are dietary estimates for awareness and recipe improvement, **not medical diagnosis or advice**. No individual clinical outcome is predicted.
- Fried-food values are reported as ranges, reflecting genuine variation in preparation.
- Ingredient-based estimates describe a specific recipe. Individual preparations of the same dish can differ substantially, and restaurant versions are often richer, so the system does not present a single value as "the" composition of a dish.
- Sodium for unquantified salt and trans fat outside fried, bakery and sweet foods are lower-confidence estimates and are flagged as such.
- A recipe as written may differ from what is consumed, especially street and restaurant food. Preparation settings are therefore modelled explicitly.
- Data collection uses publicly accessible pages only, respects robots.txt and rate limits, stores extracted ingredient facts with source attribution, and does not republish recipe text. No social-media or food-delivery platform data is used.

## 9. Work plan
1. Data curation: fried-food dataset, nutrient mapping resources, baselines.
2. Liver and heart load engine and frying model, with validation against laboratory-analysed cooked dishes.
3. Substitution engine.
4. Cuisine-level analysis.
5. Web application, grounded conversational assistant and final report.

## 10. Key references
1. Phenome India cohort. Burden of MASLD and liver fibrosis in India. *Lancet Regional Health – Southeast Asia*, 2026.
2. Nair A. et al. Prevalence of transaminitis and MASLD among young Indian adults. *J Clin Exp Hepatol* 15(3):102466, 2025.
3. Luukkonen P.K. et al. Saturated fat is more metabolically harmful for the human liver than unsaturated fat or simple sugars. *Diabetes Care*, 2018.
4. Anjana R.M. et al. Dietary profiles and associated metabolic risk factors in India from the ICMR–INDIAB survey-21. *Nature Medicine* 31:3813–3824, 2025.
5. National Statistics Office. *Nutritional Intake in India* (HCES 2022–24), 2025.
6. ICMR-NIN. *Dietary Guidelines for Indians*, 2024.
7. Vijayakumar A. et al. Development of an Indian Food Composition Database (INDB). 2024 (PMC11277795).
8. Gupta V. et al. Unhealthy fat in street and snack foods in low-socioeconomic settings in India. 2016 (PMC4826272).
9. Joshee K. et al. Fatty acid profiling of 75 Indian snack samples. *PLOS ONE*, 2019.
10. Jain A., Passi S.J., Selvamurthy W. Total fat and fatty acid profile including TFA content of Indian fried foods versus the oils used for frying. *J Food Sci Technol* 61:2185–2195, 2024.
11. Chen A., Gilbert P., Khokhar S. Estimating the nutrient composition of South Asian foods using a recipe calculation method. *Food Chemistry* 113:825–831, 2009.
12. Teng C.-Y., Lin Y.-R., Adamic L.A. Recipe recommendation using ingredient networks. *ACM WebSci*, 2012.
13. Garg N. et al. FlavorDB: a database of flavor molecules. *Nucleic Acids Research* 46:D1210, 2018.
14. Ahn Y.-Y. et al. Flavor network and the principles of food pairing. *Scientific Reports* 1:196, 2011.
15. Goel M. et al. Cultural context shapes the carbon footprints of recipes. arXiv:2311.08416, 2023.
16. Kalra J.S. et al. Nutritional profile estimation in cooking recipes. arXiv:2004.12286, 2020.
17. Zinzuvadia V. et al. Statewide burden of cardiovascular disease attributable to dietary risk factors in India in the last 3 decades. *JACC* 85(12 Suppl):354, 2025.
18. Awareness, behavior, and determinants of dietary salt intake in adults: results from the National NCD Monitoring Survey, India. *Scientific Reports*, 2023 (PMC10517942).
19. Knowledge and behaviors related to dietary salt and sources of dietary sodium in north India (PMC6482771).
20. FSSAI. PAN-India Survey Results on Trans-fat in Different Food Categories, 2021.
21. Studies on saturated and trans fatty acids composition of biscuits in the Indian market (PMC4571254).
