# Liver and Heart Footprint of Indian Recipes

**Course:** BIO544 Computational Gastronomy, IIIT-Delhi (Monsoon 2026)  
**Instructor:** Prof. Ganesh Bagler  
**Group 45:** Parth Verma (`2024407`) · Pratyaksh Kumar (`2024431`)

---

## Overview

This project defines and computes the **Liver & Heart Footprint** of Indian recipes—quantifying per-serving **saturated fat (SFA)**, **added free sugar**, **refined starch**, **sodium**, **total fat**, and **energy** against **ICMR-NIN Dietary Guidelines (2024)**, **WHO** thresholds, and **NSO HCES 2022–24** baselines (`2,240 kcal/day` urban adult).

Unlike generic Western calorie calculators, the pipeline grounds ingredient quantities in **IFCT 2017 / INDB** household density rules and corrects deep-frying recipes (`103` INDB dishes) by replacing oil-bath volumes (`"500 ml oil for deep frying"`) with empirical **Soxhlet / Proximate / GC-FID** lab fat absorption values across preparation settings (`street`, `home`, `restaurant-takeaway`, `retail-packaged`, `lab-controlled`).

---

## Quickstart: Run the Web Application (Deliverable 4)

```bash
# 1. Create / activate Python environment and install dependencies
uv pip install -r requirements.txt

# 2. Launch the FastAPI web app & live URL scraper
PYTHONPATH=src uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **`http://127.0.0.1:8000`** in your browser:
- **Paste a Recipe URL:** Scrapes `schema.org/Recipe` JSON-LD (or falls back via `recipe-scrapers` / editable ingredient paste) and computes the live footprint via `POST /api/scrape` → `POST /api/analyze`.
- **Paste Ingredients:** Analyzes arbitrary typed ingredient lines, servings count, frying cooking setting, `1× / 2× / Per-100g` scaling, and General (`24.9g SFA`) vs. High-Risk (`17.4g SFA`) ceilings.
- **Inspect All 4 Deliverables (`D1`–`D4`):** Interactive tabs covering the 67-row Fried-Food Lab Dataset (`D1`), 5-Stage Deterministic Engine (`D2`), 1,014-Recipe Cuisine Atlas (`D3`), and Live Analyzer (`D4`).

---

## Four Course Deliverables

| Deliverable | Description | Key Artifacts |
| :--- | :--- | :--- |
| **D1 · Fried-Food Lab Dataset** | `67` curated empirical rows (`227` samples across `9` verified studies: Gupta 2016, UK CoFID 2021, Safefood 2015, Joshee 2019, Jain 2024, Chen 2009, Sakhale 2011, Yadav 2012, Gaikwad 2022) capturing oil-retention spread by setting. | `data/curated/fried_foods_lab.csv`, `src/lhf/frying.py` |
| **D2 · Core Computational Engine** | Deterministic grammar parser (`parse.py`), `4,204`-alias IFCT/INDB matcher (`match.py`), `243` Indian measure conversions (`grams.py`), nutrient classifier (`classify.py`), frying correction, and daily budget scorer. | `src/lhf/` (`pipeline.py`, `cli.py`) |
| **D3 · Cuisine Footprint Atlas** | Macro audit of `1,014` INDB recipes (`932` with servings) + `71` web recipes across `11` categories (`fig1`–`fig4`) comparing textbook vs. modern recipes (`1.10×` fat / `1.18×` SFA median inflation across `12` comparable pairs). | `experiments/atlas/run_atlas.py`, `atlas_metrics.json`, `fig1`–`fig4.png` |
| **D4 · Interactive Web Application** | FastAPI backend (`app/main.py`, `app/scraper.py`) + Puppertino/Alpine.js SPA (`app/index.html`) with live URL scraping, custom recipe analysis, frying setting & provenance drawers, portion scaling, and organ breakdowns. | `app/main.py`, `app/scraper.py`, `app/index.html` |

---

## CLI & Atlas Usage

```bash
# Run CLI analysis on a single recipe JSON
PYTHONPATH=src python -m lhf.cli demo/samosa_test.json --setting urban --risk general --frying-setting street

# Regenerate Deliverable 3 Atlas CSVs, metrics, figures, and app data payload
PYTHONPATH=src python experiments/atlas/run_atlas.py
```

---

## Verification & Tests

```bash
# Full unit + API + scraper test suite
PYTHONPATH=src:. python -m unittest discover -s tests -v

# Engine rule & empirical validation checks
PYTHONPATH=src python acceptance/test_rules.py
PYTHONPATH=src python acceptance/test_t8_pipeline.py
PYTHONPATH=src python acceptance/test_t9_validation.py
```
