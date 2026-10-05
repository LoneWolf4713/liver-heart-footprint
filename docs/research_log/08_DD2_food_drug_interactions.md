# 08 Deep Dive 2: Food-drug interactions (GLP-1 angle + general) (2026-09-29)
Legend: [V] verified from source read | [S] secondary | [B] blog/vendor | [U] unverified / inference

## 1. Problem reality
### 1a. GLP-1 as a driver of interactions  (WEAKER than assumed)
- [V] DDDT review (Dove Press, Apr 2025): interactions caused by GLP-1 RA delayed gastric emptying are "currently limited" and mostly clinically insignificant; no PK interactions via metabolic enzymes/transporters reported. Exceptions with notable exposure change: oral contraceptives with TIRZEPATIDE, levothyroxine with ORAL SEMAGLUTIDE. Digoxin/warfarin: no clinically significant PK change (exenatide postmarketing INR rises noted). Delayed gastric emptying shows tachyphylaxis; mitigation = give other oral drug ~1 h before GLP-1.
- [S] Endocrinology Advisor (Nov 2025): tirzepatide may reduce oral-contraceptive efficacy; advise non-oral/barrier method for >=4 weeks after start and after each dose increase. Oral semaglutide raised levothyroxine exposure ~33%; a thyroidectomy patient needed 25% dose cut on SC semaglutide (mechanism unclear: absorption vs weight loss).
- => These are DRUG-DRUG/timing effects, handled by monitoring rules and labels. Not a rich food-drug computational problem. The GLP-1 angle does NOT justify DD2 as a standalone project. (Related but out of scope: reduced intake + sulfonylurea/insulin -> hypoglycaemia; weight loss + antihypertensives -> hypotension: physiology/clinical, not recipe-level.)
### 1b. General food-drug interactions (DFIs)
- [V] Vitamin K-warfarin: guidance is CONSISTENCY, not avoidance ("problem is sudden changes"). Vitamin K1 in the same vegetable varies ~3x across sources/markets (spinach 305-971 ug/100 g in Bandung study vs 245-286 Australia, 316-423 Brazil; PMC11960828). Patients with >195 ug/day had more stable INR (Kim et al. cited). => quantity/variance-aware reasoning is genuinely needed; Indian greens (palak, methi, sarson) plausible but [U] no Indian computational tool found (only patient-education blogs).
- [V] Turmeric/piperine: in vitro curcuminoids inhibit CYP3A, CYP2C9/2C19, UGT, SULT at low-micromolar IC50; piperine noncompetitive CYP3A inhibitor (Ki 5.4 uM); trials use 2-8 g/day curcuminoids because of poor bioavailability; piperine raises curcumin bioavailability ~20x (Shoba 1998). [S] Drugs.com lists 134 "moderate" interactions for Curcumin 95 (a SUPPLEMENT).
  => the classic DOSE PROBLEM: in-vitro inhibition and supplement-grade interaction lists say little about a pinch of haldi in dal. Existing checkers do not separate culinary exposure from supplement exposure.
- [U] No India-specific burden data for food-drug harms found this round (would need a clinical source).

## 2. Prior-art kill-check
- [V] Compound-level ML (Development and validation of explainable ML for DFIs, PMC10143839): 70,477 FooDB compounds x 13,580 DrugBank drugs, 3,780 features/pair, XGBoost, external set 1,922 DFIs. LABELS come from DrugBank text heuristics ("take with food" -> positive; reduced absorption + adverse effect -> negative). Predicts at COMPOUND (SMILES) level; no dose, no dish.
- [V] FDMine (Sci Rep 2022; homogeneous graph, DDI-based evaluation), FARFOOD (structural similarity of food compounds to drugs), FooDrugs DB (text + transcriptional data), NPDI KG (labelled data lacking; models trained on DDI data as proxy).
- [V] KG-DFI (PubMed 42614428, 2026): explicitly says most approaches decompose food into constituent molecules and "align poorly with real-world clinical practice where dietary decisions are made at the level of whole foods" -> models each FOOD as a node linked to compounds and biological entities. => whole-FOOD level is now prior art (2026). Dish/recipe level and dose are NOT covered in what I saw.
- [S] Machine learning for food effects during drug development (J Cheminform 2025): drug-side fed/fasted prediction; traditional models fail to capture GI variability.
- [U] Dose-aware / dish-level / cooking-aware DFI prediction: searches returned nothing (3 of 4 source fetches blocked by ScienceDirect/ResearchGate). Novelty check is INCOMPLETE.
- Lab overlap: SpiceRx (spice-disease), DietRx (food-disease-chemical-gene text mining), DietRxDB "coming soon" (100+ diseases). Food-drug not seen [U].

