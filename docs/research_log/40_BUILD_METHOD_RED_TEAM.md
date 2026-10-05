# 40 Red team: building this project with session-architect/builder and cheap models (2026-10-05)
Question: can cheap models build the 5 deliverables as "labour" via builder/build.py without fake results or propagated false claims? Where does the plan break?

## Checks run (real)
- builder/test_builder.py: 19/19 PASS (tool works). Python 3.12.3; ~/subjects/cgas_env has pandas+openpyxl, no rapidfuzz.
- INDB.xlsx = 1,014 DISH rows (ASC/BFP/OSR codes), NOT raw ingredients. recipes.xlsx (10,271 lines) links ingredients to IFCT codes (e.g. L002) whose composition is NOT in the repo; only UK_fct (144) and US_fct (54) ingredient rows are included. Validation v2 therefore mapped to CoFID, not INDB.
- An unofficial transcription of IFCT 2017 exists: github.com/nodef/ifct2017, Zenodo 7088590 (528-542 foods) [V exists; accuracy/licence U].
- fried_foods_lab.csv: 69 rows; category x setting cells mostly 0-9 rows; Gupta 2016 alone = 21 rows. Stratified LOSO will have very thin strata.

## Where the plan breaks, and the fix
1. Tests check mechanics, not science. A wrong-but-plausible mapping ("ghee" -> "ghee rice") passes schema tests. FIX: architect-made GOLD fixtures (hand-verified line->grams->food code for ~150 real lines), created now, before any code exists.
2. Teaching to the test. The builder can read acceptance/ and special-case inputs. FIX: invariant tests over ALL real sample lines (790 + 558), a forbidden-pattern gate for test strings in src/, and a held-out gold half the user runs at review time.
3. Outcome thresholds invite gaming. "Frying coverage >= 80%" would get faked or tuned. FIX: tests check the PROCEDURE against an independent reference implementation; the result is whatever it is.
4. Invented constants (densities, piece weights, limits, weights). FIX: one protected, cited constants file; a test scans src/ for unexplained numeric literals.
5. False claim already in the proposal chain: "mapping to INDB (IFCT-based)" is not possible with data in hand. FIX: get IFCT (NIN / professor, or the nodef transcription after verifying it), and verify it independently: recompute INDB dish nutrients from recipes.xlsx x IFCT and compare with INDB.xlsx values.
6. Data that does not exist yet (recipe corpus, substitutions: 6 real, IFCT). Code tasks can't be accepted against missing data. FIX: data-collection jobs come first, as separate packages; their outputs are checked for provenance (URL per row, counts reconcile, robots respected) and then frozen.
7. LLM components (parse fallback, mapping assist, chatbot) are nondeterministic and need keys. FIX: deterministic core gated by tests; LLM parts behind an interface with recorded responses for tests; chatbot faithfulness checked by a deterministic "every number in the reply exists in tool outputs" checker.
8. Prose and reports (atlas findings) can't be gated by code. FIX: reports templated from results.json; a test asserts every number in the report appears in results.json; interpretation is written by an expensive-model review, not the builder.
9. Interface drift between tasks. FIX: architect writes data contracts (schemas) up front; tests enforce them.
10. Some integrity rules are process, not code (independent gold, honest language). They cannot become acceptance tests; they need the architect (gold) and review checkpoints.
11. Frying stratified model may not be estimable with 61 verified rows. Honest outcome may be "category-level ranges only"; plan for that rather than promise strata.
12. Understanding gap for the user. FIX: a human-readable SPEC (why each task exists, what its output means), plus short review checkpoints with an expensive model reading only BUILD_REPORT + diffs + results, not the whole history.
13. build.py mechanics: init commits the whole repo (18 MB, fine); failed tasks run `git clean -fd`, so untracked work outside tasks is lost; data/raw/**, data/curated inputs, constants and gold must be protected globs.

## Verdict
Feasible for the deterministic core (D1 code, D2, D3 mechanics, D4 analysis scripts, D5 backend), PROVIDED the architect first builds: gold fixtures, constants file, data contracts, the IFCT decision, and the data-collection packages. UI needs an opinionated CSS library choice. The chatbot and the interpretation of results need human or expensive-model review; the tool cannot certify them.
