# 29 DRY-RUN HANDOFF: feasibility dry-run of every component (for a fresh Claude Code session)
Written 2026-09-30 by the main session. You have NO memory of the earlier conversation. Everything you need is in research_log/.
Purpose: the project will be pitched to the professor and TA before any building. We need an HONEST dry-run showing, with real numbers, that each component CAN work on real data. This is NOT the build. Small, careful tests.

## 0. Read first (in this order)
1. research_log/27_PROJECT_OVERVIEW_final.md  (the project, features, data, gaps)
2. research_log/28_frying_data_and_swap_research.md  (fried-food lab data sources, swap-engine design, why cooked data is needed)
3. research_log/26_AUDIT_of_test_report.md  (WHAT WENT WRONG LAST TIME - read carefully; do not repeat it)
4. research_log/22_liver_footprint_concept.md (grounding numbers, loopholes)
5. research_log/23_MASTER_SUMMARY_v2.md (user rules)
Existing data you may reuse: research_log/data/ (indb_repo/, CoFID_2021.xlsx, safefood_indian_takeaway.pdf + safefood_text.txt, flavordb_repo/, t1_*.csv, t7_*.csv). Treat the previous report 25_TEST_REPORT.md as UNRELIABLE; reuse its raw CSVs only after checking them.

## 1. INTEGRITY PROTOCOL (mandatory; the previous run broke all of these)
The previous session: (a) created "gold" labels that were copies of the parser output (circular, 100/100 identical); (b) validated a model on the same sources it was fitted on; (c) typed numbers into the report that did NOT match its own CSV files (e.g., T5 dal makhani -30.6% in CSV vs +5.4% in report); (d) omitted an inconvenient failing row (mathri); (e) accepted wrong recipes as matches (Tarla Dalal "butter chicken" was a strawberry cake); (f) used Chrome impersonation (curl_cffi) to bypass Cloudflare; (g) used overclaiming language. To prevent this:
I1. EVERY number in the final report must come from a machine-written results file (results.json) produced by code you save. The final report is ASSEMBLED BY A SCRIPT (build_report.py) that reads the results.json files and inserts the numbers. You may write narrative text, but you may not type any statistic by hand.
I2. A separate VERIFIER subagent recomputes every headline metric independently from the raw CSVs (with its own code, without reading the other agents' scripts) and produces a reconciliation table (metric | reported | recomputed | match?). Any mismatch must be fixed or reported. The reconciliation table goes into the report.
I3. Gold labels must be INDEPENDENT: the labelling subagent never sees parser output; the parser subagent never sees gold labels. Record who produced what. Additionally output a 30-line random sample file for HUMAN spot-check by the students (they will verify later) and say so.
I4. Train/test separation: any parameter fitted from data must be evaluated only on data it was not fitted on (leave-one-source-out or held-out split). State the split explicitly.
I5. No row may be dropped silently. Every exclusion gets a reason in an exclusions.csv.
I6. Recipe identity check: a fetched recipe counts for a dish only if its title (or name in JSON-LD) matches the dish (fuzzy match + manual check list). Log mismatches; never count them.
I7. Politeness/legality: <=1 request/second per site, normal user agent, respect robots.txt. NO browser impersonation, NO Cloudflare/anti-bot bypass, NO login-walled content, NO Instagram/Zomato. If a site blocks you, drop it and record it.
I8. Web SEARCH only via the Stealth Search MCP tools (mcp__stealth-search__*); never the built-in WebSearch. Direct file/page downloads may use Python requests or the Stealth fetch tool.
I9. Language: report numbers with denominators; mark [V] verified vs [U] unverified; no words like "conclusively", "decisively", "perfect", "proves". A failed test is a valid, useful result - report it plainly.
I10. Log progress continuously: each agent appends to its own notes.md as it works, so nothing is lost on a crash.

## 2. Layout and parallelism
Create research_log/dryrun/ with one folder per test: D1_link_reader/, D2_normaliser/, D3_mapping/, D4_frying/, D5_end_to_end/, D6_swaps/, D7_baselines/, D8_research_questions/, VERIFY/. Each folder holds: code (*.py), raw data (*.csv), results.json (all metrics, with numerator and denominator), exclusions.csv, notes.md.
Check tools first: python3, pip (install locally if needed: requests, beautifulsoup4, extruct, rapidfuzz, openpyxl, pandas). If pip is unavailable, use the standard library.
USE SUBAGENTS IN PARALLEL (Agent tool, general-purpose type). Each subagent gets: the relevant section below verbatim, the integrity protocol (Section 1) verbatim, its output folder, and the instruction to finish by writing results.json.
Phase A (launch all at once): D1, D4, D6a (author-stated substitutions), D7, D8a (corpus size).
Phase B (after Phase A): D2+D3 (need D1 ingredient lines), D5 (needs D3 + D4), D6b/c (needs D1 corpus), D8b (needs D1 + INDB).
Phase C: VERIFY agent (independent recomputation), then build_report.py -> research_log/30_DRYRUN_REPORT.md.
Target runtime: moderate. Keep sample sizes as specified; do not expand.

## 3. The tests

### D1 Link reader (can we get ingredient + quantity data from a recipe link?)
Sample: 8 dishes x 6 sites = up to 48 recipes, PLUS 2 non-veg dishes x 3 sites that publish non-veg (e.g., indianhealthyrecipes.com, archanaskitchen.com, and one more non-veg Indian site found via Stealth search). Dishes: paneer butter masala, dal makhani, chole, gajar ka halwa, gulab jamun, samosa, onion pakora, poha; non-veg: butter chicken, chicken biryani. Sites: hebbarskitchen.com, vegrecipesofindia.com, tarladalal.com, indianhealthyrecipes.com, archanaskitchen.com, + one more (e.g., cookwithmanali.com or ranveerbrar.com). Find each URL via Stealth search or the site's sitemap; apply I6.
For each page: fetch politely; extract schema.org Recipe JSON-LD (extruct or parse ld+json). If none, run a FALLBACK: give the page's visible text to an LLM subagent (you) with a strict JSON schema {ingredients:[{line, qty, unit, name}], servings} and record the output.
Metrics (results.json): pages attempted / fetched / blocked; JSON-LD present; fallback success; servings present; identity-check pass rate; for liver-relevant lines (oil, ghee, butter, cream, malai, khoya, sugar, jaggery, honey, condensed milk, maida, vanaspati, coconut milk; salt separately): exact / range / count / vague / missing; deep-fried recipes with unquantified frying oil.
Pass criterion: >=80% of non-salt liver-relevant lines in non-fried recipes are exact or range (combined JSON-LD + fallback).

### D2 Quantity normaliser (text -> grams)
Sample: 200 ingredient lines from D1 (stratified: 100 liver-relevant, 100 other; random seed recorded).
Gold: a LABELLING subagent (blind to any parser) writes gold {name, qty, unit, grams, reasoning} for each line using a conversion table it must cite: tsp 5 ml, tbsp 15 ml, cup 240 ml (sensitivity 200 ml), katori: find a sourced value via Stealth search (else mark [U] and use 150 ml), oil 0.92 g/ml, ghee 0.91 g/ml, INDB Units.xlsx piece weights where available (data/indb_repo/Units.xlsx). Vague lines ("to taste", "for frying") get gold = "NOT_QUANTIFIED" (not a number).
Parser: a PARSING subagent writes a rule-based parser (regex + unit table) and, separately, an LLM-assisted parse; both run on the 200 lines without seeing gold.
Metrics: name correct %, qty correct %, grams within +/-10% and +/-25% (for quantified lines), correct NOT_QUANTIFIED detection %, error by category; rule-based vs LLM-assisted.
Pass: LLM-assisted >=80% grams within +/-25% on quantified lines.

### D3 Ingredient -> nutrient mapping (INDB)
Use data/indb_repo (INDB.xlsx / NIN food table; confirm which sheet holds per-100 g nutrients incl. SFA/MUFA/PUFA, free sugar). Build an alias dictionary + fuzzy matcher (rapidfuzz) + LLM fallback.
Gold: the LABELLING subagent (blind) assigns the correct INDB food code for the 200 D2 lines (or "NO_MATCH" with reason).
Metrics: exact-code match %, "nutritionally equivalent" match % (e.g., groundnut oil vs sunflower oil both oils: record separately), NO_MATCH rate, and coverage: what % of ALL D1 ingredient lines map to some INDB item. Also list the 50 most frequent ingredient strings in D1 and their mapping.
Pass: >=80% of liver-relevant lines map to a correct or nutritionally equivalent INDB item.

### D4 Frying model (the scientific core)
Step 1 COMPILE a single dataset fried_foods_lab.csv of lab-measured fat (g/100 g as eaten) for fried South Asian foods, one row per measured sample/value with columns: item, category (flat dough / battered fritter / stuffed pastry / crisp namkeen / syrup-soaked sweet / other), setting (street / home / restaurant-takeaway / retail-packaged / lab-controlled), oil if known, fat_g_100g, SFA % of fat if given, method (Soxhlet / proximate / FAME-sum / unknown), n_samples, source, table/page, notes.
Sources (all identified already; see file 28): Gupta et al. 2016 PMC4826272 Tables 1-2 (use Europe PMC fullTextXML: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4826272/fullTextXML); Joshee et al. 2019 PMC6894861 Tables 1-2 and S2 per-sample table (FAME sums - keep separate, method=FAME-sum); UK CoFID 2021 (data/CoFID_2021.xlsx sheet "1.3 Proximates"; use column F "Main data references"/G footnotes to classify each item as ANALYSED vs RECIPE-CALCULATED; only analysed rows count as ground truth); Chen, Gilbert & Khokhar 2009 (zenodo.org/records/10043766); safefood 2015 (data/safefood_text.txt); Jain, Passi & Selvamurthy 2024 (PMC11465016; dry basis - convert with moisture if reported, else mark). Search (Stealth) for 3-5 more Indian lab studies (vada, jalebi, kachori, papad, bhujia, puri) and add them.
Step 2 DESCRIBE: per item and per category x setting: n, median, IQR, min-max. Show the within-dish spread (e.g., samosa across sources).
Step 3 MODEL (range model): for each category x setting, predicted range = empirical 10th-90th percentile of TRAINING data. Evaluate with LEAVE-ONE-SOURCE-OUT: fit on all sources except one, predict the held-out source's values; metrics = coverage (% of held-out values inside predicted range), median absolute error of the predicted median, range width. Report Soxhlet/proximate and FAME-sum separately (do not mix without a stated correction).
Step 4 RECIPE LINK: for 5 fried dishes from D1, show recipe-ingredient fat alone (dough oil etc.) vs model range after adding uptake -> demonstrates the gap the model fills.
Pass: coverage >=70% under leave-one-source-out with a range width that is still informative (report width; e.g., not 0-60 g). If it fails, report by how much and why.

### D5 End-to-end dry run on real recipes + validation against measured cooked dishes
(a) For the 10 D1 dishes (use 1 recipe each, preferably the most popular site): run D2 -> D3 -> nutrient sum -> (D4 for fried) -> per-serving energy, total fat, SFA, added sugar, salt; % of daily budgets (SFA <7%E and <10%E of 2,000 kcal; added sugar 25 g; salt 5 g); HFSS flag (ICMR-NIN 2024: >15% energy from added oil/fat). Save a per-dish breakdown showing which ingredients contribute most.
(b) VALIDATION of ingredient-sum for NON-fried dishes against MEASURED cooked dishes: use safefood 2015 measured curries (chicken tikka masala, korma, jalfrezi; rice, naan) and CoFID ANALYSED South Asian cooked dishes (sabzi "bhaji" entries, dal/curry entries - check analysed vs calculated) and Chen 2009 analysed dishes. For each, take 3-5 matching web recipes (D1 method), compute their fat/100 g distribution, and check whether the measured value falls within the web-recipe range. Report coverage and median ratio (estimated/measured). This tests "can we infer from ingredients" directly.
(c) Sanity: compare our energy per serving with Tarla Dalal's stated kcal for the same recipe where present (both calculated; consistency check only).
Pass: (b) coverage >=70%; (a) no absurd outputs (list any).

### D6 Swap engine dry run
D6a AUTHOR-STATED SUBSTITUTIONS: from the D1 pages (and up to 30 more pages for the 10 dishes), extract substitution statements in notes/FAQs/tips (e.g., "alternative to cream, you can use curd"; "use jaggery instead of sugar"; "air fry instead of deep fry"). Output substitutions.csv: dish, original, substitute, quantity guidance, exact quote (<=25 words), URL. Metric: # pages with >=1 statement; # unique (original->substitute) pairs; how many are liver-lightening (compute nutrient delta with D3/INDB).
D6b CONTEXT SIMILARITY: build a small corpus (30 recipes per dish for 5 dishes: paneer butter masala, dal makhani, chole, gajar halwa, samosa; via sitemaps/search, I6 applies). Compute ingredient context vectors (co-occurrence) and, for cream, butter, ghee, sugar, maida, find the top-5 context-similar ingredients that rarely co-occur with them. Metric: overlap between these candidates and D6a author-stated substitutes (precision@5).
D6c QUANTITY RULE: from the same corpus, distribution (per serving) of butter, cream, ghee, oil, sugar for each dish; report median and 25th percentile; compute load saved by moving a recipe from its value to the 25th percentile.
D6d FOOD-PAIRING FIT CHECK: for 5 proposed swaps, compute FlavorDB shared-molecule overlap of the substitute with the REST of the dish's ingredients (data/flavordb_repo) vs the original's; report coverage (how many ingredients have FlavorDB entries; beware wrong matches such as "cashew" -> "cashew apple").
Pass: D6a finds >=1 real liver-lightening substitute for >=7 of 10 dishes; D6b precision@5 reported (no threshold, exploratory).

### D7 Baseline numbers (source verification)
Fetch and record exact values WITH page/table references: NSO "Nutritional Intake in India" 2022-24 (all-India and, if available, state-wise per capita kcal/protein/fat); ICMR-INDIAB-21 Nat Med 2025 (Anjana et al., s41591-025-03949-4) regional/state SFA %E, added sugar %E, total fat %E (Extended Data Tables 2 and 4); ICMR-NIN Dietary Guidelines 2024 thresholds (added sugar, salt, fat %E, HFSS definition incl. Table 15.2) with page numbers; SFA recommendation (<7%E vs <10%E: find which document says which). Output baselines.csv (value, unit, source, page/table, quote <=25 words).
Pass: every number used in D5 has a primary-source citation.

### D8 Research-question feasibility
D8a CORPUS SIZE: from site sitemaps (robots.txt lists them), count recipe URLs per site and estimate how many Indian recipes we could collect politely; estimate non-veg share.
D8b RQ2 (dietetic textbook vs web): for dishes present in INDB recipes (data/indb_repo/recipes.xlsx + recipes_names.xlsx; earlier check found close matches for ~12 of 20), compute fat/serving and SFA/serving for INDB version vs 3 web versions each (from D1/D6 corpus). Report differences with the caveat that this is textbook-vs-web, not change over time.
D8c RQ3 hidden load: from fried_foods_lab.csv and Gupta mithai/snack rows, summarise fat and SFA in unlabelled street foods vs packaged/labelled equivalents where available.

### VERIFY (independent)
A separate subagent, given only the raw CSVs of D1-D8 and the metric definitions, recomputes every metric listed in each results.json with its own code and writes VERIFY/reconciliation.csv. It also checks: gold independence (no identical gold vs parser rows beyond chance), identity-check failures excluded, no silently missing rows (row counts reconcile with exclusions.csv).

## 4. Final report: research_log/30_DRYRUN_REPORT.md (built by build_report.py)
1. Plain-language summary (8-10 lines) + overall verdict per component: READY / READY-WITH-CAVEATS / NOT-READY.
2. Table: component | metric | numerator/denominator | pass criterion | result.
3. One section per test: what was run, sample, numbers (from results.json), 3 concrete examples, failures and blockers, exclusions summary.
4. Reconciliation table from VERIFY (must show all matches or explain mismatches).
5. What the professor/TA pitch can honestly claim, and what it cannot.
6. Updated risk list and what to ask the professor for.
7. The 30-line human spot-check file path for the students.
Also append the new files to research_log/00_README_and_method.md.

## 5. When done
Tell the user in chat: component verdicts, the 5 most important numbers (with denominators), anything that failed, and whether the idea is ready to pitch. Short and honest.
