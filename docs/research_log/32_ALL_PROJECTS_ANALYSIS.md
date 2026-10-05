# 32 Complete analysis: the selected project + every project considered (2026-09-30)

## A. Selection criteria (accumulated from the user over both sessions)
1. Real, CURRENT problem Indians actually face (India-specific; evidence of demand).
2. Rare among classmates (they build chatbots/recommenders/meal planners/allergen apps on the lab APIs).
3. Mini-project scale: no fieldwork, no lab work, data we can get.
4. DATA GATE: ground-truth/validation data verified before scoring.
5. Genuinely scientific / AI used intentionally (not rule-application, not an LLM wrapper).
6. Clearly COMPUTATIONAL GASTRONOMY (recipes, flavour, nutrition, health, cuisine patterns).
7. Judge = Prof. Bagler: builds on his course/data, does not duplicate his lab.
8. Symposium feature = upside, grade (20%) first.

## B. Scoring rubric used (my judgement; provisional, not measurements)
100 points: Real problem + evidence 25 | Novelty 25 | Technical originality 20 | Data + validation feasibility 15 | Symposium/chef relevance 10 (later replaced by PROFESSOR FIT 10) | Bio leverage 5. Only rounds 1, 2 and the red team were scored numerically; later rounds were judged qualitatively against the criteria above.

## C. THE SELECTED PROJECT: "Liver footprint of Indian recipes"
Idea: paste an Indian recipe link -> the app reads ingredients and quantities, converts to grams, maps to Indian nutrition data (INDB/IFCT), adds a frying-oil model for fried items, and shows per serving how much of the day's liver-relevant budgets (saturated fat, added sugar, refined carbs, energy, salt) the dish uses, against what the average person in your region already eats; explains why; suggests authentic lighter versions (author-stated swaps, "cook like the lightest 25% of real recipes", food-pairing fit check). Research side: liver footprint of Indian cuisine, textbook vs web recipes, hidden load of street food, load-vs-authenticity trade-off.
Why it won: fatty liver 38.9% of Indian adults (Phenome India 2026); drivers known (SFA, sugar, refined carbs, fried food); average Indian already over SFA/sugar limits (ICMR-INDIAB 2025); existing liver apps are Western; mirrors the lab's carbon-footprint-of-recipes work (strong CG + professor fit); no fieldwork; data open or obtainable.
Evidence status: link reader, parsing (~80%; ~95% on fat/sugar lines), INDB mapping (~97%) proven on real data; 61 verified lab values for fried Indian foods; remaining accuracy questions (frying ranges, ingredient-sum vs measured cooked fat, swap rule) to be tested during build. Verdict: BUILDABLE -> submit.
Origin: the user's own observation (Instagram masala recipes + fatty liver); premise corrected (spices are not the culprit; oil/fat/sugar/maida/frying are).

## D. Every project considered, by round
### Round 1 - Deep dives (session 1; scored /100)
| # | Direction | Score | Verdict | Why |
|---|---|---|---|---|
| DD1 | GLP-1-era Indian food (meal design for GLP-1 drug users) | 69 | Maybe | Real (Indian consensus 2026) but HealthifyRx/Sugarfit sell programmes; medical-adjacent; trend-driven |
| DD2 | Food-drug interactions (GLP-1 angle) | 59 | Component only | GLP-1 interactions mostly insignificant; label-poor; safety risk |
| DD3 | Whole-dish cooking + bioavailability engine | 74 | Best then | Real gap (lab + INDB ignore cooking) but later found cooked ground truth is scarce |
| DD4 | Executable recipe representation | - | Folded into DD3 | - |
| DD5 | Ayurveda informatics ("falsifiable Ayurveda") | 62 | Angle only | Chatbots crowded/weak; needs expert; pseudoscience optics |
| DD6 | Verifying AI-generated recipes | 53 | Killed | Crowded (FKG.in soundness, FoodGuardBench, Fudan, Springer 2026) |

### Round 2 - Phase 2 concepts (session 1; scored, superseded)
| Concept | Score | Outcome |
|---|---|---|
| A process-aware "what your dish actually delivers" nutrition engine | 79 (77 +2 legibility) | Forced as single pick; user rejected the format |
| B GLP-1 portion menu for kitchens | 68 | Skin of A |
| C "Test the Tradition" (falsifiable Ayurveda rules) | 62 | Evaluation layer |
| D Warfarin-steady thali (vitamin K exposure) | 60 | Safety demo |
Then a 13-item menu P1-P13 (pairing robustness audit, absorption pairing, error-budget audit, Yield Kitchen measurements, Pareto recipes, nutrition copy-mutate, minimal-edit repair, GLP-1 atlas, cooking-effects atlas, kitchen parser benchmark, protein-turn trend, Test the Tradition, warfarin thali) - unscored; session crashed before selection.

