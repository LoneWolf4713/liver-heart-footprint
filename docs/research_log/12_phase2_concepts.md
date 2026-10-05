# 12 Phase 2: Concept synthesis (2026-09-29)
Status: PROVISIONAL, written BEFORE the Phase 3 red team. Scores are estimates from DD1-DD6 evidence and can drop after fresh novelty attacks.
Legend as before: [V] verified in a source read | [U] unverified/inference. Legibility modifier (-3..+3) is a small tie-breaker per the 06_roadmap tweak.
Shared design principle (2026 trend, file 05): small local model for parsing/extraction + structured knowledge + DETERMINISTIC verifier (LLM never sets nutrient values or safety verdicts) + honest uncertainty.

---
## CONCEPT A (PRIMARY): "What your dish actually delivers" - a process-aware, uncertainty-aware nutrition engine for Indian food
**10-second pitch:** Nutrition labels add up raw ingredients; real Indian cooking (soaking, fermenting, tempering, pressure-cooking, curd/lemon, chai timing) changes what your body actually gets. We built an open engine that shows it, with confidence bands.
**Demo (<1 min):** pick a dish (e.g., dal tadka + rice); toggle cooking choices (soak / pressure-cook / add lemon / add curd / chai with the meal) and watch predicted cooked nutrients AND absorbable iron, zinc, calcium and protein change, with uncertainty ranges and the evidence behind each step. Optional GLP-1 lens: "does this small portion meet the consensus targets, and what is the smallest change that fixes it?"
**Problem (real):** the lab's own recipe-nutrition method sums raw USDA values, admits cooking yield is ignored, validates only calories (36 kcal/serving error) and lacks Indian ingredients [V, Kalra 2020]; INDB (1,014 Indian recipes) models cooking only as a sensitivity analysis with one USDA factor per food matched for 42.6% of ingredients and no yield correction [V, PMC11277795]. India's micronutrient gaps: vit D 61%, iron 54%, B12 53% [V]. Lab states health must be judged "for the complete dish" [V].
**Novelty vs closest prior art:** USDA retention tables (US, 2007), INDB (raw sum + partial retention), Hallberg/Armah iron-absorption algorithms (generic, meal-level, full text not read [U]), Phenol-Explorer retention/PK tables. Gap: an OPEN, process-aware, probabilistic engine covering Indian preparations and combinations, end to end from recipe text to bioavailable nutrients [U: checks partly blocked].
**Method (intentional engineering):**
 1. Parse free-text recipes into a "dish program": ingredients with quantities -> unit operations (soak, ferment, sprout, boil, pressure-cook, temper in fat, fry, combine with acid/dairy). Small local model does parsing; grammar/units checks keep it honest.
 2. Mass-balance + nutrient-state propagation with distributions for yield, retention and leaching (not point values).
 3. Bioavailability layer: phytate:mineral molar ratios (Phy:Zn<15, Phy:Fe<1), enhancers/inhibitors (acid, vitamin C, tannins in tea, fat for carotenoids), protein digestibility/limiting amino acids for dal+cereal mixes.
 4. Hybrid calibration: a small learned residual fitted to ~100-300 literature measurements of cooked vs raw and in-vitro digestion results; report calibrated intervals and an "which measurement would reduce uncertainty most" list.
 5. Quantity-plausibility prior (from DD6): ratio distributions per dish family from RecipeDB/INDB flag implausible inputs and act as the authenticity constraint for repair suggestions.
**Data:** IFCT 2017 (528 foods x 151 components, open) [V]; INDB (open, code on GitHub) [V]; RecipeDB Indian subset via professor [V]; Phenol-Explorer + USDA retention [V]; curated literature set for calibration/back-test (we build it) [U].
**Validation (no wet lab):** back-test predicted cooked/raw ratios vs curated measurements (MAE + interval coverage); baselines = INDB raw sum, INDB+USDA retention, lab's USDA-SR summation; direction/magnitude check vs published in-vitro results (e.g., buttermilk + green gram) [V exists]; blind dietitian/chef review of 20-30 dish audits; ablations (with/without bioavailability, with/without prior).
**Local-AI role:** offline recipe parsing incl. regional/Hinglish phrasing in kitchens and clinics; tiered routing (small model default). Moderate but real.
**Symposium fit / who cares:** chefs (tadka, fermentation, dal+curd are their craft), nutrition orgs (deficiency burden), lab (extends their estimator; natural collaboration hook, but overlap risk).
**Scope tiers:** MVP = ~30 staple dishes, cooked-vs-raw + bioavailability with uncertainty, back-test on curated data. Stretch = GLP-1 lens + minimal-edit repair (DD1 F2/F4). Moonshot = Ayurveda rule tests (Concept C) and exposure layer (Concept D).
**Risks:** cooked ground truth is scattered; no wet lab; CoSyLab may already be extending their estimator [U]; technical originality is integration + uncertainty, not a new learning paradigm; bioavailability numbers must be shown as estimates.
**Provisional score:** Real problem 22 | Novelty 17 | Tech originality 16 | Data/validation 9 | Symposium 8 | Bio 5 = **77**; legibility **+2** ("what your body actually gets from your dal" is instantly graspable) => **79**.

