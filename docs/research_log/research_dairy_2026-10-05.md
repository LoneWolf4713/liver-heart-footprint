# Dairy nutrition research log - 2026-10-05

Access date for all rows: 2026-10-05. Tool: Stealth Search MCP only.
Status key: VERIFIED = the page was fetched and the text seen in full; SNIPPET_ONLY = seen only in a search-result snippet (fetch failed or was not attempted).
Important caveats:
- amul.com and shop.amul.com, bigbasket, blinkit, motherdairy.com all failed to load (browser error / blocked). NO value below comes from amul.com or motherdairy.com directly.
- VERIFIED Amul values come from Sabar Dairy (sabardairy.org, an Amul-federation member milk union, pages dated 2022/2025) and Savaj Dairy (savajdairy.com, a distributor site). They reproduce Amul label tables, but they are third-party pages, not the manufacturer's site.
- Calorie-app sites (myfooddata, fatsecret, eatthismuch, nutribit, mynetdiary) are user/aggregator data and are listed only as low-trust SNIPPET_ONLY cross-checks.
- Nothing computed or filled from memory.

## (a) Values table

| # | Product | Nutrient | Value | Unit | Basis | Source URL | Verbatim quote | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Amul Fresh Cream (25% milk fat, "low fat cream") | Energy | 246 | kcal | per 100 g | https://www.amazon.in/Amul-Fresh-Cream-250ml/dp/B0758LVKLL | "Nutrition_per: 100g Energy, kcal: 246 kcal" | SNIPPET_ONLY (retailer page; fetch returned unrelated text) |
| 2 | Amul Fresh Cream | Total fat | 25 | g | per 100 g | same | "Total Fat, g: 25 g" | SNIPPET_ONLY |
| 3 | Amul Fresh Cream | Saturated fat | 16 | g | per 100 g | same | "Saturated fat,g: 16 g" | SNIPPET_ONLY |
| 4 | Amul Fresh Cream | Trans fat | 1 | g | per 100 g | same | "Trans fat, g: 1 g" | SNIPPET_ONLY |
| 5 | Amul Fresh Cream | Total carbohydrate | 3.2 | g | per 100 g | same | "Total Carbohydrate, g: 3.2 g Added sugar, g: 0 g" | SNIPPET_ONLY |
| 6 | Amul Fresh Cream | Protein | 2 | g | per 100 g | same | "Protein, g: 2 g" | SNIPPET_ONLY |
| 7 | Amul Fresh Cream | Milk fat content (claim) | 25 | % | product spec | https://www.hyperpure.com/in/amul-fresh-cream-1-l | "Milk Fat Content 25% ... Type Low fat cream" | SNIPPET_ONLY |
| 8 | Amul Fresh Cream (cross-check, aggregator) | Energy / fat / carb / protein | 246 kcal / 25 g / 3.2 g / 2 g | - | per 100 g | https://www.fatsecret.co.in/calories-nutrition/amul/fresh-cream/100g | "Cals 246 \| Fat 25g \| Carbs 3.2g \| Prot 2g" | SNIPPET_ONLY (aggregator) |
| 9 | Mother Dairy Fresh Cream | any | not found | - | - | https://www.indiamart.com/proddetail/mother-dairy-fresh-cream-2856873802712.html | "smooth, low-fat cream with 25% milk fat" (reseller text; no nutrient table seen) | SNIPPET_ONLY (fat % claim only) |
| 10 | Malai, optimised lab-made (heat-desiccated, Indian J. Dairy Sci. 75(5)) | Moisture | 49.6 | % | per 100 g malai (assumed % w/w; paper abstract says "%") | https://epubs.icar.org.in/index.php/IJDS/article/view/100089 | "The average composition of optimised malai samples was moisture, 49.6; fat, 38.2; and protein, 9.01%." | VERIFIED (abstract) |
| 11 | Malai (same paper) | Fat | 38.2 | % | same | same | same | VERIFIED |
| 12 | Malai (same paper) | Protein | 9.01 | % | same | same | same | VERIFIED |
| 13 | Malai (Wikipedia, secondary) | Butterfat | ~55 | % | not stated | https://en.wikipedia.org/wiki/Malai | "Malai has about 55% butterfat." | SNIPPET_ONLY (low trust; conflicts with row 11) |
| 14 | Amul Masti Dahi | Energy | 65 (55 per 85 g serving) | kcal | per 100 g (column "100 gm") | https://sabardairy.org/product/amul-masti-dahi/ | "Energy, k cal \| 55 \| 3% \| 65 \| 3%" | VERIFIED (Sabar Dairy, Amul union) |
| 15 | Amul Masti Dahi | Total fat | 3.1 | g | per 100 g | same | "Total fat(g) \| 2.6 \| 4% \| 3.1 \| 5%" | VERIFIED |
| 16 | Amul Masti Dahi | Saturated fat | 2.0 | g | per 100 g | same | "Saturated fat(g) \| 1.7 \| 8% \| 2.0 \| 9%" | VERIFIED |
| 17 | Amul Masti Dahi | Trans fat | 0.0 | g | per 100 g | same | "Trans Fat(g) \| 0.0" | VERIFIED |
| 18 | Amul Masti Dahi | Cholesterol | 9 | mg | per 100 g | same | "Cholesterol(mg) \| 8 \| \| 9" | VERIFIED |
| 19 | Amul Masti Dahi | Carbohydrate (= total sugars) | 4.6 | g | per 100 g | same | "Carbohydrate (g) \| 3.9 \| \| 4.6" | VERIFIED |
| 20 | Amul Masti Dahi | Protein | 4.0 | g | per 100 g | same | "Protein (g) \| 3.4 \| \| 4.0" | VERIFIED |
| 21 | Amul Masti Dahi | Sodium | 50 | mg | per 100 g | same | "Sodium(mg) \| 43 \| 2% \| 50 \| 3%" | VERIFIED |
| 22 | Amul Masti Dahi | Calcium | 150 | mg | per 100 g | same | "Calcium, mg \| 127 \| \| 150" | VERIFIED |
| 23 | Mother Dairy Plain Dahi (aggregator) | Energy/fat/carb/protein | 75 kcal / 4.5 g / 5.0 g / 3.7 g | - | per 100 g | https://www.fatsecret.co.in/calories-nutrition/search?q=Mother+Dairy+Ultimate+Dahi | "Plain Dahi (Mother Dairy) per 100g - Calories: 75kcal \| Fat: 4.50g \| Carbs: 5.00g \| Prot: 3.70g" | SNIPPET_ONLY (aggregator; also "Classic Dahi 62 kcal, 3.00 g fat") |
| 24 | Amul Pure Ghee | Energy | 814 | kcal | "Amount per 100 g" (Savaj) / "Amount per 100 ml" (Sabar) | https://savajdairy.com/product/amul-pure-ghee/ ; https://sabardairy.org/product/amul-pure-ghee/ | "Amount per 100 g Energy, kcal 814" / "Amount per 100 ml ... Energy,kcal \| 814.00" | VERIFIED (both) |
| 25 | Amul Pure Ghee | Total fat | 90.5 | g | as above | same | "Total Fat, g 90.5" | VERIFIED |
| 26 | Amul Pure Ghee | Saturated fat | 58 | g | as above | same | "Saturated fat,g 58" | VERIFIED |
| 27 | Amul Pure Ghee | Cholesterol | 190 | mg | as above | same | "Cholesterol, mg 190" | VERIFIED |
| 28 | Amul Pure Ghee | Sodium / carbohydrate / protein / sugar | 0 / 0 / 0 / 0 | mg / g / g / g | as above | same | "Sodium, mg 0 Total Carbohydrate, g 0 Sugar, g 0 Protein, g 0" | VERIFIED |
| 29 | Amul Pure Ghee | Vitamin A | 78 | mcg | as above | same | "Vitamin A, mcg 78" | VERIFIED |
| 30 | Amul Pure Ghee | Trans fat | not on the label table seen | - | - | same | table has no trans-fat row | VERIFIED absence on these two pages |
| 31 | Amul Pure Ghee | Serving size per tbsp/tsp | not found on label | - | - | - | - | NOT FOUND |
| 32 | Amul Pure Ghee (aggregator, NOT label) | Energy per tbsp | 130 kcal / 14 g fat / 9 g sat / 1 g trans | - | "1 tbsp"; page also says 929 kcal/100 g | https://www.eatthismuch.com/calories/pure-ghee-2877975 | "1 tbsp of Amul pure ghee contains 130 Calories ... 929 Calories per 100g" | SNIPPET_ONLY (user-entered; do not use) |
| 33 | Amul Pure Cow Ghee (aggregator) | serving | 14 g serving: 126 kcal, 9.1 g sat fat | - | per 14 g | https://tools.myfooddata.com/nutrition-facts/102135875/wt1 | "14g (14g) ... Calories 126 ... Saturated Fat 9.1g" | SNIPPET_ONLY (aggregator; only hint at a ~14 g tbsp) |
| 34 | Amul Pasteurized Butter (salted) | Energy | 724 | kcal | per 100 g (serving 10 g) | https://sabardairy.org/product/amul-pasteurized-butter/ | "Energy (kcal) \| 724 \| 4%" | VERIFIED |
| 35 | Amul Butter | Total fat | 80.0 | g | per 100 g | same | "Total fat(g) \| 80.0 \| 12%" | VERIFIED |
| 36 | Amul Butter | Saturated fat | 48.0 | g | per 100 g | same | "Saturated fat(g) \| 48.0 \| 22%" | VERIFIED |
| 37 | Amul Butter | Trans fat | 0.0 | g | per 100 g | same | "Trans Fat(g) \| 0.0 \| 0%" | VERIFIED |
| 38 | Amul Butter | Cholesterol | 220 | mg | per 100 g | same | "Cholesterol(mg) \| 220" | VERIFIED |
| 39 | Amul Butter | Carbohydrate / sugars | 0.0 / 0.0 | g | per 100 g | same | "Carbohydrate (g) \| 0.0" | VERIFIED |
| 40 | Amul Butter | Protein | 1.0 | g | per 100 g | same | "Protein (g) \| 1.0" | VERIFIED |
| 41 | Amul Butter | Sodium | 955 | mg | per 100 g (salt not stated separately) | same | "Sodium(mg) \| 955 \| 5%" | VERIFIED |
| 42 | Amul Taaza (toned, pouch) | Energy | 58 | kcal | basis ambiguous (see conflicts); table header says "Serving Size 200 ml" | https://sabardairy.org/product/amul-taaza/ | "Energy (k. cal) \| 58 \| 6%" | VERIFIED (as printed) |
| 43 | Amul Taaza | Total fat | 3.0 | g | same | same | "Total Fat (gm) \| 3.0 \| 9%" | VERIFIED |
| 44 | Amul Taaza | Saturated fat | 2.0 | g | same | same | "Saturated Fat (gm) \| 2.0 \| 16%" | VERIFIED |
| 45 | Amul Taaza | Trans fat / cholesterol | 0.0 g / 8 mg | - | same | same | "Trans Fat (gm) \| 0.0 ... Cholesterol (mg) \| 8" | VERIFIED |
| 46 | Amul Taaza | Carbohydrate (= sugars) | 4.7 | g | same | same | "Total carbohydrates (gm) \| 4.7" | VERIFIED |
| 47 | Amul Taaza | Protein | 3.0 | g | same | same | "Protein (gm) \| 3.0" | VERIFIED |
| 48 | Amul Taaza | Sodium / calcium | 40 mg / 110 mg | - | same | same | "Sodium (mg) \| 40 \| 4% ... Calcium (mg) \| 110" | VERIFIED |
| 49 | Amul Taaza (Savaj copy) | Energy/fat/carb/protein | 58 kcal / 3 g / 4.7 g / 3 g | - | "Amount per 100 g" | https://savajdairy.com/product/amul-tazza-milk/ | "Amount per 100 g: Energy: 58 kcal Calcium: 110 mg (100%) Total Fat: 3 g Total Carbohydrates: 4.7 g ... Protein: 3 g" | VERIFIED |
| 50 | Amul Gold (full cream) | Energy | 87 | kcal | table header "Serving Size 200 ml" (basis ambiguous) | https://sabardairy.org/product/amul-gold/ | "Energy (k. cal) \| 87 \| 9%" | VERIFIED |
| 51 | Amul Gold | Total fat | 6.0 | g | same | same | "Total Fat (gm) \| 6.0 \| 18%" | VERIFIED |
| 52 | Amul Gold | Saturated fat | 3.8 | g | same | same | "Saturated Fat (gm) \| 3.8 \| 35%" | VERIFIED |
| 53 | Amul Gold | Carbohydrate / protein | 5.0 g / 3.2 g | - | same | same | "Total carbohydrates (gm) \| 5.0 ... Protein (gm) \| 3.2" | VERIFIED |
| 54 | Amul Gold | Cholesterol / sodium / calcium | 16 mg / 42 mg / 120 mg | - | same | same | "Cholesterol (mg) \| 16 ... Sodium (mg) \| 42 \| 4% ... Calcium (mg) \| 120" | VERIFIED |
| 55 | Amul Gold (Savaj copy) | Energy/fat/sat fat/carb/protein | 87 kcal / 6 g / 3.7 g / 5 g / 3.3 g | - | listed without an explicit basis | https://savajdairy.com/product/amul-gold-milk/ (seen via https://savajdairy.com/product/amul-tazza-milk/ related-products block) | "Energy: 87 kcal ... Total Fat: 6 g Saturated Fat: 3.7 g ... Total Carbohydrates: 5 g Protein: 3.3 g" | VERIFIED |
| 56 | Amul Slim n Trim (double toned, 180 ml pouch) | Energy | 87 | kcal | table header "Serving Size 190 ml" - values are clearly PER SERVING (190 ml), not per 100 ml | https://sabardairy.org/product/amul-slim-n-trim/ | "Serving Size \| 190 ml ... Energy (k. cal) \| 87 \| 4%" | VERIFIED (as printed) |
| 57 | Amul Slim n Trim | Total fat / sat fat | 2.8 g / 1.9 g | - | per 190 ml serving | same | "Total Fat (gm) \| 2.8 \| 4% ... Saturated Fat (gm) \| 1.9 \| 9%" | VERIFIED |
| 58 | Amul Slim n Trim | Carbohydrate / protein | 9.5 g / 6.0 g | - | per 190 ml serving | same | "Total carbohydrates (gm) \| 9.5 ... Protein (gm) \| 6.0" | VERIFIED |
| 59 | Amul Slim n Trim | Sodium / calcium / cholesterol | 80 mg / 228 mg / 8 mg | - | per 190 ml serving | same | "Sodium (mg) \| 80 \| 4% ... Calcium (mg) \| 228" | VERIFIED |
| 60 | Amul Slim n Trim Skimmed (aggregator) | Energy/fat/carb/protein | 35 kcal / 0.1 g / 5 g / 3.5 g | - | per 100 ml | https://www.fatsecret.co.in/calories-nutrition/amul/slim-n-trim-skimmed-milk/100ml | "Cals 35 \| Fat 0.1g \| Carbs 5g \| Prot 3.5g" | SNIPPET_ONLY (this is the skimmed variant, not double toned) |
| 61 | Amul Slim n Trim (double toned) | Fat %, SNF % printed on label | not found | - | - | - | - | NOT FOUND |
| 62 | Amul Taaza / Gold / Slim | Fat %, SNF % printed on label | not found (fat % only inferable from the kcal/fat grams above; not stated) | - | - | - | - | NOT FOUND |
| 63 | Mother Dairy Toned Milk (aggregator) | Energy/fat/carb/protein | 59 kcal / 3.1 g / 4.7 g / 3.1 g | - | per 100 ml | https://www.fatsecret.co.in/calories-nutrition/mother-dairy/toned-milk/100ml | "Cals 59 \| Fat 3.1g \| Carbs 4.7g \| Prot 3.1g" | SNIPPET_ONLY (aggregator; saturated fat not given) |
| 64 | Mother Dairy Toned Milk (aggregator) | Energy/fat/carb/protein | 64 kcal / 3.6 g / 5 g / 3 g | - | per 100 ml | https://www.mynetdiary.com/food/calories-in-toned-milk-by-mother-dairy-ml-34647084-0.html | "There are 64 calories in 100 ml of Toned Milk from: Carbs 5g, Fat 3.6g, Protein 3g." | SNIPPET_ONLY (conflicts with row 63) |
| 65 | Amul Malai Paneer | Energy | 314 | kcal | per 100 g (serving 50 g) | https://sabardairy.org/product/amul-malai-paneer/ | "Energy (k. cal) \| 314 \| 8%" | VERIFIED |
| 66 | Amul Malai Paneer | Total fat | 25 | g | per 100 g | same | "Total Fat (gm) \| 25 \| 19%" | VERIFIED |
| 67 | Amul Malai Paneer | Saturated fat | 15 | g | per 100 g | same | "Saturated Fat (gm) \| 15 \| 34%" | VERIFIED |
| 68 | Amul Malai Paneer | Trans fat / cholesterol | 0.0 g / 65 mg | - | per 100 g | same | "Trans Fat (gm) \| 0.0 ... Cholesterol (mg) \| 65" | VERIFIED |
| 69 | Amul Malai Paneer | Carbohydrate (= sugars) / added sugar | 4.5 g / 0 g | - | per 100 g | same | "Carbohydrates (gm) \| 4.5 ... Added Sugar (gm) \| 0" | VERIFIED |
| 70 | Amul Malai Paneer | Protein | 20.0 | g | per 100 g | same | "Protein (gm) \| 20.0" | VERIFIED |
| 71 | Amul Malai Paneer | Sodium / calcium | 22 mg / 480 mg | - | per 100 g | same | "Sodium (mg) \| 22 \| 1% ... Calcium (mg) \| 480" | VERIFIED |
| 72 | FSSAI: Toned milk | Min fat / min SNF | 3.0 / 8.5 | % | regulatory minimum | https://www.foodsafetymantra.com/regulatory-insight/consumer-products/milk-cream/fssai-categorization-of-milk-products-and-their-standards/ | "Toned milk \| 3.0 \| 8.5" (cites FSS Food Products Standards Regulations 2011) | VERIFIED (secondary summary, not fssai.gov.in; official PDF failed to load) |
| 73 | FSSAI: Double toned milk | Min fat / min SNF | 1.5 / 9.0 | % | regulatory minimum | same | "Double Toned milk \| 1.5 \| 9.0" | VERIFIED (secondary) |
| 74 | FSSAI: Full cream milk | Min fat / min SNF | 6.0 / 9.0 | % | regulatory minimum | same | "Full Cream \| 6.0 \| 9.0" | VERIFIED (secondary) |
| 75 | FSSAI: Standardized milk | Min fat / min SNF | 4.5 / 8.5 | % | regulatory minimum | same | "Standardized milk \| 4.5 \| 8.5" | VERIFIED (secondary) |
| 76 | FSSAI: Skimmed milk | Max fat / min SNF | 0.5 / 8.7 | % | regulatory | same | "Skimmed milk \| Not more than 0.5 \| 8.7" | VERIFIED (secondary) |
| 77 | FSSAI: Cow milk / buffalo milk (species) | Min fat / min SNF | cow 3.2 / 8.3; buffalo 6.0 / 9.0 | % | regulatory minimum | same | "Buffalo milk \| 6.0 \| 9.0 ... Cow milk \| 3.2 \| 8.3" | VERIFIED (secondary) |
| 78 | India milk production by species (2023-24) | Cow share | 53.12 | % of 239.30 Mt | national | https://www.thehindu.com/news/national/india-produces-23930-million-tonnes-of-milk-centre/article69924801.ece | "53.12% of the total milk produced is contributed by cows, while buffaloes' share is 43.62%." (Lok Sabha reply, 12 Aug 2025) | VERIFIED (news report of Govt reply; BAHS PDF failed to load) |
| 79 | Same | Buffalo share | 43.62 | % | national | same | same | VERIFIED |
| 80 | Same | Cow milk / buffalo milk tonnage | 1,27,105.15 / 1,04,388.29 | '000 tonnes | national | same | "production of cow milk is 1,27,105.15 thousand tonnes, while ... buffaloes is 1,04,388.29 thousand tonnes" | VERIFIED |
| 81 | India total milk production | Total | 239,299 | '000 tonnes (2023-24) | national | https://www.nddb.coop/information/stats/milkprodstate | "All India ... 2022-23 2,30,577 \| 2023-24 2,39,299" | SNIPPET_ONLY (table in search result) |

