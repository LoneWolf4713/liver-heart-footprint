# D4 Web App — Architecture & Flow Discussion

**Date:** 2026-11-24  
**Purpose:** Map out what D4 looks like before writing a single line of code.

---

## 1. What We Actually Promised (From the Proposal)

> *"A web app where a user enters a recipe link or ingredient list and sees the recipe's Liver and Heart load per serving and the ingredients contributing most to it."*

Two input modes were promised:
1. **A recipe link** (URL → scrape schema.org Recipe data)
2. **An ingredient list** (typed or pasted as text)

> IMPORTANT: We promised a URL input mode. That's not optional — it was in the proposal. If we only do paste/upload, the professor will notice. The URL path doesn't need to work flawlessly, but it needs to exist.

We did NOT promise a JSON file upload. That's an internal developer convenience, not a user-facing feature. Don't ship it as the primary interface.

---

## 2. The Tab Structure (Proposal-Aligned)

The app has **five tabs**. The professor opens it, he sees all four deliverables plus a sources tab — no juggling, no switching contexts.

```
+------------------------------------------------------------------+
|  Liver & Heart Footprint of Indian Recipes                       |
|  BIO544 Computational Gastronomy · Group 45                      |
+----------+----------+----------+----------+---------------------+
|  D1      |  D2      |  D3      |  D4      |  About & Sources    |
|  Lab     |  Engine  |  Atlas   |  Try It  |                     |
|  Dataset |  Explainer| Results |  Live    |                     |
+----------+----------+----------+----------+---------------------+
```

Each tab is a **standalone story**. The professor can jump to any tab at any point in the presentation without needing the previous tab's context.

---

## 3. Tab-by-Tab Breakdown

---

### Tab 1 — D1: Lab Dataset

**What it shows:** The fried foods fat dataset we compiled from published studies.

**Flow:**
- A short one-paragraph explanation of *why* we needed a lab dataset (textbook recipes say "480ml oil for frying" — that's the bath, not what the food absorbs).
- A filterable, searchable table of `fried_foods_lab.csv` — dish name, fat g/100g, SFA%, source study, year.
- A bar chart: fat content by food category (deep-fried snacks vs. shallow-fried vs. stir-fried).
- A callout box: "Lab-measured values are 3–8× lower than the stated bath oil volume in textbook recipes."

**Professor sees:** We didn't make up the absorbed fat numbers. These come from published studies. The table is auditable — he can click a source and read the paper.

---

### Tab 2 — D2: Engine Explainer

**What it shows:** How the pipeline works, step by step, with real example numbers.

**Flow:**
This is not a wall of text. It's a **step-by-step walkthrough** using a fixed example (Samosa) as the running illustration.

```
Step 1: Parse Ingredients
  "25g maida, 100g potatoes, 2 tbsp oil" → structured lines

Step 2: Unit Conversion
  "2 tbsp" → 28g  (using ICMR-NIN household measures)

Step 3: Ingredient Mapping
  "maida" → Refined Wheat Flour [A503, IFCT 2017]

Step 4: Nutrient Lookup
  A503 → fat: 1.1g/100g, SFA: 0.3g/100g, energy: 348 kcal/100g

Step 5: Frying Correction (if applicable)
  Bath oil (480ml) → EXCLUDED
  Absorbed fat → 12.4g/100g × fried mass → substituted in

Step 6: Footprint Calculation
  Total fat per serving / ICMR-NIN daily limit × 100 = % of daily limit
```

Each step has: a plain English sentence + the number it produced for the samosa example.

At the bottom: a small table showing what ICMR-NIN daily limits we're using (SFA ≤10% energy, sodium ≤2000mg, added sugar ≤10% energy, etc.). This is the source of every percentage bar the app shows.

**Professor sees:** The pipeline is transparent and reproducible. Every number has a traceable origin.

---

### Tab 3 — D3: Atlas Results

**What it shows:** The cuisine-level analysis across 1,014 INDB recipes + web recipes.

**Flow:**
- Top-level stat cards: 1,014 recipes analyzed · 103 fried recipes corrected · Median fat inflation 0.77x
- **Chart 1:** Box plot or bar chart — fat/serving by dish category (curries, snacks, sweets, breads, rice dishes). Which category is highest?
- **Chart 2:** The textbook vs. web comparison (the 5-dish table we have). Show it visually — side-by-side bars for INDB fat vs. web fat per serving.
- **Chart 3:** Top 10 ingredient groups driving liver load across all recipes. (Which ingredient class — dairy fat, frying oil, refined carbs — contributes most on average?)
- **Finding callout:** "Frying oil as stated in textbook recipes overstates fat by up to 16×. After lab-based correction, textbook recipes are actually 23% lighter than popular web recipes (0.77x median)."

A footnote on the gulab jamun anomaly if the professor asks.

**Professor sees:** D3 is a real analysis with a real finding, not just a data dump. The frying correction changed the story — before correction it looked like textbooks were insane, after correction it inverted.

---

### Tab 4 — D4: Try It (The Live Demo)

This is the core of the presentation. It needs to be **the best-looking tab**.

**Input Section (top of page):**

Two input options, as a toggle:

```
  ( ) Paste a recipe URL    (•) Type / paste ingredients
```

**URL mode:** User pastes a URL (e.g. from Hebbar's Kitchen, Swasthi's recipes). App scrapes it, extracts ingredient list, shows "Found 12 ingredients → Analyzing..." and runs.

**Text mode:** A large text area. User types or pastes ingredient lines like:
```
250g paneer
2 tbsp oil
1 tsp cumin
100ml cream
1 tsp red chilli powder
salt to taste
```

A single "Analyze Recipe" button. The name of the dish is typed above the ingredients (used for frying detection and the display header).

**Output Section (what appears after clicking Analyze):**

Split into two columns:

**Left column — The Footprint:**

Two side-by-side gauge/bar panels:

```
HEART VIEW                   LIVER VIEW
----------------------------  ----------------------------
Saturated Fat  [████░░]  62%  Saturated Fat  [████░░]  62%
Sodium         [██░░░░]  38%  Added Sugar    [█░░░░░]  12%
Total Fat      [███░░░]  54%  Refined Carbs  [██░░░░]  31%
Energy         [██░░░░]  41%  Energy         [██░░░░]  41%
```

Color coding:
- 0–33%: Green (safe)
- 34–66%: Yellow (caution)
- 67–100%: Red (high)
- >100%: Dark red with a warning icon

Below the bars: a single-sentence plain English verdict. E.g.:
> "One serving of Paneer Butter Masala covers 62% of your daily saturated fat limit. The main drivers are cream and butter."

**Right column — Ingredient Breakdown:**

A horizontal stacked bar or a simple ranked list showing:
```
Which ingredients drive Saturated Fat?
  Cream          [████████████]  58%
  Butter         [████]          21%
  Paneer         [██]            11%
  Other          [█]             10%
```

Same breakdown for whichever nutrient is the worst offender.

**Frying Correction Banner (shown only for fried dishes):**

A clearly visible callout:
> ⚡ Frying correction applied. Bath oil (480ml) excluded. Absorbed fat estimated at 28.6g using lab data for Onion Pakora / Bhaji (14.7g/100g). Without correction, fat would read 477.6g — 16× higher.

This banner makes D1 visible inside D4. The professor doesn't need to go to D1 to understand why the numbers aren't insane.

**Coverage Report (small, below the main output):**

A simple line:
> *12 of 14 ingredients matched · 2 unmatched (skipped): "dried fenugreek leaves", "chaat masala"*

Clicking "2 unmatched" expands to show which lines were skipped — honest, transparent.

---

### Tab 5 — About & Sources

**Three sections:**

1. **Data Sources** — a numbered list matching our proposal's Section 5. Each source links to the paper/dataset where possible. INDB, IFCT 2017, ICMR-NIN 2024, our lab CSV, etc.

2. **How We Built This** — 4 bullet points max. No jargon. "We use regex parsing, not an LLM, so unit conversions are deterministic and reproducible." "Frying correction uses lab-measured values, not the stated bath volume." "Daily limits from ICMR-NIN 2024 and WHO 2023."

3. **Known Limitations** — 4 bullet points.
   - Ingredients without a quantity (e.g. "salt to taste") are skipped, not guessed.
   - Composite fried dishes (kofta in curry) are not frying-corrected in the current version.
   - Gulab jamun: sugar syrup bath inflates absorbed fat estimate. Flagged.
   - Restaurant versions of dishes are typically richer than the recipes analyzed.

---

## 4. The URL Scraping Question

The proposal promised it. Here's how to think about it:

**Realistic scope:** You don't need it to work on every URL. It needs to work on the 3–4 URLs you demo during the presentation. Pick sites that use `schema.org/Recipe` markup (Hebbars Kitchen, Swasthi's Recipes, Vegrecipesofindia — all do). The scraper reads the structured JSON-LD block embedded in the page, not raw HTML.

