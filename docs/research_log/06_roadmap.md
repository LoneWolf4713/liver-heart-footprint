# 06 Roadmap (written 2026-09-29)

Goal: choose ONE project idea that is (a) a real, current, under-served problem, (b) confirmed novel by an adversarial prior-art check,
(c) technically original (intentional engineering, AI is necessary and grounded, not a wrapper), (d) feasible with data we can actually get, (e) validated in a credible way,
(f) legible and useful to the symposium audience (chefs, food businesses, nutrition/health orgs, the lab).
Standing rules: Stealth Search MCP only; log every step in research_log/; no timing/format talk unless asked; forward-looking (2026+) evidence weighs equal to past evidence.

## Phase 0: Baseline  [DONE]
- 00 method, 01 broad landscape, 02 categories, 03 tool re-test, 04 symposium baseline, 05 forward-looking 2026.
- Output: ranked leads (see below).

## Phase 1: Deep dives (one file each, same protocol)
Order (from file 05): 
- DD1  GLP-1-era Indian food (meal design/whole-plate for users; protein, small volume, GI tolerance, cost, culture)
- DD2  Food-drug interactions (GLP-1 gastric-emptying effects on drug absorption; general food-drug prediction with low labels)
- DD3  Whole-dish health reasoning + cooking transformation of flavor/bioactives
- DD4  Executable recipe representation (quantities, timings, states; robot/smart-kitchen ready)
- DD5  Ayurveda informatics (validation-first framing)
- DD6  Verification of AI-generated recipes (quantities, feasibility, safety)
Protocol for every deep dive (answer all 8, cite sources, mark VERIFIED / UNVERIFIED):
 1. Problem reality: who has it, evidence of need, size, why now (2026).
 2. Prior-art kill-check: papers (2023-2026), products, GitHub, lab (CoSyLab) work. Search "has anyone done X" in 3+ phrasings. Record closest existing work and exactly what it does NOT do.
 3. Data: what exists, licence/access (public vs CoSyLab vs proprietary), size, quality, biases. What we would ask the professor for.
 4. Technical contribution candidates: 2-3 possible novel method framings (BERT-style "new way to frame the problem"), and why each needs AI.
 5. Local-AI justification: is there a genuine reason for small/local models (privacy, offline, latency, cost, India connectivity)?
 6. Validation route: how a claim would be tested without a clinical trial or sensory panel (public benchmarks, chef panel, literature back-testing, simulated ablations).
 7. Symposium fit: would a chef / food business / nutrition org understand and want it? Demo-able?
 8. Bio leverage: does it use our biosciences depth (physiology, biochem, pharmacology)?
Kill criteria (stop a lead immediately if any hit): an existing published/productised solution covers the core; no data path; needs a clinical/sensory study we cannot run; claims cannot be falsified; health-claim risk cannot be contained.
Deliverable per deep dive: `07_DDx_<name>.md` with a 1-paragraph verdict (GO / MAYBE / KILL) and a 0-100 score.

## Phase 2: Concept synthesis
- From surviving leads, write 3-5 concept sheets (`08_concepts.md`): problem, why novel (with the closest prior art), method sketch (tiered small-model + structured knowledge + deterministic verifier where relevant), data, validation plan, local-AI role, demo, risks, what we need from the professor.
- Include at least one CROSS-LEAD concept (e.g., GLP-1 meal design + drug-food safety layer + executable recipe output).

## Phase 3: Red team
For each concept, try to break it:
 a. Novelty attack: fresh searches phrased as a skeptical reviewer; check arXiv/PubMed/Google-Scholar-style hits from 2025-2026 and CoSyLab's newest papers/preprints.
 b. Feasibility attack: data actually obtainable? (test Foodoscope trial tokens / ask professor); compute; ML soundness; leakage/confounding risks.
 c. Overlap attack: does it duplicate the host lab's published or announced work?
 d. Safety/ethics attack: health advice, medication interactions, vulnerable users; how do we frame it (decision support, evidence-linked, no dosing advice).
 e. Symposium attack: could a chef or nutritionist explain back why it matters in one sentence?
Optional de-risk spike: tiny data pull (trial tokens or public data) to confirm the key table can be built.

## Phase 4: Decision
- Score with rubric: Real problem + evidence 25 | Novelty confirmed by red team 25 | Technical originality (intentional engineering, AI necessary) 20 | Data + validation feasibility 15 | Symposium/chef relevance 10 | Bio leverage 5.
- Pick primary + one backup. Present the scoring table and the strongest argument AGAINST the primary.

