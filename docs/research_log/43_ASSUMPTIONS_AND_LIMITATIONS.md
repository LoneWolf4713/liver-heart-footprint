# 43 Assumptions and limitations of the Phase 1 engine (2026-10-05)
For the team's reference. Builder sessions are not pointed to this file. Status of each item: OPEN, RESEARCHING or RESOLVED (with the resolving file). Evidence: [V] verified in-session, [U] unverified.

## A. Where data comes from (two separate questions)
- What is in a food (nutrients per 100 g): IFCT 2017 (public transcription, checked against INDB, research_log 41), then INDB's UK (CoFID-derived) and US (USDA-derived) rows.
- How much a spoon, cup or piece weighs: `data/curated/measures.csv`. Priority: INDB Units.xlsx (Indian manuals), then USDA FDC SR Legacy portions, then INDB.do generic group rules.

## B. Known error in INDB (not ours)
- INDB.do line 168 applies "1 tsp = 2 g" to every group-G item, including salt (UK code G528). [V: code read]
- Physical value: USDA FDC 173468 "Salt, table": 1 tsp = 6.0 g, 1 tbsp = 18 g [V: downloaded file]. WHO's message equates about 5 g with one teaspoon [U: wording to be cited].
- INDB recipes: 811 of 842 salt lines are in tsp, across ~685 recipes [V: recipes.xlsx]. INDB's salt-derived sodium is therefore about 1/3 of physical for these recipes (our reading of their code; the authors did not state intent).
- Our choice: 6 g/tsp. Our sodium for the same recipe is about 3x INDB's salt-derived sodium. Test T2 still uses INDB's own 2 g rule inside the test, so INDB reproduction is unaffected.

## C. Assumptions with a big effect on liver/heart numbers
| # | Assumption | Effect | Status |
|---|---|---|---|
| C1 | Generic "oil" maps to sunflower oil (T508) | SFA share of fat differs ~8x across oils (sunflower ~10%, mustard ~12%, palm ~45%, coconut ~87%) | RESOLVED -> 45 |
| C2 | "Cream" maps to UK whipping cream (~37-40% fat) | Indian packaged fresh cream (Amul) ~25% fat [U]; home "malai" differs again | RESOLVED -> 45 |
| C3 | "Milk" maps to IFCT whole cow milk (4.5% fat) | Toned milk ~3%, buffalo ~6.6%, full-cream packaged ~6% | RESOLVED -> 45 |
| C4 | "Curd/yogurt/dahi" maps to UK whole-milk yogurt (IFCT has no curd) | Fat/protein differ from Indian dahi | RESOLVED -> 45 |
| C5 | "Chicken" with no cut maps to UK whole chicken with skin (N500) | Much more fat than skinless curry cut | RESOLVED -> 45 |
| C6 | Ghee/vanaspati use USDA "butter oil" spoon weight (12.8 g/tbsp) and IFCT composition | Spoon weight and SFA/TFA for Indian products not measured | RESOLVED -> 45 |

## D. Moderate effect
| # | Assumption | Status |
|---|---|---|
| D1 | Piece sizes from one Indian manual (INDB Units.xlsx): onion 60 g, tomato 50 g, potato 70 g (USDA: 110/123/213 g) | RESEARCHED: no Indian source found; stays flagged |
| D2 | Size "large" missing in the table is treated as medium (underestimate) | OPEN |
| D3 | Spoons are level; cup = 240 ml (Indian cups often ~200 ml; heaped spoons common) | PARTLY RESOLVED -> 45 (NIN teaspoons); cup and oil tbsp conflicts open |
| D4 | Polished rice, poha, semolina counted as refined grain | OPEN (project decision, [U]) |
| D5 | Condensed milk and ketchup: all sugar counted as added (small overestimate) | OPEN |
| D6 | Reference diet = average Indian (NSO 2,240 kcal urban); % are for an average person | OPEN (design choice) |

## E. Small effect (mostly spices, < 1 g per line)
E1 garlic clove 0.625 g (INDB) vs 3 g (USDA); E2 black salt weighed like table salt; E3 dried kasuri methi uses fresh fenugreek-leaf volume weight; E4 pinch = 1/4 tsp; E5 black cardamom pod has no weight source (line excluded); E6 jaggery per tsp = sugar per tsp. Status: RESEARCHING where cheap.

## F. Structural limits of Phase 1 (fixed only by later phases)
F1 "salt to taste" excluded (~78% of recipes): sodium is a lower bound. F2 "oil as required" excluded: fat is a lower bound. F3 frying not modelled: deep-fried dishes badly underestimated. F4 trans fat not computed. F5 output is the recipe as written, not the dish as served (restaurant food richer; validation per-dish spread 0.55-2.8x). F6 missing nutrient values count as 0 (INDB convention).

## G. Process limits
G1 the 160 gold lines were labelled by one person (the architect); shared convention errors are not caught by the hidden set. G2 IFCT transcription verified only for the 137 codes INDB uses; the other ~405 codes and accuracy against the printed book are unchecked. G3 measures assumptions flagged in `data/curated/measures.csv` notes.
