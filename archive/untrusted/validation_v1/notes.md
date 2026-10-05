# Validation Notes

- Data extraction from `safefood_text.txt` and `CoFID_2021.xlsx` was successful. 9 dishes were identified as ground truth.
- Web recipes were scraped using `recipe-scrapers` after fetching URLs. Some sites did not have schema.org markup (or blocked requests), so these dishes were marked as "NOT AVAILABLE".
- INDB `fat_g` values were successfully used to compute the total fat of the recipe.
- Estimated fat was consistently lower than the measured takeaway fat, showing the large discrepancy between home cooking (recipes) and restaurant dishes.
