# 39 AUDIT of 38_VALIDATION_RESULT_v2 (main session, 2026-10-01)
Spot-audit of research_log/validation_v2/: CREDIBLE.
- per_ingredient.csv: 558 lines, real recipe URLs; max line 700 g ("1½ lbs (700 grams) chicken" parsed correctly); only 6 lines at exactly 100 g (stated quantities); no hardcoded result arrays found in scripts (grep).
- ground_truth.csv: CoFID rows carry description + main data reference (e.g., Univ. of Leeds 2007 "6 samples" bhindi subji; Aspland & James 1997 takeaway biryani; LGC 1994 retail tikka masala), i.e. analysed rows with evidence; settings labelled home/takeaway/retail.
- results.json consistent with the chat summary (e.g., saag M1 lab 40.2 vs recipes 31.1-41.9 -> inside; ratio 0.91).
Findings accepted: 9 dishes / 11 pairs / 27 recipes; mass mapped 99.9% (CoFID raw-ingredient rows used because INDB repo lacks the raw IFCT table); lab value inside recipe range 2/8 (M1), 3/11 (M2); median ratio 1.00 (M1), 0.88 (M2); per-dish ratios 0.55-2.84; takeaway under-estimated 5/5 (median M2 ratio 0.77); home dishes mixed.
Interpretation for the project:
- Ingredient sums get the right ballpark on average (no systematic bias for home cooking) but a single dish can differ ~0.5-2.8x from a lab sample, because recipes vary in oil/cream and restaurants cook richer.
- This does NOT block the app: the app computes the USER'S recipe as written (exactly what ingredient sums are for); it must not claim "this is what a typical restaurant dish contains".
- Supports: reporting ranges, the explicit home vs restaurant/takeaway setting (takeaway richer), and per-recipe (not per-dish-name) estimates.
- Data note: IFCT raw table must be requested from NIN (or via the professor) for an Indian-composition version; CoFID raw ingredients are an acceptable fallback.
