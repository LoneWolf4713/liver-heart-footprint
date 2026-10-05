# 05 Forward-looking research (date of research: 2026-09-29). Tool: batch_search (works; caps at 25K chars/batch, 3 queries max)

NOTE ON SOURCE QUALITY: many 2026 sources below are vendor/consultancy/clinic blogs (Lushbinary, digitalapplied, InsightRx, ALTRcare, CLP). Numbers are directional, NOT verified. Stanford AI Index 2026, arXiv, PMC, CNBC, FoodNavigator = stronger.

## A. AI landscape 2026
- Agents + MCP mainstream (claimed: agentic AI in ~80% of new apps, MCP ~97M downloads [blog claim]). Best practice = TIERED ROUTING: small model for most steps, escalate to frontier only for hard reasoning.
- Inference cost down ~80% for comparable capability over ~1 year [blog estimate]; "estimates that killed projects in 2024 are often wrong by 10x in 2026".
- ON-DEVICE stack landed May-June 2026 in one week: NVIDIA RTX Spark / DGX Station, Microsoft Scout (private preview; GA early 2027), Microsoft Aion 1.0 Instruct (small, open-source on HF July 2026) and Aion 1.0 Plan (14B reasoning), Hermes Desktop (open-source on-device learning agent).
  Hybrid routing (local default, cloud on escalation) expected to be standard. Latency win clear; cost win usage-dependent; privacy improves structurally but needs governance.
- Stanford AI Index 2026 (Science chapter): natural-science AI publications ~80,150 in 2025 (+26%); AI = 5.8-8.8% of research output. Breakthroughs cluster where DATA INFRASTRUCTURE exists (structural biology, physics, chemistry, materials).
  Agents still weak at real analysis: BixBench ~17% (bioinformatics), PaperArena 38.8% vs PhD 83.5%, ReplicationBench <20%, UnivEarth 33%. Best models beat human-expert avg on ChemBench but fail basic tasks.
  "Experimental validation remains expensive and time-consuming" = the bottleneck. Google AI Co-scientist, Sakana AI Scientist-v2 (paper accepted at an ICLR workshop), Evo 2, AlphaGenome, virtual-cell models.
- IMPLICATION: local/small models are now credible and justified when privacy/offline/cost matter. LLM-only wrappers are commoditised. The scarce thing is grounded structured data + a validation loop.

