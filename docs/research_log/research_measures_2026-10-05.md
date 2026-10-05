# Research log: Indian household measures and piece weights (2026-10-05)

Tools: Stealth Search MCP only. Status key: VERIFIED = I saw the text on a page fetched in full by `fetch`; SNIPPET_ONLY = seen only in a search-result passage (for the NIN PDF, a page extract returned by the search tool; the full-PDF fetch was truncated at page 19 and `read_section` could not reach later pages, so Annexure pages were not seen via a direct fetch).
Several fetches (tarladalal, vegrecipesofindia, indianhealthyrecipes) failed with a tool browser error ("cannot switch to a different thread"); no blocked-login bypass attempted.

## (a) Values

### Q1. Cup / katori / spoon volumes

| Item | Value | Unit | Source | URL | Verbatim quote | Year | Status |
|---|---|---|---|---|---|---|---|
| Large katori | 360 | ml | ICMR-NIN Dietary Guidelines for Indians, Annexure I (p.111) | https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf | "Large Katori C6 - 360ml" | 2024 | SNIPPET_ONLY |
| Medium katori | 200 | ml | same | same | "Medium Katori C7 - 200ml" | 2024 | SNIPPET_ONLY |
| Small katori | 155 | ml | same | same | "Small Katori C8 - 155ml" | 2024 | SNIPPET_ONLY |
| Small katori (alt, marked *) | 115 | ml | same | same | "*Small Katori C9 -115ml" | 2024 | SNIPPET_ONLY |
| Tablespoon (NIN) | 15 | g (as printed; NIN states grams not ml) | same | same | "Tablespoon 15g" | 2024 | SNIPPET_ONLY |
| Teaspoon (NIN) | 5 | g (as printed) | same | same | "Teaspoon 5g" | 2024 | SNIPPET_ONLY |
| 1 cup / katori in NIN diet charts | 200 | ml | same (Fig 9.2, p.65) | same | "Measures: 1 cup/Katori =200ml" | 2024 | SNIPPET_ONLY |
| Cup (NIN-affiliated IMD site) | 250 | ml | iamdiet.in Household Measure | https://iamdiet.in/household_measure | "1 Cup 250ml ... 1 Glass 250ml ... 1 Katori 210ml ... Teaspoon (tsp) 5g ... Tablespoon (Tbsp) 15g ... 1 Large glass 310ml" | n/d | SNIPPET_ONLY (not verified as NIN-official) |
| Cup per "BIS" | 240 | ml | measurements.in guide (author Vijay Pandit; see reliability note) | https://measurements.in/guides/how-many-ml-in-one-cup-for-indian-cooking-recipes | "The Bureau of Indian Standards (BIS) defines 1 cup as 240 ml." | 2026 | VERIFIED (page seen; claim itself unsourced) |
| Katori on same site | 120 / 150 / 200 (small/medium/large) | ml | same | same | "A standard medium katori has a volume of approximately 150 ml. A large katori holds 200 ml. A small katori holds 120 ml." | 2026 | VERIFIED |
| tsp / tbsp on same site | 5 / 15 | ml | same | same | "1 Tablespoon 15 ml ... 1 Teaspoon 5 ml" | 2026 | VERIFIED |
| Cup on Loovi converter | 250 | ml | loovi.in | https://loovi.in/tools/kitchen-unit-converter | "This converter uses 1 cup = 250 ml, the measuring-cup size sold with most Indian kitchen sets." | 2026 | SNIPPET_ONLY |
| Katori on Loovi | 150 | ml | same | same | "1 katori = 150 ml" | 2026 | SNIPPET_ONLY |
| Katori range (blog) | 100-150 small; 150-200 standard | ml | fittrackai.in | https://www.fittrackai.in/blog/indian-food-portion-sizes-what-1-katori-1-bowl-1-plate-actually-means-2026 | "Standard katori: 150-200ml (most common home size)" | 2026 | SNIPPET_ONLY |

