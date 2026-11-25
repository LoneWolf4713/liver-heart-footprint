# Context Update — Liver & Heart Footprint Project

Paste this into your other chat to bring it up to speed.

---

## What we were debating

We were considering replacing the `difflib` fuzzy matcher in `lhf.match` (Step 7) with a **MiniLM-L6-V2 semantic embedding model** to improve ingredient name matching — specifically for Indian ingredient names like `sabudana`, `urad dal`, `keema`, etc.

## What we did to decide

We ran a full audit of all **1,014 INDB recipes** (10,271 ingredient lines) through the existing engine. The audit script is at `demo/run_indb_audit.py`. Results:

- **Before fix:** 1,908 UNMAPPED lines — **18.58% failure rate**
- We collected every UNMAPPED ingredient name and ranked by frequency
- Top failures: `fat` (218x), `castor sugar` (139x), `pepper powder` (60x), `bread` (43x), `pepper corns` (33x), `mushroom` (26x), `red chilli` (15x), `keema` (18x), etc.

## The decision on MiniLM

**We decided NOT to add MiniLM.** Here's why:

1. The failures were **not semantic gaps** — they were missing dictionary entries. `red chilli` wasn't matched not because the model didn't understand it semantically, but because `aliases.csv` only had `red chillies` (plural). That's a one-line fix, not a model problem.

2. MiniLM is **dangerous on generic terms** like `fat`, `flour`, `stock` — it would silently pick the nearest neighbour (maybe `ghee`, maybe `butter`) with no warning, corrupting lipid calculations. Aliases fail loudly (UNMAPPED = excluded + flagged). MiniLM fails quietly.

3. After analysis: MiniLM would have helped ~12-15 of the top-40 failures. It would have been risky on 3-4. Net gain: ~1-2% improvement at the cost of silent wrong matches and 500MB of new dependencies.

## What we actually fixed

We added **85 new alias rows** to `data/curated/aliases.csv` covering the high-frequency genuine gaps:

- Chilli variants: `red chilli`, `whole red chilli`, `dry red chilli`, `dried red chillies` → `G022`
- Pepper: `pepper powder`, `pepper corns`, `peppercorns`, `pepper corn` → `G031`
- Hindi spice variants: `haldi powder` → `G033`, `jaiphal` → `G028`, `sonth`/`saunth` → `G554`, `amchur`/`aamchur`/`mango powder` → `G535`, `kalonji`/`nigella seeds` → `A512`, `jeera powder`/`roasted cumin powder` → `G025`
- Mushrooms: `mushroom`, `mushrooms` → `J001`
- Bread: `bread`, `bread slice`, `bread crumbs`, `double roti` → `U511`; `brown bread` → `U501`
- Flour: `flour`, `plain flour` → `A018`; `cornflour` → `A503`; `makki ka atta` → `A006`
- Vermicelli: `vermicelli`, `seviyan`, `sewaiyan` → `A023`
- Lentils: `lentils`, `lentil` → `B013`; `channa dal` → `B001`; `washed urad dal`, `black gram dehusked` → `B003`
- Vegetables: `beetroot` → `F001`; `radish`, `mooli` → `F010`; `turnip` → `F501`; `sprouted moong` → `B011`
- Meat: `keema`, `mince`, `minced meat`, `kheema` → `O502`; `chicken mince`, `chicken keema` → `N500`
- Fat: `fat`, `melted fat`, `shortening`, `cooking fat` → `T508`
- Misc: `kewra essence`/`kewra water` → `K505`; `bengal gram flour` → `A504`; `processed cheese` → `L505`

## Results after the fix

- **After fix:** 1,085 UNMAPPED lines — **10.56% failure rate**
- **823 lines fixed** (43.1% of original failures resolved) with zero new dependencies
- Recipes with zero UNMAPPED: **454 / 1014** (was 191)
- Recipes with >20% UNMAPPED: **220 / 1014** (was 410)

## What remains UNMAPPED (and why we're not fixing it)

The remaining 1,085 failures are almost entirely Western/bakery items: `castor sugar`, `vanilla essence`, `mayonnaise`, `glaced cherries`, `cocoa`, `pineapple juice`, `chicken stock`, `citric acid`. These would not appear in a standard Indian recipe demo. We are leaving these alone.

## Current state of the project

- `src/lhf/` — untouched, all existing tests still pass
- `data/curated/aliases.csv` — 4,198 rows (was 4,113), patch logged in `data/curated/aliases_patch.csv`
- `demo/indb_audit_unmapped.csv` — updated with post-fix UNMAPPED data
- `demo/indb_audit_coverage.csv` — updated coverage per recipe
- `demo/run_indb_audit.py` — audit runner (re-runnable anytime)
- `demo/analyze_audit.py` — generates the markdown summary report

## The defense answer (if asked about NLP vs Regex)

> *"We ran a full empirical audit of all 1,014 INDB recipes. We found 18.58% UNMAPPED rate and analyzed the failure distribution. The top failures were concentrated in missing aliases, not semantic vocabulary gaps. MiniLM would have solved ~1-2% of additional failures while introducing silent mis-mappings on generic terms like 'fat' that would corrupt lipid calculations with no warning. We chose deterministic alias curation: 85 new entries dropped the UNMAPPED rate to 10.56%, fixing 43% of all failures with zero new dependencies and 100% auditability."*