### Round 3 - Phase 2 packages (session 2; qualitative)
| Package | Fit | Outcome |
|---|---|---|
| 1 Iron-smart kitchens (do Indian recipes pair iron with absorption enhancers?) | Novel, scientific, course-native | User liked; rejected as main because "nobody is asking" + null-result risk; kept as grade-safe fallback (S2) |
| 2 Pairing Audit (why Indian pairing sign flips 2015 vs 2018) | Low risk, professor's own open question | Low real-world relevance |
| 3 Real menu audit (mess / PM POSHAN) | Most real-world | Rejected: fieldwork |
| 4 Nutrition-driven copy-mutate | Professor fit | Abstract, hard to validate |

### Round 4 - What India is asking (demand-pull)
| Idea | Outcome |
|---|---|
| N1 Red Hexagon (FSSAI front-of-pack warning labels impact; SC case 2026) | Good demand, but rule/threshold application ("a classifier"); thresholds not final |
| N2 Healthy Thali Index (monthly cost of a healthy thali) | Passive question, solves nothing |
| N3 Protein-washing audit | Merged into N1 |

### Round 5 - Problems we can solve
| Idea | Outcome |
|---|---|
| R1 Menu Truth (are restaurant/app calorie & allergen labels physically plausible?) | Strong demand (FSSAI Reg 2.4.6; Zomato AI values) -> red-teamed as S3 |
| R2 Iron-smart v2 (engine-first) | -> S2 |
| R3 Tomato-shock substitution | Later rejected: unverifiable |
| R4 Recipe scaling laws for catering | Data locked in paid textbooks |
| R5 Which dishes survive delivery | Weak science, attribution noise |

### Round 6 - Red team of shortlist (scored /100, professor-fit rubric)
| Shortlist | Score | Final verdict |
|---|---|---|
| S1 Red Hexagon | 69 | Out: rule-based |
| S2 Iron-smart v2 | 66 | Grade-safe fallback only |
| S3 Menu Truth | 75 -> KILLED | No cooked-dish ground truth for Indian food; app data has no standing; chain labels are calculated (circular) |
Lesson: data gate introduced.

### Round 7 - Data-gated ideas (all passed the data gate; not India-specific)
| Idea | Data | Outcome |
|---|---|---|
| I1 Kitchen Doctor (why recipes fail, which fixes work) | Food.com 700k reviews | Good; fallback pool |
| I2 Hazard fingerprint (cuisine processes vs food-safety violations) | NYC 295k violations | Good; fallback pool |
| I3 Complaint physics (which dishes disappoint diners) | Yelp | Fallback pool; prior art unchecked |
| I4 Tomato at Rs 100 | held-out recipes | Rejected: unverifiable |
| Allergens from dish names | - | Dropped: done 2025-26 |

### Round 8 - India problems
| Idea | Outcome |
|---|---|
| User's reel/masala/fatty-liver idea | Refined -> SELECTED project (Section C) |
| India Adulteration Atlas (news + Parliament data on food fraud) | Solid second; media-bias risk |
| Pesticide exposure through Indian cooking | Same ground-truth trap as S3 |

## E. How each fits the criteria (summary)
| Project | India problem | Rare | No fieldwork | Data gate | Scientific | CG fit | Prof fit |
|---|---|---|---|---|---|---|---|
| SELECTED Liver footprint | Yes (MASLD 38.9%) | Yes | Yes | Yes | Yes (frying model, cuisine study) | Strong | Strong |
| Iron-smart (S2) | Anaemia, weak demand | Yes | Yes | Yes | Yes | Strong | Strong |
| Red Hexagon (S1) | Yes | Yes | Yes | Yes | Weak | Medium | Medium |
| Menu Truth (S3) | Yes | Yes | Yes | NO | Yes | Medium | Medium |
| Kitchen Doctor (I1) | No (US data) | Yes | Yes | Yes | Yes | Good | Medium |
| Hazard fingerprint (I2) | No (US data) | Yes | Yes | Yes | Yes | Medium | Medium |
| Adulteration Atlas | Yes | Yes | Yes | Partial (media bias) | Medium | Medium | Medium |
| GLP-1 food (DD1) | Yes | No (products exist) | Yes | Partial | Medium | Medium | Medium |
| Pairing Audit | No | Medium | Yes | Yes | Yes | Strong | Strong (sensitive) |
| Real menu audit | Yes | Medium | NO | - | Medium | Medium | Medium |
