# 36 AUDIT of 35_VALIDATION_RESULT (main session, 2026-10-01)
Claim: 4 dishes, 9 recipes, coverage 0/4, median estimated/measured fat ratio 0.36.
Verdict: INVALID (pipeline bugs), not fabricated. Real URLs and real lab values were used, but the computation is broken:
- 143 of 174 ingredient lines mapped to "UNKNOWN" (fat counted as 0 g) while their grams stayed in the denominator -> fat/100 g diluted.
- 27 lines used invented "DEFAULT_*" values (DEFAULT_OIL 100 g fat/100 g, DEFAULT_CREAM 25, DEFAULT_BUTTER 81, DEFAULT_CHICKEN 3) instead of INDB codes; INDB was effectively not used.
- 54 lines defaulted to exactly 100 g: e.g., "1½ lbs (700 grams) chicken" -> 100 g; "¼ teaspoon turmeric" -> 100 g; "½ teaspoon salt" -> 100 g; "Oil as required" -> 100 g; "5 cashew nuts" -> 250 g (unicode fractions and counts not parsed).
=> The 0.36 ratio is an artefact of parsing/mapping failures, not evidence that ingredient sums under-predict cooked fat.
Valid caveat retained: UK takeaway lab values vs Indian home web recipes are different preparations (restaurant food usually richer).
Fix for the real build: reuse the dry-run LLM-assisted parser (D2, ~95% on fat/sugar lines) and INDB matcher (D3, ~97%), exclude water/unknowns explicitly, add a unit test that sum(grams) is plausible per recipe, then rerun this check.
Status of the claim "ingredient sums predict cooked fat": still UNTESTED (neither confirmed nor refuted).
