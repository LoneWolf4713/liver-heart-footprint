# D3 Ingredient -> Nutrient Mapping Notes

## Status
Evaluation finished with verdict: **PASSED**.

## Key Metrics
- **Liver-relevant equivalent match rate**: 97/100 (97.0%) [Threshold >= 80.0%]
- **Liver-relevant exact match rate**: 86/100 (86.0%)
- **Other ingredients equivalent match rate**: 77/100 (77.0%)
- **Overall sample equivalent match rate**: 174/200 (87.0%)
- **All D1 Corpus Coverage**: 770/790 (97.47%)
- **Sample NO_MATCH count**: 2/200

## Mapping Architecture
1. **Curated Alias Table**: Directly captured domain synonyms (e.g., 'ghee', 'clarified butter', 'makhan', 'malai', 'maida', 'atta', 'kashmiri chilli').
2. **Historical INDB Corpus**: Utilized 1,301 culinary aliases from `recipes.xlsx`.
3. **Rapidfuzz Fuzzy Matching**: Token sort ratio matches against cleaned head nouns.
4. **Nutritional Equivalence**: Defined equivalence classes for cooking oils (sunflower, mustard, coconut, sesame, olive), sugars (white, brown, icing), butters (salted, unsalted), and creams (single, whipping).

## Observations
- Liver-relevant drivers map with exceptionally high accuracy (97.0%) because Indian recipes use a focused set of fats (ghee, butter, vegetable oil, mustard oil), dairy creams, sugars, and refined flours (maida).
- Unmatched lines were almost exclusively instructional notes or multi-ingredient garnish sentences.
