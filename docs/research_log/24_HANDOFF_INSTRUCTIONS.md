# 24 HANDOFF: instructions for a fresh Claude session to run the feasibility tests
Written 2026-09-29 by the previous session. You (the new session) have NO memory of the earlier chat. Everything you need is in this folder.

## 0. Read first (in this order)
1. research_log/23_MASTER_SUMMARY_v2.md  (who, rules, chronology, selected project)
2. research_log/22_liver_footprint_concept.md  (full concept, grounding numbers, website dry-run, loopholes L1-L11, test plan T1-T6)
3. research_log/21_india_problems_and_reel_idea.md  (why this idea; legality notes; existing apps)
4. research_log/19_phase3_red_team.md (end section "RE-EVALUATION") - the lesson on ground truth
Skim the course files in the parent folder only if needed.

## 1. Your mission
Run feasibility tests T1-T7 below for the project "Liver footprint of Indian recipes" and write ONE report:
research_log/25_TEST_REPORT.md
Do NOT redesign or replace the project. Do NOT propose new project ideas. Your job is to measure whether the data and methods actually work, with numbers, and flag what breaks.

## 2. Non-negotiable rules
- Web SEARCH: only the Stealth Search MCP tools (mcp__stealth-search__search, batch_search, fetch, get_toc, read_section, fast_neural_search). Never the built-in WebSearch. Run searches sequentially.
- Direct downloads of data files/pages for the tests may use the Stealth fetch tool, or Python (requests/yt-dlp etc.) from the shell if available. Be polite: <= 1 request/second per site, identify a normal user agent, respect robots.txt.
- Store only extracted FACTS (ingredient lines, quantities, URLs, timestamps). Do not republish recipe prose or video content. Keep the source URL for every row.
- NO Instagram, NO Zomato/Swiggy, NO login-walled content.
- Mark every claim [V] verified (you saw it) or [U] unverified. Give counts and denominators, not adjectives.
- Log progress as you go: append to research_log/25_TEST_REPORT.md after each test (so nothing is lost if you crash).
- Put raw data under research_log/data/ (create it) as CSV/JSON, one file per test (t1_*.csv, t7_*.csv ...).
- Keep costs under control: use the sample sizes given; do not expand them without reason. If a step is blocked for >3 attempts, record the blocker and move on.
- Report back to the user honestly, including failures. The user strongly dislikes overclaiming and "betting".

## 3. Setup (do once)
- Check tools: `python3 --version`, `pip --version`, `ffmpeg -version`, `yt-dlp --version`. Work in a scratch dir or research_log/data/.
- If Python works, install as needed (user-level or venv): `recipe-scrapers extruct requests beautifulsoup4 pandas youtube-transcript-api yt-dlp faster-whisper` (faster-whisper only if T7 needs audio transcription; CPU "small" or "base" model is enough).
- If Python is unavailable, do T1/T6/T7 with the Stealth fetch tool on a reduced sample (half size) and say so in the report.

## 4. Fixed dish list (use for T1, T6, T7 so results are comparable)
Mix of gravies, fried items, sweets, street food, veg and non-veg:
1 paneer butter masala, 2 dal makhani, 3 chole (chana masala), 4 rajma, 5 aloo paratha, 6 samosa, 7 onion pakora/bhajji, 8 puri or bhature, 9 pav bhaji, 10 butter chicken, 11 chicken biryani, 12 egg curry, 13 gulab jamun, 14 gajar ka halwa, 15 jalebi, 16 poha, 17 masala dosa, 18 sambar, 19 kheer, 20 aloo tikki.

## 5. Tests

### T1 Website extraction coverage  (go/no-go for the prototype input)
Goal: Can we reliably get ingredient + quantity data from popular Indian recipe websites, especially for liver-relevant items (oil, ghee, butter, cream, sugar, jaggery, khoya, maida, salt)?
Sites (pick 5; verify they are among the most popular via Stealth search first; must include >=1 site with NON-VEG recipes): candidates hebbarskitchen.com, vegrecipesofindia.com, tarladalal.com, indianhealthyrecipes.com (Swasthi's), archanaskitchen.com, ranveerbrar.com, cookwithmanali.com. Note: Hebbar's, VegRecipesOfIndia, Tarla Dalal are mostly vegetarian.
Sample: for each site, the 20 fixed dishes where available (use the site's own URL found via Stealth search or the site sitemap); if a dish is missing, substitute the nearest dish and note it. Target ~80-100 recipes total.
Procedure per recipe:
 a) Fetch page; check for schema.org Recipe JSON-LD (extruct or parse <script type="application/ld+json">). Record: has_jsonld, recipeYield/servings present, recipeIngredient count, nutrition block present.
 b) For each ingredient line, classify quantity status: exact (number+unit), count unit ("2 onions", "20 cubes"), range ("1/4 to 1/3 cup"), vague ("as required", "to taste", "for frying", "for deep frying"), missing.
 c) Flag liver-relevant lines (oil, ghee, butter, cream, malai, khoya/mawa, sugar, jaggery, honey, condensed milk, maida, salt, vanaspati, coconut milk).
 d) Flag deep-fried recipes (steps mention deep fry / fry till golden in oil) and whether frying oil is quantified.
