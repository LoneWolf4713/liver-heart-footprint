# 45 User decisions on Indian defaults, applied (2026-10-05)
Decisions by the user (Pratyaksh), applied by the architect:
| Item | Decision | Implemented as |
|---|---|---|
| Generic oil | Home recipe -> sunflower; out-of-home recipe -> palm | Phase 1 (home recipes): "oil" -> T508. Palm (T007) for the restaurant/street setting is a Phase 2 item |
| Milk | Toned milk (households boil full-cream milk and remove malai; cooking uses toned) | "milk" -> L901 Amul Taaza toned (label); "whole/full cream milk" -> L002; "buffalo milk" -> L001 |
| Paneer | Amul | "paneer" -> L903 Amul Malai Paneer (25 g fat/100 g; IFCT home paneer 14.78 g kept as L003) |
| Chicken | Keep UK row | all chicken names -> N500 (IFCT poultry fatty acids look incomplete, research_log 44) |
| Ghee composition | IFCT lab-measured (SFA 71% of fat); Amul label as cross-check | "ghee" -> T013 |
Also applied (from research_log 44, verified sources): curd/dahi -> L902 Amul Masti Dahi; butter -> L904 Amul salted; cream/fresh cream -> L905 Amul 25% (fat only verified; SFA and energy derived, flagged); malai -> L906 (IJDS 2022; SFA, energy derived, flagged); ghee density 0.905 g/ml (Amul label) -> 13.38 g/tbsp; ICMR-NIN 2024 scale-measured teaspoons: oil/ghee 5 g, dal 5 g, rice 5 g, atta 3.33 g, poha 2.5 g, rajma 5 g.
Files changed: data/curated/indian_products.csv (new, 6 rows), measures.csv (243 rows), classes.csv, measures_README.md, docs/SPEC.md (sections 2 and 5), acceptance/test_t1_composition.py, acceptance/test_t4_match.py, acceptance/gold/gold_public.json (+ hidden set regenerated; 13 expected grams changed).
Checks: reference implementation passes all 10 tests and the hidden set; reference validation median fat-energy ratio now 1.06 (home 1.12, retail 1.29, takeaway 0.99; illustrative only). Build re-locked (new baseline commit).
Still open: piece weights (no Indian source), black salt sodium, kasuri methi and black cardamom weights, Dalda label (Phase 2 trans fat), cup 200 vs 240 ml, oil tablespoon 10 g (NIN adult charts) vs 13.6 g, Amul cream full label.
