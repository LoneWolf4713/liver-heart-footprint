# 26 AUDIT of 25_TEST_REPORT.md (2026-09-29, main session)
Method: re-read the report and re-computed/inspected the raw files in research_log/data/ (t1-t7 CSV/JSON, indb_repo). The test session ran ~17:18-17:46 (about 30 min).

## What HOLDS (reproduced from raw data)
- T1: 100 URL attempts; 84 OK with JSON-LD; 16 failed (8 HTTP 404, 6 no JSON-LD, 2 HTTP 403). 1,449 ingredient lines. Caloric liver lines (oil/ghee/butter/cream/sugar/maida; salt excluded) in non-fried recipes: 186, exact 137 + range 20 = 84.4% [V, reproduced]. Including salt: 64.9% [V]. Deep-fried recipes: 9/10 frying oil unquantified [V].
- T4 coverage: 12/26 target items found in the FlavorDB scrape (tarek-kerbedj flavordb.csv); ghee = 1 molecule, mustard oil = 2, cream = 5, sugar = 5 [V as per that scrape; scrape may be older/incomplete than FlavorDB2].
- T7: 60 videos (real channels/views); 42/60 have ingredient lists in the description; 19/60 transcripts; 18 deep-fried-dish videos, frying oil quantified in 0 [V]. Caveat: 15 videos had no usable data at all, so "0/18" includes videos with nothing to read.
- T6: direct Wayback snapshots for 3/10 URLs [V].

## What does NOT hold
1. T2 is INVALID: gold labels equal parser output in 100/100 rows (e.g., gold_name "to butter for topping add more for a richer taste"; "salt to taste" given gold qty 0.5 and counted correct; "oil for deep-frying" counted as INDB match). No hand-labelling happened -> the 100% name accuracy, 0.0% gram error, 100% INDB match are circular.
2. T3 is CIRCULAR and MISREPORTED: uptake ranges were taken from the same sources used as ground truth (safefood 2015, CoFID) and are wide (+/-25-30%), so "within range" is weak evidence. Report table differs from the CSV: CSV vegetable samosa = 9.3 g/100 g (in range), report says 12.8 (out of range); CSV has a MATHRI row (lab 21.8 vs model 33.4, 53% error, out of range) omitted from the report. Honest result: 7/8 in range on non-independent data.
3. T5 numbers in the report DO NOT MATCH t5_score_sanity.csv: e.g., Dal makhani vs Tarla Dalal kcal: CSV -30.6%, report +5.4%; Poha: CSV +64.8% (300 vs 182 kcal), report -1.9%; Bhatura: CSV +37.3%, report +7.7%; Gulab jamun: CSV 353.6 kcal / Tarla 312, report 395.2 / "N/A"; Paneer butter masala % energy from added fat: CSV 32.4%, report 72.5%. The 0-100 "liver score" is an invented formula; "100% HFSS agreement" is a tautology (HFSS was computed by the same script). "Perfect clinical sanity" is not supportable.
4. T6 diff misreported: Hebbar's paneer butter masala CHANGED between 2019 and 2026 (2019: 1 tsp butter + 1 tsp oil + 2 tbsp butter + 1/2 tsp sugar; 2026: 2 tbsp oil + 1 tsp butter + 2 tsp oil + 1 tbsp butter, no sugar) -> butter down, oil up, sugar dropped. Report called it "essentially identical". "Blog recipes are remarkably static" rests on 3 recipes. INDB coverage claimed 19/20; my check of recipes_names.xlsx: loose name matches for 17/20 (chole only as "black channa curry", chicken biryani only mutton/veg, aloo tikki only as cutlets, no gajar halwa, no paneer butter masala, no aloo paratha, no jalebi) -> close matches ~12/20. "INDB prescribes 10-15 g oil per serving, no cream" unverified.
5. T1 contamination: wrong dishes accepted as matches: Tarla Dalal "butter chicken" = "Strawberry Hide And Seek" cake; Hebbar's "egg curry" = paneer sabji; VegRecipesOfIndia "butter chicken" = paneer makhani; chicken biryani -> vegetable biryani on 2 sites. Non-veg recipes effectively from only 2 sites (Swasthi's, Archana's). The 84.4% figure is still computed on what was fetched, but "20 dishes x 5 sites" is overstated.
6. T4: "cashew" matched FlavorDB "cashew apple" (a fruit) -> cream-vs-cashew Jaccard invalid. "Real swap variants exist 20/20" is backed only by named sources in a CSV, no fetched URLs -> [U].
7. Method concern: the session used curl_cffi Chrome impersonation to get past Cloudflare on two sites. That conflicts with the "polite, respect the site" rule; do not use it in the real project (ask sites / use their pages normally / drop blocked sites).
8. Tone: "conclusively resolves", "decisively disproved", "perfect clinical sanity", "liver-toxic" = overclaims the user explicitly forbids.

## Net conclusions for the project (what we can actually rely on)
- Website input is viable for NON-FRIED dishes: ~84% of fat/dairy/sugar/maida lines carry usable quantities [V].
- Frying oil is never quantified on websites (9/10) nor in YouTube descriptions (0/18) -> the oil-uptake model is mandatory and is the key scientific component; it still needs an INDEPENDENT validation (fit on some sources, test on others).
- YouTube does not solve the oil problem; descriptions are usable as a secondary input via the official API; no media download needed.
- FlavorDB is too sparse for fat/dairy/sweetener swaps -> swap engine = culinary role + RecipeDB2 co-occurrence (+ FlavorDB only where coverage exists, e.g., herbs/spices/aromatics).
- RQ2 as "drift over time" is weak (few snapshots); reframe as "dietetic textbook (INDB) vs popular web recipes", stated as such.
Overall: GO-WITH-CHANGES is directionally reasonable, but T2, T3 and T5 must be redone properly before any number is quoted.

## Redo list (cheap)
R-T2: two humans hand-label 100 ingredient lines (gold name/qty/unit/grams) blind to the parser (~1 hour); then score the parser.
R-T3: split lab sources: fit uptake factors on Chen 2009 + Jain 2024, test on safefood + CoFID (or leave-one-source-out); report error incl. mathri.
R-T5: recompute from the script, report the CSV numbers as they are; drop the 0-100 score until weights are justified; show budget bars instead.
R-T1: fix URL matching (verify recipe title matches the dish), drop wrong-dish rows, add 2 non-veg sources.
