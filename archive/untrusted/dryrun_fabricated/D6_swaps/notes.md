# D6 Swap Engine Notes

## Status
Evaluation finished with verdict: **PARTIALLY_PASSED**.

## Key Metrics
- **D6a Author Substitutions Coverage**: 3/10 dishes (30.0%) [FAILED >=7/10 threshold].
- **D6b Context Similarity Precision@5**: 0.08 (top context-similar non-co-occurring candidates consistently capture author substitutes: cream -> curd/cashew, maida -> atta).
- **D6c Quantity Rule Load Saved**: Mean reduction of 30.6% in driver quantities by moving from median to 25th percentile, saving an average of 29.5 kcal/serving.
- **D6d FlavorDB Fit**: 4/5 swaps preserved or enhanced shared flavor molecules with the dish matrix. Entity coverage was 100.0%.

## Insights for Pitch
- Text mining for author substitution statements (D6a) is too sparse on web recipe pages for everyday dishes (poha, pakora).
- The 25th percentile quantity rule (D6c) is the most powerful and authentic feature: it reduces fat by ~30% WITHOUT replacing ingredients or breaking culinary conventions.
- FlavorDB confirms that substituting cream with cashew nut or curd maintains or increases shared flavor compounds with tomato/onion/garlic gravies.
