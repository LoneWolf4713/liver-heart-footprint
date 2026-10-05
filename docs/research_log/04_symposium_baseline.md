# 04 Symposium baseline (fetched 2026-09-29)

## Sources fetched OK
- iiitd.ac.in/gastrosym2023, gastrosym2024, gastrosym2025 (all load now)
- The Hindu, 4 Dec 2024, "Computational Gastronomy elective at IIIT Delhi..." (this very course)
- foodoscope.com (API product page)
- Search snippets: APN News, Spiritz, Skilloutlook, Shiksha, Unstop (2024 symposium listing), LinkedIn IIIT-Delhi post (5th edition, 10 Dec 2023)
## Failed
- unstop.com Fork-It hackathon page: "Page loaded but main content was empty or protected" even with force_browser=true (tool gap: JS-heavy/protected site; minor).

## Facts about the symposium
- Running since 2017 (except Covid years). 5th edition 10 Dec 2023, 6th edition 14 Dec 2024, "decade" edition 13 Dec 2025.
- The Hindu: it "will showcase recent computational gastronomy research FROM THE INSTITUTE" + talks by chefs, industry, policy-makers, influencers.
- NO public page/press item mentions a student poster session, mini-project track, or featured student projects. The only evidence of student features is the professor's own statement in class. => Treat as his discretion, not a published track.
- Format = talks + Fork-It Hackathon (ACM + CoSyLab; API-based). Prize pool Rs 30,000 (2023) -> Rs 80,000 (2024, 2025). 2025 = "3rd edition of Foodoscope ForkIT Challenge" (Unstop).
- Speaker mix 2023: chef of "AI Restaurant", IFCA president, Michelin-star chef (GAA Bangkok), IHM Pusa principal, exec chef Riyadh Air, Future Food Foundation CEO, Tata Trusts (nutrition), Sattvaj, Saroja Earth (sustainability),
  Ayusla founder (AYURVEDA INFORMATICS + HUMAN MICROBIOME), FoodBytes Technologies founder.
- Speaker mix 2024: + Dr Soumya Swaminathan (MSSRF chair; "AI for improving health at ground level"), Prof Kavya Dashora IIT-Delhi (agriculture + AI), Future Food Foundation (nutrition education).
- Recurring "Future" themes on all three pages: Foodoscope/FoodBytes (digital building blocks of food), AYURVEDA INFORMATICS, CENTER FOR SUSTAINABLE FOOD.
- Recurring "Applications" questions on all three: can a computer think like a chef; ingredient pairing; AI-generated recipes; tweak my recipe for better health; address nutrition deficiencies; cuisine fusion.

## Foodoscope (lab spin-out) API offering  (what the lab itself considers productizable)
- RecipeDB 118,000+ recipes; FlavorDB 1000+ ingredients; SpiceRx (phytochemical-disease associations for spices); CocktailDB 17,000+ cocktail recipes with nutrition;
  SustainableFoodDB 500+ foods ("Coming Soon"); DietRxDB food recommendations for 100+ diseases ("Coming Soon").
- Pitched use cases: fitness/wellness apps, restaurants (auto nutrition facts, allergens, health-focused dishes), healthcare apps, grocery/e-commerce, smart kitchen IoT.
- Plans: Starter 200 free tokens, 25 req/min, non-commercial; Developer Plus pay-per-20k tokens; Enterprise custom. => prof's offer of direct CoSyLab data access avoids these limits.

## What the lab says it has done / what it says is next (from the Hindu + Nature review)
- Done: Ratatouille recipe generator; carbon-footprint OPTIMISATION of generated recipes (Bagler: "optimisation algorithm which can minimise the carbon footprint of any recipe"); sweetness/bitter prediction;
  food pairing across cuisines; NER; RecipeDB/FlavorDB/SpiceRx/DietRx/SustainableFoodDB; dish detection on Indian platters; Turing test for chefs (F1 69.88%).
- Bagler's public stance: "AI won't replace chefs/nutritionists, but those who refuse to use AI will be replaced by those who do"; non-personalized nutrition advice "out of sync with reality"; wants wearable-AI personalization; NPTEL course coming.
- Stated NEXT / open (Nature 2024 review): sensory-panel palatability testing of AI recipes; health evidence exists per-ingredient but "must logically be assessed for the complete dish"; quantities/potency/cooking transformation ignored; better data with cultural+health correlates.
