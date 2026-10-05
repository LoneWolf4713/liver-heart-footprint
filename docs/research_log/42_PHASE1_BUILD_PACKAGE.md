# 42 Phase 1 build package (session-architect/builder) (2026-10-05)
What was built (architect work, by Claude):
- docs/SPEC.md: contracts for 9 tasks (composition, summing, parser, matcher, grams, classes, footprint, pipeline, validation).
- data/curated/measures.csv (238 rows; every row cited to INDB Units.xlsx, USDA FDC SR Legacy portions in data/raw/fdc_portions, or INDB.do line), constants.csv (9 rows, cited), classes.csv (project decisions, [U] flagged).
- Gold: 160 real ingredient lines sampled (seed 20261005) from the 71 sample recipes and labelled by hand by the architect (status, qty, unit, size, stated grams, optional, name keyword, allowed codes); expected grams computed from measures.csv. 120 public (acceptance/gold), 40 hidden (~/subjects/CGAS/lhf_holdout, outside the repo).
- acceptance/: 10 tests (rules + T1-T9); order.json; build.py (identical to session-architect/builder); AGENTS.md; CLAUDE.md/GEMINI.md = @AGENTS.md; docs/BUILD_GUIDE.md.

Checks run:
- Before code: rules PASS (nothing to scan), T1-T9 FAIL (exit 1).
- Private reference implementation (outside repo): all 10 PASS; hidden set PASS (parse unit 35/36, others 100%). T2 reproduces INDB for 995/995 dishes (carb 970/995).
- 9 cheat mutations, all caught: default 100 g; missing oils energy fix; hard-coded reference energy; silently dropped lines; gold line pasted as alias; typed number in report; "salt to taste" defaulted to 1 tsp; sodium skipped in sums; sugar not capped.
- Reference validation (illustrative only, not the deliverable): 31 recipe-lab pairs, median fat-energy ratio 1.00; home 1.11, retail 1.15, takeaway 0.88.

Findings that changed the design:
- INDB.do counts 1 tsp salt as 2 g (group default); USDA FDC gives 6 g. We use 6 g, so our sodium is higher than INDB's for the same recipe.
- "2-1/2 cups" in real lines is a mixed number (2.5), not a range; the spec now says so.
- Fuzzy-match cutoff and spice list moved into cited data files (constants.csv, classes.csv) so code holds no tuning numbers.
Limits: gold labels were made by one architect (no second annotator); the parser/matcher gold reflects the spec's conventions. The hidden set guards against fitting to the visible lines, not against shared convention errors.
