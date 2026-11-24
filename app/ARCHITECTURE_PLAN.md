# D4 Architecture & Implementation Plan
## Interactive Web Application — Liver & Heart Footprint of Indian Recipes
**Course:** BIO544 Computational Gastronomy, IIIT-Delhi (Monsoon 2026)  
**Group:** 45 — Parth Verma (2024407), Pratyaksh Kumar (2024431)  
**Instructor:** Prof. Ganesh Bagler  

---

## 1. Executive Vision: Demo Machine vs. Commercial MVP

This deliverable (D4) is not a commercial SaaS MVP; it is an **academic evaluation and defense instrument**.

### Design Principles:
1. **Self-Explanatory & Provenance-Rich:** Every figure, percentage, and limit on screen tracks back to an empirical publication (ICMR-NIN 2024, WHO 2012/2015, Gupta 2016, UK CoFID, ICMR-INDIAB) within one click or tooltip. The presenter never needs to switch to a slide deck to defend a methodology.
2. **Honest Scientific Transparency:** Boundary conditions (e.g. `SALT_UNQUANTIFIED` lower bound, Gulab Jamun syrup-mass frying anomaly, pot-level soup sodium artifacts) are clearly flagged with diagnostic badges, not hidden.
3. **No AI Slop / Authentic Desktop Aesthetic:** Zero generic purple gradients, oversized pill cards, or floating blurry shadows. We use Apple's Human Interface Guidelines (macOS desktop look) via Puppertino CSS to provide a clean, clinical, and data-dense interface.
4. **Zero-Build Reliability:** Runs offline on WSL2 Linux with a single command. Zero Node.js, zero Webpack/Vite bundlers, and zero risk of npm module breakdown during a live presentation.

---

## 2. Tech Stack Architecture & Rationale

```
+-----------------------------------------------------------------------------------+
|                                  FASTAPI BACKEND                                  |
|   - Serves app/index.html (Jinja2) and static assets                              |
|   - Frozen Engine: src/lhf/pipeline.py (analyse_recipe)                           |
|   - Independent Scraper: app/scraper.py (schema.org/Recipe JSON-LD)               |
|   - Endpoints:                                                                    |
|       * POST /api/analyze  (recipe dict -> full footprint JSON)                   |
|       * POST /api/scrape   (URL -> extracted ingredient lines)                    |
|       * GET  /api/lab-data (serves parsed 70-row fried_foods_lab.csv)             |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        FRONTEND CLIENT (app/index.html)                           |
|                                                                                   |
|   [Design System]                                                                 |
|   * Framework:      Puppertino CSS v2.0 (Dachshund)                               |
|   * Look & Feel:    macOS Monterey / Ventura Desktop                              |
|   * Typography:     SF Pro Text / Apple System Font Stack                         |
|   * Custom Tokens:  System Red/Orange/Green severity bars                         |
|                                                                                   |
|   [Reactivity Layer]                                                              |
|   * Library:        Alpine.js v3 (~15 KB, vendored locally in app/static/js/)     |
|   * Paradigm:       Declarative, attribute-based (x-data, x-show, x-for)          |
|                                                                                   |
|   [Motion & Transitions]                                                          |
|   * Tab Navigation: Native Alpine x-transition.opacity.duration.150ms             |
|   * Footprint Bars: Hardware-accelerated CSS cubic-bezier transitions             |
|   * Philosophy:     Subtle, snappy desktop feedback (no bouncy mobile physics)   |
+-----------------------------------------------------------------------------------+
```

### Why we chose this stack:
* **Puppertino CSS over Pico/Tailwind:** Provides native macOS segmented controls (`.p-segmented`), form controls, desktop tables (`.p-table`), and window cards without bringing a 200MB npm toolchain.
* **Rejecting the Multi-Framework Trap:** We strictly avoid mixing Pico CSS and Puppertino. Loading multiple CSS resets causes specificity collisions and visual dissonance.
* **Alpine.js over React:** Eliminates "context dilution" and JSX hallucination. The LLM writes pure semantic HTML with declarative Alpine directives, avoiding the virtual DOM lifecycle bugs that plague AI-written React components.
* **CSS/Alpine Transitions over GSAP:** GSAP requires manual DOM lifecycle polling (`$nextTick`) when paired with declarative UI frameworks. Native Alpine transitions and CSS `transition: width` are 100% immune to DOM race conditions and execute at 60 FPS.

---

## 3. Deliverable Tabs & Structural Breakdown

The web application is structured into **5 persistent tabs**, accessible via an Apple-style segmented control bar:

### Tab 4: D4 — Try It Live (Default Landing Tab)
* **Input Modes:**
  * Mode 1: Recipe URL scraper (schema.org/Recipe) with 3 one-click demo pills:
    * *Paneer Butter Masala* (`hebbarskitchen.com`)
    * *Samosa (Fried)* (`vegrecipesofindia.com`)
    * *Chicken Biryani* (`swasthi.com`)
  * Mode 2: Paste ingredients textarea (1 line per ingredient, optional dish name & servings count).
