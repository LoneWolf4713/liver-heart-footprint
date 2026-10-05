# 21 India-specific problems + evaluation of the user's reel idea (2026-09-29)
Rules in force: India-centric; real problem with evidence >= ~100 complaints (or stronger official data); data gate; no fieldwork; no scraping of Instagram/Zomato.
Note: Reddit blocks direct access from the tool (JSON + old.reddit both blocked) -> could not COUNT posts. Used official enforcement/clinical numbers instead (stronger than 100 complaints).

## Evidence: problems Indians actually face (verified this round)
1. FATTY LIVER (MASLD): [V] Phenome India cohort (Lancet Reg Health SE Asia 2026): crude 47.8%, age-adjusted 38.9% (men 45.9%, women 33%); obesity predominant driver + diabetes, dyslipidaemia, BP. [V] Young South Indian adults (JCEH Jun 2025, n=2,373, BMI<30, no alcohol): MASLD 27.4%. [V] MAP study (13,750 clinic pts): MASLD 68.2%.
2. ADULTERATION: [V] Govt in Lok Sabha (ANI, 31 Jul 2026): 223,808 samples analysed FY2025-26, 40,023 non-conforming (~17.9%), 1,918 convictions. [S] 2026 raids: fake/analogue paneer (Delhi 508 kg, Noida 300 kg, Surat 1,401 kg), ghee (Hyderabad 25 t + 36 t; Delhi-Haryana 6,500 L), 25 t spices with industrial colours (Hyderabad) (Moneycontrol 25 Aug 2026). [S] FSSAI draft 2026 to ban "analogue paneer"; Punjab 1-yr ban; FSSAI West Region notice (23 Aug 2026). [S] "83% of paneer samples failed" = Noida/Greater Noida reports, NOT national. Reddit threads exist (e.g., Patanjali ghee) but uncounted.
3. PESTICIDES: [V] MPRNL (since 2005-06; 32 labs; vegetables, fruits, cereals, pulses, curry leaves, red chilli powder, milk, water) - public outputs are mostly summary/achievement PDFs [U: residue-level data access]. [V] J Food Sci Technol 2023: "paucity of data" on residues in processed foods in India. [V] EU processing-factor database (EFSA/BfR, Zenodo, updated 2022-2025) is open.
4. Junk-food labelling fight (from 17): SC case, FSSAI FOPL proposal.

## User's reel idea: honest evaluation
- Problem (fatty liver epidemic): REAL, strongly evidenced.
- Premise "spices cause/worsen fatty liver": NOT SUPPORTED by what I found. Clinical diet guidance targets fried foods/trans fats, oil/sat fat, sugar & fructose drinks, refined carbs (maida, white rice), alcohol, processed meat. Spices themselves are not listed; curcumin RCT meta-analyses (e.g., 14 studies, n=874) show IMPROVED ALT/AST/TG/HOMA-IR. Likely reason doctors say "avoid spicy/masala food": it is a practical PROXY for oily, fried, salty restaurant/street food (masala bases are cooked in a lot of oil/ghee; tadka; cream), and capsaicin aggravates common co-conditions (GERD/gastritis) [inference; no guideline found stating spices worsen MASLD].
- App (paste reel -> recipe -> nutrition): ALREADY BUILT many times: Nutrola (TikTok/Reels/Shorts -> recipe + per-serving nutrition), Honeydew, Peel, ReciMe, Flavorish, RecipeBro, open-source kits (social-recipes-kit, recipewizard). -> app alone is NOT novel.
- Data/legal: Instagram automated collection violates ToS -> no Instagram dataset. YouTube Data API v3 (official) returns video descriptions, where many Indian recipe creators list ingredients with quantities -> legal route for a dataset [dry-run needed: % with quantities].
- Reframed, defensible version (R-Reel): SCIENCE: "Are social-media Indian recipes heavier than traditional ones?" Compare oil/ghee/butter/cream, sugar, salt, deep-frying, refined flour per serving in YouTube Indian recipe videos (API) vs traditional baselines (INDB textbook recipes 2007/2011 = home-science standard; RecipeDB2 Indian/TarlaDalal older corpus), matched by dish. Ground truth = the stated quantities themselves (compositional claim, verifiable). PRODUCT: liver-aware scorer grounded in MASLD guidance (fat/oil load, sugar, refined carbs, frying), with explanation of WHY (not "spice score").
  Risks: many videos say "oil as needed" (missing quantities); creator recipes may not reflect what people actually cook; no health-outcome claims possible.
  Prior art: no academic study of Indian social-media recipe composition vs traditional found (1 search; weak evidence).

