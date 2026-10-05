# 18 Phase 2, pass 3: real PROBLEMS we can solve (restaurants, food businesses, CG-adjacent) (2026-09-29)
Target profile (from user feedback in 17): someone actually has the problem + a genuine SCIENTIFIC question inside it (research-only answer) + AI necessary + result valuable whether the answer is yes or no + NO fieldwork + mini scale + rare among classmates.

## Evidence gathered this pass (Stealth Search)
- [S] FSSAI Labelling & Display Regs, Reg 2.4.6 / sub-reg 9(1): food service establishments with Central licence or 10+ outlets must show kcal per serving + serving size on menus, and declare 8 allergens (gluten cereals, milk, egg, fish, crustaceans, tree nuts, soy, sulphites) per dish. In force since 2022; Maharashtra FDA enforcing across ~4.5 lakh establishments in 2026; Karnataka surprise inspections Aug 2026; risk-based inspections since 1 Apr 2026. (menumanager.in Aug 2026; FSSAI letter 12 Apr 2024)
- [V] Indian menu-labelling RCT (PubMed 42586213, 2026): effect of labels on choices in two chains; accuracy of labels NOT studied (abstract only).
- [S] US/UK/AUS literature: bomb-calorimetry audits find many restaurant items exceed stated kcal by >20% (Urban JAMA 2011; Roberts 2013; McCrory 2019). No Indian accuracy audit found.
- [V] Public disclosures exist: McDonald's India booklet (per serve: kcal, protein, total/sat/trans fat, total & ADDED sugar, sodium, allergens; "based on testing of ingredients and formulations"); KFC India FSSAI booklet; DesiMacros GitHub = 258 items / 12 chains (McD, BK, Subway, Pizza Hut, KFC, Taco Bell, Domino's, Starbucks, Wow! Momo, Faasos, California Burrito, Haldiram's). CAUTION: Wow! Momo values are "calculated from standard recipe using USDA + IFCT" (not lab) -> disclosures are a MIX of measured and calculated.
- [V] Foodoscope (lab spin-out) markets "Auto-generate nutrition facts, allergens" for restaurants -> OVERLAP RISK for any plain menu-nutrition generator.
- [B] Oil absorption for Indian fried items (restaurant costing blog): pakora 15-20% of weight, vada 12-18%, samosa 10-15%, puri/bhatura 8-12%. Directional only.
- [S] Recipe scaling: industry says salt/spices/chile/leavening don't scale linearly; vendors (Culinaire AI) sell "AI scaling"; KitchenScale (ESWA 2023) predicts quantities from context but not scaling laws; Springer 2026: LLMs fail at ingredient scaling. Indian volume-cooking recipes live in hotel-management textbooks (Bali, OUP 2011; Rana 2022), not open.
- [S] CRISIL Jun 2026: tomato +31% YoY (Rs 42/kg) -> recurring tomato/onion price shocks.
- Delivery-robustness prior art: search blocked (0 sources) -> UNKNOWN.

## Ideas
### R1 "Menu Truth": can a restaurant's calorie/allergen label be physically true? (science core = inverse problem)
Problem owners: ~4.5 lakh Maharashtra establishments + chains nationally that must display kcal & allergens; regulators who cannot lab-test thousands of menus; consumers (allergy, diabetes).
Scientific question: Given a dish's disclosed nutrition, does there EXIST a realistic recipe (drawn from the learned distribution of how that dish is cooked across RecipeDB/INDB, with cooking transformations like oil uptake and water loss) that produces it? Equivalently: infer the hidden recipe (oil, ghee, sugar, cream) from the label; flag labels that are physically implausible (e.g., a deep-fried item whose declared fat implies near-zero oil uptake).
Where AI is necessary: learned probabilistic model of dish -> recipe variants -> cooked nutrition (with cooking-transformation terms), and Bayesian inversion from label to recipe. Allergen side: P(dish contains cashew / wheat via hing / milk via ghee) from recipe distributions, checked against declared allergens.
Outcomes, all informative: labels plausible (a validated cheap screening method) OR systematic implausibility (e.g., fried/gravy items under-declared) = a finding regulators and consumers care about.
Deliverables: D1 open dataset of disclosed Indian menu nutrition + allergens (chains, tagged measured vs calculated); D2 dish->recipe->cooked-nutrition probabilistic model (oil uptake, yield); D3 label plausibility audit (which items/chains fall outside plausible ranges, and by how much); D4 hidden-allergen predictor for Indian dishes (validated on declared allergens); D5 tool: enter a dish (+optional recipe) -> plausible kcal/fat/sodium ranges + likely allergens + red-hexagon status for unpackaged foods (folds in N1 and the samosa problem).
Data: disclosures (McD/KFC/BK/Domino's/Haldiram's etc.; DesiMacros 258 items as a start), RecipeDB/INDB, IFCT/USDA; no fieldwork.
Risks: overlap with Foodoscope "auto nutrition facts" -> differentiate as AUDIT + uncertainty + inverse inference (and offer it as validation for such tools); many disclosures are calculated (circular) -> tag and analyse separately (that split is itself a finding); Indian-dish coverage in chains may be only ~100-300 items [U]; must never accuse a specific brand of wrongdoing (report plausibility, not fraud).
Rarity: nobody in course/hackathon record; needs recipe modelling + inference + regulation. Professor fit: extends lab's nutrition estimation (validated only on calories vs AllRecipes), "health for the complete dish", NER, RecipeDB.