## (b) Items not found
- Any value directly from amul.com / shop.amul.com / motherdairy.com / bigbasket / blinkit (all blocked or failed to load). Amazon.in Amul Fresh Cream label was only seen in a search snippet.
- Mother Dairy fresh cream and Mother Dairy toned/dahi LABEL values (only aggregator numbers; no saturated fat for Mother Dairy toned milk).
- Fat % and SNF % as printed on Amul Taaza / Gold / Slim n Trim packs.
- Ghee serving size in grams per tbsp/tsp on the Amul label; trans fat for ghee on label (the label table has no trans-fat row).
- Amul Cow Ghee as a separate product (none located; Sabar's "Sagar Ghee" shows identical numbers per its listing snippet, not fetched).
- Salt (g) for Amul butter (only sodium 955 mg given).
- Home-made malai from ICMR-NIN/IFCT or a textbook; only the IJDS lab-made malai paper (moisture/fat/protein; no carbohydrate, ash or energy) was found.
- Statement that a specific milk type (toned vs full cream) is the MOST consumed in India. Not found; only species production shares (cow vs buffalo) were found.
- Official FSSAI/NDDB primary documents (fssai.gov.in chapter PDF, BAHS-2024 PDF, nddb species page all failed to load).

## (c) Conflicts and ambiguities
1. Amul milk basis (Sabar Dairy). Taaza and Gold tables print "Serving Size 200 ml", but the numbers are consistent with per 100 ml (Gold 87 kcal = 6 g fat + 5 g carb + 3.2 g protein, by Atwater arithmetic - this is a plausibility check only, not a stored value). Slim n Trim prints "Serving Size 190 ml" and its numbers (87 kcal, 2.8 g fat, 9.5 g carb, 6.0 g protein) are clearly per 190 ml serving, i.e. roughly 46 kcal / 1.5 g fat / 5 g carb / 3.2 g protein per 100 ml, which matches the fatsecret 100 ml entry (46 kcal, 1.5 g, 5 g, 3.2 g; SNIPPET_ONLY). Do not treat Slim n Trim 87 kcal as per 100 ml. Confirm the basis against a pack image before use.
2. Amul Gold saturated fat: 3.8 g (Sabar Dairy) vs 3.7 g (Savaj Dairy); protein 3.2 g vs 3.3 g.
3. Amul Gold vs Amul "Taaza" product naming: Sabar Dairy's listing page pairs "Amul Taaza UHT Milk" with 71 kcal / 4.5 g fat and "Amul Gold UHT" with 58.2 kcal / 3.0 g fat (from the snippet of /our-products/), which looks swapped relative to the pouch pages (Taaza 3.0 g, Gold 6.0 g). UHT pages not fetched; do not use those rows.
4. Ghee basis: Sabar says "Amount per 100 ml", Savaj says "Amount per 100 g", identical numbers. 814 kcal vs 90.5 g fat is internally inconsistent (90.5 x 9 = 814.5, so fat alone accounts for it), whereas aggregators list 897 kcal / 99.7 g fat per 100 g (myfooddata, SNIPPET_ONLY) and 929 kcal/100 g (eatthismuch). Amul's label (90.5 g fat, 58 g sat fat) implies ~9.5% non-fat/moisture which is unusual for ghee (FSSAI ghee is >=99.7% fat; not verified here). Treat the label values as printed but flag for review.
5. Amul Fresh Cream: Amazon label (246 kcal, 25 g fat) vs myfooddata entry (35 kcal, 0.19 g fat, 91.5% water) - the latter is clearly a mis-entered milk-like record; ignore it.
6. Malai fat: IJDS lab study 38.2% fat vs Wikipedia "about 55% butterfat" (no citation seen). Prefer the paper; real home malai varies with milk fat and method.
7. FSSAI double-toned/other minimums: foodsafetymantra and collegedunia agree (double toned 1.5% fat, 9.0% SNF; full cream 6.0/9.0), but dairyfarmmanager.com (SNIPPET_ONLY) states double toned SNF 8.4%, whole milk 4.5/8.7, cow milk 3.5/8.5. Primary FSSAI text could not be loaded; verify before citing.
8. Mother Dairy toned milk: fatsecret 59 kcal / 3.1 g fat vs mynetdiary 64 kcal / 3.6 g fat per 100 ml (both aggregator, unverified).
9. Cow vs buffalo: the 2025 Lok Sabha figures (cow 53.12%, buffalo 43.62%) imply cow milk is the largest single-species share nationally, but buffalo milk dominates in UP/Rajasthan/Punjab-type markets and in loose/packaged toned milk; this is not a statement about which milk type (toned/full cream) is most consumed.
