## Computational Gastronomy Prof. Ganesh Bagler (IIIT-Delhi)

## Monsoon 2026 – Week 01/02

-  Definition: Computational Gastronomy

Computational Gastronomy is a data science that blends food, data, and computation towards achieving data-driven food innovations .

Humans have evolved over millions of years as one of the most dominant species on the face of the earth. Over time, as we acquired enhanced cognitive abilities, we also developed a lifestyle that makes us vulnerable to diseases such as obesity, diabetes, and cardiovascular disorders. While we may blame our genes, our social circles , and sedentary work profiles for the rise of this epidemic of lifestyle disorders, diet is an important factor contributing to these health issues.

Cooking is a uniquely human endeavor that is suggested to be responsible for the evolution of big brains in humans. Ironically, food is also central to many modern health problems. Experts have attempted to associate food's positive and negative effects on human health without much convergence. The interaction between our body and food, leading to health consequences , is way too complex, giving rise to inconclusive and often contradictory assertions.

I believe that taking a data-centric and evidence-driven view of food is the key to leveraging food for better health. With this idea, I would like to present our investigations of Indian cuisine in search of patterns and future directions for personalized dietary recommendations. Such data-driven studies are opening new avenues for using food as medicine.

We started out by asking a simple question, "Why do we eat what we eat?". What we eat on a day-to-day basis is dictated by traditional dietary practices crystallized as elaborate cooking procedures: the recipes. This question then transforms into, "Why do we combine ingredients in our recipes the way we do?".

One of the possible answers to this question is known as the 'food pairing principle': ingredients that taste similar tend to be used together in traditional recipes. This implies that traditional recipes have evolved to combine ingredients that are uniform in taste.

To investigate the food pairing pattern in Indian cuisine, we extracted data of traditional recipes from across different regions of India. These data comprised more than 2500 recipes that are composed of around 200 ingredients from different categories: vegetables, herbs , spices, plants, nuts , dairy products etc.

Ingredients are used in recipes based on their flavor. And the 'flavor' of ingredients arises primarily from how we taste and smell it through the gustatory and olfactory sensory mechanisms that are triggered by the flavor molecules. The pungency of onions and spiciness of chilies is due to their flavor profile. So, we extracted the information on flavor molecules found in each ingredient used in Indian recipes. Thus, each ingredient is now represented by various flavor molecules that characterize its unique taste and smell.

Having obtained data on recipes, ingredients , and flavor profiles, food pairing became a measurable quantity. Each of the traditional Indian recipes was dissected into its constituent ingredients to compute its food pairing. The average number of flavor molecules among all pairs of ingredients in the recipe. This number represents 'the extent of flavor profile overlap among all ingredient pairs in a recipe'. When averaged over all the recipes, this number quantifies the average food pairing across the whole cuisine.

Food pairing is an objective measure that captures the molecular essence, the intuitive uniqueness of a cuisine. Similar to variations in regional languages, cultures worldwide have evolved variations in how they cook. Variations in how they combine ingredients to form recipes, the unique mold that characterizes a cuisine. Without cultural, climatic , and other influences, the recipes would have been combined in a random fashion to create a 'Random Cuisine.'

Consistent with the food pairing hypothesis, it has been shown that many Western cuisines, such as North American, Latin American, Eastern , and Southern European cuisines, indeed are characterized by 'uniform food pairing.' These cuisines tend to blend ingredients that are similar in their taste and smell. On the contrary, studies from our lab have shown that Indian cuisine is characterized by 'contrasting food pairing'.

This essentially means that Indian recipes tend to pair ingredients that have distinct molecular characteristics. And this probably could be one of the reasons for their unique taste. We found that contrasting food pairing is a general phenomenon across all regional cuisines: a quintessential feature of Indian recipes. It seems that, despite diverse culinary styles, there is an underlying similarity across regional cuisines of India.

