# IFCT 2017 transcription (unofficial)
- Source: github.com/nodef/ifct2017, file compositions/index.csv, commit in commit.txt, fetched_at.txt, sha256.txt. 542 foods x 421 columns. Units: proximates and fatty acids g/100 g, energy kJ/100 g (enerc), sodium g/100 g (na).
- Original data: Indian Food Composition Tables 2017, ICMR-National Institute of Nutrition, Hyderabad (Longvah et al.). Cite NIN as the data source.
- Repo licence is AGPL-3.0 (code); the data's copyright belongs to NIN. Use for research computation only; do NOT redistribute this table or ship it inside a public app/repo.
- Verification: experiments/ifct_check (research_log 41). Reproduces INDB's published per-100 g values for 982/982 dishes that use IFCT codes (energy, fat, SFA, sodium, protein, fibre, free sugar; carbohydrate 957/982, max gap 1.34 g). This covers the 137 IFCT codes used by INDB recipes; the other ~405 codes are NOT verified by this check.
- Known defect: all 14 fats/oils (T001-T014, incl. ghee, vanaspati) have enerc = 0. Never use the transcription's energy for fats; use INDB's UK codes (T5xx) or energy = 37 kJ/g fat. INDB itself uses UK codes for all fats.
