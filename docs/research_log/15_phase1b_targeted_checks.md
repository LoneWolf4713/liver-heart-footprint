# 15 Phase 1b: targeted checks before Phase 2 (new session, 2026-09-29)
Context: previous session crashed. New session re-read all logs + course files. Files 12 and 13 (Phase 2 attempts) are treated as SUPERSEDED input: ideas may be reused, but Phase 2 restarts from the Phase 1 evidence.
User's Phase 2 criteria (confirmed by user): few classmates would pick it, but not exotic/research-heavy; mini-project scale (data we can get, 2-person workload, no clinical/sensory/wet lab); relevant NOW (not 1-2 yrs out); >=3-4 concrete deliverables, combining related smaller projects is fine; guaranteed 20% grade first, symposium is designed-for upside; judge = the professor (build on his course/data, don't duplicate his lab).
Tool rule: Stealth Search MCP only.

Three checks: (1) data access; (2) what other students / hackathon teams already do; (3) prior art for course-anchored ideas.

## Check 1: data access (VERIFIED by fetch, 2026-09-29)
| Resource | Status | Notes |
|---|---|---|
| FlavorDB (cosylab.iiitd.edu.in/flavordb, /flavordb2) | LIVE | 25,595 molecules; 936 ingredients. No bulk download on page; public scrapes exist on GitHub (e.g., tarek-kerbedj/flavor_db2.0: flavordb.csv + molecules.csv via entity JSON endpoints). Ask professor for a clean dump anyway. |
| CulinaryDB (cosylab.iiitd.edu.in/culinarydb) | LIVE, DOWNLOADABLE | zip of 4 CSVs: 01_Recipe_Details (ID, title, source, region), 02_Ingredients (aliased names, synonyms, entity ID, category), 03_Compound_Ingredients (components), 04_Recipe-Ingredients_Aliases (original name -> aliased entity). 45,772 recipes, 22 regions. Entity IDs link to FlavorDB. No quantities. |
| INDB (Anuvaad portal + GitHub lindsayjaacks/Indian-Nutrient-Databank-INDB-, vikx01/Indian-Nutrient-Databank-INDB) | OPEN | 1,014 recipes with ingredient amounts + units + food codes; NIN_fct (897 raw foods, IFCT 2004+2017), UK_fct (144), US_fct (54), USDA retention factors, serving sizes, unit conversions, 40 nutrients incl. Fe, Zn, Ca, vit C, K1. Recipes: 490 Art & Science of Cooking, 378 Basic Food Preparation, 148 web. (lindsayjaacks README says IFCT files must be requested; vikx01 lists NIN_fct.xlsx as included; portal has "Download Data".) |
| Jain et al. 2015 PLoS ONE (regional Indian cuisines) | OPEN ACCESS | PLoS article + printable PDF reachable; supporting-info datasets normally attached (S1-S3 file-level check pending). |
| RecipeDB | LIVE (web), API via Foodoscope | 118k recipes, 268 processes, 23,500 ingredients; linked to FlavorDB, USDA nutrition, DietRx. Bulk access = ask professor. |
VERDICT check 1: data is NOT the bottleneck for flavor/recipe/nutrition-level projects. CulinaryDB + FlavorDB scrape + INDB are enough to start without waiting on anyone.

