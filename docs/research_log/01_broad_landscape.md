# 01 Broad landscape: raw findings (sweep 1)

## Q1: computational gastronomy review / open problems
Source: computationalgastronomy.org (directory of resources), Nature npj Syst Biol Appl 2024 review
"Computational gastronomy: capturing culinary creativity by making food computable" (Bagler, PMC11231233).
- Bagler's own framing: recipes / flavor / nutrition / health / carbon footprint as complex systems.
- The lab's headline agenda: "Can a machine think like a chef?" -> "Turing Test for Chef" (AI-generated recipes vs chef judgement).
  Envisioned: robotic kitchens using a "recipe data structure", flavor printer, digital diet coach, net-zero recipes with traceable supply chains.
- Related resources: RecipeDB, FlavorDB, DietRx, foodigIT (EU ERA Chair, Thessaloniki), FoodOn ontology, Foodoscope (commercial APIs).
- Other papers listed: "A generative grammar of cooking" (arXiv 2211.09059); "Deep learning NER models for recipes" (arXiv 2402.17447);
  traceability with IoT + blockchain + DataSpace.
- Events: Symposium on Computational Gastronomy "Celebrating a Decade of Computational Gastronomy", IIIT-Delhi, 13 Dec 2025 (gastrosym2025);
  earlier editions gastrosym2023, gastrosym2024. Other venues: CoGamy workshop at IEEE ICDM 2025, Multi-modal Food Computing workshop at ACM MM 2025,
  Scientific and Computational Gastronomy workshop, Parma, Sept 2025.
- NOT YET VERIFIED: what kinds of student projects were featured at past symposia (pages unfetchable).

## Q2: food computing surveys (application categories + unsolved challenges)
- Min et al., "A Survey on Food Computing", ACM Computing Surveys 52(5), 2019: framework = perception, recognition, retrieval, recommendation, prediction/monitoring;
  application fields = health, agriculture, culture, food science.
- Limitations listed there: lack of large diverse food image datasets; ontology/naming variation by region; poor volume estimation from single images;
  multimodal fusion difficulty; fine-grained classification does not transfer to food (no fixed semantic parts).
  Future: food multimodal knowledge graphs, personal-health food computing, food-log based recommendation, smart restaurants/retail/homes.
- Frontiers in Nutrition 2026 scoping review (46 studies, 2015-2025) of digital tech in food supply chains:
  blockchain 41%, IoT 26%, AI/ML 20%. 89% report food-safety gains, 83% report loss-reduction gains,
  BUT only 6.5% measured any nutrition outcome -> "critical evidence gap": link between supply-chain tech and nutritional security is unverified.
  Digital divide: small farms in LMICs have worst connectivity. ~1/3 of food lost/wasted; >800M hungry.
  Notable: Defraeye et al. physics-based digital twin for mango cold chain (predicts nutrient/quality change) = hybrid mechanistic + data approach.

## Q3: restaurant food waste / menu engineering / AI
- Space is CROWDED commercially: Winnow (IKEA -53%), Leanpath (4,000+ sites, -50%), Kitro (-23-51%), Supy, Restaurant365, Applova etc.
  US restaurants lose ~$162B/yr to food waste; avoidable waste 45-73% of total (Frontiers in AI 2025).
- Student/GitHub versions are everywhere and generic: Flask + XGBoost/RandomForest waste or demand predictor + dashboard + (local LLM menu text via Ollama).
  Example: rubina1905/AI-Smart-Cafeteria, Aishu-0605/Food-Waste-Prediction-System (mostly synthetic data).
- ASSESSMENT: "restaurant demand/waste prediction" = saturated + low novelty. Only viable if there is a genuinely new angle
  (e.g., an unaddressed setting like Indian small eateries / mess halls / thali-based kitchens, or a new modelling idea).

## Q4: personalized nutrition / glycemic response (health)
Note: first attempt returned 457K chars (too large, discarded); reran with compact `search`.
- ML for individual postprandial glycemic response (PPGR) in India is only at PROTOCOL/EARLY stage: medRxiv 2024 "Use of ML to predict individual PPGR among T2D in India"
  (results "will generate data to facilitate" models). IEEE 2026 paper on deep learning for Indian diabetes diet plans (100,000-record dataset, protein-focused plans).
