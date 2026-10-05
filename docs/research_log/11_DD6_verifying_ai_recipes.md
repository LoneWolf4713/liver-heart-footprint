# 11 Deep Dive 6: Verification of AI-generated recipes (2026-09-29)
Legend: [V] verified from source read | [S] secondary | [B] blog | [U] unverified / inference

## 1. Problem reality
- [V] Springer LNNS 1864 (AITA 2025; Shaw, Wasala, Punjj, 2026) "Improving LLMs for Recipe Generation via Reinforcement Learning Fine-Tuning": LLM recipes show incorrect ingredient quantities, poor texture and flavour issues (thematic analysis of YouTube cooking-channel comments + ingredient-scaling experiments). DPO fine-tuning gave only "modest gains (8-15% across evaluation metrics)". Authors call for "multi-agent systems for validating ingredient proportions, hybrid models combining structured culinary knowledge with LLMs, and targeted pretraining on verified datasets".
- [V] FoodGuardBench (arXiv 2604.01444, Apr 2026; UC Davis/USC/JHU/UGA/Rutgers): 3,339 queries from FDA guidance, 356 seed policies; LLMs and guardrails lack food-safety alignment: attack success 56.22% with two jailbreaks, Mistral-Small-4 67.58%; highest-risk categories pest control (avg ASR 64.81%), storage, hygiene, temperature control (>50%); they release FoodGuard-4B, a small specialised guardrail. This targets ADVERSARIAL misuse, not everyday benign recipe correctness.
- [V] Lab's own evaluation (Bagler & Goel 2024): Turing Test for Chef, 24 chefs, 1,472 recipes, F1 69.88%; next step = sensory panels; models "have much to improve upon in capturing subtle culinary nuances".
- [V] Small-model study (arXiv 2502.02028, Feb 2025): "traditional NLP metrics alone are insufficient" for recipe generation; used ad-hoc metrics (ingredient coverage, temperature/time specification, consistency, practicality); larger model not always better (SmolLM 360M ~ 1.7B). LLaVA-Chef (2024) lists "consider numeric information in evaluating generated recipes" as future work.
- [V] Fudan (arXiv 2602.15862, Feb 2026): MLLM recipe generation from images yields "semantically incorrect actions or ingredients despite high lexical scores (BLEU/ROUGE)"; proposes predict-then-validate action/ingredient framework (SFT + reinforcement fine-tuning + Semantic Confidence Scoring and Rectification).
- VERDICT on problem: real and documented (quantities, safety, semantic errors); but the field is moving fast and several groups are already targeting it.

## 2. Prior-art kill-check
- [V] "Validating FKG.in: Soundness Assessment in LLM-Augmented Indian Food Knowledge Graphs" (arXiv 2608.29249, Aug 2026): semi-automated soundness workflow for LLM-extracted/augmented recipe data, evaluated on Indian recipes; failure modes = structural inconsistency, semantic/logical incoherence, deviation from source; methods = formal grammars, vocabulary checks, statistical heuristics, SET TRANSFORMER coherence modelling, retrieval-based verification. => Indian-recipe soundness verification is already covered at the KG-construction level (Aug 2026). Also confirms FKG.in (Indian food KG) is active.
- [V] Proportion validation remains "future work" per the Springer authors; numeric/physical plausibility (mass balance, cooking chemistry, ratio priors) not addressed by FKG.in's described checks [U; only abstract-level read].
- [V] Food-safety guardrail model already exists (FoodGuard-4B).
- [B] Student/vendor projects: ChefAI India (JSETMS), "Culinary Class Wars: evaluating LLMs using ASH in cuisine transfer" (ResearchGate, blocked). 
- Lab overlap: Ratatouille, Turing Test, Foodoscope "Chef Co-Pilot" (2023-2025 symposium listings) -> the lab owns generation + human evaluation and is commercialising a chef assistant; a standalone "AI recipe checker" would compete with, not complement, their agenda.

## 3. Data
- RecipeDB (118k, quantities+processes), INDB (1,014 Indian recipes with grams), FKG.in [U: access], Recipe1M/RecipeNLG, FoodGuardBench [V public per paper]. Ratio priors (oil per serving, water:dal, salt %, spice mass) computable from RecipeDB/INDB.

## 4. Candidate framings
 K1 Quantity-plausibility prior: learn distributions of ingredient ratios per dish family (from RecipeDB/INDB) and flag/repair implausible quantities; compose with mass-balance (water/oil/yield) checks.
 K2 Executable-recipe verifier (units, temps/times, sequence feasibility) using formal grammar + learned ratios; compare against LLM outputs.
 K3 Use K1 as the "authenticity/plausibility prior" inside DD1's dish-repair and DD3's process engine (reuse, not standalone).
- Honest: K1/K2 alone are incremental relative to FKG.in soundness (Aug 2026), Fudan (Feb 2026), Springer DPO (2026).

## 5. Local-AI justification
- Small local verifier (Set Transformer / grammar) is natural, but FoodGuard-4B and FKG.in already occupy "small model as checker".

## 6. Validation route
- Blind chef panel on real vs LLM vs repaired recipes (mirrors lab's Turing Test); numeric error vs held-out measured quantities; ablations.

## 7. Symposium fit
- Moderate: "Can AI generate tasty recipes?" is the symposium's flagship question, but it is the lab's own territory; a student verifier looks derivative unless tied to something new.

## 8. Bio leverage
- Low.

## Score (rubric from 06_roadmap)
| Criterion | Max | Score | Note |
|---|---|---|---|
| Real problem + evidence | 25 | 17 | documented failures; adversarial-safety vs benign-correctness distinction |
| Novelty confirmed | 25 | 9 | FKG.in soundness (Aug 2026), Fudan (Feb 2026), FoodGuardBench (Apr 2026), Springer (2026) all overlap |
| Technical originality | 20 | 11 | incremental unless combined with process/nutrient state |
| Data + validation feasibility | 15 | 9 | RecipeDB/INDB + chef panel feasible |
| Symposium / chef relevance | 10 | 6 | lab's home turf |
| Bio leverage | 5 | 1 | |
| TOTAL | 100 | 53 | |
VERDICT: KILL as a standalone project. SALVAGE K1 (quantity/proportion plausibility prior) as a COMPONENT feeding DD1 (authenticity constraint for dish repair) and DD3 (mass-balance sanity checks). 
What would change this: a confirmed gap in numeric/physical plausibility checking not covered by FKG.in.

## Tool notes
- Springer chapter page and PDF both returned clean abstracts via batch_search; arXiv HTML/PDF fine.
- ResearchGate blocked (Culinary Class Wars); jsetms.com "content empty or protected".