---
## CONCEPT B: GLP-1 portion menu tool for Indian kitchens and restaurants (chef-facing skin of A)
**10-second pitch:** Make your existing menu GLP-1-friendly without changing what the dish is.
**Demo:** a chef enters a dish; the tool shows protein and fat load per small portion, plate volume, GI-tolerance flags by dose phase, and the smallest tweak (ratio, technique, side) that meets consensus-linked targets, with the evidence level of each rule.
**Problem:** GLP-1 users eat less (about half report fewer calories; ~60% dine out less) [S, CNBC/EY-Parthenon 2026]; Indian consensus stresses small frequent meals, protein 20-30% of energy, mixed fibre, fat quality [V]; no chef-facing Indian tool found [U]. Consumer coaching exists (HealthifyRx, Sugarfit) [B/S].
**Novelty:** medium. Depends on Concept A's engine; differentiation = chef-facing, dish-preserving edits, transparent evidence-linked rules.
**Method:** A's engine (lite) + rule engine from consensus statements S1-S34 with evidence levels + minimal-edit search under the DD6 plausibility prior.
**Validation:** rule back-test table; chef panel "still recognisably this dish? would you serve it?"; dietitian review.
**Risks:** medical-adjacent (must be decision support, no dosing advice; CKD/elderly protein caveats); Abbott-funded consensus is formula-leaning (show evidence levels, food-first stance); commercial competitors.
**Provisional score:** 20 | 13 | 11 | 8 | 9 | 4 = **65**; legibility **+3** => **68**.

---
## CONCEPT C: "Test the Tradition" - falsifiable Ayurvedic food rules
**10-second pitch:** Instead of believing or dismissing Ayurvedic food rules, we turn them into measurable predictions and check them against real data.
**Demo:** a scorecard of ~10 rules (e.g., "buttermilk improves mineral uptake from pulses", "fermentation/soaking makes cereals more absorbable", "ghee aids uptake of fat-soluble compounds") with verdicts: supported / contradicted / untestable, each with citations and confidence.
**Problem:** Ayurveda informatics recurs on all symposium pages [V]; classical claims are unstructured/untested; FSSAI Ayurveda Aahara rules bar disease claims [V].
**Novelty:** chatbot/classifier level is crowded and weak (AyurParam ~41% on its benchmark) [V]; falsifiable rule-testing with an engine not found [U, check incomplete].
**Method:** rule extraction (human-in-the-loop, small bilingual model) -> map to measurable variables -> run through Concept A's engine -> compare with >=3 published measurements per rule.
**Validation:** agreement with literature; expert review (we need an Ayurveda scholar).
**Risks:** pseudoscience optics, subjective labels, sparse data, expert dependency.
**Provisional score:** 15 | 15 | 14 | 6 | 8 | 4 = **62**; legibility **0** (intriguing but polarising) => **62**.
**Best use:** the evaluation/demo layer of A, not standalone.

---
## CONCEPT D: Warfarin-steady Indian thali planner (exposure-aware food-drug safety, narrow)
**10-second pitch:** For people on warfarin, consistency matters; we compute daily vitamin K exposure from real Indian meals and flag swings.
**Demo:** plan a week of dal, sabzi (palak, methi, sarson), roti; see vitamin K1 per day, variance, and a "steady" score with sourced advice.
**Problem:** guidance is consistency, not avoidance; vit K1 varies ~3x for the same vegetable across sources [V]; no Indian computational tool found [U].
**Data:** INDB has vitamin K1/K2 [V]; variability from literature.
**Method:** dose/dish-level exposure model + uncertainty; deterministic rules; low ML.
**Risks:** safety-critical (false negatives), thin validation, ML contribution modest, clinical framing.
**Provisional score:** 16 | 13 | 13 | 6 | 5 | 5 = **58**; legibility **+2** => **60**.
**Best use:** an optional "safety layer" demo inside A, not standalone.

---
## Summary table (provisional, pre-red-team)
| Concept | Score | Legibility | Adjusted | Role |
|---|---|---|---|---|
| A: process-aware dish engine | 77 | +2 | 79 | PRIMARY |
| B: GLP-1 portion menu (chef skin) | 65 | +3 | 68 | Use-case skin of A |
| C: Test the Tradition | 62 | 0 | 62 | Evaluation layer of A |
| D: Warfarin-steady thali | 58 | +2 | 60 | Optional safety demo |
Recommended packaging: ONE project (A) with a simple front (B's chef demo or the "absorbable nutrients" meter), C as a credibility/evaluation section, D as a small safety showcase. Complex engine, simple story.

## What Phase 3 (red team) must attack
1. Novelty: fresh skeptic-style searches for process-aware/bioavailability-aware Indian dish engines, recipe-to-cooked-nutrient pipelines, cooking-aware nutrition estimators (2024-2026); CoSyLab preprints; INDB follow-ups; DD4 (recipe-as-program) prior art (flow graphs, generative grammar of cooking, FKG.in grammars).
2. Feasibility: can we curate enough cooked-vs-raw Indian measurements? Can we get RecipeDB quantities/processes from the professor? Is the meal-level iron absorption algorithm implementable/validated?
3. Overlap: is CoSyLab or Foodoscope doing GLP-1/cooking-aware nutrition?
4. Safety/ethics framing: decision support, no dosing/medical advice, disclosures on industry-funded consensus.
5. Symposium legibility: can a chef repeat the pitch in one sentence?
EOF
echo ok