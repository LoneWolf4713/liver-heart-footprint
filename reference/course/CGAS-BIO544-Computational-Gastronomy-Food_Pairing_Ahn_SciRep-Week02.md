![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000000_1209407e2a619c3fb9a64230b4850ecd9a155c5380a2011c3ffda5779e7e81b0.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000001_6bbf9bb804c70153403b6e48bf64f1fdd201e25b3b3f5d3b42438264088fce08.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000002_e0dd3d2b7955f756640a0b3b31dbcbb3ad8067d35f721a9b2b66cc008c507170.png)

## Introduction

- Are there any general patterns that determine the ingredient combinations used in food today or principles that transcend individual tastes and recipes?
- A flavor network that captures the flavor compounds shared by culinary ingredients
- Food Paring Hypothesis: "Ingredients sharing flavor compounds are more likely to taste well together than ingredients that do not "
- A systematic understanding of culinary practice .

Number of recipes (cookpad): 10 6

Number of potential recipes: &gt; 10 30

Number of recipes used for the studies: 56498

## Summary

- The flavor network allows us to reformulate the food pairing hypothesis as a topological property: Do we more frequently use ingredient pairs that are strongly linked in the flavor network or do we avoid them?
- To test this hypothesis we need data on ingredient combinations preferred by humans, information readily available in the current body of recipes .
- For generality, 56 , 498 recipes, provided by two American repositories (epicurious . com and allrecipes . com), were used .
- To avoid a distinctly Western interpretation of the world's cuisine, we also used a Korean repository (menupan . com) .
- The recipes are grouped into geographically distinct cuisines (North American, Western European, Southern European, Latin American, and East Asian) .

## Basis of Flavor Network:

- (i) 381 ingredients used in recipes throughout the world, and
- (ii) 1,021 flavor compounds that are known to contribute to the flavor of each of these ingredients.

&lt;k&gt; = 214

www.epicurious.com www.allrecipes.com The average number of ingredients used in a recipe is around eight, and the overall distribution is bounded, indicating that recipes with a very large or very small number of ingredients are rare .

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000003_0eceef190ef601afb4efc356adbccdbfa196a1ffd5608775e5a35709a916aa6e.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000004_75e7ea12e829839a7dd449bc4e2eeac0662ffa5dac5c12e0a8f99b1a77f41cf7.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000005_2af039bac757b7bff33230a01d12e788443555be495fc59949437cb6219bee2e.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000006_1f2f06e0c6bec771c00d1aa74450a4b3f59d70949d1450719699cb44a7f1bc40.png)

Ingredients Jasmine tea, Jamaican rum, and 14 other ingredients are used only in one recipe.

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000007_3ffafa76116257ae151397ba7a461facfa215ac4e5f4be69f7bf9068efbc5c10.png)

Backbone extraction algorithm

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000008_810defd8e7b389cdceb3710934ff29997d794e4d209ed21b043a6ba6a83fb88a.png)

## Shared flavor molecules in ingredient pairs

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000009_249badea1099ea658ddc21a2c6e265ce377e27bff739b8614d0ea2765ced76b4.png)

## How to create a random cuisine? (Strategy – 1)

- (1) Corresponding to every recipe, create its size-controlled randomized version by randomly sampling ingredients from the 'Ingredients Basket' (without replacement).
- (2) Having thus created 'a randomized cuisine', create a large number of such cuisines (say, 100) for statistical analysis.

Randomize cuisine 1

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000010_423633ad69ad8567b6e9355a280a021e8669c2b56fc2b63658e9f721ff0f357c.png)

Randomize cuisine 100

## How to create a random cuisine? (Strategy – 2)

- (1) Find the 'recipe size distribution' of the cuisine.
- (2) Find the 'cumulative recipe size distribution' of the cuisine.
- (3) Generate a random number to pick a recipe size.
- (4) Create the recipe by randomly sampling ingredients from the 'Ingredients Basket' (without replacement).
- (5) Generate a large number of recipes (say, 100 times the total number of recipes) for statistical analysis.

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000011_502506493da9baceb64c70f043410e9969de969354e73c9ce9f2a01adf35844c.png)

## Generating the desired recipe size distribution of the cuisine

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000012_047e9f207949615c7c2deb9c41766acf4a67130bb04327b57afe3023926a3926.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000013_354cd162e7f97a06bb6d819397bbe53eea64572d457635e3c9d30270f9f1fdc8.png)

Number of shared flavor molecules between ingredients i and j

Average number of shared flavor molecules across all pairs of ingredients in the recipe R

Average number of shared flavor molecules across all recipes in a cuisine

## Mini - Project Ideas

- A theoretical model for food pairing .
- Starting with a 'basket of ingredients and their flavor profile, implement strategies for 'pairing' and observe the cuisine architecture.
- Create a python library for the analysis of cuisine, starting with cuisine data imported in a certain format.
- Recipe size distribution, ingredient popularity stats
- Category composition analysis
- Itemset analysis
- Food pairing analysis
- Random cuisine generation
- Create Computational Gastronomy Kaggle challenges
- For a given set of recipes, predict their cuisine.
- Given the flavor profile of an (unlabeled) ingredient, predict its cuisine.
- Given a molecule (SMILE format), predict its taste (bitter, sweet, tasteless).
- and more.

## Random Cuisine and comparison of food pairing

North American and Western European cuisines exhibit a statistically significant tendency towards recipes whose ingredients share flavor compounds.

By contrast, East Asian and Southern European cuisines avoid recipes whose ingredients share flavor compounds.

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000014_de47a001e27ff6e9b59c2044002d4ad869afd1ad98fb99db4d80ac90acd184e5.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000015_e308c3e75bef478efd20ab183fc4823ecb11ac6b6bcbd4e65897537f72c6cc0f.png)

## Distribution of Ns

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000016_8d46cb4675bcb7b2131e00f092ac636109cd888dabbec45d7e47ccb49fc8b0c0.png)

Ns: observed number of shared compounds characterizing the cuisines.

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000017_1f99b9515a5993f98f9bfddc6db3e98aca8d8bd18e7b8146c6a8933da61885fc.png)

East Asian (Korean) cuisine the more flavor compounds two ingredients share, the less likely they are used together.

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000018_53cdb4294aeeeb13f8fc3a27312f10c8db9da5481ab5eda6fac528cf5b2f4cba.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000019_79d6380aafd26abab95027ccf6b6c489e260ce2009d7d7f6e98fd2eb9435ab83.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000020_3f2f84988dca84a7e03d9d3bfcfc4431b3c35218f15f3e96ddf87191478a9aa6.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000021_cb8931ddb6d236b4f52794e92f343056f6683069667f9145e200e1651336e4f5.png)

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000022_b3d6ee7c3cfa1aae944e88702ba568d470b626b0f1d0b399ca219704ddb422e8.png)

- Western Cuisines use ingredient pairs that share many flavor compounds
- By contrast, Korean cuisine tend to avoid compound sharing ingredients .

## Contribution of an ingredient towards the food pairing pattern

![Image](/mnt/c/Users/prern/Downloads/Academics/CGAS/Full_Lectures/CGAS-BIO544-Computational-Gastronomy-Food_Pairing_Ahn_SciRep-Week02_figures/image_000023_4ec8394dcd1726e2dfda2f7a506cd4a51bc561db22d7ef5a955d664f320ef43b.png)