Indian recipe-site own measurement notes (hebbarskitchen, vegrecipesofindia, indianhealthyrecipes, archanaskitchen, tarladalal): NOT obtained (fetch failures / no snippet).

### Q2. Weight of 1 tsp salt

| Item | Value | Unit | Source | URL | Verbatim quote | Year | Status |
|---|---|---|---|---|---|---|---|
| Salt per day = 1 teaspoon (ICMR-NIN) | 5 (g per "1 teaspoon") | g | ICMR-NIN DGI 2024 p.74 | https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf | "around 5000mg or 5g (1 teaspoon) of common salt per day" | 2024 | SNIPPET_ONLY |
| Salt in NIN diet | 5 | g iodised salt/day | same p.65 | same | "In the meal preparation 20g oil and 5g iodised salt can be used" | 2024 | SNIPPET_ONLY |
| 1 level tsp table salt | 6 | g | cookingconverter.com | https://www.cookingconverter.com/measurements/salt/teaspoons/grams | "1 teaspoon of salt (table salt) is 6 grams." | 2026 | SNIPPET_ONLY (non-Indian converter) |
| 1 tsp iodized salt | ~6 | g | saltandolive.com | https://www.saltandolive.com/by-type/ | "One teaspoon of iodized table salt weighs approximately 6 grams." | 2026 | SNIPPET_ONLY |
| 1 tsp fine table salt | 5.69-6 | g | same | same | "Fine table salt: approximately 6 grams per teaspoon (5.69 to 6 g)" | 2026 | SNIPPET_ONLY |
| 1 tsp table salt, bulk density | ~5.67 | g (US tsp 4.93 ml) | thelivinglook.com | https://thelivinglook.com/kitchen-hacks/how-many-grams-of-salt-in-a-teaspoon | "Multiply by 4.92892 mL → ~5.67 g per level teaspoon." | 2026 | SNIPPET_ONLY |
| WHO | 5 g salt/day (WHO statement itself not seen); 2,300 mg Na ~ 5 g salt per NIN | g | secondary: nutritionsimplify.com | https://nutritionsimplify.com/how-much-salt-per-day/ | "The WHO and Indian guidelines both put the adult limit at under about 5 g of salt a day." | 2026 | SNIPPET_ONLY |

No peer-reviewed Indian salt-spoon measurement study and no WHO page giving g per tsp was found.

### Q3. Piece weights and black salt sodium

No Indian scientific/official source (NIN, IFCT, atlas, BIS) with per-piece weights was found. Only Western/general web sources below (not India-specific; treat as low-confidence).

| Item | Value | Unit | Source | URL | Verbatim quote | Year | Status |
|---|---|---|---|---|---|---|---|
| Onion small/medium/large | 105 / 150 / 202 | g (peeled, edible) | nourishatlas.com (NZ/AU style table) | https://nourishatlas.com/blog/how-much-does-an-onion-weigh.html | "Brown or red onion | 105 g | 150 g | 202 g" | 2026 | SNIPPET_ONLY |
| Onion medium | 110-150 | g | same/search digest | same | "A medium-sized onion typically weighs between 110 to 150 grams" | 2026 | SNIPPET_ONLY |
| Tomato S/M/L | 84 / 120 / 162 | g | nourishatlas.com | same | "Tomato | 84 g | 120 g | 162 g" | 2026 | SNIPPET_ONLY |
| Tomato medium | 75-150 | g | weighschool.com | https://weighschool.com/tomato-weights/ | "Medium Tomato | 75-150g" | 2026 | SNIPPET_ONLY |
| Potato S/M/L | 119 / 170 / 230 | g | nourishatlas.com | same | "Potato | 119 g | 170 g | 230 g" | 2026 | SNIPPET_ONLY |
| Potato medium (alt) | 213 | g | scaleforgram.com | https://www.scaleforgram.com/weigh-vegetables | "A medium potato runs about 213 grams" | 2026 | SNIPPET_ONLY |
| Chilli S/M/L (generic "Chilli") | 6 / 8 / 11 | g | nourishatlas.com | same | "Chilli | 6 g | 8 g | 11 g" | 2026 | SNIPPET_ONLY |
| Garlic clove S/M/L | 2 / 3 / 4 | g | nourishatlas.com | same | "Garlic clove | 2 g | 3 g | 4 g" | 2026 | SNIPPET_ONLY |
| Black cardamom pod | ~3 | g/pod | cupstogramscalculator.com | https://cupstogramscalculator.com/black-cardamom/ | "Whole pods (72g/cup, ~3g per pod, ~24 pods per cup)" | n/d | SNIPPET_ONLY |
| Kala namak sodium | 38,800 | mg Na per 100 g | kidneyfoods.com database (not a study) | https://www.kidneyfoods.com/food/black-salt-kala-namak | "Per 100.0g serving, Black Salt — Kala Namak provides 38800mg of sodium" | n/d | SNIPPET_ONLY |
| "Unrefined black salt (Himalayan)" sodium | 38,200 | mg per 100 g | health.com | https://www.health.com/black-salt-vs-regular-salt-11815739 | "Unrefined black salt (Himalayan): 38,200 milligrams" | 2026 | SNIPPET_ONLY |

