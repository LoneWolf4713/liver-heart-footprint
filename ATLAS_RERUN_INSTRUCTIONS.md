# Context Update — Frying Correction Built, Atlas Must Be Re-Run

Paste this into your other chat. It needs to re-run Deliverable 3 (the Atlas).

---

## What Changed Since You Last Ran the Atlas

A critical bug in the pipeline was fixed and a new module was added. **The Atlas figures and CSVs on disk are now stale and must be regenerated.**

### The Bug (now fixed)

When a recipe listed a deep-frying oil bath like `"500 ml oil for deep frying"`, the engine counted all 500ml (~460g of fat) as consumed nutrients. This produced physically impossible numbers — samosa showing 61g fat per serving, gulab jamun showing 204g fat per serving in the INDB textbook recipes. These values made the textbook-vs-web comparison table meaningless.

### The Fix

A new module `src/lhf/frying.py` was added and hooked into `src/lhf/pipeline.py`.

It detects frying bath lines (cooking oil ingredient that contains a phrase like "for deep frying", "to deep fry", "for frying", etc., AND whose quantity exceeds 50g). When detected:
1. The stated oil bath is **excluded** from nutrient totals (marked `FRYING_BATH`)
2. **Lab-measured absorbed fat** from `data/curated/fried_foods_lab.csv` is substituted instead
3. The footprint bars are recomputed with the corrected values
4. A `FRYING_CORRECTED` warning is added to the result

The lab dataset (`fried_foods_lab.csv`) has 60+ entries for samosa, pakora, puri, bhatura, gulab jamun, mathri, etc. from Gupta 2016, Joshee 2019, Jain 2024, UK CoFID 2021.

### Verified Regression Results (confirmed working)

- `paneer_butter_masala` fat per serving: **22.75g — unchanged** (no frying bath)
- `dal_makhani` fat per serving: **11.84g — unchanged**
- `chicken_biryani` fat per serving: **27.95g — unchanged**
- Samosa test (500ml oil bath): fat per serving **11.33g** (was 61.24g)
- Lab match used: `Samosa → 12.4g fat/100g` (median of Joshee 2019 + Sakhale 2011 + Gupta 2016)
- All 9 acceptance tests (T1–T9) **PASS**

---

## What You Need to Do

### Step 1 — Re-run the Atlas pipeline

```bash
cd /home/prtyksh/subjects/CGAS/liver-heart-footprint
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python experiments/atlas/run_atlas.py
```

This overwrites all files in `experiments/atlas/`. It processes 1,014 INDB recipes + 71 web recipes. It takes a few minutes. Let it finish completely.

### Step 2 — Verify the fried food numbers are now sane

After the run, check the textbook-vs-web comparison CSV:

```bash
cat experiments/atlas/atlas_textbook_vs_web.csv
```

The key columns are `indb_fat_g`, `web_fat_g`, and `fat_inflation_ratio`.

**Before the fix**, these were broken:
- `samosa`: indb_fat_g = 170g, web = 6g, ratio = 0.04 (nonsense)
- `gulab jamun`: indb_fat_g = 204g, web = 3g, ratio = 0.02 (nonsense)
- `onion pakora`: indb_fat_g = 484g, web = 3g, ratio = 0.01 (nonsense)

**After the fix**, these should be plausible:
- `samosa`: indb_fat_g should be in the range of 5–20g per serving
- `gulab jamun`: indb_fat_g should be in the range of 5–20g per serving
- `onion pakora`: indb_fat_g should be in the range of 3–15g per serving
- Ratios should be close to 1.0 (textbook and web recipes should roughly agree now)

Also check `experiments/atlas/atlas_metrics.json` — the `overall_median_fat_inflation` should now be much closer to 1.0 (previously it was 0.6, skewed by the broken fried food numbers).

### Step 3 — Regenerate the ATLAS_REPORT.md

After confirming the CSV numbers look sane, regenerate the markdown report:

```bash
PYTHONPATH=src /home/prtyksh/subjects/cgas_env/bin/python experiments/atlas/analyze_audit.py
```

(If `analyze_audit.py` does not regenerate `ATLAS_REPORT.md`, the atlas script itself may regenerate it — check if `run_atlas.py` already writes the report at the end.)

### Step 4 — Report back with these specific numbers

When done, report:
1. The new `atlas_textbook_vs_web.csv` rows for: `samosa`, `gulab jamun`, `onion pakora`, `poha`, `chicken biryani`
2. The new `overall_median_fat_inflation` from `atlas_metrics.json`
3. Whether `MASS_IMPLAUSIBLE` warnings dropped for fried recipes (check `experiments/atlas/atlas_coverage.csv` if it exists, or look at console output)
4. Any recipes that **still** show implausibly high fat (>50g per serving) — these would be cases the frying correction didn't catch (e.g., if the dish name didn't match the lab data or the oil phrasing was unusual)
5. The full updated content of `experiments/atlas/atlas_category_summary.csv`

---

## Important Notes

- **Do NOT modify `src/lhf/pipeline.py` or `src/lhf/frying.py`** — these are already correct and tested
- **Do NOT modify `data/curated/fried_foods_lab.csv`** — read-only reference data
- If `run_atlas.py` crashes, read the traceback carefully — it likely means a recipe JSON has an unexpected format. Report the exact error
- The Soups & Stews sodium anomaly (1028% of daily limit) is a **known data artifact** from stock concentrate recipes in INDB — do not try to fix it, just note it in the report
