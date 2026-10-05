# Liver and Heart Footprint of Indian Recipes: agent instructions

You are one session in a build. `CLAUDE.md` and `GEMINI.md` point to this file. These rules override your defaults.

## Start: do this first, without waiting to be asked
```
python3 build.py init     # only if the folder .build/ does not exist yet
python3 build.py next
```
`next` prints your task: what to build, which files you may change, which acceptance checks must pass, what earlier tasks did, and why your last attempt failed (if it did). "go" or "start" means: run `next` and execute that task.

**Each session does exactly ONE task.** When `done` says STOP, stop and tell the user exactly: "Task done — open a new session for the next one."

## Hard rules for building
1. **Change only the files `next` allows.** Other tasks own the other files. You may also add your own tests in `tests/` and append to `docs/session_log.md`.
2. **Never edit protected files:**
   - `order.json`, `build.py`, `acceptance/`, `AGENTS.md`, `docs/SPEC.md`;
   - `data/raw/`, `data/samples/`;
   - the architect's tables in `data/curated/` (measures, constants, classes, baselines, fried_foods_lab, validation_ground_truth).

   They define "done" and the science. Fix your code, not the tests or data. The tool detects any change. If a protected file looks wrong, write a note (`python3 build.py note --file note.txt`) explaining it, and stop.
3. **Read before writing.** Read `docs/SPEC.md` sections 0-1 and your task's section. Open the real input files and look at them before you assume a column name, a unit or a format. Never assume a function or file exists; check.
4. **"Done" is decided by the tool, not by you.** Run `python3 build.py check` as often as you like (it changes nothing), and `python3 build.py done` when the checks pass. After the allowed number of failed `done` attempts, the task is recorded as FAILED and rolled back. That is fine: an honest failure beats faked success.
5. **Stay small and literal.** Build exactly what the task says. No extra features, no refactoring of other tasks' code, no new dependencies.
6. **Save progress** with `python3 build.py note --file note.txt` before pausing. Write free text into files, never as shell arguments.

## Integrity rules (the reason this project exists in this form)
Earlier automated sessions invented results (see `docs/research_log/26`, `31`, `36`). So:
1. **No invented numbers.** Every number in code output traces to a source row: a composition table code, a measures/constants/baselines row (each has a citation), or a recipe line. Code contains no numeric literals except 0-12, 100 and 1000; the test enforces this.
2. **No defaults for missing data.** If a quantity, unit or ingredient cannot be handled, return the documented UNQUANTIFIED / UNMAPPED / UNQUANTIFIABLE result. Never use a silent 100 g, never "assume 1 tsp".
3. **Never hard-code test answers.** Don't copy gold lines or expected values into code or `aliases.csv`. A hidden test set is run by the user afterwards.
4. **Reports are generated from results files by code.** Never type a statistic by hand.
5. **Honest language.** Give numbers with denominators. Never write "proves", "conclusively" or "perfect". An inconclusive or failed result is a valid result.
6. **Nothing in `archive/untrusted/`** may be used as data, code or evidence.

## Data and legal rules
- No network access in code. Phase 1 works only on files already in the repo.
- If web search is ever needed outside the build, use only the Stealth Search MCP tools. Never use anti-bot bypass, browser impersonation, Instagram, Zomato or Swiggy data.
- The IFCT 2017 transcription (`data/raw/ifct2017_transcription/`) is NIN-copyrighted data. Use it for computation only, and never publish the table or push this repo publicly with it inside.

## Science rules (context; the spec turns them into code)
- Ingredient sums describe the **recipe as written**, not "the" dish. Restaurant and takeaway food is richer.
- Frying oil uptake, trans fat, "salt to taste" imputation and swaps are later phases. Phase 1 must not guess them.
- Spices are not the liver/heart culprits. Oil, ghee, butter, cream, sugar, maida, salt and frying are.
- Outputs are dietary estimates, never a diagnosis.

## Repository map
| Path | What |
|---|---|
| `docs/SPEC.md` | What Phase 1 builds (contracts). Read your section. |
| `docs/BUILD_GUIDE.md` | For the human: how to run and review the build |
| `docs/project/LIVER_FOOTPRINT_PROJECT.md` | Master project document (background; not needed for a build task) |
| `docs/research_log/` | Numbered history and audits (read-only) |
| `docs/session_log.md` | Append one line per session: date, model, task, result |
| `data/raw/` | Source data (read-only) |
| `data/curated/` | Cited tables (read-only, except `aliases.csv`, which task T4 creates) |
| `data/samples/recipes_phase1.jsonl` | 71 real recipes (1,339 lines) used by the tests |
| `src/lhf/` | The package you build |
| `acceptance/` | Tests that define "done" (read-only) |
| `experiments/` | Earlier genuine experiments (read-only), and `phase1_validation/` (task T9) |
| `archive/untrusted/` | Fabricated or broken outputs from earlier sessions. Never use. |