Outputs: data/t1_recipes.csv (one row per recipe), data/t1_ingredient_lines.csv (one row per line with status + liver flag).
Report: % recipes with JSON-LD; % with servings; for liver-relevant lines: % exact / count / range / vague / missing; % deep-fried recipes with unquantified frying oil (expected high); per-site table; 3-5 concrete examples.
Go/no-go: GO if >=70% of liver-relevant lines in non-fried recipes are exact or range. Report the number either way.

### T2 Parsing, unit-to-gram, ingredient-to-nutrient mapping accuracy
Goal: estimate error of the pipeline's front end.
Sample: 100 random ingredient lines from T1 (stratify: 50 liver-relevant, 50 other).
Procedure: hand-label (you, carefully) the gold ingredient name, quantity, unit, grams. Then run an automatic parser (a small rule/regex parser or the recipe-scrapers ingredient parser; if you use an LLM, state which) and a unit->gram table. Build the unit table from INDB's units file if you can get it (GitHub: lindsayjaacks/Indian-Nutrient-Databank-INDB- or vikx01/Indian-Nutrient-Databank-INDB; file units.xlsx) plus standard values: tsp 5 ml, tbsp 15 ml, cup 240 ml (also report sensitivity at 200 ml), katori ~150 ml [U; find a source], oil density ~0.92 g/ml, ghee ~0.91 g/ml. Map ingredient names to INDB food items (NIN_fct / recipes files) and note unmatched.
Report: name accuracy, quantity accuracy, gram error (median abs % error), INDB match rate, top failure types (Hinglish names, count units, compound items like "ginger garlic paste").

### T3 Fried-food fat validation (the biggest scientific loophole, L1)
Goal: can literature oil-uptake factors give fat estimates for deep-fried items that are close to LAB-MEASURED values?
Collect lab-measured fat (g/100 g, as eaten) for as many of: puri, bhatura, samosa, onion bhaji/pakora, chicken pakora, vada, jalebi, mathri, bread pakora, chips/fries. Sources to try (fetch via Stealth tools):
 - Chen, Gilbert & Khokhar 2009, Food Chemistry 113:825 (open copy: zenodo.org/records/10043766) - puri values (analysed vs calculated).
 - safefood Ireland 2015 "What's in your Indian takeaway?" PDF (safefood.net) - onion bhaji, chicken pakora (lab analysed; per portion; portion weights given).
 - UK CoFID 2021 dataset (gov.uk "composition-of-foods-integrated-dataset-cofid"; Excel) - filter South Asian items and keep only items whose source/comments indicate ANALYSED, not recipe-calculated.
 - Jain, Passi & Selvamurthy 2024, J Food Sci Technol 61:2185 - poori, bread pakora, mathri fat % (dry basis; convert with moisture if given).
 - Any Indian study measuring fat in samosa/pakora/jalebi (search; record exact citation).
Then, for 5-8 of these items, compute our estimate: recipe ingredients (from T1 or INDB) + oil uptake factor range (e.g., 8-20% of fried weight; cite each factor's source) and compare to the lab value.
Report: table item | lab fat g/100 g (source) | our estimate range | within range? | error. State clearly if lab data is too thin.

### T4 FlavorDB coverage + swap back-test (L8)
Goal: can the flavour-preserving swap engine work for Indian liver-heavy ingredients?
 a) Coverage: check whether FlavorDB (cosylab.iiitd.edu.in/flavordb or /flavordb2) has entities for: ghee, butter, cream, milk, khoya/mawa, paneer, curd/yogurt, hung curd, cashew, coconut milk, coconut oil, mustard oil, groundnut/peanut oil, sesame oil, rice bran oil, sunflower oil, olive oil, vanaspati/hydrogenated fat, palm oil, sugar, jaggery, honey, maida/refined wheat flour, whole wheat flour. Record entity id and number of molecules. (Public scrapes exist, e.g., github.com/tarek-kerbedj/flavor_db2.0 flavordb.csv; FlavorDB entity JSON endpoints were used by those scrapers - try them politely.)
 b) Swap back-test: find real recipe variants where cooks already made the healthier swap for the SAME dish (e.g., "dal makhani without cream", "paneer butter masala with curd/cashew instead of cream", "mustard oil instead of ghee", "air fryer samosa", "jaggery vs sugar halwa"). Count how many exist for the 20 dishes (web search). For 5 swaps, compute FlavorDB shared-molecule Jaccard between original and substitute (if both covered).
Report: coverage table; count of real swap variants per dish; whether FlavorDB similarity is available/meaningful for dairy/fat swaps; verdict on the swap feature.

