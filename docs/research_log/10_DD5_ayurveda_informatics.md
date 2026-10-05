# 10 Deep Dive 5: Ayurveda informatics (2026-09-29)
Legend: [V] verified from source read | [S] secondary | [B] blog/vendor | [U] unverified / inference

## 1. Problem reality
- Symposium signal [V, DD baseline 04]: "Ayurveda Informatics" is a named "Future" theme on all three GastroSym pages (2023, 2024, 2025); 2023 speaker "Founder & CEO, Ayusla: Ayurveda Informatics, Human Microbiome". [U] Ayusla/IIIT-Delhi microbiome link: searches surfaced a separate IIIT-Delhi "Microbiome Informatics Lab / FMT Hub" website repo, NOT CoSyLab; I could not confirm who Ayusla is.
- What "the problem" is (my decomposition):
  (a) Classical food knowledge (viruddha ahara = incompatible combinations; anupana = adjuvant/vehicle; samskara = processing; rasa/guna/virya/vipaka properties) is unstructured, untested, and the source of many popular health claims.
  (b) Regulation: [V] FSS (Ayurveda Aahara) Regulations 2022 define Ayurveda Aahara as food prepared per recipes/ingredients/processes in authoritative books listed in Schedule A; Regulation 8 PROHIBITS labelling/advertising claims that it prevents, treats or cures disease. [S] FSSAI clarification 25 Jul 2025 published a Category "A" product list (formulations directly supported by classical texts) with AYUSH. => a compliance/provenance need exists (is this product/recipe really a Schedule-A preparation?) and a hard guardrail against health claims.
  (c) Evidence gap: claims like "milk + fish is toxic" or "ghee stored 10 days in bronze becomes poisonous" appear in review-level Ayurveda papers [V: J Res Ayurvedic Sci 2025, Viruddha Ahara review] with generic statements that "scientific research supports" the concept; I saw no rigorous quantitative test in what I could read [U: 2 of 3 full texts blocked].
- Only experimental anchor found: [V] PMC12900709 (INFOGEST + Caco-2): buttermilk (Takra, an anupana) raised estimated bioavailable Fe/Ca/Zn from cooked green gram; authors caution in-vitro != whole-body absorption. Shows Ayurvedic combination rules CAN be tested with modern methods.
- Demand evidence from users/clinicians: not found. Interest is high (many products, startups), but a concrete unmet need is weaker than DD1's.

## 2. Prior-art kill-check
- CROWDED at chatbot/classifier level [V]: AyurParam-2.9B (BharatGen, arXiv 2511.02374, Nov 2025) bilingual Ayurveda LLM; on BhashaBench-Ayur it reaches only ~41.1% (English) / 38.0% (Hindi) accuracy while beating same-size open models; authors list limits (pre-2024 corpus, exam-style eval only, no safety/clinical evaluation). TriDoshaX (student CDSS, IJARCCE Jun 2026: prakriti questionnaire + ML + rules + diet/panchakarma advice); RAG dosha chatbots (ICAISDA 2025); AyurvedaAI (Charaka Samhita retrieval, GitHub); "Computational-Food-Intelligence-Platform" (GitHub, food digital twins). => "Ayurveda chatbot / dosha classifier / diet recommender" is NOT novel.
- RESEARCH-GRADE [V]: IMSc Chennai (Areejit Samal): "Computational investigation of single herbal drugs in Ayurveda for diabetes and obesity using knowledge graph and network pharmacology" (arXiv 2601.21643, Jan 2026), Neo4j KG, quantitative phytochemical complementarity framework. AyurKOSH (IEEE DataPort): KG of diseases, symptoms, herbs, formulations with Rasa/Guna/Virya/Vipaka/Karma and herb-substitution relations (non-commercial academic use). SitoshnaPred (J Ethnopharmacol 2025 [title only; blocked]): learning phytochemical descriptors to elucidate Ayurvedic potency (cold/hot) => ML from composition to Ayurvedic property already exists at least for potency.
- Lab side [V]: CoSyLab site lists 10+ databases, 50+ publications; team areas include "systems biology of drugs, targets, adverse reactions" and "computational systems biology for drug discovery from medicinal plants"; SpiceRx/DietRx exist. No Ayurveda-FOOD-combination work seen [U].
- NOT found: a computational framework that turns classical FOOD rules (viruddha/anupana/samskara) into falsifiable predictions and back-tests them against measured data. [U: incomplete; ScienceDirect/ResearchGate blocked.]