* **Output Display Hierarchy:**
  1. **Hero Sentence:** Automatically computes dominant axis and declares clinical impact (e.g., *"One serving uses 75% of your daily saturated fat limit — driven by cream, paneer, and butter."*).
  2. **Frying Correction Banner:** Amber macOS callout box triggered only when `frying_correction.applied == True` (explains bath exclusion and lab absorption ratio).
  3. **Dual Footprint Comparison Cards:**
     * **Liver Footprint:** Saturated Fat, Added Sugar, Refined Carbs (grams), Energy.
     * **Heart Footprint:** Saturated Fat, Sodium, Total Fat, Energy.
     * Severity color thresholds: Green (<30%), Amber (30–59%), Red (≥60%).
  4. **Dominant Ingredient Drivers:** Ranked percentage contribution bars (top 5 + rest) for the leading risk axis, with accordion expand for all axes.
  5. **Coverage & Diagnostic Footnote:** Displays matched ingredient ratio, unquantified items (`SALT_UNQUANTIFIED`), and empirical lower bound warnings.
  6. **Per-Ingredient Inspection Table:** Collapsible macOS table disclosing individual IFCT codes, mass basis, and nutrient vectors.

### Tab 1: D1 — Lab Dataset (Foundations of Frying Correction)
* **Dataset:** 70 verified laboratory measurements from 5 peer-reviewed sources (Gupta 2016, UK CoFID 2021, safefood 2015, Joshee 2019, Neethu 2025, etc.).
* **Controls:** Multi-filter bar by food category (6 categories) and setting (5 settings: Street, Home, Restaurant, Retail, Lab).
* **Core Academic Callout:** *"The Range Problem"* — Demonstrates the 4× fat spread in real-world samosas (7.7 g/100g GC vs. 29.6 g/100g Soxhlet) and why empirical calibration is required.

### Tab 2: D2 — How It Works (Pipeline Methodology)
* **Interactive 5-Stage Walkthrough:** Uses Samosa as a cohesive running example:
  1. *Parse:* Raw text to structured quantity, unit, and ingredient token.
  2. *Convert:* Unit conversion to grams via curated density dictionary (`measures.csv`).
  3. *Match:* Fuzzy token matching against 1,003 IFCT 2017 entries (cutoff 0.85).
  4. *Frying Bath Correction:* Volume exclusion and Soxhlet absorption re-injection.
  5. *Score:* Serving division and percentage derivation against ICMR-NIN 2024 limits.
* **Epidemiological Context:** MASLD prevalence (38.9% in India) and CVD mortality (28% of deaths).

### Tab 3: D3 — Atlas (Cuisine-Scale Findings)
* **Scale Metrics:** 1,014 INDB recipes, 71 web recipes, 11,610 lines, 103 frying corrections.
* **Category Breakdown:** 11-category summary table displaying median SFA, added sugar, and sodium burdens.
* **Textbook vs. Web Divergence:** 15-dish benchmark table showcasing commercial fat and SFA inflation (e.g., Chicken Biryani 6.31× SFA inflation).
* **Embedded Pipeline Figures:** Direct rendering of `fig1_category_footprint_bars.png` through `fig4_liver_risk_matrix.png`.

### Tab 5: About & Sources
* **Complete Citations:** Full academic bibliography for IFCT, INDB, ICMR-NIN, and clinical studies.
* **Transparent Limitations:** Frank documentation of confection syrup absorption, unquantified salt bounds, and pot-level soup coding.

---

## 4. Implementation Stages

- [x] **Stage 1: Directory Setup & Offline Asset Staging**
  - Create `app/` subdirectories (`static/css/`, `static/js/`, `static/figures/`, `data/`).
  - Vendor `puppertino.min.css` and `alpine.min.js` locally for 100% offline autonomy.
  - Copy generated figures and lab dataset CSV into static paths.
- [ ] **Stage 2: Standalone Hardcoded Frontend (`app/index.html`)**
  - Build the complete single-page application with pre-computed real payloads for PBM, Samosa, and Biryani.
  - Implement macOS segmented control tabs with Alpine reactivity.
  - Render all 5 tabs with realistic tables, progress bars, and callouts.
- [ ] **Stage 3: Verification & Visual Polish**
  - Verify layout responsiveness, tab switching, and table filtering in headless browser / local server.
  - Validate typography and system color thresholds.
- [ ] **Stage 4: Backend Integration (FastAPI & Scraper)**
  - Wire `app/main.py` to `src/lhf/pipeline.py` and `app/scraper.py`.
  - Connect live analyze and scrape endpoints.
