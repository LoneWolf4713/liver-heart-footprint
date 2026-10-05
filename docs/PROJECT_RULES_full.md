# Project rules (full version, written 2026-10-05; for research and planning sessions. Build sessions follow AGENTS.md)
These rules were the original CLAUDE.md. Build sessions follow AGENTS.md; this full version keeps the science and data rules for research, planning and later phases.

## 1. The project in brief
- **What:** BIO544 Computational Gastronomy mini-project (IIIT-Delhi, Prof. Ganesh Bagler, Monsoon 2026). Group 45: Parth Verma (2024407), Pratyaksh Kumar (2024431).
- **Idea:** paste an Indian recipe link and get its per-serving **liver and heart footprint**: how much of the day's saturated fat, trans fat, added sugar, refined carbohydrate, energy and sodium budget it uses, against ICMR-NIN 2024 / WHO limits and the average Indian's existing intake. The app also explains *why* and suggests authentic lighter versions. It is backed by a cuisine-level study. Framing: the lab's "carbon footprint of recipes", applied to liver and heart load.
- **Submitted deliverables (5):**
  1. Indian fried-food fat dataset + frying oil-uptake model.
  2. Recipe cardiometabolic load engine (Liver and Heart profiles).
  3. Authenticity-preserving substitution engine.
  4. Cardiometabolic footprint atlas of Indian cuisine.
  5. Web app with a grounded conversational assistant.
- **Read before doing anything substantial:**
  1. `docs/project/LIVER_FOOTPRINT_PROJECT.md` (master document).
  2. `docs/submission/PROPOSAL.md` (what was promised to the professor).
  3. `docs/research_log/39_AUDIT_of_validation_v2.md` (latest validation status).
  4. `data/README.md` (what data is trustworthy).

## 2. Repository layout
```
CLAUDE.md / GEMINI.md   agent rules (identical)
README.md               human overview
docs/project/           master project document (+ PDF)
docs/submission/        proposal and form answers as submitted (do not edit; they are the record)
docs/research_log/      numbered history of research, decisions and audits (append-only)
docs/session_log.md     one entry per agent session (append-only)
reference/course/       course lecture notes, papers, assignment (read-only)
data/raw/               downloaded source data (read-only; never modify in place)
data/curated/           cleaned, provenance-tracked datasets used by the project
data/samples/           small real samples from feasibility runs (real URLs)
experiments/            feasibility and validation code + outputs (genuine runs only)
src/                    production code for the deliverables (to be built)
tests/                  tests for src/
archive/untrusted/      outputs found to be fabricated, synthetic or broken; NEVER use as data or evidence
```

## 3. Integrity rules (non-negotiable)
These exist because earlier automated sessions invented results. See research_log files 26, 31 and 36.
1. **No hardcoded or synthetic numbers.** Every number in code output, a report or the app must trace to a saved source: recipe URL + ingredient line, a food-composition row (code), or a lab/literature table row (source + table/page). Random or simulated data may be used only in clearly named unit tests, never as evidence.
2. **Reports are generated from saved results files** (e.g., `results.json`) by code. Do not type statistics by hand.
3. **Independent gold labels.** Whoever (or whatever) labels ground truth must not see the system's output. Never derive gold from the parser.
4. **Held-out validation.** A parameter fitted on data must be evaluated on data it was not fitted on (e.g., leave-one-source-out). State the split explicitly.
5. **No silent drops.** Every excluded row or recipe goes into an `exclusions.csv` with a reason. Row counts must reconcile.
6. **Identity checks.** A fetched recipe counts for a dish only if its title matches the dish. Log mismatches and do not use them.
7. **Sanity tests before computing.** No single spice/condiment over 30 g; no line silently defaulted to 100 g; stated grams win ("1½ lbs (700 g)" → 700 g); unicode fractions are parsed; per-recipe mass is plausible.
8. **Never invent food-composition values.** Use IFCT/INDB, then UK CoFID, then USDA FoodData Central (with the code cited). If no match is found, mark it UNMAPPED and report the mass share.
9. **Honest language.** Give numbers with denominators. Mark claims [V] verified or [U] unverified. Never write "conclusively", "proves", "perfect" and the like. A failed or inconclusive result is a valid result: report it plainly.
10. **Nothing in `archive/untrusted/`** may be used as data, code or evidence.

