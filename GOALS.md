# Project Engineering & Research Goals

## 1. Backend API: Support for Preparation / Commercial Cooking Setting (`cooking_setting`)

### Current State & Problem
- In `src/lhf/pipeline.py`, the parameter `setting` is overloaded for demographic caloric references:
  ```python
  def analyse_recipe(recipe: dict, setting: str = "urban", risk: str = "general") -> dict
  ```
  Where `setting` only differentiates between ICMR-NIN urban (2,240 kcal) and rural (2,320 kcal) ceilings.
- In `src/lhf/frying.py`, the lab fat lookup function accepts only the dish name:
  ```python
  def _lookup_lab_fat(dish_name: str) -> tuple[float, float, str]
  ```
  It does not accept any commercial or culinary setting parameter. It internally looks for `"home"`, and because only 8 of the 69 rows in `data/curated/fried_foods_lab.csv` are marked `home`, it falls back to the pooled median across all settings (`street`, `restaurant-takeaway`, `lab-controlled`).

### The Goal
When building the backend API service (and exposing CLI flags for offline runs):
1. **Disambiguate Parameters**:
   - Rename demographic setting to `demographic_setting: str = "urban"` (`urban` | `rural`).
   - Add explicit commercial cooking setting parameter:
     ```python
     cooking_setting: str = "median"  # 'home', 'street', 'restaurant-takeaway', 'retail-packaged', 'lab-controlled', 'median'
     ```
2. **Propagate Down to Frying Module**:
   - Update `correct_frying(...)` and `_lookup_lab_fat(dish_name, cooking_setting=...)`.
   - When a specific `cooking_setting` is provided by the API request, filter matched dish rows by that setting first before falling back to category medians.
3. **Frontend Integration**:
   - Pass this parameter from the web interface so users can toggle between:
     - `🏠 Home / Domestic` (baseline absorption)
     - `🏪 Street / Halwai` (high absorption due to oil reuse and thermal degradation: ~29g fat / 100g)
     - `🍽️ Restaurant / Takeaway` (commercial fryer crust flash-seal: ~16.5g fat / 100g)
     - `📊 Statistical Median` (conservative default when setting is unknown)

### Research & Pedagogical Value (Prof. Bagler Defense)
- Solves the **"Range Problem in Dietary Epidemiology"**: The same culinary dish exhibits up to a **4× lipid spread** between commercial street food and domestic cooking.
- Demonstrates true computational gastronomy sensitivity modeling rather than relying on a static, hidden single-point assumption.
