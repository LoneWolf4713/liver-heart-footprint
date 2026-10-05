# 33 Extension research: cardiovascular (heart) axis + AI chatbot (2026-09-30)
User idea: add a natural-language chatbot on top of the engine (explains why, with numbers; more agentic/modern), and add cardiovascular health since heart disease is a major Indian problem and shares dietary drivers.

## Heart: evidence [V unless marked]
- CVD ~28.1% of all deaths in India (Sci Rep 2023, NNMS salt paper, citing GBD).
- Dietary risks caused 38.48% of CVD deaths in India in 2021 (Zinzuvadia et al., JACC 85(12_Suppl):354, 2025; GBD secondary analysis, statewide). Fastest-rising dietary risks 1990-2021 (AAPC in deaths): sugar-sweetened beverages +9.73%, processed meat +5.44%, low omega-6 PUFA +5.1%, low whole grains +5.04%, HIGH SODIUM +5%, low fruit, red meat, low nuts/legumes/vegetables, low fibre, high trans fat +1.3%.
- Salt: National NCD Monitoring Survey (spot urine): mean 8.0 g/day (men 8.9, women 7.1) vs WHO/ICMR <5 g (Sci Rep 2023, PMC10517942); a systematic review found ~11 g/day.
- ICMR-INDIAB-21 (Nat Med 2025): high SFA, high refined carbs, low protein across states; authors could not capture trans fat (no Indian TFA database) -> our fried-food data (Gupta 2016 TFA % per item; Jain 2024 reuse) partly fills this.
- GBD 2023 CVD burden estimates available (IHME, non-commercial).
Overlap with the liver engine: SFA, added sugar, refined carbohydrate, energy, SALT are already computed. Heart axis adds: sodium as a primary axis, trans fat (fried/reused oil, bakery/vanaspati), fat QUALITY (PUFA/MUFA vs SFA), fibre/whole grains/legumes as protective. => cheap, credible extension using the same pipeline; different weighting/limits (WHO: SFA <10%E, TFA <1%E, sodium <2 g; ICMR 2024 salt <5 g).
Recommendation: frame as a "cardiometabolic footprint" with two profiles (Liver, Heart) sharing one engine; liver stays the lead story; do NOT add diabetes/glycaemic scoring now (scope).

## Chatbot: evidence and design
- [V, from file 05/earlier] Multimodal LLMs estimating meal nutrition (GPT-4o, Claude, Gemini; PMC12513282) are imprecise, weak on mixed dishes and portions -> an LLM must NOT produce the numbers.
- Nutrition/diet chatbots are common in apps (not novel by itself); value is as an interface.
- Design (grounded / tool-calling agent): the chatbot answers in natural language but every number comes from engine tools (parse_recipe, compute_budget, frying_range, suggest_swaps, what_if(change), day_total); explanations cite the stored sources; refuses diagnosis/medication advice; can run on a small local model for privacy.
- Valuable uses: "why is this bad?", "what if I use half the butter?", "can I eat this after the samosa I had?", "make this lighter but keep it Punjabi".
- Evaluation: answer faithfulness (numbers in replies == engine outputs), citation correctness, refusal on medical questions.
Placement: fold into Deliverable 5 (web app + grounded conversational assistant); heart profile into Deliverables 2 and 4. Keeps within the 5-deliverable cap.

## "What else is free?" analysis (2026-09-30)
Free = computable from data already in the pipeline (INDB nutrient columns: energy, carbs, protein, fat, free sugar, fibre, SFA, MUFA, PUFA, cholesterol, Ca, P, Mg, Na, K, Fe, Zn, Cu, Se, vit A/E/D/K, folate, B vitamins, vit C, carotenoids; ingredient lists) + a published threshold.
ADD (free, fits the story):
- Sodium:potassium ratio -> into the Heart profile (K is in INDB).
- Positive "balance" axes: protein per serving (INDIAB: Indian diets low in protein), fibre per serving -> shows what a dish does well, not just harms.
- Allergen flags (8 FSSAI-notified allergens) from ingredients -> app utility only, not a deliverable.
- Iron/calcium per serving as display only (no absorption claims).
DO NOT ADD (not free or off-strategy):
- Diabetes/glycaemic load: needs glycaemic-index data per ingredient (not in INDB) -> only a proxy (added sugar + refined carbs - fibre) would be possible; label as future work.
- Carbon footprint: CoSyLab already owns this (SustainableFoodDB) -> duplication.
- Cost per serving: needs price data.
- Purines/gout, medication interactions, pregnancy advice: no data / medical risk.
Principle: two profiles (Liver lead, Heart second) + positive axes; resist scope creep given the 5-deliverable cap.

