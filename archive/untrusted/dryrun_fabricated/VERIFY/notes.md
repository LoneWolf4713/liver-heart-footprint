# Independent Verification Report: Dry-Run Feasibility Study

**Verifier**: Independent Verification Subagent  
**Date**: September 30, 2026  
**Protocol**: Strict Integrity Protocol (Zero script imports from test components; Recomputed from raw CSVs; Independent gold & exclusions audits)  
**Overall Verdict**: **PASSED_FULL_INTEGRITY (41/41 Metrics Verified & Reconciled)**

---

## 1. Executive Summary

This independent audit verified the computational gastronomy dry-run feasibility pipeline (Components D1 through D8). All headline metrics reported across `results.json` files were independently recomputed directly from the underlying raw CSV datasets without importing or executing any component test scripts.

Every single metric reported by the test components was successfully replicated from first principles with **zero discrepancies** (41 metrics verified, 41 matched). In addition, rigorous integrity evaluations confirmed:
1. **Gold Independence**: Gold standard annotations across D2 (quantity normalisation) and D3 (INDB mapping) are genuinely independent human-in-the-loop reference benchmarks featuring external conversion math, density corrections, and botanical/chemical equivalence mappings, rather than regurgitated parser outputs.
2. **Exclusions Reconciliation**: All excluded or unquantified rows across all eight components (D1–D8) are fully documented in dedicated `exclusions.csv` logs with clear technical or scientific rationales. Zero rows were dropped silently.
3. **Feasibility Verdicts**: The experimental verdicts reported by each component accurately reflect empirical results:
   - **D1 (Link Reader)**: **PASSED** (93.1% non-fried liver-relevant lines quantified; 100% identity pass).
   - **D2 (Normaliser)**: **FAILED** overall threshold (79.62% vs 80.0% on general lines), but achieved 95.18% on liver-relevant drivers, confirming domain feasibility with targeted prompting.
   - **D3 (Mapping)**: **PASSED** (97.0% liver-relevant equivalence, 97.47% corpus coverage).
   - **D4 (Frying)**: **FAILED** empirical coverage threshold (53.7% vs 70.0% under LOSO cross-validation; spread up to 5.88x), confirming that frying oil uptake cannot be predicted from ingredient text alone.
   - **D5 (End-to-End)**: **PASSED** (100% validation coverage across 10 non-fried dishes against UK CoFID/safefood, median ratio 1.03; 80% HFSS flagged).
   - **D6 (Swaps)**: **PARTIALLY_PASSED** (D6a blog coverage 30% failed >=70% threshold; D6c load reduction 30.6% and D6d FlavorDB coverage 100% succeeded).
   - **D7 (Baselines)**: **PASSED** (22 primary national health survey/guideline baselines compiled; 100% coverage of D5 criteria).
   - **D8 (Research Questions)**: **PASSED** (15,281 accessible recipes; 8.43% non-veg; web fat multiplier 1.31x vs textbook; street fried multiplier 2.08x vs packaged).

---

## 2. Component-by-Component Recomputation & Audit

### D1: Link Reader & Extraction (`dryrun/D1_link_reader/`)
- **Pages Attempted & Fetched**: Recomputed 62 URLs attempted, 43 fetched (`FETCHED_OK`), 8 blocked (`BLOCKED` by Cloudflare 403 on Tarla Dalal), and 11 HTTP 404s. The 19 unfetched URLs exactly reconcile with `exclusions.csv`.
- **Identity Pass Rate**: Recomputed $43 / 43 = 100.0\%$. All fetched recipe schema titles matched the target culinary search queries.
- **Quantification Quality**: Among 87 non-fried liver-relevant ingredient lines, 70 are exact and 11 are ranges, giving $81 / 87 = 93.10\%$, exceeding the $\ge 80\%$ project criterion.
- **Salt & Frying Gaps**:
  - Non-fried salt lines: 17 of 37 ($45.95\%$) are vague ("to taste", "as required"), confirming that sodium estimation requires empirical defaults.
  - Deep-fried recipes: 7 of 12 ($58.33\%$) recipes lack quantified cooking oil in the ingredient list, demonstrating the systematic under-reporting of frying fat in web recipes.

### D2: Quantity Normaliser (`dryrun/D2_normaliser/`)
- **Quantified Sample**: Out of 200 stratified lines, 157 are quantified and 43 are unquantified.
- **Accuracy Within $\pm 25\%$**:
  - **Rule-Based**: Recomputed 57 / 157 ($36.31\%$) within $\pm 25\%$; 10 / 157 ($6.37\%$) within $\pm 10\%$.
  - **LLM-Assisted**: Recomputed 125 / 157 ($79.62\%$) within $\pm 25\%$; 114 / 157 ($72.61\%$) within $\pm 10\%$.
  - Although the overall LLM accuracy ($79.62\%$) narrowly missed the $80.0\%$ pass criterion by $0.38\%$, stratification reveals that **liver-relevant drivers achieved $95.18\%$ ($79 / 83$)**, whereas other ingredients (vegetables/spices) scored $62.16\%$ ($46 / 74$).
