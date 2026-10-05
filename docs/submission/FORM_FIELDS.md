# Google Form entries (copy-paste)

**Group Number:** 45

**Roll numbers of all the students in the group:** 2024407, 2024431

**Project Title:**
Liver and Heart Footprint of Indian Recipes: A Computational Gastronomy Framework for Estimating and Reducing the Cardiometabolic Dietary Load of Indian Food

**Description:**
Fatty liver disease (MASLD) affects an estimated 38.9% of Indian adults, and cardiovascular disease causes about 28% of deaths in India, with dietary risks accounting for 38.5% of cardiovascular deaths. Their shared dietary drivers are embedded in everyday Indian recipes: saturated and trans fat, added sugar, refined carbohydrate, sodium, excess energy and deep-fried foods. Yet no tool tells a cook how much a given recipe contributes to this load. Existing nutrition apps are built on Western foods and ignore oil absorbed during frying. We propose a cardiometabolic "footprint" for recipes, analogous to the carbon footprint of recipes: recipe → ingredients × quantities × cooking process → liver- and heart-relevant nutrient load. The load is expressed as a share of ICMR-NIN 2024 and WHO daily limits and placed against the average Indian's existing intake (NSO, ICMR-INDIAB).

The project delivers:
1. an open dataset and validated model of oil uptake in Indian fried foods;
2. a recipe-to-load computation engine with Liver and Heart profiles, grounded in Indian food composition data (INDB/IFCT);
3. an authenticity-preserving substitution engine combining recipe statistics with food-pairing fit;
4. a cuisine-level footprint analysis of Indian food;
5. a web application that accepts any recipe link, with a grounded conversational assistant that explains results in natural language using only engine-computed numbers.

All estimates are presented as evidence-based ranges, not medical diagnoses.

**Deliverable 1:**
Indian Fried-Food Fat Dataset and Frying Oil-Uptake Model. An open, curated dataset of laboratory-measured fat and fatty-acid composition (SFA/MUFA/PUFA/TFA) of Indian fried foods, compiled from published analytical studies and food composition tables. It is paired with a food-category × preparation-setting (home / street / restaurant) range model that estimates oil absorbed during frying and the trans-fat shift under oil reuse, validated by leave-one-source-out testing.

**Deliverable 2:**
Recipe Cardiometabolic Load Engine (Liver and Heart profiles). A pipeline that converts a recipe into per-serving load:
- ingredient and quantity extraction;
- unit normalisation to grams, including Indian household measures;
- mapping to the Indian Nutrient Databank (IFCT-based);
- cooking and frying adjustments;
- transparent budgets for saturated fat, trans fat, added sugar, refined carbohydrate, energy and sodium, measured against ICMR-NIN 2024 / WHO limits and regional baselines (NSO 2025, ICMR-INDIAB 2025).
- data-driven handling of gaps: sodium for "salt to taste" lines is estimated from dish-specific salt quantities in recipes that state them, cross-checked with national salt-intake surveys; trans fat is drawn from FSSAI's national survey and measured street and fried-food data.
- estimates are produced per recipe and reported as ranges, with an explicit home vs restaurant/street setting.

The Liver profile and Heart profile use evidence-based weightings. The engine is validated against laboratory-analysed cooked South Asian dishes.

**Deliverable 3:**
Authenticity-Preserving Substitution Engine. An Indian ingredient-substitution network built from substitutions stated in Indian recipe sources, recipe-context similarity, and quantity distributions across real recipes of the same dish ("cook like the lightest quartile"). A FlavorDB food-pairing fit check is applied to each candidate. Outputs are ranked swaps with quantified liver and heart load reduction.

**Deliverable 4:**
Cardiometabolic Footprint Atlas of Indian Cuisine. A cuisine-level analysis covering:
- liver and heart load across Indian dish categories and regions;
- contribution analysis of the ingredients that drive it (cooking fats, dairy fats, sugar, refined flour, salt vs spices);
- dietetic textbook recipes compared with popular web recipes of the same dishes;
- the hidden load (including trans fat and sodium) of unlabelled street snacks and sweets.

**Deliverable 5:**
Web Application with a Grounded Conversational Assistant. A web app where a user pastes a recipe link (or text) and receives:
- per-serving Liver and Heart budget bars;
- ingredient-level explanations with citations;
- home-vs-street preparation estimates and a day builder;
- ranked authentic lighter alternatives.

A tool-calling conversational assistant answers natural-language questions ("why is this bad?", "what if I halve the butter?"). Every number it states comes from the engine, not the language model. It is evaluated for numeric faithfulness and appropriate refusal of medical questions.

**Supporting files:** upload the proposal PDF generated from PROPOSAL.md.
