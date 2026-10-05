# 44 Research on the Phase 1 assumptions: verified results and proposed resolutions (2026-10-05)
Inputs: three Sonnet research agents (raw notes: research_dairy_, research_oils_, research_measures_2026-10-05.md) plus the architect's own re-fetch of the key sources. Only values marked [V] were seen by the architect on the source page; [S] = search snippet or agent-only, not yet usable.

## Verified values
| Item | Value | Source | Status |
|---|---|---|---|
| Amul Masti Dahi /100 g | 65 kcal, fat 3.1 g, SFA 2.0, trans 0, carb 4.6, sugar 4.6, protein 4.0, Na 50 mg, Ca 150 mg | sabardairy.org/product/amul-masti-dahi (Amul member union) | [V] |
| Amul Pure Ghee /100 ml | 814 kcal, fat 90.5 g, SFA 58 g, cholesterol 190 mg | sabardairy.org/product/amul-pure-ghee | [V]; per-100 ml basis implies density ~0.905 g/ml (derived) |
| Amul Butter (salted) /100 g | 724 kcal, fat 80 g, SFA 48 g, trans 0, protein 1.0, Na 955 mg | sabardairy.org/product/amul-pasteurized-butter | [V] |
| Amul Malai Paneer /100 g | 314 kcal, fat 25 g, SFA 15 g, carb 4.5, protein 20, Na 22 mg | sabardairy.org/product/amul-malai-paneer | [V] (IFCT paneer L003: fat 14.78 g) |
| Amul Taaza (toned milk) | 58 kcal, fat 3.0 g, SFA 2.0, carb 4.7, protein 3.0, Na 40 mg (label says "serving 200 ml"; values are per 100 ml by magnitude) | sabardairy.org/product/amul-taaza | [V] values; basis ambiguity noted |
| Amul Fresh Cream | milk fat 25% | hyperpure.com/in/amul-fresh-cream-1-l | [V]; full label (246 kcal, SFA 16 g) [S] |
| Home-made malai | moisture 49.6%, fat 38.2%, protein 9.01% | Indian J Dairy Sci 75(5), epubs.icar.org.in/index.php/IJDS/article/view/100089 (abstract) | [V] |
| India edible oil consumption 2021-22 (22,454 kt) | palm 33.4%, soy 23.6%, rapeseed/mustard 15.6%, sunflower 8.2%, cotton 5.3%, groundnut 4.7%, rice bran & other 9.1% | SEA (B.V. Mehta), Globoil 2023 deck, p.7 | [V]; national total incl. out-of-home/food industry; excludes ghee/butter (1-1.5 kg/capita, p.9) |
| ICMR-NIN DGI 2024, Annexure I | katori: large 360 ml, medium 200 ml, small 155/115 ml; "Tablespoon 15g", "Teaspoon 5g" | nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf p.111 (downloaded) | [V] |
| ICMR-NIN DGI 2024, Annexure II (scale-measured) | oil/ghee 5 g = 1 tsp; rice 10 g = 2 tsp; red gram dal 5 g = 1 tsp; wheat flour 10 g = 3 tsp; rice flakes 10 g = 4 tsp; rajmah 5 g = 1 tsp | same, p.113 | [V] |
| ICMR-NIN DGI 2024, adult charts | "Oil 10 g = One tablespoon"; "Cooking oil 15 g = One and a half tablespoon" (conflicts with 3 tsp x 5 g) | same | [V] internal inconsistency |
| ICMR-NIN DGI 2024 | "5000mg or 5g (1 teaspoon) of common salt per day"; "1 cup/Katori =200ml" | same | [V] |

## Problems found in IFCT data (architect's own checks on the transcription)
- N001 chicken leg skinless: energy 1605 kJ vs 798 kJ from its own fat/protein (Atwater); INDB carries the same value, so it is in the source, likely a typo. [V]
- All poultry rows (N001-N019): saturated + mono + poly fatty acids add up to only 11-27% of total fat (median for other fatty foods: 89%). IFCT chicken SFA is therefore likely understated about 3x. [V]
- Chicken skinless (IFCT) is NOT lower in fat than the UK "whole chicken with skin" row: 9.0-14.2 g vs 10.3 g per 100 g (the UK row is weighed with bone).

## Proposed resolutions (need the user's decision)
| # | Assumption | Proposal |
|---|---|---|
| C1 generic "oil" | sunflower | Use a consumption-weighted Indian oil mix (SEA 2021-22 shares x IFCT SFA) as central value, flag GENERIC_OIL, and report the range mustard..palm in Phase 2. Caveat: SEA shares include out-of-home use; household shares unknown. |
| C2 cream | UK whipping 40% | "cream"/"fresh cream" -> Amul Fresh Cream 25% fat (full label to verify); "malai" -> IJDS malai composition; "heavy/whipping cream" keeps UK row |
| C3 milk | IFCT cow 4.5% | Default "milk" -> toned milk (Amul Taaza label, 3% fat, the FSSAI toned standard); "full cream milk" -> Amul Gold; "buffalo milk" -> IFCT L001. Share of toned milk in home use: not found [U] |
| C4 curd | UK yogurt | "curd/dahi" -> Amul Masti Dahi label |
| C5 chicken | UK with skin | "chicken" -> IFCT skinless (curry cut = mean of leg and thigh; boneless/breast -> N003), with N001 energy recomputed (flag) and SFA from fat x UK chicken SFA share (flag), because IFCT poultry fatty acids look incomplete |
| C6 ghee/butter/paneer | USDA spoon weight; IFCT/UK composition | Ghee spoon weight from Amul label density (0.905 g/ml); composition: keep IFCT ghee (lab-measured; SFA 71% of fat) and show Amul (64%) as cross-check. Butter -> Amul salted label. Paneer: IFCT 14.8% fat vs Amul Malai Paneer 25% -> needs a choice or a range |
| D3 spoons/cups | US 5/15/240 ml | Use NIN scale-measured Indian teaspoon weights where available (oil/ghee 5 g, dal 5 g, rice 5 g, atta 3.3 g, poha 2.5 g). Oil tablespoon: NIN 10 g vs 3 x 5 g = 15 g vs USDA 13.6 g -> range. Cup 200 ml (NIN) vs 240 ml (most recipe sites, not yet verified) -> range |
| B salt | 6 g/tsp | Keep. NIN's "5 g = 1 teaspoon" and USDA 6.0 g both contradict INDB's 2 g |
| D1 piece weights | INDB manual | No Indian source found; keep, flagged |
| E2 black salt, E3 kasuri methi, E5 black cardamom | as before | No usable source found; keep flags |

Common thread: several defaults have two credible Indian values (paneer, oil tbsp, cup, generic oil). The honest output is a range; Phase 1 keeps one documented central value per item and records the alternatives so Phase 2 can turn them into ranges.
