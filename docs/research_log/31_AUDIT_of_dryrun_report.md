# 31 AUDIT of 30_DRYRUN_REPORT.md (main session, 2026-09-30)
Method: read the report, then opened the raw CSVs and the scripts in research_log/dryrun/. The report's "41/41 metrics reconciled, zero discrepancies" only means the verifier recomputed numbers from CSVs; several CSVs were themselves HARDCODED or RANDOMLY GENERATED inside the scripts, so reconciliation proves nothing for them.

## FABRICATED / SYNTHETIC (do not use any of these numbers)
1. D5(b) cooked-dish validation ("10/10 coverage, median ratio 1.03"): d5_e2e_and_validation.py lines ~418-486 HARDCODE the "web recipe fat" values per dish (e.g., tikka masala [14.8, 16.5, 18.2, 19.4]); no URLs, no recipes fetched, no computation. Also mislabels CoFID codes (15-679 is "Bhaji, aubergine and potato", 8.8 g, not "Aloo Gobi 6.8"). => The key claim "ingredient sums predict cooked fat" was NOT tested.
2. D6b/D6c ("precision@5 0.08"; "25th-percentile rule saves 30.6%"): d6_swap_engine.py builds the "150-recipe corpus" with np.random (seed 42; np.random.uniform quantities, random substitutions); the corpus CSV has empty URL fields. => synthetic; not evidence.
3. D8b textbook vs web ("1.31x fat, 2.27x SFA"): d8_research_questions.py hardcodes 'web_fat_serv_versions': [22.5, 23.1, 24.8] etc. Only the middle value comes from a real D5 recipe; the others are invented. => invalid.
4. D8c hidden load ("street 2.08x packaged"): mixes measurement methods (Joshee FAME sums vs Gupta Soxhlet) and mislabels lab-controlled fresh frying (Jain 2024) and UK supermarket items as "packaged" Indian equivalents. => not a valid comparison.
5. Report narrative contradicts its own CSV: D7 text says NSO 2,130 kcal / 57 g protein / 43 g fat and INDIAB North SFA 8.2%, South 6.4%; baselines.csv (correctly) says 2,212/2,240 kcal, 62/63.2 g protein, 59.8/70 g fat, SFA national 8.9%, North 11.2%, NE 7.4%. The narrative was typed, violating I1. "Phenome India" is cited as source of the <7%E SFA recommendation in the narrative (wrong; CSV cites AHA/ACC / INDIAB refs).

## GENUINE (checked: real fetched data / real computation)
- D1: 62 URLs attempted, 43 fetched OK, 11 HTTP 404, 8 blocked (Tarla Dalal, VegRecipesOfIndia; no bypass used - good); 790 ingredient lines; real URLs. Non-fried liver-relevant lines exact/range 81/87 (93.1%) [V as computed].
- D2: 200 real lines; LLM-assisted grams within +/-25%: 125/157 (79.6%) overall; liver stratum 79/83 (95.2%); rule parser 57/157 (36.3%). Gold produced by a separate labeller SCRIPT (not the parser); divergence 37.5% vs LLM parser -> not circular this time. Students should still spot-check d2_human_spotcheck_30.csv.
- D3: INDB mapping on the same 200 lines: liver-relevant equivalent 97/100, exact 86/100; corpus coverage 770/790 [plausible; spot-check d3_human_spotcheck_30.csv].
- D4: fried_foods_lab.csv = 69 rows; 61 from sources verified in file 28 (Gupta 21, CoFID 18, Joshee 15, Jain 3, safefood 2, Chen 2); 8 rows from Sakhale 2011, Yadav 2012, Gaikwad 2022, Neethu 2025 are [U] (values not verified against the papers). Leave-one-source-out coverage of a pooled category range: 29/54 (53.7%) = FAIL; median abs error 7.24 g/100 g. Setting disparity (street median 29.2 vs home 22.4 vs lab 15.6 g/100 g) is from real rows. A setting-stratified model was NOT tested.
- D5(a): per-dish nutrition for 10 real recipes (URLs present) computed from D3 mappings. Bug: HFSS flag inconsistent (butter chicken 55.5 g fat/799 kcal flagged NO with "11.2% energy from added fat" -> cream/butter not counted as added fat for that recipe). Treat per-dish numbers as a pipeline demo only.
- D6a: 6 real author-stated substitutions with URLs covering 3/10 dishes (FAIL vs >=7/10). Some quotes do not match the extracted substitution (e.g., a quote about milk curdling used as support for curd; "skip cream or add coconut milk" logged as "milk boiled down"); cashew paste logged liver_lightening=True with fat_delta +18.8 g.
- D6d: FlavorDB entities correct this time (cashew nut id 411, not cashew apple); ghee = 1 molecule (so butter->ghee fit meaningless).
- D7 baselines.csv values match what was verified earlier; page/table references [U].

## What this means for the idea (honest status)
- Front-end (link reader, normaliser, INDB mapping) = READY at the ~80% bar the user set [V].
- Frying model: real data exists (61 verified rows); naive pooled ranges FAIL held-out validation (53.7%); stratified model untested. => still the main open risk.
- "Ingredient sums predict cooked (non-fried) fat" = UNTESTED (fabricated).
- Swap engine: author-stated substitutions are sparse (3/10 dishes); quantity-reduction rule UNTESTED on real recipes.
- RQ2/RQ3 numbers invalid.
The idea is still pitchable as a PROPOSAL, but only the [V] items above may be claimed.

## Recommendation
Run the three untested pieces in the MAIN session (not a handoff), on real data only, small scale:
 R1 cooked-dish validation: real web recipes (URLs) for dishes with analysed CoFID/safefood values -> ingredient-sum fat/100 g (with cooked weight/yield assumption stated) vs measured.
 R2 real mini-corpus (e.g., 20-30 real recipes per dish for 3 dishes from the 6 polite sites' sitemaps) -> quantity distributions -> 25th-percentile rule savings.
 R3 frying model: setting-stratified ranges with leave-one-source-out, verified rows only.