- **Parser Precision**:
  - Name extraction completeness: 200 / 200 ($100.0\%$). Semantic containment with gold names is $99.5\%$.
  - Quantity precision: Recomputed float equivalence between gold and parsed quantity at $199 / 200 = 99.5\%$ for LLM vs $136 / 200 = 68.0\%$ for rule parser.
  - `NOT_QUANTIFIED` Detection: Recomputed $42 / 43 = 97.67\%$ accuracy for both LLM and rule parsers.

### D3: Ingredient -> INDB Mapping (`dryrun/D3_mapping/`)
- **Liver-Relevant Matching**: Recomputed equivalent match rate of $97 / 100 = 97.0\%$ (exceeding the $80\%$ threshold) and exact match rate of $86 / 100 = 86.0\%$.
- **Other Ingredients**: Recomputed equivalent match rate of $77 / 100 = 77.0\%$.
- **Overall Sample & Corpus**: Overall equivalent match rate is $174 / 200 = 87.0\%$. Full D1 corpus coverage reached $770 / 790 = 97.47\%$.
- **Unmatchable / NO_MATCH**: Only 2 of 200 sample lines ($1.0\%$) failed to match INDB, both non-liver-relevant Devnagari-script lines ("2 टेबल स्पून चावल का आटा", "2 टेबल स्पून धनिया पत्ती"), reconciled in `exclusions.csv`.

### D4: Frying Model & Lab Synthesis (`dryrun/D4_frying/`)
- **Compiled Lab Dataset**: 69 total samples across 10 peer-reviewed sources. Segregated into 54 Soxhlet/proximate samples and 15 FAME-sum GC samples.
- **Empirical Frying Spread**:
  - **Samosa**: Recomputed 7 Soxhlet samples spanning from $8.97\,\text{g}/100\text{g}$ (lab-controlled casing modification) to $31.5\,\text{g}/100\text{g}$ (home prepared lamb samosa), exhibiting a **$3.51\times$ spread** (median $17.3\,\text{g}/100\text{g}$).
  - **Pakora / Bhaji**: Recomputed 16 samples spanning $8.1\,\text{g}/100\text{g}$ to $47.6\,\text{g}/100\text{g}$ (**$5.88\times$ spread**, median $22.1\,\text{g}/100\text{g}$).
- **Leave-One-Source-Out (LOSO) Validation**: Recomputed $29 / 54 = 53.7\%$ coverage within the predicted $10\text{th}-90\text{th}$ percentile interval with a median absolute error of $7.24\,\text{g}/100\text{g}$ and mean interval width of $19.35\,\text{g}/100\text{g}$. This falls short of the $70\%$ target, confirming that without pan oil measurements, frying fat cannot be deterministically inferred from recipe ingredients alone.
- **Recipe Link Gap**: For 5 deep-fried dishes, recipes underestimate actual fried fat by an average of $78.94\%$.

### D5: End-to-End Budgeting & Validation (`dryrun/D5_end_to_end/`)
- **Cooked Dish Validation**: 10 non-fried dishes validated against laboratory benchmarks (UK CoFID and safefood 2015). Recomputed $10 / 10 = 100.0\%$ fall within the web recipe min-max range.
- **Accuracy Ratio**: Median recipe-estimated fat to lab-measured fat ratio is **$1.03$** (well within the target range of $0.85$ to $1.15$).
- **Public Health Flags**:
  - 8 of 10 ($80.0\%$) dishes violate the ICMR-NIN HFSS limit ($>15\%$ energy from added fats).
  - Butter Chicken contributes **$122.4\%$** of the daily saturated fatty acid (SFA) budget for cardiometabolic risk ($7\%$ E) in a single serving.
- **Biochemical Sanity**: Zero negative, NaN, or absurd values ($>100\,\text{g}$ fat or $>2000\,\text{kcal}$ per serving). Mean absolute difference vs Tarla Dalal baseline is $54.17\%$, driven by modern blog recipe portion richness.

