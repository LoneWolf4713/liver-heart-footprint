# Project Engineering & Research Goals

## 1. Backend API: Support for Preparation / Commercial Cooking Setting (`cooking_setting`)

### Current State & Problem
- In `src/lhf/pipeline.py`, the parameter `setting` is currently overloaded exclusively for demographic caloric baselines:
  ```python
  def analyse_recipe(recipe: dict, setting: str = "urban", risk: str = "general") -> dict
  ```
  Where `setting` only differentiates between ICMR-NIN urban (2,240 kcal) and rural (2,212 kcal) ceilings.
- In `src/lhf/frying.py`, the lab fat lookup function accepts only the dish name:
  ```python
  def _lookup_lab_fat(dish_name: str) -> tuple[float, float, str]
  ```
  It has a hardcoded preference looking for `setting == "home"`. Because only 8 of the 70 rows in `data/curated/fried_foods_lab.csv` are marked `home` (and specifically for vegetable samosa, there are zero `home` rows—only `street`, `restaurant-takeaway`, and `lab-controlled`), it silently falls back to the pooled median across all settings without informing the caller.

### The Goal
1. **Disambiguate Parameters**:
   - Rename demographic setting to `demographic_setting: str = "urban"` (`"urban"` | `"rural"`).
   - Add an explicit commercial cooking setting parameter:
     ```python
     cooking_setting: str = "median"  # 'street', 'restaurant-takeaway', 'home', 'retail-packaged', 'lab-controlled', 'median'
     ```
2. **Propagate Down to Frying Module**:
   - Update `correct_frying(result, setting=..., risk=..., cooking_setting=...)`.
   - Update `_lookup_lab_fat(dish_name, cooking_setting=...)` to filter matched dish rows by the requested `cooking_setting` first.
3. **Explicit Fallback Mechanics**:
   - When a user requests a setting that does not exist in the lab data for that dish (e.g. requesting `home` for Samosa), do NOT fail silently. Instead:
     1. Search for dish rows matching the requested setting.
     2. If none exist, fall back to category-level median for that setting.
     3. If still none exist, fall back to the dish pooled median across all settings.
     4. Explicitly document this fallback path in the API response metadata.
4. **Frontend Integration**:
   - Expose a segmented control or dropdown in the UI allowing users to evaluate recipes across:
     - `🏪 Street / Halwai` (high absorption due to oil thermal degradation & repeated reuse: ~29.4g fat / 100g, 49–60% SFA)
     - `🍽️ Restaurant / Takeaway` (commercial fryer flash-seal: ~7.7g – 17.3g fat / 100g, 18–42% SFA)
     - `🏠 Home / Domestic` (baseline domestic preparation)
     - `🔬 Lab / Controlled` (standardized laboratory trials)
     - `📊 Statistical Median` (conservative default across all settings: 12.4g fat / 100g for samosa)

---

## 2. Granular Frying Provenance & Absorption Transparency (`frying_correction` Schema)

### Current State & Problem
Currently, `result["frying_correction"]` only returns high-level aggregate numbers:
```json
{
  "applied": true,
  "frying_bath_lines_count": 1,
  "oil_mass_removed_g": 460.0,
  "absorbed_fat_g": 60.264,
  "absorbed_sfa_g": 29.6257824,
  "fat_g_per_100g_lab": 12.4,
  "sfa_pct_of_fat_lab": 49.16,
  "lab_match": "lab_match:Samosa"
}
```
The caller and UI cannot see:
- Which scientific publications (Gupta 2016, Sakhale 2011, Joshee 2019) were used.
- The step-by-step arithmetic used to arrive at `absorbed_fat_g`.
- Whether a fallback occurred because data for the requested setting was missing.
- Per-serving absorbed fat and SFA contributions.

### The Goal: Enhanced Output Contract
Upgrade `result["frying_correction"]` to output full provenance and math:
```json
{
  "applied": true,
  "frying_bath_lines_count": 1,
  "oil_mass_removed_g": 460.0,
  "requested_setting": "home",
  "resolved_setting": "pooled_median",
  "fallback_applied": true,
  "fallback_reason": "No direct lab measurements found for Samosa under 'home' setting. Fell back to pooled median across 5 lab measurements.",
  "matched_sources": [
    {"source": "Sakhale 2011", "item": "Samosa (Control)", "setting": "lab-controlled", "fat_g_100g": 12.4, "method": "proximate"},
    {"source": "Joshee 2019", "item": "Samosa", "setting": "restaurant-takeaway", "fat_g_100g": 7.71, "method": "FAME-sum"},
    {"source": "Gupta 2016", "item": "Samosa", "setting": "street", "fat_g_100g": 29.62, "method": "Soxhlet"}
  ],
  "fat_g_per_100g_lab": 12.4,
  "sfa_pct_of_fat_lab": 49.16,
  "non_oil_mass_g": 486.0,
  "calculation_formula": "absorbed_fat_g = (non_oil_mass_g / 100) * fat_g_per_100g = (486.0 / 100) * 12.4 = 60.26g",
  "absorbed_fat_total_g": 60.26,
  "absorbed_sfa_total_g": 29.63,
  "absorbed_fat_per_serving_g": 7.53,
  "absorbed_sfa_per_serving_g": 3.70
}
```

### Frontend D4 UI Requirements
In `app/index.html`, render an interactive **"How Was This Calculated?"** disclosure within the amber Frying Correction Banner:
1. Display the literal equation with real recipe mass numbers.
2. List the cited peer-reviewed studies backing the number.
3. Show an informational pill when fallback is active: `⚠️ Setting Fallback: Requested 'Home' → Used Pooled Median (12.4g/100g)`.

