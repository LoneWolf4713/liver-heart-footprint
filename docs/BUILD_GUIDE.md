# Build guide (for you, the human)

## How to run Phase 1
1. Open a terminal in `~/subjects/CGAS/liver-heart-footprint`.
2. Start your agent tool here (Claude Code, Antigravity, Gemini CLI) with a cheap model. It reads `AGENTS.md` automatically.
3. Type `go`. The model runs `python3 build.py next`, builds one task, and the tool decides whether it is done.
4. When it says "Task done — open a new session for the next one", close the session and open a fresh one. Type `go` again.
5. There are 9 tasks (T1-T9). At any time:
   - `python3 build.py status` shows where you are;
   - `python3 build.py report` writes `BUILD_REPORT.md`;
   - `git log --oneline` shows one commit per finished task.

## What each task produces, in plain English
| Task | What it builds | How "done" is checked (by the tool, not the model) |
|---|---|---|
| T1 | Loads the Indian (IFCT 2017) + UK/US food tables into one table | Every one of 740 foods is compared with the raw files, value by value |
| T2 | Adds up nutrients for a list of ingredients | Must reproduce INDB's published values for ~995 Indian dishes |
| T3 | Reads a line like "2 cups (350 grams) tomatoes" into number, unit and name | 120 lines hand-checked by the architect + 1,339 real lines must not break |
| T4 | Maps "maida", "jeera", "बेसन" to the right food code | ≥85% of hand-checked lines get an allowed code; no invented codes |
| T5 | Converts "2 tbsp ghee" to grams using the cited measures table | Every table row is checked, plus the hand-checked lines; no default grams |
| T6 | Counts added sugar, refined carbs, salt and fat sources | Recomputed independently from the class table |
| T7 | Turns per-serving amounts into % of daily limits | Recomputed from the cited baselines file (ICMR-NIN, WHO, NSO) |
| T8 | Runs the full pipeline on a recipe, plus a command line | 71 real recipes: totals must reconcile, every exclusion has a reason |
| T9 | Compares recipe estimates with lab-measured dishes and writes a report | Test recomputes every number. There is no pass mark on the result: the honest number is the output |

## Gates on every `done`
- **Tests and science files are locked.** If the model edits the tests, the spec or the data tables, the task fails.
- **Each task may only touch its own files.**
- **No invented numbers.** Code may not contain numbers other than 0-12, 100 and 1000. Every value comes from a cited table.
- **No network, randomness, browser automation or anti-bot tools.**
- **Earlier tasks must still pass.**
- **Limited attempts:** 3 per task. After that the task is marked FAILED, its changes are rolled back (kept as a patch in `.build/`), and the build moves on.

## What the tests can and cannot vouch for
- **Verified by the tool:**
  - the code does what `docs/SPEC.md` says, on real data;
  - every number traces to a table;
  - the engine reproduces INDB's published dish values;
  - nothing is silently dropped.
- **Not verified by the tool:**
  - whether the spec's scientific choices are right (they are documented, with sources and [U] flags, in `data/curated/*` and `docs/research_log/41-42`);
  - how good the matcher is on ingredients it has never seen;
  - the wording of the T9 report.

  These need a review (below).

## Your review checkpoints
1. **After T5:** run the hidden test set, which the builder never saw:
   `bash ~/subjects/CGAS/lhf_holdout/run_holdout.sh`.
   If parse, match or grams fail there but passed the visible tests, the model fitted to the visible answers.
2. **After T9:**
   - Run the hidden set again.
   - Read `experiments/phase1_validation/REPORT.md`.
   - Run one recipe yourself: `PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python -m lhf.cli some_recipe.json`.
3. **Expensive-model review (short and cheap):** open a session with a strong model and give it only:
   - `BUILD_REPORT.md`;
   - `git log -p` for the tasks you want checked;
   - `experiments/phase1_validation/results.json` and `REPORT.md`;
   - `docs/SPEC.md`.

   Ask it to compare code and outputs with the spec, and to spot-check five lines of output against the source tables. It does not need the long research history.

## If a task FAILS
- Read `BUILD_REPORT.md` → "Not done", and the patch in `.build/<task>-failed.patch`.
- Usually the cause is a spec ambiguity or a test that is too strict for real data. That is an architect decision: bring it to an expensive-model session with `docs/SPEC.md` and the failing test output. Do not let a cheap model edit the tests.
- To retry a failed task after the architect fixes the spec or test, the state file must be edited. Ask the architect session to do it.

## Reference implementation (exists, not in this repo)
Before handing over, the architect wrote a private reference implementation and ran every acceptance test against it. All 10 tests passed, including the hidden set, which shows every test is achievable on the real data. It is kept outside the repo on purpose, so the builder writes its own code against the spec.