## Further "2026" AI features discussed (user wants AI beyond a trivial chatbot)
Principle: AI proposes / perceives / explains; the deterministic engine computes every number (generate-then-verify).
Recommended (fit the core, add real AI):
1. Generate-then-verify recipe rewriter (agentic): LLM rewrites a recipe into a lighter version; engine recomputes load; authenticity model scores it; loop until load drops and authenticity stays high. -> D3.
2. Learned authenticity model: embedding / set-model trained on real Indian recipes that scores whether a modified recipe is still "that dish" (replaces hand heuristics; ties to lab's recipe-generation work). -> D3.
3. Multimodal input: (a) Hindi/Hinglish voice dictation of home recipes -> structured recipe (Indic ASR + LLM); (b) plate/thali photo -> dish recognition (lab's Indian platter detection; ICVGIP 2025 thali dataset) -> footprint RANGE from recipe distributions (not pixel-based calorie guessing). -> D5.
4. Personal weekly agent (on-device/private): remembers logged dishes, weekly liver/heart report, proactive nudges ("third fried snack this week"). -> D5.
5. Multilingual explanations (Hindi + regional). -> D5.
Avoid: numbers from LLMs; photo calorie estimation as primary; generic chatbot as a headline.

## Data sources for SODIUM and TRANS FAT (searched 2026-09-30)
Gap: ~78% of recipe salt lines say "to taste"; INDB has no trans-fat column.
SODIUM:
- [V] Johnson/Delhi study (PMC6482771; women 20-59, Delhi): 90% of daily salt from home-cooked food, 95% of sodium from salt added while cooking; contributions by dish type: vegetable dishes 31%, pulse dishes 26%, cereal dishes 23%; papad/pickle minor (small quantities). South India (Ravi et al.): pulse 30%, rice 27%, vegetable 17%.
- [V] National NCD Monitoring Survey (Sci Rep 2023, PMC10517942): mean 8.0 g salt/day (men 8.9, women 7.1); systematic review 1986-2014: 10.98 g/day (95% CI 8.57-13.40).
- [V] safefood 2015 measured SALT in Indian takeaway dishes (lab) -> validation for restaurant dishes; UK CoFID has sodium for analysed South Asian dishes.
- [V] INDB has sodium for ingredients -> intrinsic sodium (papad, pickle, cheese, baking soda, bread).
Method: default for "salt to taste" = dish-specific median from recipes in our corpus that DO state salt (~22% of salt lines are quantified), cross-checked against the population figure (~8 g/day distributed by dish-type shares above); report a range; validate against measured takeaway salt (safefood/CoFID).
TRANS FAT:
- [V] FSSAI PAN-India Food Survey 2021 (trans fat & acrylamide; NABL labs): 6,245 samples across 6 categories; only 3.14% (196) exceeded 2% TFA of fat, 90% of those in oils/vanaspati/shortenings/margarine; in categories 1-5 only 0.4% exceeded 2%. Full report PDF (253 MB) on fssai.gov.in national surveys page. FSSAI limit since 2022: industrial TFA <= 2% of total fat.
- [V] Gupta et al. 2016: TFA as % of fat per street/snack item (up to ~12-13% in some fresh-fried street items, 23% in besan barfi).
- [V] Joshee et al. 2019: 75 snacks, TFA 0.016-4.4% of fatty acids (declining trend).
- [V] Jain, Passi & Selvamurthy 2024: TFA rises ~0.05% -> ~0.89% (dry basis) over 32 frying cycles; 20-264x in oils.
- [V] Biscuits (PMC4571254, 46 samples, Mysore 2009-11): TFA 0.1-3.2 g/100 g.
- [S] Agrawal et al. 2008: pre-regulation Indian sweets 0.3-17.7 g/100 g and snacks 0.1-19.8 g/100 g TFA (older; context only).
Method: fresh commercial oils/ghee-free home cooking -> TFA <= 2% of added fat (regulatory cap) plus natural dairy TFA; vanaspati/bakery shortening -> FSSAI survey ranges; street/reused-oil fried items -> Gupta/Jain measured ranges. Report TFA mainly for fried, bakery and sweet items; near-zero otherwise.
