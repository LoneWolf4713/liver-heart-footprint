## CGAS ASSIGNMENT - 1 RUBRIC

Name each Jupyter notebook with the question numbers. Submit a zip folder containing Jupyter notebooks, their PDFs, CSV files, and PNG images.

Answers to questions 4-8 are to be presented as a single scanned PDF file of handwritten answers.

Use this filename convention for the zip folder: Group\_No.\_Assignment1 . (Anyone not following this, 2 marks will be deducted directly). In case of plagiarism, 50% of the marks obtained will be deducted.

1. Complete the following analysis using the recipes' data.
2. (a) Scrape (using libraries such as BeautifulSoup) any 10,000 recipes. Submit the raw data. [5] Include recipe titles, ingredient phrases, cooking instructions, and other relevant details.

Use any online repository, such as allrecipes.com, tasteatlas.com, bbc.com, etc . , to extract the recipes.

Data should be saved in CSV format containing

- Column 1 - Recipe name (0.5 mark)
- Column 2 - Recipe URL (0.5 mark)
- Column 3 - List of ingredient phrases (1.5 marks)
- Column 4 - List of instructions (1.5 marks)
- Column 5 - Region/Cuisine (optional)
- Column 6 - Servings (optional)
- Column 7 - Preparation time (optional)

1 mark for the optional columns

- (b) Write a script to extract information about the ' names of the ingredients' from the ingredients section using Named Entity Recognition. [8]
- Assign random Recipe IDs to all 10,000 recipes, such as Recipe 1, Recipe 2, Recipe 3, and so on. (0.5 mark)
- Fetch non - duplicate ingredient entries from the recipes. Store the recipe ID and ingredient phrase in separate columns.
- Apply NER (Named Entity Recognition) to extract the named entity (ingredient) from ingredient phrases. You can use built-in libraries, such as SpaCy, Stanford NER, etc. (7.5 marks)
- (c) Store recipes in the form of a (Recipe ID)—(Ingredient Name) form . [2]
- Randomly choose 100 recipe IDs and save the recipe and ingredient information in (Recipe

ID)—(Ingredient Name) format in a text file. (1.7 marks)

```
For, e.g., Ingredients for Recipe 'Egyptian-lentil-soup' (http://allrecipes.com/recipe/222661/egyptian-lentil-soup/) 3 cups water
```

## 1 cup red lentils

## 1 roma tomato, quartered

|   Recipe ID  | Ingredient Name   |
|--------------|-------------------|
|            1 | water             |
|            1 | Red lentils       |
|            1 | Roma tomato       |

2. Analyze the data obtained for the following.
2. (a) Find the number of unique ingredients. List them with their frequencies. Submit the file. [2]
- Code to find the count of unique ingredients (0.5 mark)
- List all unique ingredients along with their frequencies (1 mark)
- Store the list in a data frame (0.5 mark)
6. (b) Plot the recipe size distribution for these recipes and the average size of the recipes (s). Properly label the axes. Submit the file. [3]
- Code to plot the recipe size distribution (1 mark)
- Find the average size of the recipes and round it off to the nearest integer (1 mark)
- Label the axes and tick marks properly. Save the plot as PNG (1 mark)
10. (c) Plot cumulative distribution of recipe size (label axes properly). Submit the file. [5]
- Code to plot the CDF of recipe size (3.5 marks)
- Label the axes and tick marks properly. Save the plot as PNG (1.5 mark)
3. For the data of recipes obtained in the above question (1):
14. (a) Plot the frequency-rank distribution. Scale and label axes properly. Submit the file. [5]
- Code to plot the normalized Freq-Rank Distribution. (3.5 marks)
- Label the axes and tick marks properly. Save the plot as SVG and PNG (1.5 mark)
4. Compare the nutritional profile of a 'boiled egg' versus that of a 'boiled rice and daal'. [2] Write atleast two comparison points for the nutritional profile of a 'boiled egg' versus that of a 'boiled rice and daal'. (2 marks)
5. List five most uncommon food ingredients that you (or your parents or grandparents) know of. List their (a) Common/Vernacular/Local Name, (b) English Name (if available), (c) Seasonal Use (if known), and (d) Nutritional Values (if available). [5]
19. List 5 most uncommon food ingredients with their common name, English name, seasonal use, and nutritional value. ((5*(4*0.25)) = 5 marks)
6. Consider the following statements and provide scientific arguments about whether they are a scientific truth or a myth. [3]
21. (a) Cooking food in the microwave destroys its 'nutritional value'.

Provide the scientific argument (1 mark)

- (b) Refrigerating food destroys its 'nutritional value'.

Provide the scientific argument (1 mark)

## (c) Genetic modifications in plants or animals are

'bad'. Provide the scientific argument (1 mark)

7. Write a brief (5-8 lines) summary on the technique used for finding out the calorific content of food products. [2]

Write the summary mentioning at least 5 points. (2 marks)

8. List eight specific technologies/products, with 1-3 lines of description for each that you envision could emerge from the application of the Computational Gastronomy paradigm. Be as specific/narrow as possible. [8]

List eight specific technologies/products with their description (1 mark for each product. (1*8 marks))