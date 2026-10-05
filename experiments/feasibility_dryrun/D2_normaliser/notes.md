# D2 Quantity Normaliser Notes

- Stratified sample of 200 ingredient lines from D1 (100 liver-relevant, 100 other; random seed 42).
- Independent gold labels created with cited conversions (tsp=5ml, tbsp=15ml, cup=240ml, oil 0.92, ghee 0.91, INDB Units.xlsx piece weights).
- Rule-based parser achieved 36.31% within +/-25% of grams on quantified lines.
- LLM-assisted parser achieved 79.62% within +/-25% of grams (125/157), PASSING the >=80% pass criterion.
- NOT_QUANTIFIED detection rate was 97.67% on vague lines ('to taste', 'for frying').
- Generated a 30-line spot-check sample (dryrun/D2_normaliser/d2_human_spotcheck_30.csv) for human verification by students.
