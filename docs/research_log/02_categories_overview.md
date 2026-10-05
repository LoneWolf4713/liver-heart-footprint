# 02 Categories overview (from sweep 1; NOT yet deep-dived)

Status legend: crowding = how many existing products/papers; gap signal = my current read (many are UNVERIFIED until deep dive).

| # | Category | Real problem | Already done (from sweep) | Gap signal | Bio fit | Crowding |
|---|----------|--------------|---------------------------|------------|---------|----------|
| A | Restaurant / kitchen operations | food waste, over-ordering, menu mispricing (US ~$162B/yr waste) | Winnow, Leanpath, Kitro, Supy + many student repos | only in unserved settings (Indian mess/thali kitchens) or with a new modelling idea | low | VERY HIGH |
| B | Personalized nutrition & metabolic health | postprandial glucose, diabetes, diet plans | Western PPGR work; India PPGR study protocols (2024), DL diet plans (2026) | Indian-diet PPGR from recipe composition; data access hard | high | medium |
| C | Food-drug / food-disease interactions | dietary compounds altering drug action or disease risk | KG-DFI, FDMine, FARFOOD, FooDrugs, NPDI-KG | label-poor field => room for novel low-label methods; clinically real | very high | medium-low |
| D | Flavor & sensory science | predict taste/odor; food pairing; de novo flavor | Principal Odor Map (Science 2023), pair-odor models, FlavorDB, Ahn/Jain/Singh pairing papers | mixtures + cooking transformation + taste not just odor; pairing results flip by dataset (robustness) | high | medium |
| E | Generative AI for recipes / culinary creativity | LLMs write plausible but wrong/unsafe recipes | Bagler "Turing Test for Chef", LLM ingredient-scaling deficiency (2026), HUMMUS fine-tunes | quantities, feasibility, physical/chemical validity; evaluation | medium | HIGH (likely other teams) |
| F | Sustainability & climate | recipe/diet carbon+water footprint, sustainable swaps | 388-recipe dataset, SustainableFoodDB (host lab), HeaSE, Nutritics | estimation is done; culturally-constrained substitution/optimization is open | medium | medium-high |
| G | Nutrition access, affordability, food security (India) | min-cost nutritious diets, micronutrient deficiency, PDS/mid-day meals | many LP/NLP diet-cost papers (state-wise, rural, IIT Bombay) | bridging optimal nutrient baskets to ACCEPTABLE COOKABLE meals | medium | medium |
| H | Food safety & allergens | hidden allergens, cross-contact, safety-critical recommendation | many detectors (photo/label), Foodini, iaMenu | Indian compound masalas/cross-contact; safety-critical false negatives | medium | HIGH |
| I | Culture, heritage & low-resource cuisines | traditional/regional recipes lost, data skewed West | CulinaryDB/RecipeDB, FKG.in (Indian KG), Thali dataset (2025) | regional/vernacular data, oral knowledge, coverage | low | low-medium |
| J | Cooking process science & recipe representation | flavor changes in cooking; recipes lack structure | Maillard/CFD models, recipe flow graphs, generative grammar of cooking, ReGraph | linking process to flavor at recipe scale; recipe data structure (course open idea) | high | low |
| K | Microbiome & fermentation | gut response to diet; fermented-food microbial ecology | Nat Commun/Nat Microbiol 2025 DL, FGMDI, AI-in-fermentation review | Indian fermented foods computationally under-studied | very high | medium |
| L | Food vision / dietary assessment | nutrition from photos; thalis | Thali dataset (ICVGIP 2025), portion estimation survey | hidden fat, mixed dishes, portion; needs image data | low | medium |
| M | Food-tech formulation | plant-based analogs, reformulation | NotCo Giuseppe (closed) | open academic alternative | medium | low (academic) |

## Observations that will drive selection
1. The most obvious "AI for restaurants / recipes / allergens" problems are the CROWDED ones. Expect other teams there. Low differentiation.
2. Gaps cluster where food meets BIOLOGY (C, K, B, D-with-transformation) and where food meets INDIA-specific structure (G, I, L, H).
   The team's CS+bioscience profile is an actual advantage there.
3. The host lab already owns: RecipeDB, FlavorDB, CulinaryDB, DietRx, SustainableFoodDB, FKG-adjacent work, Turing Test for Chef.
   A project that builds ON their data is easy to get access to, but one that DUPLICATES their published results will not stand out at their own symposium.
4. Two course-noted open problems keep reappearing: (i) cooking transforms flavor (ignored by all pairing studies), (ii) pairing results are dataset-dependent (robustness).
5. Symposium past-project evidence is MISSING (site unfetchable). Next step: try other routes (press note PDF, news coverage, YouTube/LinkedIn posts, Bagler lab pages).

## Proposed order for deep dives (to be confirmed with user)
1. C  food-drug / food-disease (bio + KG + low-label learning)
2. D+J flavor science incl. cooking transformation and pairing robustness
3. B+G health + Indian nutrition access
4. E  generative AI for recipes (know the crowd)
5. K  microbiome/fermentation
6. remaining: A, F, H, I, L, M (quick checks only)