## 3. Data
- [V] AyurKOSH (academic), IMPPAT-type phytochemical resources [U: not fetched], classical texts digitised (eGangotri, NDLI, archive.org per AyurParam refs), INDB/IFCT/RecipeDB for dishes (DD3), FlavorDB/SpiceRx/DietRx.
- Problems: Ayurvedic property labels are text-derived, sometimes inconsistent across sources; no ground-truth for "incompatibility harm"; experimental in-vitro data for combinations is sparse (a handful of studies). Label reliability is the weak point.

## 4. Candidate technical framings (untested)
 A1 "Falsifiable Ayurveda": encode a small set of classical food-combination rules as machine-readable hypotheses with measurable predicted variables (e.g., anupana X raises bioaccessible Fe/Zn/Ca of pulse Y; fermentation/soaking lowers phytate:mineral ratio; ghee/fat raises carotenoid/curcuminoid uptake), run them through the DD3 dish/bioavailability engine, and score agreement with published in-vitro/human data. Output: which rules are supported, contradicted, or untestable, with evidence links. Directly answers "can we test Ayurvedic food wisdom?" with method, not belief.
 A2 Schedule-A provenance alignment: NLP mapping modern recipes/product formulations to classical formulations (Category A/Schedule A) with evidence spans; a compliance aid for food businesses; also flags disease-claim language (Reg. 8).
 A3 Property prediction from composition (rasa/virya): already partially done (SitoshnaPred); low novelty.
 Where AI is necessary: (a) multilingual/Sanskrit-English text mining to extract rules and entity normalisation (AyurParam-class small models are ~41% on benchmarks, so extraction must be human-in-the-loop with citations), (b) mapping rules to measurable variables, (c) uncertainty-aware scoring. The verdicts remain deterministic/evidence-linked.

## 5. Local-AI justification
- Small/local bilingual model is sensible for Hindi/Sanskrit-English extraction and for offline use in Ayurvedic clinics/kitchens; models like AyurParam-2.9B exist as open small models. Moderate-good, and the "small model + evidence-linked verifier" pattern fits the 2026 trend.

## 6. Validation route
- Rule-level back-test: for each encoded rule, gather >=3 independent measurements/studies; report supported/contradicted/inconclusive; calibration of predicted direction and magnitude.
- Expert review by an Ayurveda scholar (needed; we do not have one) [risk]; inter-annotator agreement on rule encoding.
- Must never present outputs as medical advice or disease claims (Reg. 8 spirit).

## 7. Symposium fit
- High interest (recurring theme), and "we test the tradition with data" is a distinctive, respectful framing. Risk: audience split between sceptics and believers; an overclaim would sink credibility.

## 8. Bio leverage
- High: digestion, bioaccessibility, phytochemistry, microbiome.

## Score (rubric from 06_roadmap)
| Criterion | Max | Score | Note |
|---|---|---|---|
| Real problem + evidence | 25 | 15 | strong interest + compliance need; unmet-need evidence weak |
| Novelty confirmed | 25 | 15 | chatbot/classifier level crowded; falsifiable rule-testing not found but check incomplete |
| Technical originality | 20 | 14 | rules->measurable hypotheses->engine->back-test is a real design; extraction is standard NLP |
| Data + validation feasibility | 15 | 6 | subjective labels; few experimental datasets; needs an Ayurveda expert |
| Symposium / chef relevance | 10 | 8 | |
| Bio leverage | 5 | 4 | |
| TOTAL | 100 | 62 | |
VERDICT: MAYBE as an ANGLE on DD3, not standalone. Best use = "A1 falsifiable Ayurveda" as the evaluation/demo layer of the DD3 engine (anupana/samskara predictions tested against real data). Standalone Ayurveda chatbots/recommenders = KILL (crowded, unsafe, weak validation).
What would raise it: >=10 rules with >=3 published measurements each (feasible for iron/zinc/calcium bioaccessibility, phytate, fat-soluble uptake); an Ayurveda-trained collaborator.
What would kill it: no quantitative literature for enough rules; inability to get expert review; regulatory/claim risk judged too high.

## Tool notes
- batch_search regression AGAIN: query "Bagler IIIT Delhi Ayurveda informatics food Ayurveda computational Ayusla human microbiome" returned "All 3 sources inaccessible" with `[None](None)` entries incl. "Ganesh Bagler - Wikipedia"; same topic via `search` worked. Pattern: person/lab-name queries in batch mode return None-URL sources (seen 3 times now).
- `search` also returned a `[None](None)` result once (3rd item of the Ayusla query).
- cosylab.iiitd.edu.in/index.html -> 404 but cosylab.iiitd.edu.in/ with force_browser=true worked.
