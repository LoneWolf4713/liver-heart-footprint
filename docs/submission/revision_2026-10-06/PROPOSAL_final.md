# Liver and Heart Footprint of Indian Recipes

**A Computational Gastronomy Framework for Estimating and Reducing the Cardiometabolic Dietary Load of Indian Food**

**Course:** BIO544 Computational Gastronomy, Monsoon 2026

**Instructor:** Prof. Ganesh Bagler, IIIT-Delhi

**Group:** Group 45 | Parth Verma [2024407], Pratyaksh Kumar [2024431]

---

## 1. Problem
Fatty liver disease (MASLD) affects an estimated 38.9% of Indian adults (Phenome India, 2026). Dietary risks account for 38.5% of cardiovascular deaths in India (GBD-based analysis, 2025).

The dietary drivers the two share are present in everyday Indian cooking:

- saturated fat;
- added sugar;
- refined carbohydrate;
- sodium;
- excess energy;
- oil absorbed during frying.

The Indian baseline is already high: saturated fat supplies 8.9% of energy nationally and 11.2% in North India (ICMR-INDIAB-21, 2025). Yet a cook has no way to tell how much a given recipe adds to this load. Common nutrition tools rely on Western food data and ignore the oil a fried food absorbs.

## 2. Idea
We define the **liver and heart footprint** of a recipe: its per-serving nutrient load, expressed as a share of the daily limits recommended by ICMR-NIN (2024) and WHO.

The approach parallels the carbon footprint of recipes. The recipe is the computational object (ingredients × quantities × cooking process), and the impact axes are liver- and heart-relevant nutrients instead of emissions.

## 3. Approach

- **Recipe input.** Ingredient lists are read from recipe web pages (schema.org Recipe data) or entered as text. Each line is converted into a quantity, a unit and an ingredient.
- **Quantities.** Household measures (spoons, cups, katoris, pieces) are converted to grams using Indian household-measure references (ICMR-NIN; Indian Nutrient Databank).
- **Composition.** Ingredients are matched to Indian food composition data (IFCT 2017, as used by the Indian Nutrient Databank). Labels of common Indian dairy products are used for items such as toned milk, dahi and paneer. International tables are used only where Indian values are unavailable.
- **Frying.** Recipes do not state how much oil a fried food absorbs. For fried dishes, we use fat values measured in laboratory studies of Indian fried foods.
- **Footprint.** Per serving, the engine computes:
  - energy;
  - total fat;
  - saturated fat;
  - added sugar;
  - sodium;
  - refined carbohydrate.

  Each is shown as a percentage of the daily limit, in two views: a **Liver view** (saturated fat, added sugar, refined carbohydrate, energy) and a **Heart view** (saturated fat, sodium, total fat, energy).
- **Drivers.** Each value is traced back to the ingredients contributing to it. This shows which ingredients matter most, and so where a recipe can be made lighter.
- **Cuisine-level analysis.** The engine is applied to recipes from the Indian Nutrient Databank, which are drawn from Indian cookery textbooks, and to recipes from popular Indian recipe websites. We compare loads across dish categories and identify the ingredient groups that drive them.

## 4. Deliverables

1. **Indian Fried-Food Fat Dataset.** A CSV of laboratory-measured fat content of Indian fried foods, compiled from published studies with the source of each value, along with fat ranges for the main categories of fried foods.
2. **Recipe Liver and Heart Load Engine.** A tool that takes a recipe's ingredients and calculates its per-serving energy, fat, saturated fat, added sugar, sodium and refined carbohydrate as a percentage of ICMR-NIN / WHO daily limits, shown as a Liver view and a Heart view.
3. **Liver and Heart Footprint Atlas of Indian Recipes.** An analysis of Indian recipes from the Indian Nutrient Databank and popular Indian recipe websites, showing which dish categories carry the highest liver and heart load and which ingredients drive it.
4. **Web Application.** A web app where a user enters a recipe link or ingredient list and sees the recipe's Liver and Heart load per serving and the ingredients contributing most to it.

## 5. Data sources

- **Indian Nutrient Databank** (INDB; IFCT 2017-based): food composition, unit conventions and a set of standardised Indian recipes.
- **ICMR-NIN Dietary Guidelines for Indians (2024) and WHO guidelines:** daily limits and Indian household measures.
- **NSO Nutritional Intake in India (2025) and ICMR-INDIAB-21 (2025):** average Indian intake, for context.
- **Published laboratory analyses of Indian fried foods** (e.g., Gupta et al. 2016; Joshee et al. 2019; Jain et al. 2024): the fried-food dataset.
- **Public Indian recipe websites:** recipes collected in line with each site's robots.txt, without republishing recipe text.

## 6. Relation to computational gastronomy
The project works with the field's core objects: recipes, ingredients and their composition, and diet-health links. It uses standard methods: recipe structuring, ingredient mapping and contribution analysis. It extends the recipe-footprint idea to liver and heart health, and accounts for frying, which ingredient-only calculations miss.

## 7. Scope and limitations

- The results are dietary estimates for awareness, **not medical advice**.
- An estimate describes a recipe as written; restaurant versions of the same dish are often richer.
- Ingredients listed without a quantity, such as "salt to taste", are reported as unquantified rather than guessed.

## 8. Key references

1. Phenome India cohort. Burden of MASLD and liver fibrosis in India. *Lancet Regional Health – Southeast Asia*, 2026.
2. Luukkonen P.K. et al. Saturated fat is more metabolically harmful for the human liver than unsaturated fat or simple sugars. *Diabetes Care*, 2018.
3. Anjana R.M. et al. Dietary profiles and associated metabolic risk factors in India from the ICMR–INDIAB survey-21. *Nature Medicine*, 2025.
4. ICMR-NIN. *Dietary Guidelines for Indians*, 2024.
5. Vijayakumar A. et al. Development of an Indian Food Composition Database (INDB). 2024.
6. Longvah T. et al. *Indian Food Composition Tables*. ICMR-NIN, 2017.
7. Gupta V. et al. Unhealthy fat in street and snack foods in low-socioeconomic settings in India. 2016.
8. Joshee K. et al. Fatty acid profiling of 75 Indian snack samples. *PLOS ONE*, 2019.
9. Jain A. et al. Total fat and fatty acid profile including TFA content of Indian fried foods. *J Food Sci Technol*, 2024.
10. Goel M. et al. Cultural context shapes the carbon footprints of recipes. arXiv:2311.08416, 2023.
11. Zinzuvadia V. et al. Statewide burden of cardiovascular disease attributable to dietary risk factors in India. *JACC*, 2025.
