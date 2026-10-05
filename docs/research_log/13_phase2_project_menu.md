# 13 Phase 2 (REDONE): Project menu, no default pick (2026-09-29)
Supersedes 12_phase2_concepts.md (that file forced one main concept; user wanted MANY options to choose from, less obvious, with realistic data/processing burden).
Rules for this menu: (1) many distinct projects, not one project with add-ons; (2) each states data + processing burden honestly; (3) each states how OBVIOUS it is to classmates; (4) each states dependence on COOKED ground truth (the hard part); (5) scores are NOT used to force a winner; user chooses. Legend: [V] verified in a source read this session | [U] unverified/inference.

## Reality check first (things that change how to judge every idea)
1. "The lab tool ignores cooking" does NOT mean cooking is the dominant error. INDB (open Indian recipe-nutrient dataset) applied USDA retention factors as a sensitivity analysis and found differences "small" in magnitude (largest for vitamin C, potassium, phosphorus) [V, PMC11277795]. Bigger unknowns may be ingredient matching, unit conversion, yield/oil uptake and (unmeasured) bioavailability. Any project premised on "cooking is the big error" is a hypothesis, not a fact.
2. Why cooked ground truth is scarce: [V] IFCT 2017 is raw-only except eggs; [V] USDA states that when analytical data for cooked foods are lacking, cooked values are CALCULATED from raw using retention factors -> many cooked entries in national tables are circular (learning from them recovers the factors, not reality). Analytical cooked data are rare and expensive ("cost-prohibitive", INDB authors).
3. Data sizes are small; ground truth is the constraint, not compute. Sizes: INDB ~1,095 raw foods + 1,014 recipes (<5 MB) [V]; IFCT 2017 528 foods x 151 components with standard deviations, open PDF ~500 pages (tables: proximate, vitamins, carotenoids, minerals, starch/sugars, fatty acids, amino acids, organic acids, polyphenols, oligosaccharides/phytosterols/saponins/PHYTATES) [V]; RecipeDB 118k recipes / CulinaryDB 45,772 recipes across 22 regions / FlavorDB 936 ingredients x 2,254 molecules (each well under 1 GB) [V from papers; access via cosylab site/professor]; USDA FoodData Central (SR Legacy, Foundation Foods with sample variability, FNDDS) downloadable CSV [V exists; sizes U]. Null-model simulations (100k-10M random recipes) run on a laptop in minutes to hours; no GPU needed except for optional small-LLM parsing (7B-class model runs locally on a consumer GPU/CPU).
4. Licence flag: IFCT 2017 copyright notice says no part may be stored/reproduced in any electronic format for creating a product without NIN's written permission [V]. INDB is a published open derivative with public code [V]. For anything that re-tabulates IFCT ourselves, ask NIN/professor first; safer to build on INDB.
5. Hand-curation is the real cost: e.g., 100-300 literature measurements of cooked vs raw = person-days to weeks; own kitchen measurements (weigh before/after) are cheap primary data (Idea 4).

## Legend for the menu
Obviousness to classmates: LOW / MED / HIGH. Data burden: S (a few files, clean) / M (parse + alias + curate) / H (needs new measurement/curation at scale). Cooked-truth dependence: none / partial / high.

---
## THE MENU

