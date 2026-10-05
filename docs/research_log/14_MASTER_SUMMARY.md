# 14 MASTER SUMMARY: everything done so far (written 2026-09-29)
Purpose: one file that reconstructs the whole session: the goal, YOUR instructions and ground rules (in order), what was read, what research was done, what changed along the way, mistakes/corrections, current state, and where each detail lives. Read this first; other files hold the details.

## 0. Honest note on logging
- Research, decisions, scores, tool issues and roadmap were logged as they happened (files 00-13).
- GAPS before this file: (a) the summary of the course material was only in chat; (b) the user's instructions were partly in 00 (rules) and 06 (corrections) but never consolidated; (c) several corrections (multiple ideas, non-obvious, data burden, professor as evaluator) were only in chat or in 06/13. This file fixes that.

## 1. The goal (why any of this exists)
- User: CS + biosciences student, team of 2, course CGAS BIO544 Computational Gastronomy (Prof. Ganesh Bagler, IIIT-Delhi, Monsoon 2026).
- Need: a mini-project idea (for now, the IDEA only, not the full project; due "tomorrow" as of 2026-09-29).
- Professor said (per the user): the project can be about anything in food + data science, even a restaurant problem; if it is really good, solves a real problem others aren't solving, and is relevant, it may be featured at the annual Symposium on Computational Gastronomy. Professor can give access to CoSyLab data/resources if needed; any dataset is otherwise fine.
- User's stance: being featured at the symposium is NON-NEGOTIABLE; wants a genuinely creative solution, real-world problem, nobody else solving it.

## 2. USER INSTRUCTIONS AND GROUND RULES (chronological, as given)
1. Read ALL course material in the folder, understand the course, report back (no ideas yet).
2. Constraints: team size 2; both CS + biosciences; professor can provide CoSyLab/IIIT-Delhi data; aim = strong grade AND symposium feature ("no going back on this").
3. Do NOT think about timing or submission format unless told; focus on the idea.
4. Wants AI integrated only if genuinely creative and intentional: not "put an LLM between problem and solution". Local AI is welcome if genuinely justified. Wants BERT/early-transformer-style thinking: a new way to frame a problem, real engineering, not cut-paste. No scale limits.
5. Use ONLY the user's custom "Stealth Search" MCP tool for web research (not standard web search). Research must be exhaustive but done in steps, not one go.
6. LOG everything into files in a directory (research_log/) so nothing is lost over the long chat.
7. First produce a broad overview of categories (>= 6) to dive into; then dive deep one by one.
8. While testing/fixing the tool: report tool issues concisely; retest after fixes (user fixed the MCP several times; a /mcp reconnect was needed for changes to load).
9. Do forward-looking (2026 and beyond) research too, weighed equally with past evidence, before deep dives.
10. Make a step-by-step roadmap first and log it; then deep dives; then Phase 2.
11. Legibility: "people prefer what they understand": give it VERY LITTLE weight, not a whole point of existence. (I over-applied it; withdrawn, see 4.)
12. Correction: the deciding evaluator is the PROFESSOR, not a general audience; "10-second pitch/demo" are not criteria now; the idea must make sense to the professor.
13. Correction: user wants MULTIPLE project ideas to choose from, NOT one concept forced; ideas must be NON-OBVIOUS (classmates will also chase "what the professor stated as open"); must consider how much data and processing each needs; and note that if his own tool ignores cooking, judging cooking must be hard.
14. General: be concise on explanations when asked; report back after each step before moving on; user confirms order/dropping.
15. Style/standing: answer honestly about uncertainty; mark unverified claims.