## New India-specific idea from the evidence
- R-Fraud "India Adulteration Atlas": build a structured, open database of food-adulteration enforcement events from Indian news (2019-2026) + Parliament answers (state-wise samples/non-conforming), via LLM information extraction (product, adulterant, quantity, place, date, festival proximity); test hypotheses: festival-season spikes, milk supply-demand gap -> dairy adulteration, geography; map risk onto RECIPES (which dishes/sweets are most exposed via paneer/khoya/ghee/spices, by state & season); consumer alert/explainer.
  Precedent: EU JRC MedISys-FF media monitoring (2018; benchmarked vs RASFF/EMA) -> method is proven; no India equivalent found. India computational work found = FTIR+ML lab detection (NIT Rourkela patent).
  Ground truth: news reports + official state statistics (documents; verifiable). Validation: extraction accuracy on hand-labelled sample; hypothesis tests vs official counts.
  Risks: media bias (reporting != occurrence); allegations vs convictions; must not name/shame small vendors.
- R-Pesticide (weaker): recipe-level pesticide exposure estimates using MPRNL summaries + EU processing factors; SAME TRAP as S3 (no measured cooked-dish residue ground truth in India) -> flagged weak.

## Round 2 on the liver idea (user refinement request, 2026-09-29)
User direction: NOT a "paste reel -> score" gimmick; model food against the obesity/fatty-liver epidemic with GROUNDED data; inputs could be recipe text / YouTube URL / Instagram URL (only if legal) / product image; wants to know the computational gastronomy angle.

### Existing apps (what they actually do) [V]
- Video->recipe: Nutrola (TikTok/Reels/Shorts URL -> speech + on-screen text + visual ingredient ID -> ingredients w/ quantities, steps, per-serving kcal/protein/carb/fat/fibre, diary logging); Honeydew; Peel (Reels/posts import, meal planning, grocery list); ReciMe (5 imports/wk free); Flavorish; RecipeBro (AI reads Reel captions + text overlays); open-source social-recipes-kit (works without captions by "watching" video; Instagram DM-share automation); recipewizard (yt-dlp + Claude).
- Liver-specific: Liverly (liverly.app: snap a meal -> liver-friendly or not; 0-100 recipe score per diagnosis MASLD/MASH/fibrosis/cirrhosis; tracks added sugar, sat fat, kcal, fibre; imports recipes from websites; 100+ Mediterranean-leaning recipes). Liver Nutrition App (UK hepatologist Dr N. G. Ladep; 800+ meal ideas, 14 cuisines incl South Asian; condition-aware guidance; barcode scanning; 1K+ downloads).
=> Both the video->recipe->nutrition pipeline and a liver-friendliness scorer EXIST (Western-centric). Novelty must come from India-specific science, not the app.

### Instagram legality [V, not legal advice]
- Instagram Terms: "can't ... collect information in an automated way without our express permission"; Meta Automated Data Collection Terms require written permission.
- Meta v. Bright Data (N.D. Cal., 23 Jan 2024): Terms do not bar LOGGED-OFF scraping of public data (terms govern logged-in "use"); US district ruling only; Meta may rewrite terms; tortious-interference claim was pending; does not settle Indian law; Meta technically blocks.
- Official route: Meta oEmbed (tokenless since 15 Jun 2026) is for EMBEDDING/display; author/thumbnail fields removed Nov 2025; using it to harvest caption text for analysis = outside stated purpose (grey).
- Decision: a person reading a caption = fine; our server auto-fetching captions = automated collection (grey/against ToS). SAFE DESIGN: user pastes the caption text themselves (or shares text); YouTube via official YouTube Data API (descriptions allowed) for both URL input and any dataset. No Instagram dataset.

### Grounding evidence for a "liver load" model
- [V] Luukkonen et al., Diabetes Care 2018 (PMC7082640): 38 overweight adults, +1,000 kcal/day for 3 weeks from saturated fat vs unsaturated fat vs simple sugars; SATURATED FAT caused the largest rise in intrahepatic triglyceride (via adipose lipolysis) plus insulin resistance and ceramides; sugars raised liver fat via de novo lipogenesis; unsaturated fat the smallest rise. => Indian cooking fats matter: ghee, butter, vanaspati, coconut/palm oil, cream, khoa vs mustard/groundnut/rice-bran oil.
- [V] Guideline-level: fried foods/trans fats, sugary drinks/fructose, refined carbs (maida, white rice), alcohol, processed meat; obesity (energy surplus) is the predominant driver in India (Phenome India 2026).
- [V] Spices not implicated; curcumin RCT meta-analyses show improved liver markers.
- [U] INASL guidance / India-specific MASLD-in-T2D consensus (Diabetes Care 2025) exist but full text blocked.
- [V] ICMR-NIN DGI 2024 (HFSS definitions; copyright: no electronic reproduction for a product without NIN permission).
