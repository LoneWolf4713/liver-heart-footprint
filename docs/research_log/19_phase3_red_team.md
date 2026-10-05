# 19 Phase 3: red team of the shortlist (2026-09-29)
SHORTLIST (user decision):
 S1 = N1 "Red Hexagon" (FSSAI front-of-pack warning impact, packaged + traditional foods; N3 protein-washing merged in)  [file 17]
 S2 = Iron-smart kitchens v2 (engine-first; "does cuisine encode absorption wisdom" as one chapter)  [files 16, 18 R2]
 S3 = R1 "Menu Truth" (label plausibility via inverse recipe inference + hidden allergens)  [file 18]
Note: S1 and S3 overlap (both infer nutrition of unlabelled/unpackaged dishes); may merge after red team.
Protocol per idea (from 06): (a) novelty attack, (b) feasibility/data dry-run, (c) overlap with CoSyLab/Foodoscope, (d) safety/ethics, (e) professor-fit; then verdict.

## Cross-cutting finding: lab's newest resource = ENABLER, not overlap
- [V] arXiv 2609.22099 (12 Aug 2026, Bagler): RecipeDB2 = 128,942 recipes, 35,474 ingredients, 32 regions, 99 countries, 34 (Indian) states; NER into 7 attributes; ingredients linked to USDA (BERT embeddings, F1 87.90 on top-200) -> 148 nutrient params; RF propagates 34 categories; rule-based dietary style. Live at cosylab.iiitd.edu.in/recipedb2/.
  Does NOT do: cooking yield/oil uptake, bioavailability, HFSS/FOPL, label audit, uncertainty. -> all three shortlist ideas can BUILD ON RecipeDB2 (strong professor fit).
- [V] arXiv 2604.28021 (Apr 2026, Bagler lab): universal statistical laws of recipes (Zipf, Heaps, Menzerath-Altmann; macronutrient concentrations log-normal). Not overlapping.