## 3. What was read (course material, 14 files in All_Markdown_For_AI)
- Course = data-driven science of food: definition "Computational Gastronomy = Food + Data Science + AI". Weeks: intro/history/culture; recipe data (structure, cleaning, cuisine structure, ingredient popularity); flavor data (molecular composition, taste/odor); food pairing (hypothesis testing, culinary fingerprints); health/nutrition; ML for cuisine classification; taste/odor prediction; opportunities. Grading: mid-sem 20, end-sem 30, three assignments 30, mini-project 20. Mini-project: teams of 1-2, >=3 weeks, wide scope (scraping, ML, apps, Kaggle design, APIs, NER, blockchain, etc.); opportunities include symposium posters/presentations.
- Core science: 5 data pillars (recipes, flavor profiles, health associations, nutrition, carbon footprint); recipe = unordered ingredient set, ingredient = unordered set of flavor molecules (deliberate simplifications); food pairing hypothesis and score N_s (average shared flavor molecules over ingredient pairs), random-cuisine null models (uniform, frequency-preserved, category-preserved), Z-scores, ingredient contribution, authenticity; recipe size bounded (~8-9), ingredient frequency-rank power law; copy-mutate culinary evolution (Kinouchi; Jain & Bagler).
- Papers: Ahn et al. 2011 (flavor network; West positive pairing, East Asia negative); Jain/Rakhi/Bagler 2015 (Indian cuisine strongly NEGATIVE pairing, Z ~ -54.7; spices the "molecular fulcrum"; copy-mutate with frequency-scaled fitness reproduces it); Singh & Bagler 2018 (45,772 recipes, 22 regions; 16 regions positive INCLUDING Indian Subcontinent, 6 negative; contradicts earlier reports, attributes to data quality); FlavorDB (25,595 molecules; 2,254 linked to 936 ingredients).
- Assignment 1: scrape 10k recipes (not RecipeDB), NER for ingredients, recipe-ingredient table, ingredient frequencies, recipe-size and frequency-rank plots, conceptual questions.
- Slide "ideas" (project seeds from the professor): pairing model/library, Kaggle challenges (cuisine prediction, taste from SMILES), evolution models with pair selection/flavor, FlavorDB analytics, chemical elements (Fe/Ca/Zn) flavor-wise/food-wise, A.Recipe.A.Day, artificial flavors/fragrance, flavor transformation under boiling/frying/roasting, recipe data structure, crowdsourcing app, itemset mining, ingredient-disease bipartite mining.
- Admitted limitations in the material: repositories may not be "traditional"; flavor data incomplete, no concentrations; cooking transformations ignored; quantities/order ignored; results flip by dataset; pair-level only.