- ASSESSMENT: real gap for Indian diets (Western PPGR work: Segal/Zeevi 2015 line). Needs CGM/clinical data => hard to get without a clinical partner.
  Possible angle: predict from recipe composition alone (no CGM) or use public CGM datasets. UNVERIFIED which datasets exist.

## Q5: LLM recipe generation / evaluation
- Springer (Apr 2026) "Improving LLMs for Recipe Generation via Reinforcement..." identifies DEFICIENCIES in LLM recipes, focus on INGREDIENT PROPORTIONS
  (thematic analysis of YouTube cooking comments + experiments on ingredient-scaling tasks). => LLMs are bad at quantities. Real, documented weakness.
- AtaJS/llm-recipe-finetuning: TinyLlama-1.1B + HUMMUS (500K+ recipes) + RAG + hallucination detection (student-level).
- Bagler lab "Turing Test for Chef": humans vs AI-generated recipes. => AI recipe generation is the lab's own flagship topic; a project here is directly on-theme
  but also the most likely area for other student teams to pick.

## Q6: odor / flavor prediction
- Lee et al., Science 2023, "A principal odor map unifies diverse tasks in olfactory perception" (GNN, Osmo/Google): as reliable as a human panel on 400 novel odorants.
- Follow-ons: olfactory label prediction on aroma-chemical PAIRS (arXiv 2312.16124), interpretable multitask DL linking odorants to olfactory receptors (PMC12547293, 2025).
- GAP (my inference, to verify): mixtures and cooking-transformed flavor; POM is single-molecule. Food is mixtures. Bagler's course slides flag taste/odor prediction + de novo molecules as core.

## Q7: sustainability / carbon footprint
- Scientific Data 2023: carbon footprint + embodied nutrition of 388 recipes (ingredients + cooking methods).
- Bagler lab: "Cultural context shapes the carbon footprints of recipes" (2024) + SustainableFoodDB web server (lab already covers recipe carbon footprints!).
- HeaSE (RecSys 2024): healthy + sustainable meal recommendation with food retrieval + LLMs; extended HUMMUS with sustainability scores.
- Commercial: Nutritics Foodprint, Touchpoint Gourmet (TGC India) carbon analysis of recipes.
- ASSESSMENT: recipe carbon-footprint estimation itself is done by the host lab => avoid duplicating; only new angle would be beyond estimation (e.g., substitution under cultural constraints).

## Q8: allergens / food safety at menus
- Many student GitHub repos (image or label allergen detectors, random-forest multilabel). Startups: Foodini (Forbes Mar 2026: new US restaurant allergy regulations), iaMenu, BiteKit.
- Key point from AllerGuard-AI README: single ML prediction is not enough for a SAFETY-critical workflow; false negatives are dangerous => hybrid/explainable.
- ASSESSMENT: saturated at the "detect from photo/label" level. Hidden allergens in Indian dishes (compound masalas, ghee, asafoetida w/ wheat flour, cross-contact) may be under-served: UNVERIFIED.

## Q9: food-drug interactions (bioscience-heavy)
- KG-DFI (PMC13481788, food-drug interaction via knowledge graph embedding), FDMine (Sci Rep 2022, homogeneous graph), FARFOOD (PMC12645732, structural similarity of food compounds to drugs),
  FooDrugs DB (Database 2023), NP-drug interaction KG (PMC10150409). Lack of labelled NPDI data; models trained on drug-drug data as proxy.
- ASSESSMENT: active research but data-poor/label-poor => room for novel method (self-supervised / few-shot), directly uses CS + bioscience. Also clinically real (warfarin-vit K, grapefruit-CYP3A4, etc.).
  Caveat: needs careful validation; risk of overclaiming.

## Q10: plant-based analogs / formulation
- NotCo "Giuseppe" (Chile, MIT TR Climate Tech 2023): ML matches taste/texture/smell of animal products using plant ingredients from molecular composition. Commercial, proprietary, closed.
- ASSESSMENT: real + valuable + closed => open academic alternative is possible; needs flavor/texture data; validation without a sensory panel is the hard part.