## Phase 5: Idea write-up (the submission)
- Problem statement, gap (with citations), proposed approach, expected contribution, validation, what we request from the professor (which CoSyLab data/APIs), risks and mitigations.
- Format decided when the user says so.

## Working agreements
- After each deep dive: short report to user (verdict + what surprised me + what would change my mind), then user confirms order/dropping before continuing.
- Any claim from a vendor/blog is marked UNVERIFIED until corroborated.
- Log first, report second.

## Current lead ranking (from file 05; will change as deep dives kill or promote)
1 GLP-1-era Indian food | 2 food-drug interactions (GLP-1 angle) | 3 whole-dish + cooking transformation | 4 executable recipe representation | 5 Ayurveda informatics | 6 verification of AI recipes

## STATUS UPDATE (2026-09-29, after DD1-DD3)
Scores: DD1 GLP-1 Indian food 69 (MAYBE-GO, use case) | DD2 food-drug interactions 59 (MAYBE, component/safety layer) | DD3 whole-dish + cooking/bioavailability 74 (GO, core engine).
Emerging combined direction (hypothesis, to be red-teamed in Phase 3): DD3 engine (process-aware, uncertainty-aware, bioavailability-aware dish model on INDB/IFCT/RecipeDB) + DD1 use case (GLP-1-era Indian meals: small-volume nutrient adequacy, consensus-linked rules, minimal-edit dish repair) + optional DD2 exposure/safety layer.
Remaining deep dives: DD4 executable recipe representation (now partly absorbed by DD3's "dish as process"), DD5 Ayurveda informatics (anupana evidence found in DD3), DD6 verification of AI recipes.

## STATUS UPDATE 2 (2026-09-29, Phase 1 complete)
Scores: DD1 69 (MAYBE-GO, use case) | DD2 59 (MAYBE, safety-layer component) | DD3 74 (GO, core engine) | DD5 62 (MAYBE, "falsifiable Ayurveda" as evaluation angle on DD3) | DD6 53 (KILL standalone; salvage quantity-plausibility prior as component).
DD4 (executable recipe representation) was NOT researched separately: folded into DD3's "dish as process". Known prior art to differentiate from in Phase 3: recipe flow graphs (Kyoto FG corpus), lab's "generative grammar of cooking" (arXiv 2211.09059), ReGraph (2026), FKG.in soundness grammars (Aug 2026), robot-wok recipe programming. GAP: separate DD4 novelty check still owed.
Next: Phase 2 concept synthesis (3-5 concept sheets), then Phase 3 red team.

## RUBRIC TWEAK (2026-09-29, user request): LEGIBILITY MODIFIER
Rationale (user's hackathon experience): audiences/judges often reward what they instantly understand over a more complex but better idea.
Rule: small weight only. Add a legibility modifier of -3..+3 to the 100-pt score (tie-breaker), never overriding science/novelty. Every concept sheet must include: (1) a one-sentence, 10-second pitch a chef or non-expert understands; (2) a concrete demo a viewer can follow in under a minute; (3) "complex engine, simple front" separation.

## CORRECTION (2026-09-29, user feedback): WITHDRAW the legibility modifier; USE "PROFESSOR LENS" instead
- User clarified: the deciding evaluator is PROFESSOR Bagler, not a general audience. "10-second pitch" and "demo" were over-weighted and are NOT criteria now (can be handled later). The earlier "legibility -3..+3" modifier is withdrawn (keep only a very small note: the idea should be easy for the professor to follow).
- Replace "Symposium / chef relevance (10)" with "PROFESSOR FIT (10)": (a) scientific soundness/rigour he would respect; (b) novelty within computational gastronomy; (c) alignment with problems HE has stated as open (Nature 2024 review, Hindu interview, symposium "Future" themes); (d) uses his data/resources (RecipeDB, FlavorDB, DietRx, SpiceRx, Foodoscope) and course concepts (recipe/flavor data, food pairing, culinary fingerprints, copy-mutate evolution, NER); (e) does not duplicate his own ongoing/published work; (f) feasible as a mini-project.
- Phase 2 sheets in 12_phase2_concepts.md must be re-scored with this lens and pitch/demo lines de-emphasised.
- Also clarify: DD1-DD6 = research DIRECTIONS; Phase 2 concepts A-D = project proposals assembled from them. A is the main project; B, C, D are variants/add-ons that depend on A (not four independent projects).
