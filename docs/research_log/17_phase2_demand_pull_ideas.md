# 17 Phase 2 (v4): demand-pull ideas (2026-09-29)
Trigger: user feedback in 16 -> ideas must answer a question the world is ACTUALLY asking now; no fieldwork; mini scale; still rare among classmates.

## Evidence gathered (Stealth Search)
FRONT-OF-PACK WARNING LABELS (FOPL), live policy fight:
- [S] SC case 3S and Our Health Society v. UoI: 10 Feb 2026 bench unhappy with FSSAI; 13 Aug ultimatum; FSSAI filed revised proposal 28 Aug 2026; hearing 10 Sep 2026; Court questioned timeline, readability, and whether single-nutrient trigger is needed. (foodos360, LinkedIn pulse Sep 2026, Drishti IAS 1 Sep 2026)
- [S] FSSAI proposal: red hexagon "High Sugar/Salt/Fat"; Phase I = products high in TWO OR MORE of added sugar, added (saturated) fat, salt + sweetened beverages; Phase II (no date) = any one; thresholds from ICMR-NIN Dietary Guidelines 2024; exemptions for single-ingredient/inherently HFSS foods (ghee, oil, sugar, jaggery, honey); text one font point larger than back-of-pack.
- [S] Expert/petitioner criticism: "two or more" loophole; "added" vs "total" nutrients (ICMR-NIN defines on total per 100 g); size; no multilingual warnings.
- [V] Lancet Regional Health SE Asia 2026 commentary (UPF & HFSS in India): India lacks a regulatory UPF definition; "commonly consumed non-industrially prepared foods such as samosas, chaat, jalebi are HFSS ... remain largely outside regulatory focus"; calls for a two-axis (processing x nutrient) India-specific definition.
- [S] ThePrint Jun 2025: FSSAI to adopt ICMR-NIN HFSS norms (e.g., >15% energy from added fat/oil; salt >5 g/day; sugar >5% energy).
- [V] Prior art: Nutrients 2021 (MDPI 13/8/2799): WHO SEARO vs Chilean model on 10,501 Indian products (Mintel 2015-20, proprietary): 68% >= 1 warning; industry "Nutrition Alchemy" (n=1,306) claimed 96%. George Institute/ATNI 2020 India product profile (Euromonitor/Innova, proprietary). Nutrients 2022 RCT (n=2,869, 6 states): warning labels best at helping identification.
  GAP: no open, reproducible analysis of the EXACT 2026 FSSAI proposal (ICMR-NIN thresholds, 2-of-3 vs 1-of-3, added vs total, exemptions) found; no analysis applying the same rule to TRADITIONAL/unpackaged Indian foods found.
- [V] Open Food Facts India: 10,000 products (Sep 2024 milestone; growing); open dump. [U] field completeness for added sugar / sat fat / sodium.
- [S] FSSAI 13 Aug 2026 warning to celebrities/influencers on misleading food claims; high-protein FMCG boom (Market Decipher 2026: high-protein FMCG ~Rs 14,000 Cr; "protein namkeen" trend, Esquire Sep 2026) -> health-halo claims are a live issue.

HEALTHY DIET AFFORDABILITY:
- [S] CRISIL Roti Rice Rate (monthly): veg/non-veg thali cost (fixed basket roti, rice, dal, onion/tomato/potato veg, curd, salad), widely reported; Jun 2026 veg +5% YoY. Basket is NOT nutrition-defined.
- [V] Azim Premji Univ CSIE working paper 2026 (HCES 2023-24): cost of guideline-compliant diet Rs 63.6 veg / 73.1 non-veg per consumer unit/day; 31.2% urban, 56.6% rural would need to spend more. Commodity-level, annual, not recipes.
- [S] SOFI/FAO: ~56% of Indians cannot afford a healthy diet (UNICEF India brief Dec 2025); CoHD India rising.
- [S] DoCA Price Monitoring Division publishes DAILY retail/wholesale prices of essential commodities across centres (fcainfoweb.nic.in).
  GAP: no recipe-level, cookable, regionally authentic, monthly "healthy thali" cost tracker found (only blogs + one organic-thali costing chapter).

