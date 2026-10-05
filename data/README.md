# Data inventory and trust levels
Trust: [V] verified/real | [P] partially verified | never use anything in `archive/untrusted/`.

## raw/ (read-only sources)
| Path | Content | Trust | Notes / licence |
|---|---|---|---|
| raw/indb/ | Indian Nutrient Databank (GitHub lindsayjaacks/INDB): INDB.xlsx (1,014 recipes, per-100 g/per-serving nutrients), recipes*.xlsx (ingredient grams), Units.xlsx, UK_fct, US_fct, USDA_nrf | [V] | Open; the raw IFCT ingredient table is NOT included (request it from NIN / the professor) |
| raw/cofid/CoFID_2021.xlsx | UK McCance & Widdowson CoFID 2021 (proximates incl. water, fatty acids; analysed South Asian dishes) | [V] | UK Open Government Licence; check column F/G for analysed vs calculated |
| raw/safefood/ | safefood (Ireland) 2015 "What's in your Indian takeaway?" PDF + extracted text: lab-analysed takeaway dishes | [V] | Cite source |
| raw/flavordb/ | Public FlavorDB scrape (tarek-kerbedj/flavor_db2.0): flavordb.csv, molecules.csv | [V] | Scrape of CoSyLab FlavorDB; coverage of fats/sugars is sparse |
| raw/ifct2017_transcription/ | Unofficial IFCT 2017 transcription (nodef/ifct2017), 542 foods; see PROVENANCE.md | [V] for the 137 codes INDB uses (reproduces INDB 982/982); other codes [U]; fats' energy = 0 (defect) | NIN copyright: research use, do not redistribute |
| raw/fdc_portions/ | USDA FoodData Central SR Legacy 2018-04 bulk CSV (food, food_portion, measure_unit + zip) | [V] public domain |
| raw/literature/ | Europe PMC full-text XML: Gupta 2016 (PMC4826272), Joshee 2019 (PMC6894861), Jain 2024 (PMC11465016) | [V] | Open access |

## curated/
| File | Content | Trust |
|---|---|---|
| measures.csv (+ measures_README.md) | Household measure -> grams, every row cited (INDB Units.xlsx, USDA FDC SR Legacy portions, INDB.do rules) | [V] sources; assumptions flagged in note column |
| indian_products.csv | 6 Indian products (Amul toned milk, dahi, Malai Paneer, salted butter, fresh cream; home malai) per 100 g, codes L901-L906, with citations and derivations | [V] labels; cream/malai partly derived [U] |
| constants.csv | Conversion factors and sanity bounds with sources (FAO FNP 77, IUPAC, INDB) | [V] |
| classes.csv | Food code -> class (ADDED_SUGAR, REFINED_GRAIN, COOKING_OIL, DAIRY_FAT, HYDROGENATED_FAT, SALT, SPICE, WATER) | project decisions; [U] items marked |
| aliases.csv | Ingredient name -> code (created by build task T4) | checked by acceptance tests + hidden set |
| fried_foods_lab.csv | 69 lab-measured fat values for fried South Asian foods (item, category, setting, method, source) | [P]: 61 rows from verified sources (Gupta, CoFID, Joshee, Jain, safefood, Chen); 8 rows (Sakhale 2011, Yadav 2012, Gaikwad 2022, Neethu 2025) not yet checked against the papers. Joshee values are FAME sums (lower than Soxhlet); keep them separate |
| baselines.csv | NSO 2025 intake, ICMR-INDIAB-21 regional SFA/fat/sugar, ICMR-NIN 2024 limits, MASLD prevalence | [V] values; page/table references [U] |
| validation_ground_truth.csv | Lab-analysed cooked dishes (CoFID with evidence strings; safefood) used in validation v2 | [V] |

## samples/
| Path | Content | Trust |
|---|---|---|
| samples/dryrun_recipes/ | 62 attempted / 43 fetched recipe pages, 790 ingredient lines (real URLs) | [V] |
| samples/validation_v2/ | 27 recipes + parsed per-ingredient table (CoFID-mapped) | [V] |

## Still needed
- IFCT 2017: transcription in hand and checked (research_log 41); official table from NIN still preferable. RecipeDB2 bulk (optional, professor).
- A real recipe corpus (~15,000 URLs reachable on hebbarskitchen, archanaskitchen, indianhealthyrecipes, cookwithmanali, pipingpotcurry, ranveerbrar).
- More author-stated substitutions (6 real so far).