## 3. Data
- [V] FooDB (foodb.ca): compounds in foods (concentration coverage sparse [U]). Phenol-Explorer: >37,000 data points from 638 papers; retention factors for 155 foods x 139 polyphenols x 35 processes; PK data on 380 metabolites from 221 studies (cooking + metabolism = useful for exposure modelling). USDA FoodData Central. [V] 2023 work coupled FooDB+Phenol-Explorer to the Dutch NEVO food-coding system to translate diet intake to compound intake (precedent for the pipeline, not for Indian dishes/dose-aware DFI).
- DrugBank (food interaction annotations; licence limits [U]), FDA/DailyMed labels (text), Stockley/Micromedex (paid).
- Ground truth is the bottleneck: no large clean labelled set of DOSE-dependent food-drug outcomes. Validation would be back-testing against well-established quantity-dependent interactions (warfarin-vit K, grapefruit-CYP3A4, tyramine-MAOI, potassium-ACEi/ARB, calcium/iron/fibre/tea-levothyroxine, dairy-tetracycline/quinolone) [known clinical pharmacology; sources not fetched this round].

## 4. Candidate technical framings (untested)
 G1 "Exposure-aware DFI": estimate compound EXPOSURE per dish/day (quantity x concentration x cooking retention x bioaccessibility) and compare to interaction thresholds, instead of predicting interaction labels from structure alone. Hybrid mechanistic + learned; explicit uncertainty.
 G2 Temporal: meal timing relative to dose (levothyroxine, GLP-1, antibiotics) as a scheduling constraint on a day plan.
 G3 Low-label learning: self-supervised food/drug KG embeddings + few-shot for rare classes, evaluated on dose-dependent benchmark cases only.
 Where AI is necessary: (a) mapping messy dish text to compounds/quantities (NER), (b) representation learning on the sparse KG, (c) uncertainty-aware ranking. The safety-critical core (thresholds, rules) must stay deterministic and evidence-linked.
- Honest: G1's ML contribution is modest; its value is the mechanistic exposure layer + honest uncertainty, which is engineering-heavy but not "BERT-style" novel.

## 5. Local-AI justification
- Medication lists are sensitive; on-device checking is defensible (same as DD1). Small model only for parsing; verdicts from deterministic rules. Moderate.

## 6. Validation route
- Literature back-test on a curated benchmark of dose-dependent interactions (sensitivity/specificity, calibration of "risk vs quantity"); pharmacist/clinician expert review; compare with compound-level XGBoost and KG-DFI-style baselines where code exists; report false-negative rate first (safety).
- Cannot validate outcomes. High risk of overclaiming; must present as decision support with citations.

## 7. Symposium fit
- Lower for chefs; good for clinicians/pharmacists/health orgs (MSSRF, Tata Trusts). A safety layer on a chef-facing tool (DD1) is more persuasive than a standalone DFI paper.

## 8. Bio leverage
- Very high (pharmacokinetics, CYP/UGT, transporters, bioavailability) and the user's real edge over CS-only teams.

## Score (rubric from 06_roadmap)
| Criterion | Max | Score | Note |
|---|---|---|---|
| Real problem + evidence | 25 | 17 | DFIs real; GLP-1 angle weak; India burden unevidenced |
| Novelty confirmed | 25 | 13 | whole-food level now exists (KG-DFI 2026); dose/dish-level not found but check incomplete |
| Technical originality | 20 | 13 | exposure-aware hybrid is intentional design; ML novelty modest |
| Data + validation feasibility | 15 | 6 | label-poor; literature back-test only; safety risk |
| Symposium / chef relevance | 10 | 5 | |
| Bio leverage | 5 | 5 | |
| TOTAL | 100 | 59 | |
VERDICT: MAYBE as a COMPONENT, not a standalone project. Fold into DD1/DD3 as a "clinical safety layer" (exposure-aware, dose- and cooking-aware). Do not lead with GLP-1 drug interactions.
What would raise it: a fetched, confirmed absence of dose/dish-level DFI work; a clean benchmark of quantity-dependent interactions; Indian evidence of real harm (e.g., levothyroxine + chai/millets, warfarin + methi).
What would kill it: KG-DFI or lab work already doing dish-level exposure reasoning; no way to build a trustworthy benchmark.

## Tool notes
- ScienceDirect/ResearchGate pages blocked ("Bot check", "login wall") in 6 of 8 attempts this round; `search` snippets still gave the abstracts, so snippets are the workable fallback.
- batch_search: query 1 of the last batch returned "All 3 sources inaccessible" (all three were ScienceDirect/ResearchGate), so that one is a genuine block, not the `[None](None)` regression seen earlier.