## B. AI x food, 2026
- arXiv 2607.09529 (Jul 2026) "AI and the Generative Science of Food": food formulation becoming generative science; multi-objective design (nutrition, sensory, sustainability, cost, manufacturability, consumer acceptance, culture); forward models -> generative + personalized.
- FoodPuzzle (arXiv 2409.12832, 2024; USC + UC Davis): LLM AGENTS AS FLAVOR SCIENTISTS, benchmark of 978 foods x 1,766 flavor molecules built on FlavorDB; tasks Molecular Food Prediction and Molecular Profile Completion. => "LLM agent for flavor sourcing on FlavorDB" is already done; cannot claim novelty there.
- Commercial AI food innovation (Tastewise: consumer-intent data, 1M+ menus; Givaudan flavor) is segmented into horizon scanning / concept validation / flavor formulation.
- Multimodal LLM nutrition-from-photo (PMC12513282, GPT-4o/Claude 3.5/Gemini 1.5, mid-2024 models): GPT-4V MAE 46.3 g vs dietitians 48.5 g (Lo et al.); weak on mixed dishes, 2D volume; FoodSky = food-specific LLM passing culinary exams. => dietary assessment by generic multimodal LLM is commoditising. Poor project target.
- Kitchen robotics 2026: single-format robots (pizza, fry, bowl assembly: Chipotle+Hyphen) have track records; robot wok in Philadelphia can do 5,000+ dishes but needs "recipe programming, sensor calibration"; humanoids not ready (Haidilao safety issues; McDonald's Shanghai pilot);
  Kitchen Robotics Beastro (45 dishes/h, acquired by Circus Group 30 Apr 2026). BOTTLENECK = encoding recipes into machine-executable form. Ties to the course/lab open idea "recipe data structure ... combined with robotics".

## C. GLP-1 wave (BIGGEST time-sensitive shift found)
- Global: GLP-1 users eat less; ~half report fewer calories (UBS); ~70% of those snack less; ~60% dine out less; 45% drink less alcohol (EY-Parthenon via CNBC Mar 2026). Every calorie must count -> protein (muscle preservation), fiber, hydration, smaller portions, GI-side-effect-friendly food.
  Nestle Vital Pursuit (2024), Ingredion reformulation guidance (Jan 2026). ~39% quit within 3 months, ~50% within 12 (Ingredion cites); oral GLP-1 pills expected to raise adoption. "Food won't replace the drug but can complement fat/muscle loss" (FoodNavigator Apr 2026).
- INDIA: semaglutide patent expired March 2026; 40+ generic brands; price fell from up to Rs 16,400/month to ~Rs 1,290 (-90%) [InsightRx]; branded GLP-1 sales Rs 1,446 Cr in 12 months to Feb 2026 (+178% YoY); projected 5x to Rs 4,500-5,000 Cr by 2030 [InsightRx projection].
  "India has barely built the clinical service layer: titration, monitoring, muscle preservation, relapse prevention" [InsightRx]. CDSCO advisory Mar 2026 on obesity-drug advertising.
- Indian diet issue (clinic blog claim, unverified): traditional Indian vegetarian plate ~60-70% carbohydrate; GLP-1 cuts intake by a third or more -> protein share shrinks -> muscle-loss risk; suggested target 1.2-1.6 g/kg (80-110 g/day) protein.
- What I found for Indian GLP-1 food guidance = clinic/telehealth marketing blogs (generic lists: dal, curd, paneer, soya, millets). I did NOT find a computational, recipe-level, data-driven Indian-food solution. (NOT yet searched deeply => must verify in deep dive.)

## D. India regulation
- FSSAI Labelling & Display (First Amendment) Regulations notified 24 Mar 2026, effective 1 Jul 2027 (small packs, B2B/non-retail containers, infant nutrition exemptions; coffee-chicory front-of-pack direction 22 Jul 2026). Allergen/veg-nonveg/nutrition declarations remain. => modest; low leverage for a project.

## E. Ayurveda informatics (recurs on all 3 symposium pages)
- AyurKOSH (IEEE DataPort): machine-readable Ayurvedic knowledge graph (diseases, symptoms, herbs, formulations) from Charaka Samhita, Bhaishajya Ratnawali.
- AyurvedaAI (GitHub): explainable semantic retrieval (RAG) over Charaka Samhita, "does not invent answers".
- L9G9N0/Computational-Food-Intelligence-Platform (GitHub): "Food Digital Twins" translating Rasa/Virya/Rasa Panchaka into quantitative objects with nutrition + flavor volatiles + clinical evidence; claims there is no rigorous translation layer between Ayurvedic and molecular views [README claim; hobby-grade].
- Status: early, mostly retrieval/KG resources; validation of Ayurvedic food properties against molecular/clinical data is thin (my reading). Risk: pseudoscience optics -> must be framed as knowledge representation + falsifiable tests, not health claims.

## Synthesis of forward-looking forces (feeds the final decision)
1. Local/small models are credible in 2026 -> legit when privacy, offline, cost, or latency matter (health data, restaurant kitchens, low-connectivity India).
2. AI is strongest where data infrastructure exists; agents fail at real analysis; validation is the bottleneck -> the winning design = small model + structured knowledge + deterministic verifier/validation loop, not a big LLM alone.
3. Generic LLM/agent wrappers for flavor (FoodPuzzle), nutrition-from-photo, and recipe generation are done or commoditising.
4. GLP-1 in India in 2026 is a real, fast, under-served food problem with a food-side computational gap (unverified) and a strong bio hook (drug-food/physiology).
5. Kitchen automation needs executable structured recipes; recipe representation with quantities/timings/states is a bottleneck.
6. Ayurveda informatics is early and symposium-favoured, but needs a validation-first framing.
