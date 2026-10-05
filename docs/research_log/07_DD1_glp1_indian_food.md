# 07 Deep Dive 1: GLP-1-era Indian food (2026-09-29)
Legend: [V] verified from primary/peer-reviewed source read in this session | [S] secondary/news | [B] vendor/clinic blog (directional) | [U] unverified / my inference

## 1. Problem reality
- [V] Indian consensus: Joshi, Misra, Mithal, Saboo, Seshadri, ..., Mohan V. "Nutritional considerations for glucagon-like peptide-based therapies: An Asian Indian consensus recommendation." Obesity Pillars 19:100296, epub 15 Jul 2026 (Sep 2026 issue), DOI 10.1016/j.obpill.2026.100296, PMC13418229, CC-BY. Modified Delphi, 13 Indian endocrinologists/diabetologists, 44 statements; 42 high consensus, 1 moderate after 2nd round.
  FUNDING/COI: Abbott Nutrition grant; two authors from Abbott Healthcare. Statements 26-34 centre on diabetes-specific nutrition (DSN) formula / partial meal replacement.
- [V] Key statements (voting %, evidence level): S1 GI side effects impair adherence (100%, L1); S4 "individuals often lack structured nutrition guidance" (92%, L1); S10 individualized nutrition plans essential (100%, L3);
  S11 protein 20-30% of energy (92%, L1); S12 small frequent meals, good-quality fat, high-fibre (85%, L2); S15 >2 L fluids (84%, L5); S17 mixed soluble+insoluble fibre for GI symptoms (92%, L2); S18 slow eating, avoid large evening meals (100%, L5); S19 nutrient-dense foods for micronutrients despite low appetite (92%, L3);
  S25 do NOT skew to a single nutrient profile (100%, L3); S28 ideal = nutrient-dense meal at lower volume + address altered taste; S9 ~2/3 of lost weight regained within a year after stopping (85%, L1).
- [V] India-specific facts in that paper: micronutrient deficiency prevalence vit D 61%, iron 54%, B12 53%, folate 37%, iodine 17%; ICMR-INDIAB refined-cereal predominance (NE 99%, South 87%, East 78%; whole wheat higher in North 90%, Central 70%); Western India high-fat low-protein pattern;
  normal-weight obesity -> sarcopenia risk 22x (men) / 25x (women); "need for culturally oriented Asian Indian-specific recommendations given India's diverse geography and varied dietary patterns"; cites transcultural diabetes nutrition algorithms (tDNA).
- [V] Clinical facts: STEP-1 DXA substudy (n=140): weight -15.0%, lean mass -9.7%, fat mass -19.3% (PMC8089287). SURMOUNT-1 substudy tirzepatide: weight -21.3%, lean -10.9%, fat -33.9%.
  [S/B] meta-analysis (Karakasis 2025, 22 RCTs) lean mass ~25% of weight lost; popular claims 20-40%. Range is contested; single-number claims should not be used.
  [V/S] GI events 74.2% vs 47.9% placebo in STEP-1 (Wharton 2022, via dietitian guide); GI burden concentrates in titration/dose-escalation. Consensus: nutritional deficiencies almost double between 6 and 12 months of therapy (Butsch 2025).
  [V] US cross-sectional (Frontiers Nutr 2025, n=69, convenience, self-report): GLP-1RA users met too little protein per kg, calcium, iron, magnesium, potassium, vit A/C/D/E/K, choline.
  [S] Food preference changes: reduced preference for high-fat, non-sweet foods (Blundell/Gibbons via Nature Int J Obes 2024 review); ~1 in 5 self-report taste change; sensory/liking/wanting dissociate (Du et al., Front Nutr 2026).
