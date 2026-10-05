## Computational Gastronomy Prof. Ganesh Bagler (IIIT-Delhi)

Monsoon 2026 – Week 01/02

-  Three major aspects of Computational Gastronomy data:
1. Recipes – Information of recipes that reflects its constituent ingredients. Further, this could also include details of the temporal sequence of ingredients, the quantity of each ingredient, their state (chopped, ground, etc.), size and the method of processing ingredients (cook, boil, fry, saute, etc.).
2. Flavor Profiles of Ingredients: Every natural ingredient that is used in recipes is primarily selected based on its flavors—taste and odor. The flavor profile of the ingredient represents the set of empirically reported flavor molecules.
3. Health Associations of Ingredients: Each ingredient may be associated with the health impacts as identified from experimental studies investigating linking them to diseases.
4. Nutritional Profile of Ingredients/Dishes: Each ingredient can be associated with its nutritional profile, including macro- as well as micro-nutrients.
5. Carbon Footprints of Food: Every time we consume food, we leave an ecological footprint on the globe. The carbon footprint of our dietary consumption consists of around 1/3rd of the total footprint.

In each of these aspects, we are simplifying food and cooking by making certain assumptions. Given the complexity of the phenomena under consideration and lack of quantitative formalism, this is expected to be a first step which could be elaborated later to bring the necessary nuances.

Here, to begin with, a recipe is defined as an unordered list of ingredients . Clearly , such a definition while convenient for certain analysis misses out many critical factors such as the quantity of each ingredient, their sensory potency, the order in which they are used while cooking, the method used for processes among others.

Similarly, an ingredient is defined as an unordered set of its constituent flavor molecules. The flavor/aroma as experienced through the sensory mechanisms is an emergent property. The quantity/concentration of each flavor molecule and its potency is extremely important for the flavor profile. Beyond that, the synergy among the flavor compounds and transformation while undergoing the cooking also contribute to the final flavor of the ingredient.

While most of the empirical data on the health impacts of food are available for individual ingredients, it only makes sense to assess these for a dish. The bipartite associations between ingredients and MeSH (Medical Subject Headings) terms, could be investigated for meaningful inferences for dietary interventions and diet design.

##  Potential Data - Driven Food Innovations

1. Novel Recipes Design: Cooking is a combinatorial system that combines the raw material (ingredients) and ways of processing them (cooking rules). Given that the average recipe uses 10 ingredients and that there are around 1000 unique ingredients, one could create around 10 30 recipes sheerly with the power of combinations. Not every such 'recipe' would be palatable, leave alone delicious. Knowing the patterns in the traditional recipes from various cuisines, one could filter recipes that conform to the cultural norms. This requires the use of statistics, data/patterns mining , and natural language processing.
2. Culinary Fingerprints: Starting with the tripartite data of recipes, their constituent ingredients and further the flavor profiles of ingredients, one could mine for patterns in traditional recipes to obtain the 'culinary fingerprints' of cuisines. These fingerprints represent the characteristic pattern of ingredient couse as well as the idiosyncratic flavor patterns of a cuisine depicting the culinary preferences of a population. Such insights are of value for food/recipe design for targeted audiences .
3. Taste/Odor Prediction: Large compilation of flavor molecules along with their taste/odor attributes presents an interesting case for machine learning-based taste and odor prediction algorithms. Here the battery of molecular properties (starting from simple ones such as number of atoms, molecular weight to all the way up to molecular fingerprints comprising of thousands of attributes) are features which could be used for building statistical models for classification into taste and odor classes.

4. De novo design of flavor/taste molecules: Along with in silico methods for generation of organic compounds, taste/odor classification models can enable de novo synthesis of compounds of desirable profile.
5. Healthy and Sustainable Diet Design: Systematically curated data of health impacts of ingredients, along with rules of making recipes, can be used for designing potentially healthy recipes. Interestingly, such strategies could be used to propel the use of ingredients for promoting a sustainable food culture.