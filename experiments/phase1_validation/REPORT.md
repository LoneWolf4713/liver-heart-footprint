# Validation Report: Phase 1 Core Engine vs Lab-Analysed Dishes

## Summary

This validation evaluates the Phase-1 recipe analysis pipeline (`analyse_recipe`) against independently laboratory-analysed Indian dishes from published nutritional surveys. A total of 31 recipe-lab pairs were evaluated across 28 recipes representing 10 distinct dishes.

The primary metric of comparison is M2: fat energy share (fat grams multiplied by the fat energy conversion factor divided by total energy in kilocalories multiplied by 100). The ratio is defined as recipe M2 divided by lab M2.

- Overall median ratio: 1.06 (mean: 1.13, range: 0.19 to 2.51)
- Home setting median ratio: 1.12
- Retail setting median ratio: 1.29
- Takeaway setting median ratio: 0.98

Overall, the median ratio across all 31 pairs is close to unity (1.06). However, this overall figure encompasses noticeable variation across dish categories and preparation settings. Takeaway dishes show a median ratio of 0.98, with several dishes (such as prawn bhuna) yielding lower fat energy shares in written recipes than in restaurant preparations. In contrast, home-style recipes with frying or tadka (such as sambar and vegetable pilau) exhibit higher fat energy shares than the laboratory-measured home samples. These findings indicate that ingredient sums provide a reasonable first-order approximation of dietary fat, while individual dish predictions remain subject to culinary variation.

## Per-dish table

The following table details all evaluated recipe-lab pairs, reporting recipe fat energy share (Recipe M2), laboratory-analysed fat energy share (Lab M2), the recipe-to-lab ratio, and the ingredient line inclusion count.

| Recipe ID | Dish | Setting | Lab Code | Recipe M2 (%) | Lab M2 (%) | Ratio | Lines (Included/Total) |
|---|---|---|---|---|---|---|---|
| V2-R01 | saag | home | 15-629 | 71.4% | 71.4% | 1.00 | 16/17 |
| V2-R02 | saag | home | 15-629 | 60.7% | 71.4% | 0.85 | 12/14 |
| V2-R03 | methi aloo | home | 15-628 | 56.0% | 65.9% | 0.85 | 14/16 |
| V2-R04 | methi aloo | home | 15-628 | 57.6% | 65.9% | 0.87 | 10/10 |
| V2-R05 | bhindi sabzi | home | 15-627 | 11.1% | 58.3% | 0.19 | 6/7 |
| V2-R06 | bhindi sabzi | home | 15-627 | 68.7% | 58.3% | 1.18 | 14/15 |
| V2-R07 | bhindi sabzi | home | 15-627 | 61.7% | 58.3% | 1.06 | 12/13 |
| V2-R08 | chicken biryani | takeaway | 19-454 | 34.5% | 40.9% | 0.84 | 25/27 |
| V2-R09 | chicken tikka masala | retail | 19-296 | 73.4% | 56.5% | 1.30 | 27/28 |
| V2-R09 | chicken tikka masala | takeaway | p.14 Table 5 | 73.4% | 65.4% | 1.12 | 27/28 |
| V2-R10 | chicken korma | takeaway | p.14 Table 5 | 70.0% | 65.9% | 1.06 | 23/24 |
| V2-R11 | chicken jalfrezi | takeaway | p.14 Table 5 | 67.8% | 46.7% | 1.45 | 26/27 |
| V2-R12 | sambar | home | 12-467 | 19.8% | 16.5% | 1.20 | 26/27 |
| V2-R13 | sambar | home | 12-467 | 32.1% | 16.5% | 1.94 | 13/21 |
| V2-R14 | sambar | home | 12-467 | 22.6% | 16.5% | 1.37 | 18/25 |
| V2-R15 | sambar | home | 12-467 | 25.7% | 16.5% | 1.55 | 23/27 |
| V2-R16 | vegetable pilau | home | 12-472 | 23.6% | 12.1% | 1.95 | 23/31 |
| V2-R17 | vegetable pilau | home | 12-472 | 30.2% | 12.1% | 2.51 | 11/13 |
| V2-R18 | chicken korma | takeaway | p.14 Table 5 | 63.2% | 65.9% | 0.96 | 15/18 |
| V2-R19 | chicken korma | takeaway | p.14 Table 5 | 66.6% | 65.9% | 1.01 | 17/20 |
| V2-R20 | chicken biryani | takeaway | 19-454 | 68.1% | 40.9% | 1.67 | 25/28 |
| V2-R21 | chicken tikka masala | retail | 19-296 | 59.4% | 56.5% | 1.05 | 22/25 |
| V2-R21 | chicken tikka masala | takeaway | p.14 Table 5 | 59.4% | 65.4% | 0.91 | 22/25 |
| V2-R22 | chicken tikka masala | retail | 19-296 | 73.2% | 56.5% | 1.29 | 19/22 |
| V2-R22 | chicken tikka masala | takeaway | p.14 Table 5 | 73.2% | 65.4% | 1.12 | 19/22 |
| V2-R23 | chicken jalfrezi | takeaway | p.14 Table 5 | 56.3% | 46.7% | 1.21 | 14/17 |
| V2-R24 | methi aloo | home | 15-628 | 59.9% | 65.9% | 0.91 | 4/6 |
| V2-R25 | prawn bhuna | takeaway | 16-365 | 49.5% | 65.2% | 0.76 | 14/16 |
| V2-R26 | prawn bhuna | takeaway | 16-365 | 45.2% | 65.2% | 0.69 | 21/23 |
| V2-R27 | prawn bhuna | takeaway | 16-365 | 21.7% | 65.2% | 0.33 | 9/15 |
| V2-R28 | prawn bhuna | takeaway | 16-365 | 49.7% | 65.2% | 0.76 | 14/17 |