### R2 Iron-smart kitchens v2 (Pkg 1 reframed so value does not hinge on yes/no)
Problem owner: dietitians / programme menu designers facing 57% anaemia in women (NFHS-5).
Change: lead with the ENGINE (absorbable iron/zinc per dish from recipe + phytate + enhancers) and the minimal-tweak recommender; the "does cuisine encode absorption wisdom?" test becomes one chapter. Null result no longer wastes the project.
Weakness remains: nobody is explicitly asking for an "absorbable iron per dish" tool; validation of absorbability numbers is literature-only.

### R3 Tomato-shock substitution: what can replace tomato in Indian gravies when prices spike?
Problem owners: restaurants, cloud kitchens, households every price spike (tomato +31% YoY Jun 2026; Rs 200/kg in 2023).
Scientific question: what FUNCTIONAL roles does tomato play in Indian gravies (acidity, umami/glutamate, colour, body/pectin, aroma), and which combinations of cheaper ingredients reproduce that role profile? Test: Indian regional recipes that make the same dish type WITHOUT tomato (tamarind, kokum, curd, amchur, onion-heavy bases) = "cuisine already found substitutes"; learn role vectors from FlavorDB + nutrient composition + co-occurrence.
Deliverables: role-profile model of ingredients; substitution recommender; back-test on held-out tomato-free regional recipes; price-aware tool using DoCA daily prices.
Risks: no tasting validation (literature + recipe back-test only); substitution research exists generally (novelty is function+price+Indian).

### R4 Scaling laws of recipes (catering / cloud kitchens / fixing LLM scaling)
Scientific question: do experienced cooks scale spices, salt, oil sub-linearly with batch size? Fit per-category exponents; test on independently written small vs large versions of the same dish.
Deliverables: scaling-law dataset + exponents by ingredient class; scaler tool; LLM benchmark showing where linear/LLM scaling fails.
Risks: DATA: Indian volume recipes mostly in paid textbooks; web "for 100 people" recipes may be linearly multiplied by authors (circular); confounds between authors. Highest data risk.

### R5 Which dishes survive delivery? (cloud-kitchen menu design)
Question: does recipe structure (fried/crisp, gravy, bread, rice) predict delivery complaints ("soggy", "cold", "spilled") mined from reviews?
Data: public Zomato Bangalore Kaggle dataset (reviews; known, not re-fetched) [U]; reviews are restaurant-level, not dish-level -> attribution problem. Prior art unknown (search blocked).
Risks: noisy attribution; weak science unless linked to food physics.

## Assessment against target profile
| Idea | Someone has the problem | Science inside | AI necessary | Valuable either way | No fieldwork | Data risk | Rarity |
|---|---|---|---|---|---|---|---|
| R1 Menu Truth | YES (regulation enforced 2026) | YES (inverse recipe inference, cooking transformation) | YES | YES | YES | Medium | High |
| R2 Iron-smart v2 | Weak | YES | Partly | YES (after reframe) | YES | Medium | High |
| R3 Tomato-shock | YES (recurring) | Medium | YES | Mostly | YES | Low-Med | Med-High |
| R4 Scaling laws | YES | YES | Partly | YES | YES | HIGH | High |
| R5 Delivery | YES | Weak-Med | YES (NLP) | Mostly | YES | High | Med |
Lean: R1 strongest on every axis; R3 second; R2 kept as the science-first option.
