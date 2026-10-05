# 23 MASTER SUMMARY v2 (written 2026-09-29, second session)
Read this first. It supersedes 14 for anything after Phase 1. Details live in the numbered files.

## 1. Who / what / constraints
- Student: 3rd-year IIIT-Delhi, CS + biosciences, team of 2, course BIO544 Computational Gastronomy (Prof. Ganesh Bagler, CoSyLab), Monsoon 2026. Mini-project = 20% of grade; goal also = feature at the Symposium on Computational Gastronomy (professor's discretion; Fork-IT hackathon top projects are publicly stated to be showcased).
- Hard rules from the user (accumulated):
  1. Web research ONLY via the Stealth Search MCP (mcp__stealth-search__*), never built-in search.
  2. Log everything in research_log/.
  3. Real, CURRENT problem that Indians actually face (India-centric); evidence bar ~100 complaints or stronger official data.
  4. Not exotic, mini-project scale, NO fieldwork, NO lab work.
  5. Rare among classmates (they build chatbots/recommenders/meal planners/allergen apps on the lab's APIs).
  6. DATA GATE: no idea is scored until its ground-truth/validation data is verified, accessible and sized.
  7. No Instagram/Zomato scraping or hand-copying of platform data (legal/ethical/no scientific standing).
  8. Must be clearly COMPUTATIONAL GASTRONOMY (recipes/flavour/nutrition/health/cuisine data), not a pure biology project.
  9. Judge = the professor; build on his course concepts and data, do not duplicate his lab.
  10. Be honest; mark verified [V] vs unverified [U]; do not overclaim; report back after each step.

## 2. Chronology of this session (files 15-22)
- 15: Phase 1b checks. Data access: CulinaryDB downloadable (45,772 recipes, 4 CSVs), FlavorDB live (public scrapes exist), INDB open on GitHub (1,014 Indian recipes w/ grams + NIN_fct), Jain 2015 PLoS open. What students build: past BIO544 mini-project = AI recipe chatbot; Fork-IT 2025 = 40 team repos, apps on APIs. Prior art for course-anchored ideas.
- 16: Phase 2 v3 packages (Iron-smart kitchens, Pairing Audit, Real menu audit, Nutrition copy-mutate). User: liked Iron-smart (scientific) but "nobody is asking"; null-result fear; menu audit rejected (fieldwork).
- 17: Demand-pull round: N1 Red Hexagon (FSSAI front-of-pack warning labels; SC case), N2 Healthy Thali Index, N3 protein-washing. User: N1 = rule-based classifier (not scientific), N3 merged into N1, N2 = passive question.
- 18: Pass 3 "problems to solve": R1 Menu Truth (restaurant label plausibility; FSSAI Reg 2.4.6 calorie+allergen menus; Zomato Healthy Mode AI values), R2 Iron-smart v2, R3 tomato-shock, R4 recipe scaling laws, R5 delivery complaints.
- 19: Phase 3 red team of shortlist (S1 Red Hexagon, S2 Iron-smart v2, S3 Menu Truth). Lab's RecipeDB2 (arXiv 2609.22099, Aug 2026: 128,942 recipes, 34 Indian states, USDA-linked 148 nutrients) = enabler. USER REJECTED the red team as poor: Zomato data has no standing; S3 lacked COOKED-DISH ground truth. Redo verified: IFCT 2017 = raw only, no composite dishes; lab-analysed South Asian cooked dishes exist only abroad in small numbers (Chen, Gilbert & Khokhar 2009, n=10; safefood Ireland 2015; UK CoFID; MyFCD). S3 KILLED; S2 = grade-safe fallback only.
- 20: Data-gated round: I1 Kitchen Doctor (Food.com 700k reviews: why recipes fail, which fixes work), I2 Hazard fingerprint (NYC 295k inspection violations vs cuisine processes), I3 Complaint physics (Yelp), I4 tomato-shock. Allergen-from-dish-name dropped (done 2025-26). User: I1-I3 good but NOT India-specific (kept as FALLBACK POOL); I4 rejected (unverifiable).
- 21: India problems with evidence: fatty liver (MASLD) epidemic; adulteration (40,023 of 223,808 samples non-conforming FY26; 2026 paneer/ghee/spice raids; analogue-paneer ban draft); pesticides (data paucity). User's own idea evaluated: reel recipes + masala + fatty liver. Findings: spices NOT implicated (curcumin improves markers); reel->recipe->nutrition apps exist (Nutrola, Honeydew, Peel, ReciMe, Flavorish, RecipeBro); liver apps exist (Liverly, Liver Nutrition App) but Western. Instagram: ToS bars automated collection (Meta v. Bright Data 2024 is US-only, logged-off); decision = no Instagram.
- 22: FINAL CONCEPT "Liver footprint of Indian food" (see section 3). Website dry-run, loopholes L1-L11, test plan T1-T6.

## 3. THE SELECTED PROJECT (as of end of session 2)
Working title: Liver footprint of Indian recipes (Indian-context liver-aware recipe analyser + cuisine-level study).
Framing: the lab computed the CARBON footprint of recipes; we compute the LIVER footprint (recipe -> ingredients x quantities x cooking processes -> liver-relevant nutrient load -> placed in an average Indian day).
Input (prototype): a recipe WEBSITE link (schema.org Recipe JSON-LD, LLM fallback). YouTube to be added (user expects videos state oil quantities better than blogs; to be TESTED, not assumed). No Instagram.
Pipeline: parse (recipe NER / small LLM, JSON) -> units to grams (INDB units; katori/cup/tbsp) -> ingredient to nutrients (INDB/IFCT first, RecipeDB2/USDA fallback) -> cooking adjustments (deep-fry oil uptake ranges; tadka/bhuna oil counted; oil-reuse toggle) -> Liver Budget vs daily limits and vs the average Indian's existing day -> transparent Liver Load Index (weights ordered SFA > added sugar > refined carbs/energy surplus > unsaturated fat; protective fibre/pulses/veg) -> flavour-preserving, culturally real swaps (same role + FlavorDB shared molecules + RecipeDB2 co-occurrence + lower load).
Research questions: RQ1 liver footprint of Indian cuisine by region/dish + contribution analysis ("is it the masala?"); RQ2 traditional vs modern drift of the same dishes; RQ3 hidden load of unlabelled foods (mithai, street food, bakery); RQ4 load-vs-authenticity trade-off of swaps.
Key grounding numbers [V]: NSO Nutritional Intake in India (Jul 2025): ~2,212 (rural) / 2,240 (urban) kcal/day, fat ~60/70 g, protein ~62/63 g. ICMR-INDIAB-21 (Nat Med 2025, n=18,090): 62% energy from carbs; SFA 8.9%E nationally (North 11.2%E, NE 7.4%E) vs <7%E recommended; added sugar >5%E in 21 states; unlabelled mithai/street food not captured. ICMR-NIN DGI 2024: added sugar 25-30 g/day, salt <5 g, fat <=30%E, HFSS = >15%E from added oil/fat. Luukkonen 2018 (Diabetes Care): overfeeding SFA raises liver fat most, sugar via DNL, unsaturated least. Phenome India (Lancet SEA 2026): MASLD age-adjusted 38.9%. Frying: Chen 2009 puri up to 18.4 g fat/100 g; Jain & Passi 2024 fried foods 22.5% -> 27.4% fat (dry) with reuse, SFA ~5% -> ~15%, TFA up 0.05 -> 0.89%.
Data asks to the lab: RecipeDB2 bulk, FlavorDB bulk, recipe NER model, ingredient-nutrient mapping.

## 4. Open items / next step
- Execute the test plan (handoff file 24_HANDOFF_INSTRUCTIONS.md): T1 website extraction coverage, T2 parsing/mapping accuracy, T3 fried-food fat validation, T4 FlavorDB coverage + swap back-test, T5 score sanity, T6 Wayback longitudinal feasibility, T7 YouTube quantity coverage.
- Fallback pool if the concept fails: I1 Kitchen Doctor, I2 Hazard fingerprint, I3 Complaint physics (file 20); S2 Iron-smart v2 (grade-safe).

## 5. Lessons (mistakes not to repeat)
- Never score an idea before verifying its ground-truth data (the S3 failure).
- Do not propose platform data collection with unclear legality or scientific standing.
- Avoid rule-application projects dressed up as AI (S1 critique).
- Tie every idea to a specific, current India problem with evidence.
- Keep scores/ratings honest; do not present guesses as findings.