### T5 Score sanity (light)
Goal: sanity-check the numbers pipeline, not validate health outcomes.
For 10 recipes from T1 (include 3 fried, 3 creamy gravies, 2 sweets, 2 light dishes): compute per-serving energy, total fat, SFA, added sugar, using INDB/IFCT composition (and T3 oil uptake for fried). Compare energy per serving with Tarla Dalal's published "calories per serving" for the same dish where available (both are calculations: this tests consistency, not truth). Classify each recipe with the ICMR-NIN 2024 HFSS rule (>15% energy from added oil/fat) and show % of daily budgets: SFA (<7%E and <10%E of 2,000 kcal), added sugar (25 g), salt (5 g).
Report: table + whether rankings look sensible (e.g., dal makhani/paneer butter masala/samosa/gulab jamun high; poha/sambar low). Note any absurd outputs.

### T6 Wayback longitudinal feasibility for RQ2 (L4)
Goal: can we compare the SAME recipe URL across years (true traditional-vs-modern drift) instead of textbook-vs-blog?
For 10 recipe URLs from T1 (popular dishes, ideally from sites that existed pre-2015 e.g., tarladalal, vegrecipesofindia): query the Wayback CDX API via fetch: http://web.archive.org/cdx/search/cdx?url=<URL>&output=json&fl=timestamp,statuscode&filter=statuscode:200&collapse=timestamp:4 . Record earliest snapshot year and number of yearly snapshots. For 3-5 URLs, fetch the earliest and latest snapshots and diff the liver-relevant ingredient quantities (oil/ghee/butter/cream/sugar).
Also check the INDB baseline: how many of the 20 dishes exist among INDB's 1,014 recipes (ASC/BFP textbook recipes) with gram amounts.
Report: snapshot availability stats; examples of quantity changes (or none); INDB coverage of the 20 dishes; recommendation for RQ2 design.

### T7 YouTube quantity coverage (the user's hypothesis: videos state oil amounts better than blogs)
Goal: TEST (do not assume) whether popular YouTube recipe videos give usable quantities for liver-relevant ingredients, especially deep-frying and tadka oil, and whether their amounts differ from website versions of the same dishes.
Sample: the 20 fixed dishes x top 3 results (search "<dish> recipe", prefer Indian creators with high views; record channel, views, upload date, duration) = ~60 videos. Discover videos via Stealth search (site:youtube.com) or `yt-dlp "ytsearch5:<dish> recipe" --flat-playlist --dump-json` (metadata only).
Data sources per video, in this order (stop at the first that gives the ingredient list):
 1. Video DESCRIPTION (yt-dlp --skip-download --dump-json gives description; or the YouTube Data API v3 videos.list if an API key is available). Many Indian creators list ingredients with quantities here.
 2. CAPTIONS/TRANSCRIPT: youtube-transcript-api (or yt-dlp --write-auto-subs --skip-download --sub-langs "en,hi"). Hindi/Hinglish auto-captions are common; keep them.
 3. LAST RESORT, only if 1 and 2 fail and only for <=15 videos total: download AUDIO only (yt-dlp -x), transcribe locally with faster-whisper, then DELETE the audio file immediately. IMPORTANT: downloading YouTube media is generally against YouTube's Terms of Service (captions via unofficial endpoints are also a grey area). Keep this to a tiny research sample, never redistribute audio/video, and state this clearly in the report so the user can decide whether to keep this method in the real project.
Extraction: from description/transcript, extract ingredient + quantity + unit (small LLM or careful manual reading for this sample; state which). Normalise units: tsp 5 ml, tbsp 15 ml, cup 240 ml (sensitivity 200 ml), katori ~150 ml [U, cite], "1 ladle/karchi" [U], "thoda sa / as needed" = vague; oil density ~0.92 g/ml.
Measure: % videos with ingredient list in description; % with transcript; for liver-relevant items: % exact / range / vague / missing; specifically for deep-fried dishes: % that state frying oil quantity (the user's claim); units used (katori, cup, ladle, spoon, "thoda"). Compare, per dish, YouTube vs website amounts of oil/ghee/butter/cream/sugar per serving (where servings are stated).
Report: numbers + examples; verdict on the user's hypothesis; whether YouTube should be added to the prototype and which access method is legally safest (description via official API = safest).

## 6. Final report format: research_log/25_TEST_REPORT.md
1. One-paragraph executive summary (plain language) + overall GO / GO-WITH-CHANGES / NO-GO for the project.
2. Table: test | key number(s) | pass/fail vs criterion | consequence for the project.
3. One section per test (method as actually run, sample, numbers, examples, blockers).
4. Updated loophole list (L1-L11 from file 22): which are resolved, which remain, any NEW loopholes.
5. Concrete recommendations: data sources to use, which sites, whether to add YouTube and how, what to ask the professor for (RecipeDB2, FlavorDB, NER model), and what to build first for the prototype.
6. Everything you could not verify, listed explicitly.
Also append a 5-line entry to research_log/00_README_and_method.md file index describing files 23-25.

## 7. When finished
Tell the user in chat: the executive summary, the GO/NO-GO, the 3 most important numbers, and the top 3 risks. Keep it short and honest.
