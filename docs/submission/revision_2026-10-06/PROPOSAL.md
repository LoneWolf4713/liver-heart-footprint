# Liver and Heart Footprint of Indian Recipes
**A Computational Gastronomy Framework for Estimating and Reducing the Cardiometabolic Dietary Load of Indian Food**

**Course:** BIO544 Computational Gastronomy, Monsoon 2026

**Instructor:** Prof. Ganesh Bagler, IIIT-Delhi

**Group:** Group 45 | Parth Verma [2024407], Pratyaksh Kumar [2024431]

**Version:** revised scope, 6 October 2026 (four deliverables, each with a stated verification)

---

## 1. Abstract
Fatty liver disease (MASLD) affects an estimated 38.9% of Indian adults. Cardiovascular disease causes about 28% of deaths in India, and dietary risks account for 38.5% of cardiovascular deaths. The dietary drivers the two share are built into everyday Indian recipes:

- saturated fat;
- added sugar;
- refined carbohydrate;
- sodium;
- excess energy;
- oil absorbed in frying.

We define the **liver and heart footprint** of a recipe as a transparent, per-serving estimate of these loads, expressed as a share of national daily limits.

Methodologically, this parallels the carbon footprint of recipes: the recipe is the computational object, and the impact axes are hepatic and cardiovascular dietary load.

The project delivers four verifiable outputs:

1. an open dataset of laboratory-measured fat in Indian fried foods;
2. a recipe-to-load computation engine grounded in Indian food composition data;
3. a footprint atlas of at least 2,000 Indian recipes;
4. a web application that applies the engine to a recipe link or ingredient list.

## 2. Motivation

- **Liver burden.** Age-adjusted MASLD prevalence in Indian adults is 38.9% (Phenome India cohort, 2026). Saturated fat raises liver fat the most in controlled overfeeding, and simple sugars raise it through de novo lipogenesis (Luukkonen et al., 2018).
- **Heart burden.** Dietary risks caused 38.5% of cardiovascular deaths in India in 2021 (GBD-based analysis, 2025). Mean salt intake is about 8 g/day against a 5 g limit (National NCD Monitoring Survey).
- **A high baseline.** Saturated fat supplies 8.9% of energy nationally and 11.2% in North India (ICMR-INDIAB-21, 2025). Mean intake is about 2,212–2,240 kcal/day (NSO, 2025).
- **The gap.** No tool tells a cook how much a given Indian recipe adds to this load. Existing nutrition tools:
  - sum raw ingredients;
  - ignore oil absorbed in frying;
  - rely on Western composition data.

## 3. Objectives

1. Estimate the per-serving liver- and heart-relevant load of an Indian recipe from its ingredients, quantities and cooking process.
2. Express the load against ICMR-NIN 2024 / WHO daily limits and the average Indian intake.
3. Identify the ingredients that drive the load, to guide reduction.
4. Characterise the load across a large set of Indian recipes.

## 4. Methodology
### 4.1 Recipe representation and ingestion

- **Representation.** A recipe is a set of ingredient lines with quantities, units and processes.
- **Ingestion.** Ingredient lists come from schema.org `Recipe` data on supported recipe websites, or from text pasted by the user. Collection follows each site's robots.txt and is rate-limited.

### 4.2 Quantities and composition

- **Quantities.** Quantities are converted to grams with a cited household-measures table, drawing on:
  - ICMR-NIN Dietary Guidelines 2024 (scale-measured Indian teaspoons and katoris);
  - INDB unit conventions;
  - USDA portion weights.
- **Composition.** Ingredients are mapped to Indian food composition data in this order:
  1. IFCT 2017, as used by the Indian Nutrient Databank (INDB);
  2. labels of common Indian dairy products;
  3. UK and US tables where Indian values are unavailable.
- **Unhandled lines.** Lines that cannot be quantified or mapped are reported, never silently filled.

### 4.3 Frying
Recipes do not state how much oil a fried food absorbs. For fried dishes, the engine uses fat ranges per fried-food category derived from Deliverable 1, and reports the result as a range.

### 4.4 Footprint

- **Six quantities per serving:**
  - energy;
  - total fat;
  - saturated fat;
  - added sugar;
  - sodium;
  - refined carbohydrate.
- **Limits.** Each is shown as a percentage of the ICMR-NIN 2024 / WHO daily limit, alongside the national average intake (NSO 2025; ICMR-INDIAB-21).
- **Two views of the same values:**
  - Liver view: saturated fat, added sugar, refined carbohydrate, energy;
  - Heart view: saturated fat, sodium, total fat, energy.

  No composite score is computed.

- **Traceability.** Every value is traced to the contributing ingredient lines and their composition-table rows.

### 4.5 Cuisine-level analysis
The engine is applied to two recipe sets:

- the 1,014 standardised recipes of the Indian Nutrient Databank, drawn from two Indian cookery textbooks and open-source recipes;
- recipes collected from Indian recipe websites.

The analysis covers:

- load by dish category;
- the ingredient groups that drive saturated fat, added sugar and sodium (contribution analysis);
- textbook versus web versions of the same dishes.

## 5. Data sources
| Data | Use |
|---|---|
| Indian Nutrient Databank (INDB): 1,014 recipes with ingredient amounts; IFCT 2017-based composition | Composition, unit conventions, textbook recipe set, validation |
| ICMR-NIN Dietary Guidelines for Indians (2024) | Daily limits; Indian household measures |
| NSO Nutritional Intake in India (2025); ICMR-INDIAB-21 (2025) | National intake baselines |
| Published laboratory analyses of Indian fried foods (Gupta et al. 2016; Joshee et al. 2019; Jain et al. 2024; Chen et al. 2009; safefood 2015) and UK CoFID 2021 analysed South Asian dishes | Deliverable 1; validation of cooked-dish estimates |
| Product labels of common Indian dairy products (toned milk, dahi, paneer, butter, cream) | Indian composition for dairy |
| Indian recipe websites (public pages, per robots.txt) | Web recipe set |