## S1 Red Hexagon
(a) Novelty: [V] Nutrients 2021 applied WHO SEARO + Chile NPMs to 10,501 Indian products (Mintel, proprietary): 68% >=1 warning. [V] ML added-sugar prediction exists (Davies et al. J Nutr 2022, KNN, George Institute). [S] Exact FOPL cut-offs "yet to be notified" (Inspeckt, Regbite); Parliamentary committee pushing; SC hearing 23 Aug 2026 REJECTED the argument that international-style labelling unfairly hits traditional Indian foods (Mondaq) -> our traditional-food analysis tests a claim argued in court. Open, reproducible analysis of the exact 2026 variants + traditional foods: not found.
(b) Data: [V] Open Food Facts India = 24,072 products (API count, 2026-09-29). Nutrient-field completeness NOT yet measured (API rate-limited; use bulk dump/HF parquet). Thresholds not final -> must simulate a parameter range.
(c) Overlap: none with CoSyLab found. Zomato Healthy Score is a different (positive) score.
(d) Ethics: neutral analysis, not advocacy; no brand shaming.
(e) Prof fit: medium (policy + packaged foods are less "gastronomy"; traditional-dish half fits).
Weakness confirmed (user's point): core is rule application; science only in estimating added sat fat/sugar for unlabelled items.
Score (rubric 06 w/ professor-fit): Real 23 | Novelty 15 | Tech 10 | Data/valid 11 | Prof fit 7 | Bio 3 = 69.

## S2 Iron-smart v2
(a) Novelty: [V] Hallberg & Hulthen AJCN 2000 meal iron-absorption algorithm (phytate, polyphenols, ascorbic acid, meat, calcium, egg, soy, alcohol; r2=0.987 vs 24 measured meals) = mature, implementable engine. Generic web iron calculators exist (crude multipliers). Indian-dish absorbable-iron atlas + minimal-tweak search + cuisine null-model test: not found.
(b) Data: [V] PhyFoodComp 1.0 Excel datasheet downloadable from FAO; INDB (Fe, vit C, Ca) + RecipeDB2 (USDA iron, vit C); polyphenol (galloyl) inputs from Phenol-Explorer = partial gap; validation literature-only.
(c) Overlap: none.
(d) Ethics: must not claim health outcomes; "estimated absorbable iron".
(e) Prof fit: high (his pairing/null-model method + "Fe/Ca/Zn food-wise" seed).
Weakness: demand (nobody explicitly asking); engine largely = applying Hallberg.
Score: Real 14 | Novelty 16 | Tech 13 | Data/valid 9 | Prof fit 9 | Bio 5 = 66.

## S3 Menu Truth
(a) Novelty: [V] Inverse "label -> ingredient amounts" exists for PACKAGED foods (Ng et al. LP used in Davies 2022; JFCA 2022 "Estimating food ingredient compositions based on mandatory product labeling"; hobby repos reciper, food-reverse-engineering). NOT found: cooked restaurant dishes with cooking transformations + learned recipe-distribution priors + plausibility audit + hidden allergens for Indian food.
(b) Data / demand: [V] Zomato Healthy Mode (launched 29 Sep 2025; 7 metros): nutrition for EVERY dish + Healthy Score, "derived from restaurant inputs and AI-generated estimates" -> millions of AI-estimated Indian dish values shown to consumers, unaudited. [V] Chain disclosures: McD India (measured-style, sat fat/added sugar/sodium/allergens), Behrouz NI guide (43 pp) and Haldiram's/Wow! Momo values "calculated from standard recipe using USDA + IFCT" (per aggregator). DesiMacros = 258 items/12 chains, macros only, mostly Western items -> Indian coverage THIN [count pending]. Zomato scraping = ToS risk -> manual sample only.
(c) Overlap: Foodoscope sells auto nutrition facts -> position as AUDIT/validation, not generator.
(d) Ethics: report plausibility, never "fraud"; anonymise brands in public outputs if needed.
(e) Prof fit: high (extends RecipeDB2 nutrition mapping to COOKED dishes; "health for the complete dish").
Strongest argument AGAINST: circularity. Many "ground truth" labels are themselves calculated from USDA/IFCT, and we have no lab. So S3 can only say "physically implausible", never "wrong by X"; if most labels are recipe-sums, the audit may find little (but that split is itself reportable).
Score: Real 22 | Novelty 17 | Tech 16 | Data/valid 9 | Prof fit 8 | Bio 3 = 75.

## Merge option M = S3 + S1 ("Truth in Indian food labels")
One science core (recipe -> cooked composition with uncertainty; Bayesian inverse from label to recipe) with applications: (1) plausibility audit of restaurant/app nutrition (Zomato AI values, chain disclosures); (2) red-hexagon status for UNPACKAGED traditional foods under FSSAI variants (tests the argument made in the SC); (3) hidden allergens + health-halo. Est. score ~78. S2 stays as the science-first alternative.

## Open dry-runs before final decision
1. OFF India nutrient-field completeness (bulk dump).
2. Count of Indian dishes with public disclosed nutrition (McD India Indian items, Behrouz PDF, Haldiram's, KFC booklet, others) -> need >= ~150 for S3.
3. Feasibility of a manual Zomato Healthy Mode sample (ToS-safe, ~200-300 dishes).

## USER VERDICT on this red team (2026-09-29): REJECTED as poor
- The red team drifted into "betting" instead of producing a concrete project.
- S1: just applying thresholds. S2: acceptable only if targeting the grade alone.
- S3: (i) manually collecting Zomato data = unclear ethics/legality and NO scientific standing (what is the basis of hand-copied app numbers?); (ii) FATAL GAP not addressed: where is the ground truth of ACTUAL COOKED-dish nutrients to compare calculated labels against? Without it the whole idea has no basis.
- Instruction: re-evaluate properly; search specifically for the data question; none of the shortlist yet meets the criteria.
- Corrections adopted: Zomato/app data DROPPED entirely (no scraping, no manual copying). Every idea must name a VERIFIED ground-truth source before it is scored.

## RE-EVALUATION (redo, 2026-09-29): the cooked-dish GROUND TRUTH question
Verified facts:
- [V] INDB paper (PMC11277795): IFCT 2017 = 528 RAW items; "does not include data for composite dishes, i.e., chapattis or curries"; "nutrient composition of composite Indian dishes is limited"; analysing cooked samples "cost-prohibitive". (Correction: a Grokipedia page claiming IFCT 2017 includes cooked foods is WRONG; ignore.)
- [V] Chen, Gilbert & Khokhar, Food Chem 113:825 (2009), open on Zenodo 10043766: 10 South Asian dishes (puri x2, aloo palak, Bengali chicken-potato curry, prawn bhuna, zarda, rasmalai, chicken bhuna, Bombay aloo, lamb kebab) ANALYSED vs recipe-CALCULATED with water-loss + fat-uptake terms. Findings: water loss up to 24%; puri fat uptake up to 18.4 g/100 g; calculated > analysed for most nutrients; macros closest; fibre, sodium, vit C, D, thiamin, riboflavin poorly estimated. => the core "calculated vs measured" science for South Asian dishes EXISTS (small n=10).
- [V] EuroFIR ethnic foods programme: Khokhar et al. 2009 harmonised procedures; Khokhar et al. EJCN 2010 new analytical data on ethnic foods in Europe (included in national FCDBs).
- [V] safefood (Ireland) 2015 "What's in your Indian takeaway?": lab-analysed (Foodtest Labs) onion bhaji, chicken pakora, chicken tikka, tikka masala, korma, jalfrezi (n=30 each), rice, pilau, naan (n=20 each); energy, fat, sat fat, protein, salt. Summary statistics only; NO recipes.
- [V] UK CoFID: mixes analysed and recipe-calculated items (source flagged per item); some South Asian takeaway items analysed; count NOT yet made.
- [S] MyFCD Malaysia: 668 prepared foods with a sampling + analysis protocol (likely analysed; Malaysian-Indian dishes subset unknown). Singapore SG FoodID: downloadable; method/analysed status UNVERIFIED (JS-only site).
Conclusion on data: open, lab-measured cooked-dish data for INDIAN (India-cooked) dishes essentially does not exist. Abroad: a scattered ~tens (maybe ~100) of lab-analysed South-Asian-style dishes, mostly UK/Ireland/Malaysia preparations, mostly WITHOUT paired recipes.

## Revised verdicts
- S3 Menu Truth (audit of Indian menu/app labels): KILL. No ground truth for Indian cooked dishes; app data (Zomato) dropped on ethics/legality/standing grounds; chain disclosures are largely recipe-calculated (circular).
  Salvage only as a narrower BENCHMARK ("how accurate is recipe-database nutrition estimation for South Asian dishes vs all open lab-analysed sources?") IF a count shows >= ~80-100 analysed dishes; prior art (Chen 2009, n=10) already exists -> incremental. Not recommended without the count.
- S1 Red Hexagon: user-rejected (rule application; thresholds not even notified). Stays out.
- S2 Iron-smart v2: grade-safe fallback only (user's judgement). Its "ground truth" is the published, validated Hallberg algorithm (r2=0.987 on 24 measured meals) -> the ONLY shortlist item whose core model already has external validation; weakness remains demand.
Lesson/rule for next round: no idea is scored until its ground-truth/validation dataset is identified, verified accessible, and sized.
