# Deliverable 4 (D4) · Live Web App 10+ URL Verification Report

- **Endpoint tested:** `POST http://127.0.0.1:8001/api/scrape-and-analyze`
- **URLs passed:** **13 / 13** across **5 distinct recipe websites** (`archanaskitchen.com, cookwithmanali.com, hebbarskitchen.com, indianhealthyrecipes.com, pipingpotcurry.com`)
- **Engine parity check:** Every passing URL compared per-serving outputs (`energy_kcal`, `fat_g`, `sfa_g`, `added_sugar_g`, `sodium_mg`, `refined_carb_g`) directly against `lhf.pipeline.analyse_recipe` with exact match.

| Site | Dish Title | Servings | Lines (Inc/Tot) | Frying Fix | Kcal / Serv | SFA / Serv | Engine Parity |
|---|---|---:|---:|---|---:|---:|---|
| indianhealthyrecipes.com | Samosa Recipe (Punjabi Potato Samosa) | 10.0 | 18/21 | Applied | 297.0 | 6.5 g | Exact Match |
| indianhealthyrecipes.com | Paneer Butter Masala Recipe | 4.0 | 19/21 | No | 442.0 | 18.6 g | Exact Match |
| indianhealthyrecipes.com | Chole Recipe (Punjabi Chole Masala) | 4.0 | 28/31 | No | 306.5 | 3.6 g | Exact Match |
| indianhealthyrecipes.com | Chicken Biryani Recipe | 4.0 | 25/27 | No | 560.4 | 9.2 g | Exact Match |
| hebbarskitchen.com | Paneer Butter Masala Recipe - Restaurant Style | 5.0 | 24/26 | No | 416.7 | 16.0 g | Exact Match |
| hebbarskitchen.com | Dal Makhani Recipe Restaurant Style in Cooker - Tips & Tricks | 4.0 | 16/22 | No | 249.2 | 7.2 g | Exact Match |
| hebbarskitchen.com | Gulab Jamun Recipe - Milk Powder: Delicious Indian Dessert | 14.0 | 8/12 | Applied | 243.8 | 4.5 g | Exact Match |
| cookwithmanali.com | How to Make Paneer Butter Masala, Step by Step | 4.0 | 20/22 | No | 391.9 | 15.9 g | Exact Match |
| cookwithmanali.com | Chole Recipe (Punjabi Chole Masala) | 5.0 | 19/23 | No | 353.7 | 2.9 g | Exact Match |
| archanaskitchen.com | Restaurant Style Paneer Butter Masala Recipe | Paneer Makhani Recipe | 4.0 | 21/23 | No | 367.6 | 18.5 g | Exact Match |
| archanaskitchen.com | Calcutta Style Chicken Biryani Recipe | 3.0 | 15/18 | No | 1109.6 | 19.7 g | Exact Match |
| pipingpotcurry.com | Paneer Butter Masala (Instant Pot & Stovetop) | 6.0 | 21/23 | No | 354.5 | 15.6 g | Exact Match |
| pipingpotcurry.com | Authentic Chicken Biryani | 6.0 | 25/28 | No | 687.2 | 9.5 g | Exact Match |