We wanted to find the contribution of each ingredient category towards the observed food pairing phenomena. For this, we randomized the recipes— one category at a time. For example, to find how important a specific vegetable in recipes is, we randomly shuffled every vegetable with any one of the vegetables from the basket of 'all vegetables available'. We found that such random shuffling affects food pairing only marginally for most categories, except for one: Spice. The random shuffling of spices in recipes with other spices disturbs the food pairing pattern significantly. This suggests that spice forms the 'molecular fulcrum' of Indian cuisine. Chefs suggest that such unique positioning of spices is, in fact, critical for the taste of a recipe.

Going further, we quantified ingredients for their contribution towards increasing or decreasing the food pairing. Among the top ingredients that make a significant contribution to the molecular contrast, the majority are spices: cayenne (chilies), capsicum, ginger, garlic, coriander, tamarind, clove, cinnamon, and spice combinations (such as garam masala). These key spices provide the basis of food pairing in Indian cuisine.

While food pairing is a simple measure of molecular combination in recipes, I am tempted to link it to taste. I must warn , though , that sensation of taste is a complex phenomenon involving a myriad of interlinked molecular mechanisms, and hence this suggestion needs to be taken with a 'pinch of salt.'

Our data - driven discovery of this unique contrasting food pairing has been adjudged as an 'Emerging Technology' by the MIT Technology Review. Similar to how the knowledge of the law of gravity has allowed us to predict eclipses and launch satellites into space, I believe that such data-driven investigations of food will take us closer to developing divergent applications for food, nutrition, and health.

With the variety of ingredients available, the number of possible recipes is astronomically large. Knowing the 'culinary fingerprints of a cuisine' can facilitate us in generating novel recipes that are , hopefully , also palatable. Formulation of new food, food-beverage pairing, testing a food hypothesis, studying food-genome interactions, and mining food-disease associations are among a few interesting dimensions emerging from our discovery.

One of the most exciting directions from data-driven and evidence-based investigations of food is that of 'personalized nutrition.' In a pioneering study, researchers meticulously collected data of personal features , such as the nature of gut microbes, blood reports, body measures , and food habits, from many people. One of their meal was substituted with a standardized diet. These were then correlated with post-meal glucose levels using a machine-learning algorithm. Interestingly, such a 'personalized nutrition predictor' could predict the expected rise in glucose levels even for a new set of people with a fairly good accuracy. More importantly, it could also suggest a personalized dietary recommendation used to successfully mitigate glucose levels, which is closely linked to Type 2 Diabetes. Such studies are setting the foundation for finding solutions for diet-linked diseases.

This may sound like science fiction. But who believed in weather predictions a few decades back? Despite the weather being a non-linear phenomenon, the availability of a large amount of climate data and computational and mathematical techniques has transformed meteorology into a believable science today , at least for short - term predictions. I believe that the day is not too far when we will be able to find diet - based interventions for many lifestyle disorders and leverage food for better health.

As a teenager, I grew up as an aspiring astronomer and astrophysicist. I saw a quote, displayed in the canteen of IUCAA, the Inter-University Centre for Astronomy and Astrophysics in Pune, while working on my master's thesis: "The discovery of a new dish confers more happiness on humanity than the discovery of a new star." While I have not been able to discover a new star, with my data-driven explorations of food, I hope to be able to discover new dishes; Making humanity happier, and hopefully, healthier!

## Resources and References:

1. A Jain, NK Rakhi and G Bagler*, "Spices form the basis of food pairing in Indian cuisine", arXiv:1502:03815, 2015.
2. A Jain, NK Rakhi and G Bagler*, "Analysis of food pairing in regional cuisines of India", PLoS ONE, 10(10): e0139539, 2015.
3. A Jain and G Bagler*, "Culinary evolution models for Indian cuisines", arXiv:150500155, 2015.
4. N Garg et al., "FlavorDB: A database of flavor molecules", Nucleic Acids Research, 46 (D1) D1210, 2018. Available at: http://cosylab.iiitd.edu.in/flavordb

Note: This article emerged from a TEDx talk by Prof. f. Ganesh Bagler.