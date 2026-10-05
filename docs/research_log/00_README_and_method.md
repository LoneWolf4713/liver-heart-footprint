# Research Log: CGAS Mini-Project Idea Search

Goal: find a real-world, unsolved, technically novel food + data science/AI project (team of 2, CS + biosciences)
that is strong enough to be featured at the IIIT-Delhi Symposium on Computational Gastronomy.

Rules agreed with user:
- Use ONLY the Stealth Search MCP tools (mcp__stealth-search__*), not the standard WebSearch.
- Log every step to files in this directory so nothing is lost across a long chat.
- Do not discuss timing or submission format unless the user asks.
- AI must be a genuine design contribution (BERT-style "new way to frame the problem"), not a wrapper around a local LLM.
- No scale limits. Aim for excellence.

File index:
- 00_README_and_method.md   (this file)
- 01_broad_landscape.md     (raw findings from the broad sweep, with sources)
- 02_categories_overview.md (the category list, filled in after the sweep)

Tool notes:
- Stealth Search queries must be run SEQUENTIALLY (tool says so).
- [OUTDATED, fixed 2026-09-29] iiitd.ac.in SSL error; gastrosym pages now fetch fine.
- ResearchGate/ScienceDirect still blocked (login/bot check); use arXiv, PMC, Europe PMC (REST API works), search snippets. PubMed needs cookies (blocked). batch_search sometimes returns [None](None) sources on person/lab-name queries; rerun via `search`.

## File index update (2026-09-29)
- 03_tool_retest_after_fix.md  (tool retests; root causes; all fixed after /mcp reconnect)
- 04_symposium_baseline.md     (GastroSym 2023-2025 pages, Foodoscope, lab stated open problems)
- 05_forward_looking_2026.md   (AI landscape 2026, GLP-1 wave, FSSAI, Ayurveda, robotics)
- 06_roadmap.md                (phases, protocol, rubric, status updates)
- 07_DD1_glp1_indian_food.md   (69)
- 08_DD2_food_drug_interactions.md (59)
- 09_DD3_whole_dish_cooking_bioavailability.md (74)
- 10_DD5_ayurveda_informatics.md (62)
- 11_DD6_verifying_ai_recipes.md (53)

## File index update (2026-09-29, session 2)
- 15_phase1b_targeted_checks.md (data access, what students build, prior art)
- 16_phase2_menu_v3.md (packages; user feedback)
- 17_phase2_demand_pull_ideas.md (Red Hexagon etc.; user feedback)
- 18_phase2_pass3_problems_to_solve.md (Menu Truth etc.)
- 19_phase3_red_team.md (shortlist red team; REJECTED; ground-truth re-evaluation)
- 20_idea_round_data_gated.md (Kitchen Doctor, Hazard fingerprint, Complaint physics = fallback pool)
- 21_india_problems_and_reel_idea.md (India evidence; reel idea; legality; existing apps)
- 22_liver_footprint_concept.md (SELECTED project; grounding numbers; website dry-run; loopholes; test plan)
- 23_MASTER_SUMMARY_v2.md (Executive overview of project selection, grounding evidence, and handoff state)
- 24_HANDOFF_INSTRUCTIONS.md (Complete test protocol T1–T7, constraints, rules, and methodology)
- 25_TEST_REPORT.md (Final empirical feasibility report: T1–T7 data, verified numbers, updated L1–L13, verdict: GO-WITH-CHANGES)
- data/ (Raw CSV and JSON artifacts for tests T1–T7, including safefood 2015, CoFID 2021, INDB, FlavorDB)
- 26_AUDIT_of_test_report.md (main-session audit of 25: what holds, what is invalid/misreported, redo list)
- 27_PROJECT_OVERVIEW_final.md (final project explanation: idea, features, RQs, data have/need, gaps, build order; verdict PROCEED)
- 28_frying_data_and_swap_research.md (>100 lab-measured fried-food fat points; same dish varies 3-5x; food pairing != substitutability; swap engine design)
- 29_DRYRUN_HANDOFF_INSTRUCTIONS.md (instructions for a fresh session: dry-run D1-D8 + independent VERIFY, integrity protocol, parallel subagents)
- 30_DRYRUN_REPORT.md (Complete empirical feasibility report across components D1–D8, built by build_report.py from machine-generated results.json files with 41/41 metrics independently verified)
- dryrun/ (Per-test directories containing code, raw CSVs, exclusions.csv, notes.md, and results.json for D1_link_reader, D2_normaliser, D3_mapping, D4_frying, D5_end_to_end, D6_swaps, D7_baselines, D8_research_questions, and VERIFY)
- 31_AUDIT_of_dryrun_report.md (audit: D5b, D6b/c, D8b hardcoded/synthetic; D8c invalid; narrative contradicts CSV; D1-D3 genuine; D4 LOSO 53.7% fail)
- 32_ALL_PROJECTS_ANALYSIS.md (overview of selected project + every idea considered, scores, fit vs criteria)
- LIVER_FOOTPRINT_PROJECT.md (single complete project document: problem, features, frying model, swaps, data, verification, limits, build order, history)
- submission/FORM_FIELDS.md + submission/PROPOSAL.md (Google Form answers; professor-facing proposal for PDF; deadline 1 Oct 2026 11:59 pm; 2-student group -> 5 deliverables)
- 33_heart_and_chatbot_extension.md (CVD evidence; cardiometabolic footprint; grounded chatbot design)
- (2026-09-30) FORM_FIELDS, PROPOSAL, LIVER_FOOTPRINT_PROJECT updated with Heart profile + grounded assistant; title now 'Liver and Heart Footprint of Indian Recipes'
- 34_VALIDATION_HANDOFF.md (strict single-check handoff: ingredient-sum vs lab-measured cooked dishes; result -> 35_VALIDATION_RESULT.md)
- 36_AUDIT_of_validation.md (validation result invalid: parsing/mapping bugs; claim still untested)
- 37_VALIDATION_HANDOFF_v2.md (robust validation handoff: careful parsing + sanity tests, INDB-only mapping, dry-matter and %energy metrics; result -> 38_VALIDATION_RESULT_v2.md)
- 39_AUDIT_of_validation_v2.md (v2 validation credible; ballpark OK on average, wide per-dish spread; takeaway richer; app should present per-recipe ranges)
- (2026-10-01) FORM_FIELDS, PROPOSAL, LIVER_FOOTPRINT_PROJECT updated: sodium/trans-fat data handling, per-recipe ranges + setting, validation v2 result, caveats context
- 40_BUILD_METHOD_RED_TEAM.md: red team of building with session-architect/builder; checks run; 13 failure points + fixes
- 41_IFCT_TRANSCRIPTION_CHECK.md: public IFCT 2017 transcription reproduces INDB for 982/982 dishes; oils energy=0 defect; decision to use it
- 42_PHASE1_BUILD_PACKAGE.md: Phase 1 builder package (spec, cited tables, 160 gold lines, 10 tests, reference impl check, 9 mutations caught)
- 43_ASSUMPTIONS_AND_LIMITATIONS.md, 44_ASSUMPTION_RESEARCH_RESULTS.md (+ research_dairy/oils/measures_2026-10-05.md raw agent notes): assumptions log and research results
- 45_USER_DECISIONS_INDIAN_DEFAULTS.md: Indian product defaults applied (toned milk, Amul dahi/paneer/butter/cream, malai, IFCT ghee, UK chicken, NIN teaspoons)