## New candidate projects
### N1 "Red Hexagon": who gets the warning? Open impact analysis of FSSAI's proposed front-of-pack labels, for packaged AND traditional Indian foods
Specific question the world is asking (SC, FSSAI, public health groups, industry): does the 2-of-3 rule catch unhealthy foods, and how much do "added vs total" and exemptions change who is flagged? Plus: what about jalebi/samosa/namkeen that escape because they are not packaged?
Deliverables:
 D1 Open dataset: Indian packaged products (Open Food Facts India, cleaned) + Indian traditional dishes (INDB 1,014 recipes; RecipeDB Indian subset) mapped to per-100 g sugar/fat/salt/energy.
 D2 Rule simulator: every variant (2-of-3 vs 1-of-3; added vs total; ICMR-NIN vs WHO SEARO thresholds; with/without exemptions) -> % flagged by category; "loophole map" (products high in one nutrient that Phase I misses).
 D3 AI component where it is genuinely needed: labels do not declare "added saturated fat" (and many OFF entries miss added sugar) [U, verify]; estimate added fat/sugar from the INGREDIENT LIST (NLP over ingredients + recipe-style mass balance), validated on products/recipes where values are known. For recipes, added vs intrinsic is computed from ingredients (sugar/jaggery/oil/ghee added vs naturally present).
 D4 Health-halo audit: share of products with "high protein / healthy / natural" claims that would still carry a red hexagon.
 D5 Public checker: search a product or enter a recipe -> which variant flags it and why.
Why rare among classmates: nobody in the visible course/hackathon record touches regulation; it needs recipe + nutrition + NLP + policy reading.
Professor fit: nutrition/health pillar, recipes (INDB/RecipeDB), NER, "health for the complete dish"; symposium speakers include policy/nutrition orgs.
Risks: final rule may be notified mid-project (analysis still valid for Phase II and as evaluation); OFF data completeness/quality; must stay neutral (analysis, not advocacy).

### N2 "Healthy Thali Index": what does a healthy home-cooked thali cost this month?
Specific question: CRISIL tells India monthly what a thali costs, but not whether that thali is healthy or what a healthy one costs; 56% can't afford a healthy diet (SOFI). What is the cheapest thali that meets ICMR-NIN 2024 targets AND is a real, cookable, regionally authentic meal, and how does it move with tomato/onion/oil price shocks?
Deliverables:
 D1 Recipe-nutrient-cost table (INDB recipes x DoCA daily prices by city).
 D2 Optimiser: least-cost thali meeting ICMR targets, constrained to plausible meals (dish combinations learned from recipe/menu co-occurrence = culinary fingerprint; this is where learning is needed, because plain LP diets are famously unpalatable).
 D3 Backfilled monthly index 2020-2026 (captures tomato/onion spikes) vs CRISIL's thali; regional variants.
 D4 Dashboard / monthly report.
Risks: price-to-ingredient mapping; DoCA covers ~22-38 items (spices, veg variety limited); authenticity constraint needs care.

### N3 (fold into N1 or standalone-lite) "Protein-washing" audit
Do "high protein" Indian products meet FSSAI claim thresholds and what protein quality (PDCAAS-style) do they have? Timely (protein boom, FSSAI influencer warning) but narrower; best as N1's D4.

## USER FEEDBACK on v4 (2026-09-29)
- N1 "genuinely good" but feels like a RULE-BASED classifier on its face (value > threshold -> red hexagon); lacks a SCIENTIFIC vibe. The AI part the user accepts: inferring composition (e.g., sat fat in a samosa) from ingredients for unlabelled foods, but that is only the backend.
- N3 -> merge into N1 (agreed).
- N2 -> rejected: answers a passive question, solves no problem.
- Iron-smart kitchens (Pkg 1 in 16) is still liked for its SCIENTIFIC character ("only research can answer it"), but the fear remains: a null answer = wasted work.
- Pass history: pass 1 = broad landscape (01-14); pass 2 = what India is asking (17); NEXT pass 3 = what real PROBLEMS can we SOLVE (restaurants, food businesses, anything related to computational gastronomy). Then generate ideas; choose afterwards.
- Implied target profile: real problem someone has + a genuine scientific question inside it (research-only answer) + AI necessary + not trivial if the answer is "no" + no fieldwork + mini scale.