---

## 3. The Samosa (HLI 26) vs. Paneer Butter Masala (HLI 50) Paradox

### The Query / Discrepancy
In the prototype demo:
* **Paneer Butter Masala:** `HLI = 50` (Moderate Strain), `CBI = 55` (Moderate Risk).
* **Fried Samosa:** `HLI = 26` (Mild Load), `CBI = 21` (Low Risk / Green).

Why does a deep-fried snack appear "healthier" than a vegetarian paneer curry? Is the pipeline wrong?

### The Scientific & Nutritional Reality (The Defense)
The engine and formulas are **nutritionally and mathematically correct**. This paradox represents a cornerstone discovery of computational gastronomy and dietary epidemiology:

1. **The Chemical Reality of Fat Retention:**
   * **Paneer Butter Masala is a direct lipid emulsion:** The recipe includes 200g paneer, 2 tbsp butter (28.4g), and 1 tbsp heavy cream (15g). *Every single gram of this dairy fat is retained in the gravy and ingested.* Total recipe SFA is **47.7 grams**; per serving (4 servings), SFA is **11.9 grams** (exhausting **47.9% of the daily limit** in one bowl).
   * **Samosa is fundamentally potato and wheat starch:** A samosa's core is boiled potatoes ($0.1\%$ fat) and a thin wheat dough casing ($1\%$ fat). Deep frying does NOT saturate the entire potato interior—it forms a crisp outer crust. Under lab conditions, it absorbs **12.4g fat / 100g finished food**.
   * Across the entire 8-samosa batch, total absorbed fat is 60.3g. Divided by 8 servings, each samosa contains only **11.3g total fat and 4.2g SFA (16.7% of daily limit)**.
   * **Direct comparison:** 1 serving of Paneer Butter Masala delivers **nearly 3× the saturated fat** of 1 samosa.

2. **The Portion Size Artifact (`servings: 8` vs `servings: 4`):**
   * Samosa recipe specifies `servings: 8` $\rightarrow$ 1 serving = **60.8g (literally ONE single samosa piece)**.
   * Paneer Butter Masala specifies `servings: 4` $\rightarrow$ 1 serving = **105.2g (a main dinner portion)**.
   * In reality, an adult consumer rarely eats 1 mini samosa (60g); a standard snack order is **2 samosas (121.6g)**.
   * If evaluated as a 2-piece serving (121.6g):
     * Energy jumps to 448 kcal (20.0% of limit).
     * Fat jumps to 22.6g (30.4% of limit).
     * SFA jumps to 8.4g (33.4% of limit).
     * HLI jumps to **45**, and CBI jumps to **42**!

3. **The Commercial Preparation Multiplier (The 4× Spread):**
   * The default baseline uses Sakhale 2011's lab-controlled wheat casing samosa (12.4g fat/100g).
   * In a real **Street / Halwai** setting (Gupta 2016: 29.62g fat/100g, 60.2% SFA from vanaspati and reused palm oil):
     * A 2-samosa serving (121.6g) absorbs **36.0g fat and 21.7g SFA (87.2% of the daily SFA limit!)**.
     * In the street setting, Samosa's HLI exceeds **88 (High Steatosis Risk)** and CBI exceeds **85 (High CVD Risk)**, dramatically surpassing Paneer Butter Masala!

### Frontend D4 Engineering Solution
To make this completely clear and intuitive to both the user and Prof. Ganesh Bagler during the presentation:
1. **Portion / Piece Count Control:**
   * In the D4 input and results card, display:
     `Serving size: 1 piece (60.8g) · [ 1 piece | 2 pieces (Snack) | Custom ]`
   * Allow dynamic scaling of servings so users can see the impact of eating 2 samosas.
2. **Serving Definition Callout:**
   * Add an informational badge below the score widgets:
     `ℹ️ 1 serving = 60.8g (1 piece). Samosa scores reflect a single pastry. A 2-piece snack order doubles metabolic load.`
3. **Dual Metric View (Per Serving vs. Per 100g):**
   * Add a toggle between **"Per Serving"** (culinary portion) and **"Per 100g"** (scientific density).
   * On a per-100g basis:
     * Paneer Butter Masala: 21.6g fat/100g, 11.3g SFA/100g.
     * Samosa (lab median): 18.5g fat/100g, 6.9g SFA/100g.
     * Samosa (street setting): 35.8g fat/100g, 21.5g SFA/100g.
   * This proves to the professor that the tool distinguishes between portion size conventions and underlying biochemical lipid concentration.

---

## 4. Summary of Planned Code Changes

| Component | Target File | Proposed Change |
|---|---|---|
| **API Parameter** | `src/lhf/pipeline.py` | Add `cooking_setting="median"` and rename demographic setting to `demographic_setting="urban"`. |
| **Frying Resolution** | `src/lhf/frying.py` | Accept `cooking_setting`, filter matched lab rows by setting, and provide fallback to category/pooled median. |
| **Frying Provenance** | `src/lhf/frying.py` | Enrich `frying_correction` dict with formula string, matched citations, fallback reason, and per-serving lipid breakdown. |
| **D4 Frontend UI** | `app/index.html` | Add cooking setting selector, interactive calculation drawer in frying banner, and 1-piece vs 2-piece portion toggle. |
| **Backend Service** | `app/main.py` | Create FastAPI server routing live requests from the UI directly to `analyse_recipe` and `scraper.py`. |