## 4. Chronology of what we did (with pointers)
1. Read course material, reported summary (chat only; now section 3 above).
2. Set the working method: log directory `research_log/`, Stealth Search only (00_README_and_method.md).
3. Broad landscape sweep (16+ queries): field reviews, food computing survey (Min et al. 2019), restaurant waste (crowded: Winnow, Leanpath, Kitro), personalized nutrition, LLM recipe evaluation, odor prediction (Principal Odor Map), carbon footprints (lab owns SustainableFoodDB), allergens (crowded), food-drug interactions, plant-based (NotCo), Indian food vision (Thali dataset), substitution (FKG.in), nutrition access, cooking transformation, microbiome, recipe representation. -> 01_broad_landscape.md, 02_categories_overview.md (13 categories with crowding/gap/bio-fit).
4. Tool problems found and fixed through several rounds (raw-PDF dump of ~438K chars, SSL failures, blocked pages, bot-check pages returned as content). After a /mcp reconnect: PDFs parse, 25K output cap, blocked-source footer, SSL fixed, batch_search added. Remaining quirks: ResearchGate/ScienceDirect blocked; PubMed cookie wall; batch_search returns [None](None) on some person/lab-name queries. -> 03_tool_retest_after_fix.md, README.
5. Symposium baseline (GastroSym 2023/24/25 pages, press, Hindu article, Foodoscope, lab site): symposium = talks by chefs/industry/policy + Fork-It Hackathon (APIs, Rs 80K); Hindu says it "showcases research from the institute"; NO public evidence of a student-poster track (only the professor's word); recurring themes: Foodoscope, Ayurveda informatics, sustainability. Lab's stated open items (Nature 2024 review): health for the complete dish, cooking transformation, quantities, sensory testing of AI recipes (Turing Test for Chef F1 69.88%). -> 04_symposium_baseline.md.
6. Forward-looking 2026 research: AI landscape (agents/MCP, small on-device models, tiered routing, inference cost down; AI Index 2026: AI works where data infrastructure exists, agents weak at real analysis, validation is the bottleneck); food-AI (generative food formulation perspective 2026, FoodPuzzle LLM flavor agents, LMM nutrition-from-photo commoditising, kitchen robotics bottleneck = recipe encoding); GLP-1 wave in India (semaglutide patent expiry Mar 2026, 40+ generics, ~90% price drop [blogs]); FSSAI labelling changes; Ayurveda informatics status. -> 05_forward_looking_2026.md.
7. Roadmap (phases 0-5, protocol of 8 questions per deep dive, kill criteria, 100-point rubric, later corrections). -> 06_roadmap.md.
8. Deep dives (DD1-DD6), scores under the ORIGINAL rubric (real problem 25, novelty 25, tech originality 20, data/validation 15, symposium/chef relevance 10, bio leverage 5):
   - DD1 GLP-1-era Indian food = 69 (MAYBE-GO). Verified: Indian Delphi consensus (Obesity Pillars 2026, 13 experts, Abbott-funded) says patients lack food guidance; India-specific gaps; but HealthifyRx/Sugarfit already sell programs. -> 07.
   - DD2 food-drug interactions = 59 (MAYBE, component). GLP-1 gastric-emptying interactions mostly insignificant (exceptions: tirzepatide-oral contraceptives, oral semaglutide-levothyroxine); compound-level ML has noisy labels; whole-food KG-DFI exists (2026); dose-aware dish-level gap unverified. -> 08.
   - DD3 whole-dish + cooking/bioavailability = 74 (best under that rubric). Verified: lab's estimator sums raw USDA values and admits cooking yield is ignored (calorie-only validation, 36 kcal/serving error, garam masala missing); INDB models cooking only as sensitivity analysis (42.6% matched, no yield); phytate:mineral, buttermilk-green gram in-vitro evidence. -> 09.
   - DD5 Ayurveda informatics = 62 (MAYBE as angle). Chatbots/dosha classifiers crowded and weak (AyurParam ~41%); serious groups (IMSc KG/network pharmacology; AyurKOSH); FSSAI Ayurveda Aahara rules bar disease claims; falsifiable rule-testing idea. -> 10.
   - DD6 verifying AI recipes = 53 (KILL standalone). Crowded (FKG.in soundness pipeline Aug 2026, FoodGuardBench Apr 2026, Fudan Feb 2026, Springer DPO 2026). -> 11.
   - DD4 (executable recipe representation) folded into DD3; separate novelty check still owed.
9. Phase 2 attempt 1 (12_phase2_concepts.md): 4 "concepts" A-D, A forced as primary; included pitch/demo + legibility modifier. USER REJECTED: wanted many independent options, professor as evaluator, non-obvious, data burden. Superseded.
10. Phase 2 REDO (13_phase2_project_menu.md): 13 independent projects P1-P13 with obviousness, data burden, compute, cooked-truth dependence, risks; no winner implied; combos optional. AWAITING USER'S CHOICE.

## 5. Key verified facts worth remembering
- Lab's recipe-nutrition tool (Kalra et al. 2020, arXiv 2004.12286): raw-ingredient sum from USDA-SR; NER + Jaccard matching; matching accuracy 71.6% on 5,000 top ingredient+state strings; 36.42 kcal/serving mean error on 2,482 recipes; USDA lacks Indian ingredients; code public (github cosylabiiit/Nutritional-Estimation-In-Recipes).
- INDB (Vijayakumar et al. 2024, PMC11277795): 1,095 raw foods + 1,014 recipes, open access + code; cooking effects only in a sensitivity analysis; retention differences "small"; yield correction listed as next step.
- IFCT 2017 (NIN): 528 key foods x 151 components with SDs, six-region composites, RAW only (except eggs); tables include amino acids, organic acids, polyphenols, phytates; copyright notice requires NIN permission to reproduce tables electronically for a product.
- USDA: cooked values often CALCULATED from raw via retention factors (circularity for learning from cooked entries).
- Jain 2015 vs Singh & Bagler 2018 conflict on Indian pairing sign (basis of P1).
- Symposium: no published student-poster track found; professor's word is the only evidence.

## 6. Known mistakes / corrections by me
- Over-weighted the "understandable to audience" point (10-second pitch, demo, legibility modifier) after the user asked for very little weight.
- Reasoned about symposium AUDIENCE (chefs) when the real gate is the PROFESSOR's evaluation.
- Collapsed Phase 2 to one primary concept; user wanted a menu of options.
- Earlier assumed India GLP-1 glucose-response work was only at protocol stage (wrong; a 488-patient study was published) - corrected in 01.
- Risk of over-stating that "cooking is the dominant error" - INDB found small retention effects; flagged in 13.
- Presented DD3's 74 as if it settled the choice; scores are provisional judgments, not truth.

## 7. Current state (what is decided vs open)
- DECIDED: research tooling and log structure; six deep-dive directions researched; Phase 2 menu produced (13 projects).
- NOT DECIDED: which project(s) to pursue. No shortlist yet. No idea write-up yet. No professor contact yet (asks list drafted in 13: RecipeDB Indian subset with quantities/processes, Jain 2015 datasets, CulinaryDB, SustainableFoodDB access, nutrition-estimation code, permission for IFCT tables).
- Next steps (only after user chooses): shortlist 2-4 ideas -> Phase 3 red team (fresh skeptic searches, feasibility of data, overlap with lab, safety framing, DD4 novelty check) -> pick primary + backup -> idea write-up (format decided by the user).
- Open verification items: availability/licences of Jain 2015 supplementary data, CulinaryDB downloads, RecipeDB via professor; whether CoSyLab is already doing GLP-1 / cooking-aware nutrition; several novelty checks were incomplete because ScienceDirect/ResearchGate blocked sources.

## 8. File index (research_log/)
00 README + method rules | 01 broad landscape (16+ queries, corrections) | 02 category table (13) | 03 tool retests | 04 symposium baseline | 05 forward-looking 2026 | 06 roadmap + rubric + corrections | 07 DD1 GLP-1 Indian food | 08 DD2 food-drug | 09 DD3 whole-dish/bioavailability | 10 DD5 Ayurveda | 11 DD6 AI-recipe verification | 12 Phase 2 attempt 1 (SUPERSEDED) | 13 Phase 2 project menu (CURRENT) | 14 this master summary.
Also: the ORIGINAL course markdown files remain in the parent folder All_Markdown_For_AI/.
