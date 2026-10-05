# 16 Phase 2 (v3): project packages (2026-09-29, new session)
Supersedes 12 and 13. Built on Phase 1 + checks in 15.
Criteria (user-confirmed): rare among classmates but not exotic; mini-project scale; relevant NOW; >=3-4 deliverables (combos OK); grade-first, symposium upside; judge = professor.
Differentiation lane (from 15): classmates/hackathon teams build APPS on lab APIs; we answer a REAL question with the COURSE's own null-model science on open data, then ship one usable artefact.

Extra facts verified this step:
- NFHS-5 (2019-21): anaemia 57.0% women 15-49, 67.1% children 6-59 mo, 25.0% men; rose from NFHS-4 (53% women). Programmes: Anemia Mukt Bharat, POSHAN 2.0, rice fortification. [V: PMC11969930 meta-analysis; ORF]
- PM POSHAN (school meals): Rs 12,750 Cr FY2026-27; 2021-26 cycle ended 31 Mar 2026, extended to 30 Sep 2026 pending the 2026-31 approval. [S: sarkariyojana, 22 Aug 2026]
- Hostel-mess nutrition audits: search returned nothing (tool gave 0 sources) -> UNVERIFIED either way.

---
## PACKAGE 1: "Iron-smart kitchens": does Indian cooking encode absorption wisdom?
Question: Food pairing asks whether recipes combine ingredients that share FLAVOUR molecules. We ask the same question for ABSORPTION: do recipes put iron/zinc sources together with absorption ENHANCERS (vit C: lemon, amla, tomato; organic acids: tamarind, kokum, curd; fermentation) and away from INHIBITORS (phytate-rich bran, tea/coffee polyphenols, calcium) more than random cuisines would? Is Indian cuisine different from others? Which ingredients drive it?
Why now: anaemia 57% of Indian women and rising (NFHS-5); food-based strategy is policy-relevant (Anemia Mukt Bharat).
Deliverables:
 D1 Open ingredient "absorption annotation" table (~200-400 ingredients: Fe, Zn, Ca, phytate, vit C, polyphenol class, enhancer/inhibitor flag) from INDB/IFCT + FAO PhyFoodComp, with sources. Reusable resource.
 D2 Null-model study (course method): absorption-pairing score per cuisine vs 4 random controls (CulinaryDB 22 regions + INDB Indian), Z-scores, ingredient contribution (chi) analysis. Mirrors Jain 2015 / Singh 2018 exactly, new axis.
 D3 Dish-level estimate for INDB's 1,014 recipes (have gram quantities): Phy:Fe, Phy:Zn molar ratios + vit C per serving -> "absorbability" atlas of Indian dishes (estimates, not measurements).
 D4 Small tool: "iron-smart tweak": for any dish, smallest culinary addition/change (lemon squeeze, amla chutney side, soak/ferment, chai timing) and its estimated effect; ranked, sourced.
Data: CulinaryDB (download), INDB (GitHub), PhyFoodComp (FAO), IFCT via INDB. Burden M (D1 annotation is the main labour; split).
Novelty: no recipe-corpus null-model test of enhancer/inhibitor pairing found [15]. Obviousness LOW.
Professor fit: HIGH (his pairing method + null models + contribution; his slide seed "chemical elements Fe/Ca/Zn food-wise"; "health for the complete dish").
Bio leverage: HIGH (mineral chemistry, absorption physiology).
Risks: result may be null (still publishable: "no evidence recipes encode it"); presence-only for CulinaryDB (no quantities) so D2 is qualitative, D3 quantitative; must avoid health claims; vit C losses in cooking (use literature range as sensitivity).
Kill if: a published recipe-level enhancer/inhibitor null-model study appears in red team.

## PACKAGE 2: "The Pairing Audit": is Indian cuisine contrasting or uniform, and does pairing even matter to eaters?
Question: The lab found Indian pairing strongly NEGATIVE (2015) then POSITIVE (2018). Singh & Bagler themselves list "How robust are the patterns to changes in recipes data and flavor profiles?" as open. Which choices flip the sign? And does pairing score track what people like (ratings)? Turkish 2023 said no for Turkey; untested for India.
Deliverables:
 D1 Reproduction of both published results from public data (PLoS S1-S3; CulinaryDB).
 D2 "Flip map": systematic perturbations (recipe source, aliasing, compound ingredients like garam masala, flavour-profile completeness, null-model type, recipe-size cut) + variance decomposition.
 D3 Independent test on a fresh Indian corpus (reuse Assignment-1 scraping on a new site) + pairing vs user ratings/reviews.
 D4 Open Python library ("cuisine analysis toolkit": size/frequency-rank stats, null models, pairing, contribution). The professor literally lists "a python library for the analysis of cuisine" as a project idea.