## Check 2: what other students / hackathon teams build (2026-09-29)
Evidence:
- Past BIO544 mini-project (2024, Sambhav-Gautam/CGAS-2024): "AI-Powered Recipe Chatbot" (React + MongoDB + NLP recipe search/recommendation over scraped Assignment-1 data).
- Other CGAS course repos on GitHub (GitHub API: 25 repos match "computational gastronomy"): recipe-review SENTIMENT analysis (hn-iiitd, 2024-25); COPY-MUTATE recipe generation (bhaktibatra19115, 2020); rohit18259/CGAS_Project (content not read); scraping + plots (assignment-style); aromatherapy Flask app; ingredient co-occurrence network for one dish (adobo).
- Fork-IT hackathon (Foodoscope + CoSyLab, 24h, RecipeDB+FlavorDB APIs). 2025 edition (12-13 Dec 2025) LinkedIn post: "Top projects showcased at the Symposium on Computational Gastronomy" -> this is the CONFIRMED student-showcase route (a public statement; mini-project route is still only the professor's word).
  Fork-IT-2026 GitHub org: 40 team repos. Visible themes: meal planners w/ constraint optimisation + clinical/fitness modes (FoodoScope "Palate Planner"), allergen tool (allergen-alchemist), Ayurveda (TeamShequence_Ayura), women's nutrition (fem-nourish), flavor substitution (flavorshift), vision (VisionAI), plus generic names. 2024 2nd place: "AI-driven project ... making food computable" (details not public).
  Organisers' own suggestion list: "personalized recipe recommenders, diet-aware systems, ingredient substitution engines, AI-driven flavor-pairing applications".
- Lab theses (IIIT-D repository): Mansi Goel PhD (Aug 2025: structured datasets, NER, novel recipe generation, carbon footprint, object detection); Ishita Sindhwani BTech 2023 (Ratatouille, constraint optimisation recipe generation).
INTERPRETATION: the "obvious pool" is APPS on the APIs: recommenders, chatbots, meal planners, allergen/diet filters, substitution engines, Ayurveda apps, recipe generators. Every hackathon team and most course teams go there. Analysis/science projects that test a hypothesis with the course's null-model machinery are RARE in what is publicly visible (only copy-mutate 2020 and sentiment analysis).
Caveat: GitHub is a biased sample (many teams never publish).

## Check 3: prior art for course-anchored ideas (2026-09-29, snippet/abstract level; ScienceDirect/ResearchGate blocked as usual)
| Idea | Closest prior art found | Gap status |
|---|---|---|
| Pairing robustness / why Indian sign flips (old P1) | Dogan & Degerli 2023 (Int J Gastron Food Sci, Turkish 7 regional cuisines): FPI "heavily influenced by the frequency of ingredient usage", mixed +/- by region, and FPI NOT positively correlated with user ratings. FlavorGraph 2021, FlavorDiffusion 2025 = embedding/prediction, not robustness. | No systematic robustness audit of the Jain-2015 vs Singh-2018 contradiction found. Turkish paper supports the hypothesis that ingredient frequency drives the sign. OPEN. |
| Pairing score vs palatability (ratings) | Turkish 2023: no correlation. Rating-prediction student projects on food.com use steps/time/nutrition, not molecular pairing. | Not tested for Indian or large Western sets in what I found. OPEN, cheap (Assignment-1 scraping gives ratings). |
| Absorption / nutrient-complementarity pairing in recipes (old P2) | Only blogs and single-meal clinical studies (vit C 50 mg optimum; complete-diet studies show weaker effect). Caprioli et al. 2025 npj Sci Food: ingredient-TYPE co-occurrence networks as culinary fingerprints (not nutrients). Old SJSU MS thesis (2000): measured phytate/minerals in Indian vegetarian dishes (lab analysis, small). | No recipe-corpus null-model test of enhancer/inhibitor co-occurrence found. OPEN. NEW DATA: FAO/INFOODS/IZiNCG PhyFoodComp 1.0 = global ANALYTICAL phytate + Fe/Zn/Ca + molar ratios database (fixes "USDA lacks phytate"). |
| Recipes as flavor x nutrition Pareto vs null (old P5) | Nothing direct. arXiv 2607.09529 (generative food science) does multi-objective GENERATION of burgers, not testing traditional cuisines. | OPEN (weak evidence). |
| Copy-mutate with health fitness (old P6) | Kinouchi 2008 (fitness abstractly "nutritional value, aspect, flavor, cost"); lab's "Computational models for the evolution of world cuisines" (158,544 recipes, 25 regions; CM-R/CM-C/CM-M; future work: recipe sizes, processing, cross-cuisine exchange). Old CGAS student repo on copy-mutate (2020). | Explicit nutrition-fitness variant not found. Moderately open; students have touched copy-mutate before. |
| Cooking-transformed flavor at recipe scale | Per-food GC-MS studies exist (chicken stew vs air-fry; roasted meat volatiles); no recipe-level/pairing-level method. | OPEN but DATA-HEAVY (hand-curating cooked volatiles). Likely too hard for a mini-project. |

## Net conclusions for Phase 2
1. Data is available; no blocker for recipe/flavor/nutrition projects.
2. Classmates + hackathon teams cluster on APPS over the lab APIs. Hypothesis-testing science with the course's null models is rare in the visible record = our differentiation lane.
3. Genuinely open, cheap, course-native questions: pairing robustness (frequency effect), pairing vs palatability, absorption pairing (now with PhyFoodComp), nutrition-fitness copy-mutate.
4. Showcase route: Fork-IT's top projects are showcased at the symposium (public); mini-project feature route is the professor's word only.