## 6. Deliverables
| # | Deliverable | What is delivered | How it is verified |
|---|---|---|---|
| 1 | **Indian Fried-Food Fat Dataset** | A CSV of at least 60 laboratory-measured fat values of Indian fried foods from at least 5 published sources, each row citing its source table; fat ranges (minimum, median, maximum) for 5 fried-food categories | Every row can be traced to its cited table. A script recomputes the ranges and reports how often values from a held-out source fall inside the range built from the other sources |
| 2 | **Recipe Liver and Heart Load Engine** | A tool that takes a recipe's ingredient list and returns, per serving, energy, total fat, saturated fat, added sugar, sodium and refined carbohydrate as % of ICMR-NIN 2024 / WHO limits (Liver and Heart views), with every value traced to its ingredient lines | Reproduces the published INDB values for at least 95% of its about 1,000 dishes. Parsing and conversion accuracy are reported on at least 150 hand-annotated real ingredient lines. Estimates for at least 10 laboratory-analysed cooked dishes are compared with the measured values, and the ratio is reported |
| 3 | **Liver and Heart Footprint Atlas of Indian Recipes** | Footprints of at least 1,000 INDB recipes and at least 1,000 web recipes from at least 3 Indian recipe websites; load by dish category; contribution of ingredient groups (cooking oils, dairy fats, sugar, refined flour, salt) to saturated fat, added sugar and sodium; textbook versus web comparison for at least 20 dishes present in both | All tables and figures are generated by scripts from saved results. The share of recipes and ingredient mass successfully analysed is reported |
| 4 | **Web Application** | A locally run web app: the user pastes an ingredient list or a link from at least 3 supported recipe websites and sees the per-serving Liver and Heart bars, a per-ingredient table with sources, and the top contributing ingredients | Demonstrated live on at least 10 recipe links. The values shown equal the engine's output for the same recipe |

## 7. Relation to computational gastronomy

- **Data.** The project works on the field's core data types: recipes, ingredient composition and health associations.
- **Methods.** It uses the field's core methods: recipe structuring, ingredient mapping and contribution analysis.
- **Extension.** It extends the carbon-footprint-of-recipes framework to a new impact axis, and adds the cooking transformation (frying) that ingredient sums miss.

## 8. Scope and limitations

- Outputs are dietary estimates, **not medical advice**.
- Estimates describe the recipe as written. Restaurant versions of a dish are often richer.
- "Salt to taste" and "oil as required" lines are reported as unquantified. Fried-dish estimates are ranges.
- Data collection uses public pages only, respects robots.txt and rate limits, and does not republish recipe text. No social-media or food-delivery platform data is used.

## 9. Work plan

1. Engine core and its validation against INDB (Deliverable 2).
2. Fried-food dataset and ranges (Deliverable 1), integrated into the engine.
3. Atlas on INDB recipes, then web recipes (Deliverable 3).
4. Web application (Deliverable 4) and final report.

**Possible extensions (not promised):**

- a question-answering assistant over the engine's results;
- frying-setting estimates (home vs street);
- region-level analysis where recipes carry cuisine tags.

## 10. Key references

1. Phenome India cohort. Burden of MASLD and liver fibrosis in India. *Lancet Regional Health – Southeast Asia*, 2026.
2. Luukkonen P.K. et al. Saturated fat is more metabolically harmful for the human liver than unsaturated fat or simple sugars. *Diabetes Care*, 2018.
3. Anjana R.M. et al. Dietary profiles and associated metabolic risk factors in India from the ICMR–INDIAB survey-21. *Nature Medicine* 31:3813–3824, 2025.
4. National Statistics Office. *Nutritional Intake in India* (HCES 2022–24), 2025.
5. ICMR-NIN. *Dietary Guidelines for Indians*, 2024.
6. Vijayakumar A. et al. Development of an Indian Food Composition Database (INDB). 2024 (PMC11277795).
7. Longvah T. et al. *Indian Food Composition Tables*. ICMR-NIN, 2017.
8. Gupta V. et al. Unhealthy fat in street and snack foods in low-socioeconomic settings in India. 2016 (PMC4826272).
9. Joshee K. et al. Fatty acid profiling of 75 Indian snack samples. *PLOS ONE*, 2019.
10. Jain A., Passi S.J., Selvamurthy W. Total fat and fatty acid profile including TFA content of Indian fried foods versus the oils used for frying. *J Food Sci Technol* 61:2185–2195, 2024.
11. Chen A., Gilbert P., Khokhar S. Estimating the nutrient composition of South Asian foods using a recipe calculation method. *Food Chemistry* 113:825–831, 2009.
12. Goel M. et al. Cultural context shapes the carbon footprints of recipes. arXiv:2311.08416, 2023.
13. Kalra J.S. et al. Nutritional profile estimation in cooking recipes. arXiv:2004.12286, 2020.
14. Zinzuvadia V. et al. Statewide burden of cardiovascular disease attributable to dietary risk factors in India in the last 3 decades. *JACC* 85(12 Suppl):354, 2025.
15. Awareness, behavior, and determinants of dietary salt intake in adults: results from the National NCD Monitoring Survey, India. *Scientific Reports*, 2023 (PMC10517942).