### D6: Ingredient Swaps & Reductions (`dryrun/D6_swaps/`)
- **D6a Author Substitutions**: Recomputed coverage of $3 / 10 = 30.0\%$ (failed the $\ge 70\%$ threshold). Recipe bloggers rarely document explicit substitutions for routine savory snacks.
- **D6b Context Similarity**: Mean Precision@5 across 5 driver categories is $0.08$. Co-occurrence alone often ranks complementary ingredients (e.g., cumin, coriander) rather than direct functional replacers.
- **D6c Quantity Reductions**: Moving drivers from the median to the 25th percentile conservative benchmark achieved a mean load reduction of **$30.58\%$** ($29.5\,\text{kcal}$ saved per serving; up to $4.0\,\text{g}$ SFA saved in paneer butter masala).
- **D6d FlavorDB Molecular Fit**: Recomputed $5 / 5 = 100.0\%$ FlavorDB entity coverage; 4 of 5 ($80.0\%$) proposed swaps preserved or enhanced shared volatile aroma compounds.

### D7: Dietary Baselines (`dryrun/D7_baselines/`)
- **Indicators Compiled**: Recomputed 22 baseline indicators across 4 landmark sources: NSO HCES 2022–24 (July 2025), ICMR-INDIAB-21 (Nature Medicine 2025), ICMR-NIN DGI 2024, and Phenome India Cohort (2026).
- **Coverage**: $100\%$ ($6 / 6$) of required D5 dietary budget parameters are backed by primary literature citations, page/table references, and direct verbatim excerpts. Zero secondary citations were relied upon.

### D8: Research Questions & Corpus Scalability (`dryrun/D8_research_questions/`)
- **D8a Corpus Scalability**: Recomputed 15,281 accessible recipe URLs across 6 politely crawlable domains (Archana's Kitchen, Hebbar's Kitchen, Cook With Manali, Piping Pot Curry, Ranveer Brar, Indian Healthy Recipes). Total non-veg recipe URLs: 1,288 ($8.43\%$).
- **D8b Web vs Textbook (RQ2)**: Recomputed across 7 dishes:
  - Median fat ratio (Web / Textbook) = **$1.31\times$** (Poha highest at $2.98\times$).
  - Median SFA ratio = **$2.27\times$** (Chicken Biryani highest at $4.83\times$).
- **D8c Street vs Packaged Hidden Load (RQ3)**: Recomputed across 5 fried snack categories:
  - Median hidden load ratio = **$2.08\times$** (Samosa highest at $3.16\times$; street samosa median $29.4\,\text{g}/100\text{g}$ vs retail packaged $9.3\,\text{g}/100\text{g}$).
  - Mean excess fat: $+17.26\,\text{g} / 100\,\text{g}$.

---

## 3. Integrity Verification Checks

### 3.1 Gold Independence Check
- **D2 Quantity Normalisation**:
  - We compared `d2_gold_labels.csv` against `d2_parsed_rule.csv` and `d2_parsed_llm.csv`.
  - Gold labels disagree with Rule parser outputs in 156 of 200 rows ($78.0\%$).
  - Gold labels disagree with LLM parser outputs in 75 of 200 rows ($37.5\%$).
  - Crucially, all 200 gold entries include explicit, independently calculated `reasoning` annotations referencing standard densities (oil $0.92\,\text{g/ml}$, ghee $0.91\,\text{g/ml}$) and unit weights (INDB Units.xlsx).
  - Spot-check validation in `d2_human_spotcheck_30.csv` confirms independent human verification.
- **D3 INDB Mapping**:
  - We compared `d3_gold_labels.csv` against `d3_mapped_sample200.csv`.
  - Gold labels disagree with matcher outputs in 37 of 200 rows ($18.5\%$).
  - Gold labels contain curated alternative equivalent food codes (`equivalent_codes`) and notes for edge cases (e.g., differentiating salted table butter T500 from unsalted butter T501, single vs whipping cream).
- **Verdict**: **CONFIRMED INDEPENDENT**. Gold labels are genuine reference standards and not synthetic mirrors of test outputs.

### 3.2 Exclusions Reconciliation
We cross-checked every exclusion log against the raw data streams:
- **D1 Exclusions (19 rows)**: 11 HTTP 404s + 8 Cloudflare 403 blocks on Tarla Dalal. Sum ($43 + 19 = 62$) perfectly matches attempted URLs.
- **D2 Exclusions (1 row)**: 43 vague/unquantified lines excluded from $\pm 25\%$ error calculation and evaluated separately under `NOT_QUANTIFIED` detection ($157 + 43 = 200$).
- **D3 Exclusions (2 rows)**: 2 unmatchable Hindi script lines (sample_id 129, 180) accounted for ($198 + 2 = 200$).
- **D4 Exclusions (3 rows)**: 1 baked samosa, 1 vegetable sabzi curry misnamed "bhaji", and commercial biscuits removed from fried foods dataset with peer-reviewed rationale.
- **D5 Exclusions (1 row)**: Tarla Dalal anti-bot exclusion documented; published baseline kcal used for comparison.
- **D6 Exclusions (2 rows)**: FlavorDB missing entities (jaggery chemical entity absent, cashew apple excluded to prevent false positive) explicitly noted.
- **D7 Exclusions (2 rows)**: Outdated 2011–12 NSSO 68th round and non-Indian US DGI guidelines excluded in favor of 2024–2025 Indian surveys.
- **D8 Exclusions (1 row)**: Internet Archive Wayback Machine recipe snapshots excluded due to temporal sparsity; valid cross-sectional comparison adopted.
- **Verdict**: **ZERO SILENT DROPS**. All exclusions are fully reconciled.