**Fallback that's still honest:** If scraping fails (the site blocks bots), the app shows "Could not auto-read this URL. Paste the ingredients below." and drops the user into text mode. This is a valid, honest fallback — not a failure.

**Don't demo URLs live** if you're unsure about network access in the presentation room. Have 2–3 URLs pre-loaded as "demo recipes" buttons that bypass scraping entirely (they just load pre-fetched ingredient lists). The URL box still exists and still works — you just have a safety net.

---

## 5. What to Demo in Front of the Professor (Suggested Order)

1. Open **Tab 4** first. No introduction needed — just paste a URL or start typing "samosa" ingredients. Run it. Show the frying correction banner appearing. Show the bars.
2. Point out: "The frying correction is using the dataset from D1." Switch to **Tab 1**. Show the lab table. Come back.
3. Switch to **Tab 2**. Walk through the samosa example step by step — "here's what it did for the recipe you just ran."
4. Switch to **Tab 3**. Show the Atlas. "We ran this on 1,014 recipes. Here's what we found at the cuisine level."
5. Switch to **Tab 5** for any methodology questions.

The whole demo should be under 10 minutes. The professor should be able to try a dish himself.

---

## 6. What We Are NOT Building

- No user accounts, no history, no database of past queries.
- No "suggest a healthier version" feature (out of scope).
- No mobile optimization needed (this is a lab demo, not a product).
- No JSON file upload as a primary feature (use text paste instead — it's cleaner).

---

## 7. Open Questions Before Building

1. **Network access in the presentation room?** If yes, URL scraping is live. If no, pre-load demo recipes as buttons.
2. **Presentation device?** Your laptop → no issue. Lab machine → test beforehand.
3. **Tech stack decision** (you said you'll handle this, noted): Just make sure the backend `analyse_recipe()` call path is the same pipeline we already have — don't rewrite the engine for the app.
4. **Language of the app:** English only, or should the disclaimer say "Indian recipes / Indian daily limits"? Recommend the latter — it differentiates from generic calorie counters.
