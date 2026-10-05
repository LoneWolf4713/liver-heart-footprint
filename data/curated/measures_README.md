# measures.csv: household measure -> grams (architect-authored, protected)
Columns: match_type (code | group | any), match (food codes separated by ';', or an IFCT/INDB food-group letter = first letter of the code, or '*'), unit, size (blank or small/medium/large), grams (grams per 1 unit; for unit 'ml' it is a density in g/ml), source, note.

Sources, in priority of trust:
0. ICMR-NIN Dietary Guidelines for Indians 2024, Annexure II: scale-measured Indian teaspoons (oil/ghee, dal, rice, atta, poha, rajma). Amul Pure Ghee label for ghee density.
1. INDB Units.xlsx (data/raw/indb/Units.xlsx): Indian household measures used by the Indian Nutrient Databank; rows cite BFP/ASC manuals or USDA.
2. USDA FoodData Central SR Legacy portions (data/raw/fdc_portions/food_portion.csv; fdc_id given).
3. INDB.do conversion rules (data/raw/indb/INDB.do, line numbers given): food-group defaults.
"derived" rows are arithmetic on a cited row (shown in the source).

Lookup order the engine must use (see docs/SPEC.md §4):
1. measure stated in the line in metric units (g, kg, ml, l) -> no table needed (ml uses the density row: code, then group, else 1.0);
2. code row for (code, unit, size);
3. group row for (first letter of code, unit);
4. 'any' row (mass units only);
5. otherwise UNQUANTIFIABLE. Never invent a default.

Known conflicts: NIN teaspoons (oil 5 g) vs USDA tablespoons (oil 13.6 g) are not in a 1:3 ratio, and NIN's adult charts say 1 tbsp oil = 10 g; household spoons vary. Phase 2 will report these as ranges.
Known assumptions (flagged in the note column): black salt = table salt; jaggery per tsp = sugar; ghee and vanaspati = anhydrous butter oil; mustard seed whole = ground; dried kasuri methi uses fresh fenugreek-leaf volume weight; Indian garlic clove 0.625 g (INDB) vs US 3.0 g (FDC).
Known gap: INDB.do itself counts 1 tsp of salt as 2 g (group G default); we use 6 g (USDA FDC 173468), so our salt values are higher than INDB's for the same recipe.