## Q11: Indian food image/nutrition
- ICVGIP 2025 "What is there in an Indian Thali?": multi-view Indian Thali dataset (796 plates, 50 dishes, 7,900 images, 7-10 views/plate). Existing CV is Western-food-centric; thalis have 5-10 overlapping items.
- Indian calorie estimates vary due to portion, cooking yield, hidden fat, mixed meals (component-level modelling helps). Portion estimation survey (arXiv 2602.05078).
- ASSESSMENT: dataset just appeared => field opening; but vision-heavy, needs data collection; "hidden fat/oil in home cooking" is the hard nutrition part.

## Q12: ingredient substitution / Indian KG
- Substitution KG + embeddings (Frontiers AI 2020, RPI); survey arXiv 2501.01958: 5 application types (vegan, allergy-safe, healthier, unavailable ingredient, LOCAL-cuisine substitution);
  MDPI Foods 2025: substitution must satisfy sensory, functional, nutritional, cultural/regulatory constraints simultaneously.
- FKG.in: knowledge graph for Indian food (FOIS 2024). => Indian KG exists (potential base).
- ASSESSMENT: substitution is well studied, but MULTI-CONSTRAINT + functional-role-aware (e.g., egg as binder vs flavor, Ahn paper mentions this) is open.

## Q13: nutrition access / affordability in India
- Literature exists: affordability of nutritious diets in rural India (2021), state-wise sustainable diets via non-linear optimization (2021), min-cost diet tools for Indian children/adults (2025),
  LP diet models for IIT Bombay students (2022), Cost of Diet software.
- ASSESSMENT: classical optimization solved at population level; gap = translating optimal nutrient baskets into ACCEPTABLE, cookable recipes/meals (culinary feasibility), i.e. bridging nutrition LP and recipe grammar. Needs check.

## Q14: cooking transformation of flavor
- Maillard reaction modelling exists at chemistry/CFD level (MDPI Foods 2022 volatile simulation; CFD baking browning model 2026; Iterated Reaction Graphs 2001).
- Nobody linked to recipe-scale food-pairing analysis in what I found (UNVERIFIED). The course notes explicitly list "flavor transformation on boiling/frying/roasting" as an open idea and as an admitted limitation.

## Q15: gut microbiome / fermented foods
- ML on diet-microbiome-metabolite prediction (Nat Commun 2025 metabolite response to dietary intervention via DL; Nat Microbiol 2025 microbiome transformation of phytonutrients; FGMDI database).
- AI for microbial resources in fermented foods (2025 review).
- ASSESSMENT: very bioscience-heavy, data mostly Western/clinical; Indian fermented foods (idli/dosa batter, kanji, dahi, pickles) are under-studied computationally (UNVERIFIED).

## Q16: procedural recipe representation
- Recipe flow graphs (Kyoto Univ FG corpus, dependency parsing) ; ReGraph (arXiv 2608.06917, Aug 2026): generate recipe graphs from food images (LMM). Bagler's "generative grammar of cooking" (arXiv 2211.09059).
- Course slides list "a recipe data structure that captures all quantifiable nuances of cooking" as an OPEN IDEA.

## Q1b (added after fetching the full Nature review, npj Syst Biol Appl 10:72, 2024, Bagler & Goel, via fetch force_browser=true)
Host lab's own published/ongoing work (so the project should NOT duplicate these):
- Databases: RecipeDB (118,000+ recipes, 74 countries, NER-annotated with quantity/unit/process/utensils), FlavorDB (936 ingredients), FlavorDB2, SpiceRx (spice-disease),
  DietRx (2,200+ ingredients, 24 categories, text-mined ingredient-disease-chemical-gene links), SustainableFoodDB / FoodPrint (recipe carbon footprints).
- Models: Ratatouille (GPT-2 fine-tuned on NER-structured recipes), BitterSweet (bitter/sweet prediction), sweetness prediction models, nutritional profile estimation of recipes,
  cuisine classification from sequentially structured recipes, hierarchical clustering of cuisines, culinary evolution models, dish detection in Indian food platters (YOLOv4, CVIP 2023), NER for recipes (LREC-COLING 2024).