### P1. "The Flip Audit": robustness of the food-pairing hypothesis (meta-science)
- Question: The same lab found Indian cuisine strongly NEGATIVE in pairing (Jain 2015: 2,543 TarlaDalal recipes, 194 ingredients, mean shared compounds 5.876 vs 9.442 random, dNs -3.566, Z -54.7) [V] and later POSITIVE for the Indian Subcontinent (Singh & Bagler 2018: 4,058 recipes, 378 ingredients, FlavorDB; 16 of 22 regions positive, only 6 negative) [V]. Which data choices flip the sign (ingredient set, aliasing, compound ingredients like garam masala pooling molecules, profile completeness, recipe source, size cut-offs, null-model choice)?
- Deliverable: a sensitivity/"flip map" showing which conclusions are robust and which are artefacts; guidance for future pairing studies.
- Data: Jain dataset S1-S3 [V listed; file availability U], CulinaryDB/RecipeDB (via cosylab/professor), FlavorDB. Burden: S-M. Compute: light. Cooked truth: none.
- Method originality: systematic perturbation + variance decomposition; null-model machinery from the course. Prior art: individual replications exist for other cuisines (Northeast India 2022, Turkish, Arab, Chinese) [V titles]; a formal robustness audit of the lab's own contradiction not found [U].
- Obviousness: LOW (most classmates will run pairing on a new cuisine; this asks whether the method's answer is stable).
- Risks: sensitive because it examines the professor's own contradictory results (he attributed the difference to data quality [V]); needs constructive framing. Result could be "unstable", which is still a finding.

### P2. "Absorption pairing": do traditional recipes encode nutrient-absorption logic?
- Question: Ahn/Jain test whether recipes pair ingredients that share flavour compounds. Analogous test: do recipes pair iron/zinc/calcium sources with absorption enhancers (organic acids, vitamin C, fermentation) and away from inhibitors (phytate, tannins/polyphenols) more than random cuisines with the same size and ingredient frequencies? Compare Indian vs other cuisines; vegetarian vs non-vegetarian.
- Data: IFCT tables 5, 8, 9, 10, 11 (minerals, amino acids, organic acids, polyphenols, phytates) [V exist]; recipes (INDB 1,014; RecipeDB Indian subset; CulinaryDB for cross-cuisine, needs a non-Indian phytate/organic-acid source: USDA lacks phytate [U]). Burden: M (extract/alias tables; licence flag). Compute: light. Cooked truth: none (recipe-level, uses raw values).
- Method originality: new "pairing hypothesis" in nutrient space using the course's null models. Prior art: none found for bioavailability pairing [U; ScienceDirect blocked].
- Obviousness: LOW.
- Risks: effect may be null; recipes omit process and side dishes (chai, curd served separately); aliasing to IFCT names is laborious.

### P3. "Where does recipe-nutrition error really come from?" (error-budget audit)
- Question: For Indian dishes, rank the sources of error in recipe-level nutrition estimates: ingredient matching, unit/quantity conversion, yield, retention, oil uptake, raw-vs-cooked, bioavailability. Compare (a) lab's USDA-SR summation method [V: 71.6% matching accuracy on 5,000 top ingredients; 36 kcal/serving error; code public], (b) INDB raw sum, (c) INDB + retention. Produce "fix this first" value-of-information ranking.
- Data: INDB (clean), Kalra code (GitHub cosylabiiit/Nutritional-Estimation-In-Recipes) [V], RecipeDB Indian subset, IFCT/USDA. Burden: S-M. Compute: light. Cooked truth: partial (uses simulation of plausible factor ranges + any measured yields from P4).
- Obviousness: LOW-MED (many do "nutrition estimator"; few audit it).
- Risks: without ground truth, conclusions rest on simulated error ranges; frame as sensitivity analysis. Directly touches the lab's own tool, so present constructively.

### P4. "Yield Kitchen": measured Indian cooking-yield and oil-uptake dataset + predictor
- Question: INDB lists yield-factor correction (weight gain/loss in cooking) as a next step [V]. We can measure it ourselves: cook ~40-60 staple preparations (dal by method, rice, roti, sabzi, tadka), weigh raw ingredients and cooked total, measure oil left in pan/residual, replicate 3x; also weigh home measures (katori, mutthi, chutki, glass) by ingredient density. Then train a small model (or hierarchical Bayesian) to predict yield/uptake from recipe text, and re-run INDB corrections.
- Data: PRIMARY data we generate (~150-300 weighings) + INDB + IFCT for calibration. Burden: H in labour but cheap and low-tech (kitchen scale). Compute: trivial. Cooked truth: this IS the ground truth for yield (not for vitamins).
- Method originality: first open, replicated measurement set of Indian preparation yields [U]; probabilistic unit normalization for home measures (FKG.in mentions imprecise/culturally specific quantities [V]).
- Obviousness: LOW (classmates rarely generate data).
- Risks: physical effort; small n; results specific to our kitchens/ingredients (need protocol, replicates, reporting of variability); little "AI" unless the predictor/parser is emphasised.

### P5. "Are traditional recipes Pareto-good?" (cuisine as multi-objective optimiser)
- Question: Against random recipes with the same size and ingredient frequencies, do real recipes sit close to the Pareto frontier of flavour harmony (pairing score), nutrient density (protein/micronutrient per energy) and (optionally) carbon footprint? Compare cuisines; find outliers.
- Data: recipes with quantities (INDB, RecipeDB), FlavorDB, nutrition (IFCT/INDB/USDA), carbon (lab's SustainableFoodDB, needs access). Burden: M. Compute: moderate (10^6-10^7 sampled recipes; laptop, hours). Cooked truth: none (raw sums; state limitation).
- Method originality: multi-objective null-model test; complex-systems framing (professor's physics/complex-systems background). Prior art: healthiness-of-cuisines papers exist; joint flavour x nutrition Pareto vs null not found [U].
- Obviousness: LOW.
- Risks: results may be inconclusive; objective definitions are contestable; nutrition needs quantities (fewer recipes).

### P6. Copy-mutate under a new selection pressure (culinary evolution simulator)
- Question: Extend the course's copy-mutate model (Kinouchi; Jain & Bagler): add a health/protein fitness term. How little can a cuisine change to meet a target (e.g., protein density per small portion) while preserving its "fingerprint" (frequency-rank curve, pairing sign, category composition)? Retro-check: can the model reproduce historical adoption of new-world ingredients (chilli, potato, tomato)?
- Data: recipe sets (RecipeDB/INDB) + nutrition + simple historical dates [U thin]. Burden: S-M. Compute: light. Cooked truth: none.
- Method originality: directed evolution with fingerprint-preservation metric. Prior art: copy-mutate models exist [V]; health-fitness variant not found [U].
- Obviousness: LOW-MED (uses his own model, but few will think of it).
- Risks: validation is abstract; historical back-test data thin.

### P7. Minimal-edit dish repair with a learned "authenticity prior" (applied system)
- Question: Given an Indian dish and a target (e.g., GLP-1-era: protein 20-30% of energy per consensus [V], smaller volume, lower fat load during dose escalation), find the smallest edit that meets it while staying in the cuisine's learned distribution (Set-Transformer or co-occurrence prior). Compare LP/heuristics/LLM proposals; judge with a blind chef/dietitian panel.
- Data: INDB + RecipeDB + IFCT + consensus rules. Burden: M. Compute: light-moderate. Cooked truth: partial (raw-sum nutrition; sensitivity to cooking bands).
- Obviousness: MED-HIGH for the GLP-1 angle (many will do a GLP-1 diet app); LOW-MED for the authenticity-prior repair.
- Risks: medical-adjacent framing; consumer competitors (HealthifyRx etc.) [S]; the consensus is Abbott-funded and formula-leaning [V].

### P8. GLP-1 compatibility atlas of Indian cuisine with honest uncertainty (screening study)
- Question: Which Indian dish types/regions already meet consensus-derived targets per small portion, and how robust is that conclusion to unmeasured cooking effects? Not an app; an atlas plus a robustness statement ("this holds even if retention/yield vary within X").
- Data: INDB (1,014) + RecipeDB Indian subset; rules from the consensus. Burden: S. Compute: trivial. Cooked truth: turned into a sensitivity analysis.
- Obviousness: MED (the topic is timely; the robustness framing is not).
- Risks: descriptive; needs a sharp finding to be memorable.

### P9. Cooking Effects Atlas from analytically measured raw/cooked pairs
- Question: Mine analytically measured (not calculated) raw-cooked pairs across national tables (e.g., USDA Foundation Foods/NFNAP-type entries, other countries' tables) to learn nutrient ratios by food class x process with uncertainty; test transfer to held-out foods and countries.
- Data: FDC downloads (S-M); the catch is [V] many cooked entries are calculated from retention factors, so only truly analytical pairs are usable (likely hundreds, not thousands [U]). Burden: M-H. Compute: light. Cooked truth: this is the attempt to build it from existing data.
- Obviousness: LOW.
- Risks: circularity, small n, unclear novelty (may exist [U]), weak transfer to Indian preparations (tadka, pressure cooking).

### P10. Kitchen parser benchmark for regional Indian recipes (small local models)
- Question: How well do small local models (1-8B) parse code-mixed Hindi/English/regional recipe phrases (units like katori/mutthi/chutki, "as needed") into structured entities with quantities, versus larger cloud models and prior NER (FKG.in, lab NER)? Release an annotated benchmark (500-1,000 phrases) + error analysis.
- Data: recipe phrases from RecipeDB/blogs/YouTube transcripts + our annotations. Burden: M-H (annotation labour). Compute: light-moderate (local inference). Cooked truth: none.
- Obviousness: MED. Prior art: lab NER (LREC-COLING 2024), FKG.in NER (Gupta 2025) [V titles]; AyurParam shows small bilingual models are weak in specialised domains [V].
- Risks: overlap with FKG.in; benchmark papers need careful annotation quality (inter-annotator agreement).

### P11. "The protein turn": observational study of recipe evolution 2022-2026
- Question: Are Indian recipe sources shifting to protein-forward ingredients (paneer, soya, sattu, millet blends) as high-protein/GLP-1 trends spread? Test copy-mutate predictions on real dated data.
- Data: dated recipes via scraping (fits Assignment-1 skills); dated corpora availability [U]. Burden: M-H (scraping, dating, dedup). Compute: light. Cooked truth: none.
- Obviousness: LOW.
- Risks: data availability/dating, confounds (site editorial policy), causal claims weak.

### P12. "Test the Tradition": falsifiable Ayurvedic food rules
- Question: Encode ~10 classical food-combination/processing rules (e.g., anupana such as buttermilk with pulses; soaking/fermentation; ghee with fat-soluble compounds) as measurable predictions; back-test against published measurements. Output: supported / contradicted / untestable scorecard with citations.
- Data: ~30-50 papers (few in-vitro anchors exist, e.g., INFOGEST+Caco-2 buttermilk-green gram [V]); AyurKOSH (non-commercial) [V]. Burden: M-H (literature curation; needs an Ayurveda scholar). Compute: trivial. Cooked truth: uses published in-vitro data.
- Obviousness: MED (Ayurveda is a fashionable topic; falsifiable framing is not). Chatbots/dosha classifiers = HIGH and weak [V AyurParam ~41% on its benchmark].
- Risks: pseudoscience optics, subjective labels, regulatory guardrail (FSSAI Ayurveda Aahara Reg. 8 bars disease claims) [V].

### P13. Warfarin-steady thali: exposure-aware vitamin K planning for Indian meals
- Question: Compute daily vitamin K1 exposure and day-to-day variability from real Indian meal plans; quantify how much uncertainty (3x variation in the same vegetable across sources [V]) matters; output a steadiness score.
- Data: INDB (has K1/K2) [V], literature ranges. Burden: S. Compute: trivial. Cooked truth: partial (cooking effect on K1 small; [U]).
- Obviousness: LOW.
- Risks: safety-critical (false negatives), thin validation, low ML content; best as a small study, not a product.

---
## Comparison table (no winner implied)
| # | Project | Type | Obviousness | Data burden | Compute | Cooked-truth need | Main risk |
|---|---------|------|-------------|-------------|---------|-------------------|-----------|
| P1 | Flip Audit (pairing robustness) | meta-science | LOW | S-M | light | none | sensitive (his contradiction) |
| P2 | Absorption pairing hypothesis | hypothesis test | LOW | M | light | none | may be null |
| P3 | Error-budget audit of nutrition estimation | audit | LOW-MED | S-M | light | partial | no ground truth |
| P4 | Yield Kitchen (measured yields + predictor) | new data | LOW | H (labour) | trivial | this IS ground truth | small n, physical effort |
| P5 | Recipes as Pareto-good? | complex-systems test | LOW | M | moderate | none | inconclusive |
| P6 | Copy-mutate under new pressure | simulation | LOW-MED | S-M | light | none | abstract validation |
| P7 | Minimal-edit repair + authenticity prior | applied system | MED-HIGH | M | light-mod | partial | crowded, medical-adjacent |
| P8 | GLP-1 compatibility atlas + robustness | screening study | MED | S | trivial | sensitivity | descriptive |
| P9 | Cooking-effects atlas from raw/cooked pairs | ML on tables | LOW | M-H | light | circularity | few true pairs |
| P10 | Regional kitchen-parser benchmark | benchmark | MED | M-H | light-mod | none | overlaps FKG.in |
| P11 | "The protein turn" (2022-2026 trend) | observational | LOW | M-H | light | none | data dating |
| P12 | Test the Tradition (Ayurveda) | literature back-test | MED | M-H | trivial | published in-vitro | pseudoscience optics |
| P13 | Warfarin-steady thali | small study | LOW | S | trivial | partial | safety, low ML |

## Trap ideas (HIGH obviousness; probably several classmates will do these)
GLP-1 diet/meal-planner app; Ayurveda chatbot or dosha classifier; LLM recipe generator or "AI chef"; allergen detector; restaurant food-waste predictor; generic nutrition estimator from ingredient lists; cuisine classifier; pairing analysis on one new cuisine; carbon-footprint calculator.

## Combinations possible (user's choice, not a default)
- P4 -> P3 (own measured yields feed the error-budget audit) = data + analysis pair.
- P2 + P12 (absorption logic in recipes + falsifiable tradition claims) = one bioscience-flavoured story.
- P1 + P5 (robust pairing + Pareto test) = one complex-systems story using the same recipe/flavour data.
- P6 + P7 (simulation + applied repair) = model then system.
Each single project is standalone; combos are optional.

## Profiles (for choosing by risk appetite; not a recommendation)
- Lowest risk / fastest: P8, P13, P3.
- Highest originality: P1, P2, P4, P5.
- Most "AI-intentional": P7, P10, P9 (learning components), P6 (simulation with learning).
- Most bioscience leverage: P2, P12, P13, P9.
- Most primary-data generation: P4.
- Most direct link to the professor's own results/tools: P1, P3, P6.

## Open items before any shortlist
1. Verify availability/licences of Jain 2015 supplementary datasets, CulinaryDB downloads, RecipeDB access via professor.
2. Novelty attacks per shortlisted idea (fresh skeptic searches) - Phase 3.
3. For P2/P9: confirm which IFCT tables can legally be re-tabulated (NIN permission) or use INDB.
4. For P4: design a measurement protocol (replicates, units, tare, oil residue method) before committing.