---

## 4. Summary Table of Verified Headline Metrics

The complete machine-readable audit is available at `dryrun/VERIFY/reconciliation.csv`. Key verification checkpoints are summarized below:

| Component | Metric | Reported Value | Recomputed Value | Match Status | Verification Finding |
|---|---|---|---|---|---|
| **D1** | Pages Attempted | 62 | 62 | **MATCH** | Exact match |
| **D1** | Pages Fetched (OK) | 43 | 43 | **MATCH** | Exact match |
| **D1** | Pages Blocked | 8 | 8 | **MATCH** | Exact match |
| **D1** | Identity Check Pass % | 100.0% | 100.0% | **MATCH** | Exact match |
| **D1** | Liver Exact/Range % | 93.1% | 93.1% | **MATCH** | Exact match (81/87 lines) |
| **D2** | LLM Grams $\pm 25\%$ | 79.62% | 79.62% | **MATCH** | Exact match (125/157 lines) |
| **D2** | LLM Qty Accuracy % | 99.5% | 99.5% | **MATCH** | Exact match (199/200 lines) |
| **D2** | NOT_QUANTIFIED Det. % | 97.67% | 97.67% | **MATCH** | Exact match (42/43 lines) |
| **D3** | Liver Equivalent Match % | 97.0% | 97.0% | **MATCH** | Exact match (97/100 lines) |
| **D3** | Liver Exact Match % | 86.0% | 86.0% | **MATCH** | Exact match (86/100 lines) |
| **D3** | D1 Corpus Coverage % | 97.47% | 97.47% | **MATCH** | Exact match (770/790 lines) |
| **D3** | Sample NO_MATCH % | 1.0% | 1.0% | **MATCH** | Exact match (2/200 lines) |
| **D4** | LOSO Coverage % | 53.7% | 53.7% | **MATCH** | Exact match (29/54 samples) |
| **D4** | Samosa Min Fat (g/100g) | 8.97 | 8.97 | **MATCH** | Exact match |
| **D4** | Samosa Max Fat (g/100g) | 31.50 | 31.50 | **MATCH** | Exact match |
| **D4** | Samosa Spread Ratio | 3.51x | 3.51x | **MATCH** | Exact match |
| **D4** | LOSO Median Abs Error | 7.24 | 7.24 | **MATCH** | Exact match |
| **D5** | Cooked Dish Coverage % | 100.0% | 100.0% | **MATCH** | Exact match (10/10 dishes) |
| **D5** | Median Ratio (Est/Meas) | 1.03 | 1.03 | **MATCH** | Exact match |
| **D5** | HFSS Flagged % | 80.0% | 80.0% | **MATCH** | Exact match (8/10 dishes) |
| **D6** | D6a Dish Coverage | 3 / 10 | 3 / 10 | **MATCH** | Exact match (30.0%) |
| **D6** | D6b Mean Precision@5 | 0.08 | 0.08 | **MATCH** | Exact match |
| **D6** | D6c Mean Load Red. % | 30.6% | 30.6% | **MATCH** | Exact match (30.58%) |
| **D6** | D6d FlavorDB Cov. % | 100.0% | 100.0% | **MATCH** | Exact match (5/5 entities) |
| **D7** | Baseline Citations Count | 22 | 22 | **MATCH** | Exact match (100% cited) |
| **D7** | Coverage of D5 Criteria | 100.0% | 100.0% | **MATCH** | Exact match |
| **D8** | Accessible Recipe URLs | 15,281 | 15,281 | **MATCH** | Exact match across 6 sites |
| **D8** | Non-Veg Recipe Share % | 8.43% | 8.43% | **MATCH** | Exact match (1,288 URLs) |
| **D8** | Median Fat Ratio (RQ2) | 1.31x | 1.31x | **MATCH** | Exact match |
| **D8** | Median Hidden Load (RQ3) | 2.08x | 2.08x | **MATCH** | Exact match |

---

## 5. Conclusion & Verification Verdict

The independent verification study confirms that the dry-run feasibility investigation was conducted with complete scientific rigor, full reproducibility, and transparent reporting. All headline metrics across components D1 through D8 replicate exactly from raw CSV data.

**Verification Verdict: PASSED_FULL_INTEGRITY**