## 4. Data collection and legal rules
- Web **search**: use only the Stealth Search MCP tools (`mcp__stealth-search__*`), not built-in web search.
- Downloads: Python `requests` (or the Stealth fetch tool), ≤ 1 request/second per site, a normal user agent, and respect for robots.txt.
- **No anti-bot or Cloudflare bypass, no browser impersonation (e.g., curl_cffi), no login-walled content.** If a site blocks access, drop it and log it. Tarla Dalal and VegRecipesOfIndia block automated access, so they are excluded.
- **No Instagram, Zomato or Swiggy data**, whether scraped or hand-copied. YouTube is allowed only through the official Data API (video descriptions); never download media.
- Store extracted facts (ingredient lines, quantities) together with their source URL; never republish recipe prose.
- IFCT 2017 tables require NIN permission to reproduce electronically in a product; cite them and do not redistribute.

## 5. Scientific and design rules
- **Ingredient sums** are valid for non-fried dishes, since fat and sugar are conserved through cooking. They describe the **user's recipe as written**, not "the" dish. Validation showed a correct average but a wide per-dish spread (0.55–2.8×); restaurant/takeaway food is richer.
- **Frying:** recipes never state absorbed oil. Use the range model built from lab-measured Indian fried foods (`data/curated/fried_foods_lab.csv`), stratified by food category × setting (home / street / restaurant) × oil, and validated leave-one-source-out. A simple pooled range failed (54% coverage); stratification is required.
- **Report ranges, not point values.** Always offer a home vs restaurant/street setting.
- **Sodium:** about 78% of recipes say "salt to taste". Use the dish-specific median salt from recipes that state it, plus ingredient-bound sodium, cross-checked with national survey data. Flag it as lower-confidence.
- **Trans fat:** apply the FSSAI cap (≤ 2% of fat) for fresh oils and fats; use measured values for street, reused-oil, bakery and sweet foods. It is near zero for most home cooking.
- **Swaps:** use author-stated substitutions, recipe-context similarity and the "lightest quartile of real recipes" quantity rule. Use FlavorDB **only as a pairing fit check**, never to generate swaps (it is too sparse for fats and sugar; ghee has 1 molecule).
- **Spices are not liver or heart culprits.** The load comes from oil, ghee, butter, cream, sugar, maida, salt and frying.
- **Never a diagnosis.** Outputs are dietary estimates. The chatbot must take every number from engine tools (never from the LLM), cite sources, and decline diagnosis or medication questions.
- Main output = per-axis budget bars. A single summary index is optional and requires a sensitivity analysis over its weights.

## 6. How to work in a session
1. Read the files in §1. Check `docs/session_log.md` for what the previous sessions did.
2. Do one self-contained task with clear inputs, outputs and checks. Do not expand scope or change the submitted deliverables without the user's approval.
3. Write code in `src/` (production) or `experiments/<name>/` (exploration), with outputs saved next to the code.
4. Before finishing, append an entry to `docs/session_log.md`: date, model, task, files created or changed, key results (with denominators), open issues.
5. Significant research findings or decisions also get a new numbered file in `docs/research_log/`, with the index updated in `docs/research_log/00_README_and_method.md`.
6. If unsure about scope, data legality or a design decision, ask the user instead of guessing.

## 7. Environment
- WSL (Linux). Python 3. A virtual environment may exist at `~/subjects/cgas_env`; otherwise create `.venv/` in the repo (git-ignored).
- Large raw data stays under `data/raw/` and must not be modified in place. Derived files go to `data/curated/` with a provenance note.