- Turing Test for Chef: 24 chefs, 1,472 recipes, F1 = 69.88% (AI recipes "barely" pass). They state next step: sensory-panel palatability evaluation of cooked AI recipes; RL and better architectures.
- Stated open challenges: structured data with cultural/taste/nutrition/health/sustainability correlates; ingredient naming diversity across geographies; curated quality data.
- They state: health data exists per ingredient but "must logically be assessed for the complete dish".
- Related outside work cited: food-bridging network (Simas 2017), Menichetti & Barabasi (nutrient concentrations universal; ML prediction of degree of food processing, Nat Commun 2023),
  Learning to Substitute Ingredients (Fatemi 2023), FIRE image-to-recipe (WACV 2024), Cook-Gen, Multimodal AI Chef, Chinese dish flavor/region prediction based on pairing (2024), Turkish/Arab/Eastern-Med pairing tests.


## CORRECTION to Q4 (after PDF now readable; 2026-09-29)
The earlier note "India PPGR ML is only at protocol/early stage" was WRONG. The full result exists:
- medRxiv 2024.10.20.24315560 (Choudhry et al., Decipher Health / Harvard; CTRI/2022/02/040619): 488 evaluable T2D patients, 14 Indian clinics, Abbott Libre CGM, 22,967 meals, 543,442 CGM readings, 14 days each.
- XGBoost PPGR predictor: r=0.69, AUC 0.80 vs calorie-only r=0.57/AUC 0.58 and carb-only r=0.39/AUC 0.60. Inputs = meal nutrition + self-reported habits + biometrics + common labs (HbA1c), NOT CGM-derived features.
- Huge person-to-person spread: aloo paratha with curd PPGR 10-170 mg/dl*h; masala dosa 10-150.
- Limits stated: study stopped early (512 of 1000 target; funding); English-literate smartphone users only; sub-optimally controlled T2D (HbA1c>=7); no microbiome; preprint not peer reviewed.
- DATA IS PROPRIETARY (Decipher Health). No public release seen. => B is NOT an open-data gap; it is a crowded-by-a-funded-team gap. Category B priority lowered.
- Take-away: a student project can't collect CGM data; only reuses public CGM sets (unverified which exist).

## Q17: GastroSym2025 (fetched OK after tool fix) : what the symposium actually is
- 13 Dec 2025, IIIT-Delhi, "Celebrating a Decade of Computational Gastronomy". Organiser: Prof. Ganesh Bagler (Dept of Computational Biology, Infosys Center for AI).
- Audience/speaker mix = CHEFS + INDUSTRY + academics: chief creative chef of an "AI Restaurant"; President of the Indian Federation of Culinary Associations; Corporate Executive Chef, ITC Maurya;
  food critic/author of "Masala Lab"; Principal, IHM Pusa; IIT Delhi professor; Dean, Le Cordon Bleu; CEO Future Food Foundation; founder Adikshay Food; Chef R&D; Univ. of Gastronomic Sciences (Italy);
  Foodoscope Technologies (spin-out; "Chef Co-Pilot").
- Themes on the page: Intro (what is CG, data sources RecipeDB/FlavorDB/SpiceRx/DietRx/SustainableFoodDB), Applications ("Can a computer think like a chef? How do I pair ingredients meaningfully?
  Can AI generate new recipes? Can we tweak my recipe for better health outcomes? How do we address nutrition deficiencies? Can I do cuisine fusion of recipes?"),
  Future ("Foodoscope: The Digital Building Blocks of Food. Ayurveda Informatics. Center for Sustainable Food.").
- Fork-It Hackathon (ACM + CoSyLab): API-based, prize pool Rs 80,000 -> lab APIs (Foodoscope) are open for participants.
- IMPLICATION: the room is chefs and industry. Projects that a chef or food business can SEE working and use will land better than a pure methods paper. Ayurveda informatics + sustainability are lab priorities.
  Non-Western "chef-facing" problems (Indian kitchens, Ayurvedic constraints) fit the room. NOT yet verified: whether student posters get featured, and which past student projects were shown (gastrosym2023/2024 pages still to fetch).