Both sodium figures are essentially pure-NaCl values (NaCl theoretical ~39,300 mg/100 g), not measured kala namak from a study; kala namak composition source (COA) says ">97% sodium chloride" (scribd, not fetched). Himalayan "black salt" in health.com may not equal kala namak.

### Q4. Kasuri methi per tablespoon

| Item | Value | Unit | Source | URL | Verbatim quote | Year | Status |
|---|---|---|---|---|---|---|---|
| 1 tbsp kasuri methi (retailer label) | 2.7 | g | trueindianspices.com.au product label | https://trueindianspices.com.au/products/kasoori-methi-dried-fenugreek-leaves | "Amount per: 1 tbsp (2.7g)" | n/d | SNIPPET_ONLY |
| 1 tbsp dried loose (calculator) | 0.75 | g | cupstogramscalculator.com | https://cupstogramscalculator.com/fenugreek-leaves/ | "1 tablespoon | 0.75g" (crumbled 1.0 g; 1 cup loose = 12 g) | n/d | SNIPPET_ONLY |

## (b) Not found
- Indian recipe sites' own measurement notes (hebbarskitchen, vegrecipesofindia, indianhealthyrecipes, archanaskitchen, tarladalal): fetches failed; nothing seen.
- NIN Annexure II (raw food measures) contents and any NIN "weight of 1 tsp salt/sugar/oil" table: not retrieved (PDF truncated by tool).
- Indian per-piece weights for onion, tomato, potato, green chilli, ginger (1 inch), green cardamom pod; garlic clove and black cardamom only from non-Indian/non-scientific web pages.
- WHO statement of g salt per teaspoon; Indian salt-spoon study.
- Measured sodium of kala namak from a peer-reviewed study.
- Reliable kasuri methi tbsp weight from an Indian scientific source.

## (c) Conflicts / reliability notes
- Cup: NIN uses 200 ml for "1 cup/katori" in its diet charts (medium katori 200 ml); measurements.in claims BIS = 240 ml (unsourced; page has odd "State Revenue Records" credit, low trust); IMD site and Loovi use 250 ml. No Indian recipe-site statement seen.
- Katori: NIN 115/155/200/360 ml vs measurements.in 120/150/200 ml vs IMD 210 ml vs Loovi 150 ml.
- Salt tsp: NIN equates 5 g with "1 teaspoon" (a dietary-limit convention, and NIN lists teaspoon as "5g" generally) vs 5.7-6 g from converter sites for a level tsp of fine salt. Not a true measured weight from NIN.
- Kasuri methi tbsp: 2.7 g (product label) vs 0.75 g (calculator); a 3.6x gap, calculator figure looks implausibly low versus its own 12 g/cup.
- Onion medium 150 g (peeled, one table) vs 110-150 g range; potato medium 170 vs 213 g.
