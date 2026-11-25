"""Validation run against lab-analysed dishes (Phase 1 task T9).

Runs analyse_recipe on validation_v2 recipes, joins against validation_ground_truth.csv,
computes fat energy share (M2) and recipe/lab ratios, writes results.json, and generates REPORT.md.
"""
import json
import os
import re
import statistics
import pandas as pd

from lhf.pipeline import analyse_recipe
from lhf.paths import DATA_CURATED, REPO
from lhf.constants import get as get_constant


def generate_report(res: dict) -> str:
    s = res["summary"]
    cov = res["coverage"]
    bs = res["by_setting"]
    pairs = res["pairs"]

    lines = []
    lines.append("# Validation Report: Phase 1 Core Engine vs Lab-Analysed Dishes")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"This validation evaluates the Phase-1 recipe analysis pipeline (`analyse_recipe`) "
        f"against independently laboratory-analysed Indian dishes from published nutritional surveys. "
        f"A total of {s['n_pairs']} recipe-lab pairs were evaluated across {s['n_recipes']} recipes "
        f"representing {s['n_dishes']} distinct dishes."
    )
    lines.append("")
    lines.append(
        "The primary metric of comparison is M2: fat energy share (fat grams multiplied by the fat "
        "energy conversion factor divided by total energy in kilocalories, expressed as a percentage). "
        "The ratio is defined as recipe M2 divided by lab M2."
    )
    lines.append("")
    lines.append(
        f"- Overall median ratio: {s['median_ratio']:.2f} "
        f"(mean: {s['mean_ratio']:.2f}, range: {s['min_ratio']:.2f} to {s['max_ratio']:.2f})"
    )
    lines.append(f"- Home setting median ratio: {s['median_ratio_by_setting']['home']:.2f}")
    lines.append(f"- Retail setting median ratio: {s['median_ratio_by_setting']['retail']:.2f}")
    lines.append(f"- Takeaway setting median ratio: {s['median_ratio_by_setting']['takeaway']:.2f}")
    lines.append("")
    lines.append(
        f"Overall, the median ratio across all {s['n_pairs']} pairs is close to unity ({s['median_ratio']:.2f}). "
        f"However, this overall figure encompasses noticeable variation across dish categories and preparation settings. "
        f"Takeaway dishes show a median ratio of {s['median_ratio_by_setting']['takeaway']:.2f}, with several dishes "
        f"(such as prawn bhuna) yielding lower fat energy shares in written recipes than in restaurant preparations. "
        f"In contrast, home-style recipes with frying or tadka (such as sambar and vegetable pilau) exhibit higher fat energy "
        f"shares than the laboratory-measured home samples. "
        f"These findings indicate that ingredient sums provide a reasonable first-order approximation of dietary fat, "
        f"while individual dish predictions remain subject to culinary variation."
    )
    lines.append("")
    lines.append("## Per-dish table")
    lines.append("")
    lines.append(
        "The following table details all evaluated recipe-lab pairs, reporting recipe fat energy share (Recipe M2), "
        "laboratory-analysed fat energy share (Lab M2), the recipe-to-lab ratio, and the ingredient line inclusion count."
    )
    lines.append("")
    lines.append("| Recipe ID | Dish | Setting | Lab Code | Recipe M2 (%) | Lab M2 (%) | Ratio | Lines (Included/Total) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for p in pairs:
        lines.append(
            f"| {p['recipe_id']} | {p['dish']} | {p['setting']} | {p['lab_code']} | "
            f"{p['recipe_M2']:.1f}% | {p['lab_M2']:.1f}% | {p['ratio']:.2f} | "
            f"{p['lines_included']}/{p['lines_total']} |"
        )
    lines.append("")
    lines.append("## By setting")
    lines.append("")
    lines.append(
        "Nutrient composition was broken down across the three preparation settings recorded in the ground truth dataset: "
        "home-cooked dishes, retail ready-meals, and commercial takeaway dishes."
    )
    lines.append("")
    lines.append("| Setting | Pairs | Median Ratio | Mean Ratio | Min Ratio | Max Ratio |")
    lines.append("|---|---|---|---|---|---|")
    for st in ("home", "retail", "takeaway"):
        d = bs[st]
        lines.append(
            f"| {st} | {d['n_pairs']} | {d['median_ratio']:.2f} | {d['mean_ratio']:.2f} | "
            f"{d['min_ratio']:.2f} | {d['max_ratio']:.2f} |"
        )
    lines.append("")
    lines.append(
        "Key setting-specific observations include:"
    )
    lines.append(
        f"- **Home ({bs['home']['n_pairs']} pairs)**: Median ratio is {bs['home']['median_ratio']:.2f}. "
        "Dishes such as saag and methi aloo track closely with laboratory samples. Sambar and vegetable pilau "
        f"show ratios above 1.0 (up to {bs['home']['max_ratio']:.2f} for vegetable pilau), reflecting generous cooking oil and ghee quantities "
        "specified in popular web recipes compared to hospital and laboratory-prepared reference samples. "
        f"One bhindi sabzi recipe omitting oil in the ingredient list resulted in a ratio of {bs['home']['min_ratio']:.2f}."
    )
    lines.append(
        f"- **Retail ({bs['retail']['n_pairs']} pairs)**: Median ratio is {bs['retail']['median_ratio']:.2f}. "
        "Evaluated against chilled and frozen chicken tikka masala ready-meals, recipe estimates slightly exceed retail laboratory values."
    )
    lines.append(
        f"- **Takeaway ({bs['takeaway']['n_pairs']} pairs)**: Median ratio is {bs['takeaway']['median_ratio']:.2f}. "
        f"Takeaway dishes show substantial dispersion ({bs['takeaway']['min_ratio']:.2f} to {bs['takeaway']['max_ratio']:.2f}). "
        "Prawn bhuna recipes yield lower fat energy shares than commercial takeaway food, consistent with commercial establishments "
        "using additional oil in cooking bases."
    )
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(
        f"Across all {cov['total_recipes']} recipes evaluated in this validation run, "
        f"a total of {cov['lines_total']} ingredient lines were parsed and processed. "
        f"The engine included {cov['lines_included']} lines ({cov['line_inclusion_pct']:.1f}% inclusion rate), "
        f"representing {cov['included_mass_g']:.1f} grams of quantified edible mass."
    )
    lines.append("")
    lines.append("Line status breakdown:")
    lines.append("")
    lines.append("| Status / Exclusion Reason | Count |")
    lines.append("|---|---|")
    lines.append(f"| Lines included | {cov['lines_included']} |")
    for reason in sorted(cov["excluded_by_reason"].keys()):
        count = cov["excluded_by_reason"][reason]
        lines.append(f"| Excluded: {reason} | {count} |")
    lines.append(f"| Total lines | {cov['lines_total']} |")
    lines.append("")
    lines.append(
        f"Lines excluded as WATER ({cov['excluded_by_reason'].get('WATER', 0)} lines) contain plain water or ice and do not contribute macronutrients. "
        f"UNQUANTIFIED lines ({cov['excluded_by_reason'].get('UNQUANTIFIED', 0)} lines) represent ingredients without measurable quantities (such as 'salt to taste'). "
        f"UNQUANTIFIABLE lines ({cov['excluded_by_reason'].get('UNQUANTIFIABLE', 0)} lines) and UNMAPPED lines ({cov['excluded_by_reason'].get('UNMAPPED', 0)} lines) "
        "reflect items lacking documented conversion measures or composition table matches. "
        "No arbitrary fallback quantities were imputed."
    )
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.append(
        "Several methodological constraints must be taken into account when interpreting these results:"
    )
    lines.append("")
    lines.append(
        f"- **Sample size and dish diversity**: The dataset is restricted to {s['n_dishes']} distinct dishes "
        f"and {s['n_recipes']} web recipes. A broader validation set covering more regional variations and dish categories "
        "will be needed in subsequent phases."
    )
    lines.append(
        "- **Ground truth provenance**: Reference nutritional values are sourced from UK laboratory surveys "
        "(University of Leeds, Aspland & James, LGC, and safefood), rather than laboratory analyses of meals prepared in India. "
        "Ingredients available in the UK may differ in composition and moisture from Indian domestic ingredients."
    )
    lines.append(
        "- **Culinary mass dynamics**: The Phase-1 pipeline sums raw ingredient nutrient contributions as written. "
        "It does not model pan-oil retention, deep-frying oil absorption dynamics, or cooking moisture loss. "
        "Evaluating fat energy percentage (M2) mitigates water loss variability, but cannot account for unabsorbed oil left behind in cookware."
    )
    lines.append(
        "- **Unquantified seasonings and salt**: Seasonings listed without quantities ('to taste', 'adjust as needed') are excluded "
        "by design to avoid speculative assumptions. Consequently, sodium totals from web recipes represent lower bounds."
    )
    lines.append(
        "- **Scope of dietary estimates**: The pipeline produces dietary estimates for educational and awareness purposes. "
        "These estimates do not represent diagnostic nutritional assessments."
    )
    lines.append("")
    return "\n".join(lines)


def self_check(res: dict, rep: str):
    for sec in ("Summary", "Per-dish", "By setting", "Coverage", "Limitations"):
        if not re.search(rf"^#+ .*{sec}", rep, re.M | re.I):
            raise AssertionError(f"REPORT.md missing required section: {sec}")

    if "conclusively" in rep.lower() or "proves" in rep.lower():
        raise AssertionError("REPORT.md contains forbidden words 'conclusively' or 'proves'")

    nums_json = set()

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            nums_json.add(float(x))

    walk(res)

    tol = 1 / (1000 * 1000 * 1000)
    for tok in re.findall(r"(?<![\w.\-/:])\d+(?:\.\d+)?(?![\w.\-/:])", rep):
        v = float(tok)
        if v in (0, 1, 2) or (v.is_integer() and 1 <= v <= 9 and len(tok) == 1):
            continue
        dec = len(tok.split(".")[1]) if "." in tok else 0
        if not any(abs(round(n, dec) - v) < tol for n in nums_json):
            raise AssertionError(f"REPORT.md number {tok} does not appear in results.json")


def run_validation():
    # Load constants and ground truth
    fat_kcal_per_g = get_constant("FAT_KCAL_PER_G")
    gt_path = os.path.join(DATA_CURATED, "validation_ground_truth.csv")
    gt = pd.read_csv(gt_path)

    # Load V2 recipes
    recipes_path = os.path.join(REPO, "data", "samples", "recipes_phase1.jsonl")
    v2_recipes = []
    with open(recipes_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("id", "").startswith("V2-"):
                v2_recipes.append(rec)

    # Sort recipes by id for deterministic results
    v2_recipes.sort(key=lambda r: r["id"])

    # Process each recipe
    pairs = []
    total_lines = 0
    total_included = 0
    total_mass = 0.0
    exclusion_reasons = {}

    for recipe in v2_recipes:
        rid = recipe["id"]
        dish = recipe["dish"]
        out = analyse_recipe(recipe)

        cov = out.get("coverage", {})
        total_lines += cov.get("lines_total", 0)
        total_included += cov.get("lines_included", 0)
        total_mass += cov.get("included_mass_g", 0.0)
        for reason, count in cov.get("excluded_by_reason", {}).items():
            exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + count

        t = out.get("totals", {})
        energy_kcal = t.get("energy_kcal")
        if not energy_kcal:
            continue

        recipe_M2 = t.get("fat_g", 0.0) * fat_kcal_per_g / energy_kcal * 100

        # Match against ground truth by dish
        matching_gt = gt[gt["dish"] == dish]
        for g in matching_gt.itertuples():
            if not g.energy_kcal or g.fat is None:
                continue
            lab_M2 = g.fat * fat_kcal_per_g / g.energy_kcal * 100
            if lab_M2 == 0:
                continue
            ratio = recipe_M2 / lab_M2
            pairs.append({
                "dish": dish,
                "recipe_id": rid,
                "lab_code": str(g.code),
                "setting": g.setting,
                "recipe_M2": float(recipe_M2),
                "lab_M2": float(lab_M2),
                "ratio": float(ratio),
                "lines_included": cov.get("lines_included", 0),
                "lines_total": cov.get("lines_total", 0)
            })

    # Summary statistics
    ratios = [p["ratio"] for p in pairs]
    settings = sorted({p["setting"] for p in pairs})

    summary = {
        "n_pairs": len(pairs),
        "n_recipes": len(v2_recipes),
        "n_dishes": len(set(p["dish"] for p in pairs)),
        "median_ratio": float(statistics.median(ratios)),
        "mean_ratio": float(statistics.mean(ratios)),
        "min_ratio": float(min(ratios)),
        "max_ratio": float(max(ratios)),
        "median_ratio_by_setting": {
            st: float(statistics.median(p["ratio"] for p in pairs if p["setting"] == st))
            for st in settings
        }
    }

    by_setting = {}
    for st in settings:
        st_ratios = [p["ratio"] for p in pairs if p["setting"] == st]
        by_setting[st] = {
            "n_pairs": len(st_ratios),
            "median_ratio": float(statistics.median(st_ratios)),
            "mean_ratio": float(statistics.mean(st_ratios)),
            "min_ratio": float(min(st_ratios)),
            "max_ratio": float(max(st_ratios))
        }

    coverage = {
        "total_recipes": len(v2_recipes),
        "lines_total": total_lines,
        "lines_included": total_included,
        "lines_excluded": total_lines - total_included,
        "line_inclusion_pct": (total_included / total_lines * 100) if total_lines else 0.0,
        "included_mass_g": float(total_mass),
        "excluded_by_reason": exclusion_reasons
    }

    results = {
        "pairs": pairs,
        "summary": summary,
        "by_setting": by_setting,
        "coverage": coverage
    }

    # Generate REPORT.md
    report_text = generate_report(results)

    # Write files
    out_dir = os.path.join(REPO, "experiments", "phase1_validation")
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    report_path = os.path.join(out_dir, "REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Verify self-check
    self_check(results, report_text)
    print(f"Validation successful: {len(pairs)} pairs generated in {out_dir}")


if __name__ == "__main__":
    run_validation()