- [S/B] Market: India semaglutide patent expired Mar 2026, 40-50+ generics, ~Rs 1,290/month [B]; CareEdge projects market Rs 1,000-1,200 Cr (2025) -> Rs 4,500-5,000 Cr (2030) [S via blog]; prices expected -40-50% FY27 [B].
- [B] Claims to treat cautiously: "Indian urban diets 40-55 g protein/day"; "Indian veg plate 60-70% carbs"; protein target "1.5-2.0 g/kg on GLP-1 (emerging consensus)" (contradicts the consensus paper's 20-30% of energy).
- VERDICT on problem: REAL, current, clinician-endorsed, and the experts themselves say Indian-specific food-level guidance is missing. Strongest evidence found for any lead so far.

## 2. Prior-art kill-check
Closest existing work and what it does NOT do:
- [B] Western GLP-1 planners: Second Nature (NHS-commissioned; 687 dietitian-approved recipes), glp1diet.app, GLP Flow (newsletter), PlateJoy/MyFitnessPal. Curated recipe libraries, Western foods, deterministic nutrition; no Indian cuisine; no generative/adaptive dish editing.
- [B/S] India: HealthifyRx / "Healthify Rx Smart": 3-phase medical programme (prep / optimisation / maintenance), GLP-1 support, "AI guidance", dietary style filter (veg/egg/non-veg/vegan), regional Indian cuisines, "1,000+ recipes", free meal swaps, doctors+coaches; Novo Nordisk patient-support agreement (Apr 2025); "high-thousands" customers, ~60 dietitians.
  Sugarfit (CGM + coaches; GLP-1 programme launched Dec 2025, ~4,000 users), VLCC, FITPASS. => An Indian GLP-1 diet PRODUCT exists (curated library + coaches). A naive "Indian GLP-1 meal planner app" is NOT novel.
- [V] Academic: ML for GLP-1 response prediction (Frontiers AI 2026, All of Us, n=3,975/11,420) predicts DRUG outcomes, not food design. MDPI Pharmaceuticals (Aug 2026) "Integrating Precision Nutrition with GLP-1 RA": explicitly states contribution of precision nutrition to outcomes "has not been isolated in prospective studies", FSMP evidence "limited and largely indirect" -> the field itself calls this an open hypothesis.
- Not found in my searches (absence of evidence, NOT proof): an open, evidence-linked, constraint-based computational method that generates or repairs Indian DISHES for GLP-1 users; any CoSyLab/Foodoscope GLP-1 work (search returned nothing; Foodoscope lists DietRxDB "coming soon" for 100+ diseases).
- Tool gaps in this step: INDB/Anuvaad and Healthify internals not fetched; no Google-Scholar-style exhaustive check yet. => Full novelty attack deferred to Phase 3 red team.

## 3. Data
- [V] IFCT 2017 (NIN Hyderabad/ICMR): 528 key foods x 151 components (macro, amino acids, fatty acids, vitamins, minerals, phytochemicals), regional composites for 6 regions, open PDF (nin.res.in/ebooks/IFCT2017.pdf). Enables protein QUALITY (amino-acid based), MUFA/SFA, micronutrient density.
- [V] RecipeDB (CoSyLab): 118,000+ recipes, 74 countries, NER-annotated (ingredient, quantity, unit, process, utensil); Foodoscope API (trial: 200 tokens, 25 req/min, non-commercial); direct access via professor.
- [U] INDB (Anuvaad Solutions Indian Nutrient Databank; recipe-level nutrient values): could not fetch; verify.
- [U] Missing/hard: cooking yield + oil absorption factors for Indian preparations, portion-size norms, GI-tolerance labels per dish, acceptability/taste labels, prices (retail/Agmarknet). No GLP-1 user intake dataset for India.
- Ask professor for: RecipeDB Indian subset with quantities+processes, FlavorDB, DietRx/SpiceRx, any nutrition-estimation pipeline (Kalra 2020).

## 4. Candidate technical framings (hypotheses, NOT yet novelty-tested)
 F1 "Feasibility frontier": compute, for Indian regional/vegetarian/budget constraints, the region of patient profiles (weight, energy target, volume/fat limits, dose phase) where a FOOD-ONLY plan can meet consensus targets vs where supplementation is unavoidable. Quantitative, falsifiable, uses IFCT amino-acid data; directly interrogates the Abbott-funded consensus' formula emphasis. Output = a map, not an app.
 F2 "Minimal-edit dish repair": treat a traditional dish as an editable structure; find the smallest culinary edit (ingredient swap, ratio change, technique change) that satisfies GLP-1 constraints while staying inside the cuisine's learned co-occurrence/pairing statistics (course material: ingredient frequency, food pairing, culinary fingerprints). Aligns with the symposium's own question "Can we tweak my recipe for better health outcomes?" and gives chefs something they can taste.
 F3 "Directed culinary evolution": use the copy-mutate model (Kinouchi; Jain & Bagler) with fitness = GLP-1 nutrition score x authenticity (learned from RecipeDB) to grow GLP-1-compatible variants of Indian recipe families. Ties the course's evolution-model content to a 2026 problem.
 F4 Phase-aware constraint model: the same dish/plan re-scored for initiation / dose-escalation / maintenance / post-discontinuation (GI fat-load limit, volume, protein front-loading, hydration timing) using consensus statements S1-S34 as machine-checkable rules with evidence levels attached (transparent, auditable, unlike a proprietary coach).
 F5 Restaurant/chef layer: "GLP-1 portion menu" (protein per small portion, fat load, plate volume) for Indian restaurants and canteens; the audience at the symposium.
 Where AI is NECESSARY (vs classical optimisation): (a) parsing free-text/regional/Hinglish recipes to structured entities with quantities; (b) learning the authenticity prior (what edits keep a dish recognisably itself); (c) proposing edits in text form chefs can read; (d) a deterministic verifier keeps outputs safe (LLM never sets nutrient values).
 Honest caveat: F1/F4 are mostly optimisation + evidence encoding; the learning-based novelty sits in F2/F3 (authenticity prior) and in (a). Technical originality is NOT yet BERT-level; needs DD3/DD4 (recipe representation, cooking transformation) to strengthen.

## 5. Local-AI justification
- Real: GLP-1 use is sensitive health data; India restricts obesity-drug advertising (CDSCO Mar 2026 advisory) so an on-device/private tool is attractive to clinics and users; offline/low-connectivity kitchens; tiered routing in 2026 makes a small model for parsing + rules engine for safety credible. Moderate, not overwhelming.

## 6. Validation route (no clinical trial)
- Rule fidelity: back-test outputs against each consensus statement (pass/fail table with evidence levels).
- Nutrient computation validity: compare computed values vs IFCT/INDB for known dishes; report error.
- Authenticity: chef/dietitian blind panel (mirrors the lab's Turing Test for Chef) rating "still recognisably X?" and "would you serve this?".
- Baselines: HealthifyRx-style plans as far as publicly visible; naive LP diet solver; unconstrained LLM.
- Ablations: with/without authenticity prior; with/without phase rules.
- Limits: no outcome (muscle, weight) validation; must be framed as decision support, not treatment.

## 7. Symposium fit
- Strong: chefs, nutrition NGOs (Tata Trusts, MSSRF), clinicians, food businesses in the room; GLP-1 is a live 2026 topic; F2/F5 are tasteable/demo-able; ties to lab's stated "recipe tweaking for health" and "nutrition deficiencies" questions. Risk: lab may already be planning GLP-1/DietRx work [U].

## 8. Bio leverage
- Strong: gastric-emptying physiology, sarcopenia, protein digestibility/amino-acid limiting factors, micronutrient absorption, drug-food effects (link to DD2).

## Risks
- Medical safety: CKD/elderly (protein), pancreatitis, dose phases, pregnancy; must not give dosing/medical advice; disclaim decision-support; keep consensus-linked.
- COI/quality of evidence: consensus is Abbott-funded and mostly L1-L3 with several L4-L5; must show evidence levels transparently.
- Novelty risk from Healthify (proprietary) and possible unseen CoSyLab work.
- Overclaiming: no outcome validation.

## Score (rubric from 06_roadmap) and verdict
| Criterion | Max | Score | Note |
|---|---|---|---|
| Real problem + evidence | 25 | 24 | verified consensus + clinical data; India-specific gap stated by experts |
| Novelty confirmed | 25 | 12 | product space contested (Healthify); research framings F1-F3 plausible but untested |
| Technical originality | 20 | 11 | needs stronger representation/learning contribution (DD3/DD4) |
| Data + validation feasibility | 15 | 9 | IFCT + RecipeDB good; no outcome data; chef panel feasible |
| Symposium / chef relevance | 10 | 9 | |
| Bio leverage | 5 | 4 | |
| TOTAL | 100 | 69 | |
VERDICT: MAYBE-GO (top candidate, not a winner yet). Problem is excellent; "Indian GLP-1 meal planner" as an app is NOT novel. The viable path is a research-grade reframing (F1 feasibility frontier and/or F2/F3 authenticity-constrained dish repair/evolution with a transparent evidence-linked verifier), ideally merged with DD2 (drug-food) and DD3/DD4 (representation, cooking).
What would change my mind: (a) finding a published/open tool already doing constraint-based Indian dish repair for GLP-1 -> KILL; (b) discovering CoSyLab is already building this -> lower; (c) IFCT/RecipeDB unable to support amino-acid-level scoring for Indian dishes -> lower; (d) a strong authenticity-prior method emerging in DD3 -> raise.

## Tool notes from this deep dive (for the user's MCP)
- batch_search: 2 of 3 queries returned "All N sources were inaccessible or blocked" with entries `[None](None)` (INDB/IFCT and Foodoscope/CoSyLab queries) although the same queries via `search` worked -> looks like a parse/rate issue in batch mode (regression vs earlier batches).
- read_section on a PMC table cut the table mid-row ("Adequate and good-quality protein " then truncation note) -> table cells with newlines truncated. Workaround: Europe PMC fullTextXML via fetch returned all statements.
- pubmed.ncbi.nlm.nih.gov returns "Cookies must be enabled" even with force_browser; Europe PMC REST API works and is a good fallback.
- sciencedirect bot-check pages now correctly reported as blocked (good).
- `search` can return sponsored ad-redirect URLs (bing.com/aclick) as results.
