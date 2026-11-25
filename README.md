# Liver and Heart Footprint of Indian Recipes

Course: BIO544 Computational Gastronomy, IIIT-Delhi (Monsoon 2026)
Instructor: Prof. Ganesh Bagler
Group 45: Parth Verma (2024407), Pratyaksh Kumar (2024431)
Live Web App: https://liver-heart-footprint.onrender.com

## Overview

This project computes the per-serving Liver and Heart footprint of Indian recipes. It tracks two daily clinical budgets separately against ICMR-NIN 2024, WHO, and MoSPI HCES 2022-24 reference thresholds (2,240 kcal urban adult baseline):

- **Liver view:** saturated fat (24.9 g general / 17.4 g high-risk), energy (2,240 kcal), added free sugar (25.0 g), and refined white starch.
- **Heart view:** saturated fat, energy, total fat (74.7 g), and sodium (1,967 mg from 5.0 g salt).

The calculation pipeline handles Indian household measures (243 density rules across 4,204 ingredient aliases paired with IFCT 2017 and INDB composition tables) and fixes deep-frying recipes (`103` INDB dishes) by dropping unconsumed pan-oil volume and substituting empirical lab fat retention values across five preparation settings (`street`, `home`, `restaurant-takeaway`, `retail-packaged`, and `lab-controlled`).

## Quickstart: Run Locally

Install dependencies and start the FastAPI web app:

```bash
uv pip install -r requirements.txt
PYTHONPATH=src uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` (or visit https://liver-heart-footprint.onrender.com) to analyze either a public Indian recipe URL or pasted ingredient text, switch frying environments, scale portions (`1x`, `2x`, `per 100g`), or explore the lab dataset, pipeline walkthrough, and 1,085-recipe Atlas.

## Project Structure & Deliverables

1. **Curated Fried-Food Lab Dataset (`data/curated/fried_foods_lab.csv`)**
   67 primary-verified laboratory measurements spanning 227 fried samples across 9 published studies (`Gupta 2016`, `UK CoFID 2021`, `Joshee 2019`, `Jain 2024`, `safefood 2015`, `Chen 2009`, `Sakhale 2011 PMC3551041`, `Yadav 2012 PMC3550836`, `Gaikwad 2022 PMC8814218`). Removing kadai frying baths strips 42.5 kg of unconsumed oil across 103 fried textbook dishes.
2. **Core Python Engine (`src/lhf/`)**
   Five-stage pipeline (`parse.py`, `match.py`, `grams.py`, `classify.py`, `frying.py`, `compute.py`, `footprint.py`, `pipeline.py`, `cli.py`). Reproduced 100% of 7 core nutrients and 97.5% of carbohydrates across 995 complete INDB recipes, hit a 1.06x median fat ratio across 10 lab-tested cooked dishes (31 comparisons), and scored 100.0% end-to-end across 160 annotated ingredient lines.
3. **Indian Dish Footprint Atlas (`experiments/atlas/run_atlas.py`)**
   Audited 1,014 INDB manuals (932 with serving counts across 11 culinary categories) alongside 71 web recipes across 19 staple dishes from 10 portals. Key outputs (`atlas_metrics.json`, `ATLAS_REPORT.md`, `fig1` to `fig4`) document high-sugar sweet loads (61.9% daily cap in Sweets, 60.0% in Beverages), fat culprit splits (63.6% dairy in Sweets vs. 46.3% oil in Snacks), 1.18x saturated fat inflation online across 12 non-fried dishes, and the INDB `K506`/`K507` bouillon-cube sodium coding error across 26 of 47 soups.
4. **Live Web Application (`app/main.py`, `app/scraper.py`, `app/index.html`)**
   FastAPI backend with `schema.org/Recipe` JSON-LD extraction, `recipe-scrapers` fallback, instruction-based `"deep fry"` detection, and mobile/desktop UI verified across 13/13 live blog URLs from 5 Indian portals with exact engine parity.

## CLI & Reproduction Commands

```bash
# Analyse a single recipe JSON from the command line
PYTHONPATH=src python -m lhf.cli demo/samosa_test.json --setting urban --risk general --frying-setting street

# Regenerate Atlas tables, figures, and web JSON payloads
PYTHONPATH=src python experiments/atlas/run_atlas.py

# Run verification suites
PYTHONPATH=src python -m unittest discover -s tests -q
PYTHONPATH=src python acceptance/test_rules.py
PYTHONPATH=src python acceptance/test_t8_pipeline.py
PYTHONPATH=src python acceptance/test_t9_validation.py
PYTHONPATH=src python experiments/d1_verification/verify_d1.py
PYTHONPATH=src python experiments/d2_verification/verify_d2.py
```