Data: all public; Burden S-M. Lowest-risk package.
Novelty: robustness audit not found; ratings angle open for India. Obviousness LOW-MED.
Professor fit: HIGH (answers his own stated open question) but SENSITIVE (examines his contradictory results): frame as robustness, his words.
Real-life relevance: LOWEST of the four (methodological). Ratings part adds some.
Risks: may be seen as "only analysis"; must deliver the library to feel like a product.

## PACKAGE 3: "What's really on the plate": auditing a real institutional menu (mess / school meal)
Question: Take a REAL menu that thousands eat (IIIT-Delhi hostel mess weekly menu, and/or a published state PM POSHAN school-meal menu) and compute per-meal energy, protein quality, iron/zinc AND absorbability (Package 1 engine), compare against ICMR-NIN Dietary Guidelines 2024 / PM POSHAN norms; then find minimal, cost-neutral, cuisine-preserving swaps.
Why now: PM POSHAN 2026-31 renewal pending; anaemia rising; the mess is our own campus.
Deliverables:
 D1 Structured dataset of the menu(s): dishes -> recipes -> grams (from mess staff / standard recipes INDB), cost.
 D2 Audit report: gaps vs guidelines, with uncertainty.
 D3 Swap optimiser: minimal edits (constraint optimisation) keeping cost and dish identity; top-10 actionable swaps.
 D4 One-page dashboard for the mess committee / tool for any institution to upload a menu.
Data: needs the menu + portion sizes (primary data collection, cheap: ask mess/weigh portions) + INDB. Burden M (fieldwork).
Novelty: generic mess/mid-day-meal nutrient audits likely exist [U]; the absorbability layer + swap optimiser is the differentiator. Obviousness MED.
Professor fit: MED-HIGH ("tweak my recipe for better health", "address nutrition deficiencies" are symposium questions).
Real-life relevance: HIGHEST, tangible, local.
Risks: access to real portion data; overlap with dietitians' work; weaker as science alone -> best combined with Package 1.

## PACKAGE 4: "Evolving healthier cuisines": copy-mutate under nutritional selection
Question: The course's copy-mutate model uses abstract fitness. Give fitness a nutritional meaning (protein density / absorbable iron). How far must a cuisine drift to reach a target, and does it keep its "fingerprint" (frequency-rank curve, pairing sign, category mix)?
Deliverables: D1 re-implementation reproducing the lab's world-cuisine results; D2 nutrition-fitness variants; D3 fingerprint-preservation metric + results; D4 interactive simulator.
Data: CulinaryDB/INDB; Burden S-M. Obviousness LOW-MED (a 2020 student did plain copy-mutate).
Professor fit: HIGH (his model). Real-life relevance: LOW (abstract; hard to validate).
Best use: an extension chapter, not the main project.

---
## Comparison
| Pkg | Real-life now | Rare among classmates | Effort | Risk | Prof fit | Bio use | Deliverables |
|---|---|---|---|---|---|---|---|
| 1 Iron-smart kitchens | High | High | Medium | Medium (null result) | High | High | 4 |
| 2 Pairing Audit | Low-Med | Med-High | Low-Med | Low (sensitivity of topic) | High | Low | 4 |
| 3 Real menu audit | Very high | Medium | Medium (fieldwork) | Medium (data access) | Med-High | Med | 4 |
| 4 Nutrition copy-mutate | Low | Med-High | Low-Med | Med (abstract) | High | Low-Med | 4 |

## Sensible combinations
- 1 + 3 = science + application: discover absorption logic in cuisines (1), apply the same engine to a real menu with swaps (3). Shared engine, one story: "from recipes to real plates". 
- 1 + 2 lite = one library powers both the flavour-pairing audit and absorption pairing (method + new axis).
- 1 core only = already 4 deliverables; smallest safe scope.

## My lean (not a forced pick)
Package 1 as core; add Package 3's menu audit as the applied deliverable if we can get the mess menu + portions within a week. Fallback if time is short: Package 1 alone. Safest-for-grade alternative: Package 2.
Reason: 1 is the only option that scores high on all of real-life relevance, rarity, professor fit and bio leverage at medium effort; its failure mode (null result) still yields a valid finding.

## USER FEEDBACK on v3 (2026-09-29)
- Likes Package 1 (novel) BUT: a possible "no" answer risks a trivial-looking result; and more importantly it is "unexplored but nobody is looking for it" = no real-world DEMAND. It answers a question the world is not asking.
- Package 3 liked but REJECTED: needs fieldwork; no time. Rule added: NO FIELDWORK.
- New ask: more ideas that are (a) unexplored, (b) answer a SPECIFIC question the world/India is ACTUALLY asking now (demand-pull), (c) mini-project scale, no fieldwork. Broad searches allowed (Stealth Search only).
