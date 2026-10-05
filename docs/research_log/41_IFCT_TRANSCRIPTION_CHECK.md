# 41 IFCT 2017 transcription check (2026-10-05)
Problem: INDB (data/raw/indb) releases dish totals but not the IFCT ingredient table (NIN copyright). Our engine needs ingredient-level Indian composition data. The proposal said "mapping to INDB (IFCT-based)", which was not possible with data in hand (file 40, point 5).

Method: INDB.do (lines 137-270) computes dishes as sum(grams x nutrient/100)/sum(grams), with no yield or retention factor. experiments/ifct_check/replicate.py ports this exactly, substitutes the public transcription (nodef/ifct2017, commit b65621d) for NIN's table, and compares with INDB.xlsx. Outputs: results.json, per_recipe.csv, per_code.csv, run_output.txt.

Results (from results.json):
- 1,014 recipes; 19 excluded (use 4 codes in no table: D091, D501, F500, O064).
- Control, UK/US codes only (tests the port): 13/13 agree on every nutrient.
- Test, uses IFCT codes: 982/982 agree on energy, fat, SFA, sodium, protein, fibre, free sugar (max abs gap: fat 0.0, energy 0.0003 kJ). Carbohydrate 957/982 (25 differ by <=1.34 g/100 g).
Interpretation:
- [V] The transcription's values are the same values INDB used, for the 137 IFCT codes INDB recipes use. INDB states its IFCT data came from NIN.
- [U] Accuracy against the printed book is not checked directly (no book in hand); if INDB itself used this transcription, the check shows consistency, not independent accuracy.
- [U] The other ~405 transcription codes are not covered by this check.
- Defect found: all 14 fats/oils (T001-T014) have energy = 0. INDB avoids this by using UK codes for all fats. Rule: never use the transcription's energy for fats.
Decision: use the transcription for ingredient mapping, IFCT first, then CoFID/USDA fallback, citing NIN; do not redistribute the table. The proposal claim "IFCT-based mapping" is now supportable.