## By setting

Nutrient composition was broken down across the three preparation settings recorded in the ground truth dataset: home-cooked dishes, retail ready-meals, and commercial takeaway dishes.

| Setting | Pairs | Median Ratio | Mean Ratio | Min Ratio | Max Ratio |
|---|---|---|---|---|---|
| home | 14 | 1.12 | 1.25 | 0.19 | 2.51 |
| retail | 3 | 1.29 | 1.21 | 1.05 | 1.30 |
| takeaway | 14 | 0.98 | 0.99 | 0.33 | 1.67 |

Key setting-specific observations include:
- **Home (14 pairs)**: Median ratio is 1.12. Dishes such as saag and methi aloo track closely with laboratory samples. Sambar and vegetable pilau show ratios above 1.0 (up to 2.51 for vegetable pilau), reflecting generous cooking oil and ghee quantities specified in popular web recipes compared to hospital and laboratory-prepared reference samples. One bhindi sabzi recipe omitting oil in the ingredient list resulted in a ratio of 0.19.
- **Retail (3 pairs)**: Median ratio is 1.29. Evaluated against chilled and frozen chicken tikka masala ready-meals, recipe estimates slightly exceed retail laboratory values.
- **Takeaway (14 pairs)**: Median ratio is 0.98. Takeaway dishes show substantial dispersion (0.33 to 1.67). Prawn bhuna recipes yield lower fat energy shares than commercial takeaway food, consistent with commercial establishments using additional oil in cooking bases.

## Coverage

Across all 28 recipes evaluated in this validation run, a total of 549 ingredient lines were parsed and processed. The engine included 473 lines (86.2% inclusion rate), representing 21665.3 grams of quantified edible mass.

Line status breakdown:

| Status / Exclusion Reason | Count |
|---|---|
| Lines included | 473 |
| Excluded: NON_FOOD | 0 |
| Excluded: UNMAPPED | 11 |
| Excluded: UNQUANTIFIABLE | 16 |
| Excluded: UNQUANTIFIED | 23 |
| Excluded: WATER | 26 |
| Total lines | 549 |

Lines excluded as WATER (26 lines) contain plain water or ice and do not contribute macronutrients. UNQUANTIFIED lines (23 lines) represent ingredients without measurable quantities (such as 'salt to taste'). UNQUANTIFIABLE lines (16 lines) and UNMAPPED lines (11 lines) reflect items lacking documented conversion measures or composition table matches. No arbitrary fallback quantities were imputed.

## Limitations

Several methodological constraints must be taken into account when interpreting these results:

- **Sample size and dish diversity**: The dataset is restricted to 10 distinct dishes and 28 web recipes. A broader validation set covering more regional variations and dish categories will be needed in subsequent phases.
- **Ground truth provenance**: Reference nutritional values are sourced from UK laboratory surveys (University of Leeds, Aspland & James, LGC, and safefood), rather than laboratory analyses of meals prepared in India. Ingredients available in the UK may differ in composition and moisture from Indian domestic ingredients.
- **Culinary mass dynamics**: The Phase-1 pipeline sums raw ingredient nutrient contributions as written. It does not model pan-oil retention, deep-frying oil absorption dynamics, or cooking moisture loss. Evaluating fat energy percentage (M2) mitigates water loss variability, but cannot account for unabsorbed oil left behind in cookware.
- **Unquantified seasonings and salt**: Seasonings listed without quantities ('to taste', 'adjust as needed') are excluded by design to avoid speculative assumptions. Consequently, sodium totals from web recipes represent lower bounds.
- **Scope of dietary estimates**: The pipeline produces dietary estimates for educational and awareness purposes. These estimates do not represent diagnostic nutritional assessments.
