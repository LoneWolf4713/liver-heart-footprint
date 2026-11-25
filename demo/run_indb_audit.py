#!/usr/bin/env python3
"""Run UNMAPPED audit across all INDB recipes.

Output files saved to demo/:
- indb_audit_unmapped.csv
- indb_audit_coverage.csv
"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from lhf.pipeline import analyse_recipe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def format_ingredient_line(amount, unit, ing_name: str) -> str:
    """Format raw amount, unit, and ingredient_name_org into a line string."""
    name_str = str(ing_name).strip() if pd.notna(ing_name) else ""
    if pd.isna(amount):
        return name_str

    amt_str = f"{amount:g}" if isinstance(amount, (int, float)) else str(amount).strip()
    unit_str = (
        str(unit).strip()
        if pd.notna(unit) and str(unit).strip() != "" and str(unit).strip().lower() != "nan"
        else ""
    )

    if not unit_str:
        return f"{amt_str} {name_str}".strip()
    return f"{amt_str} {unit_str} {name_str}".strip()


def load_recipes(recipes_path: Path, servings_path: Path) -> list:
    """Load recipes and servings from Excel files into list of recipe dicts."""
    logging.info(f"Loading recipes from {recipes_path}")
    df_recipes = pd.read_excel(recipes_path)

    logging.info(f"Loading servings from {servings_path}")
    df_servings = pd.read_excel(servings_path)

    servings_map = {}
    for _, row in df_servings.iterrows():
        code = str(row["recipe_code"]).strip()
        val = row.get("no_of_servings")
        if pd.notna(val):
            try:
                num = float(val)
                if num > 0:
                    servings_map[code] = num
            except (ValueError, TypeError):
                pass

    recipes = []
    # Group by recipe_code preserving appearance order
    for code, group in df_recipes.groupby("recipe_code", sort=False):
        code_str = str(code).strip()
        recipe_name = str(group["recipe_name"].iloc[0]).strip()
        servings = servings_map.get(code_str, 4.0)

        lines = []
        for _, row in group.iterrows():
            line_str = format_ingredient_line(
                row.get("amount"),
                row.get("unit"),
                row.get("ingredient_name_org"),
            )
            if line_str:
                lines.append(line_str)

        recipes.append({
            "id": code_str,
            "dish": recipe_name,
            "servings": servings,
            "lines": lines,
        })

    logging.info(f"Loaded {len(recipes)} recipes from {len(df_recipes)} rows.")
    return recipes


def main():
    recipes_file = PROJECT_ROOT / "data" / "raw" / "indb" / "recipes.xlsx"
    servings_file = PROJECT_ROOT / "data" / "raw" / "indb" / "recipes_servingsize.xlsx"
    output_dir = PROJECT_ROOT / "demo"
    output_dir.mkdir(parents=True, exist_ok=True)

    unmapped_csv_path = output_dir / "indb_audit_unmapped.csv"
    coverage_csv_path = output_dir / "indb_audit_coverage.csv"

    recipes = load_recipes(recipes_file, servings_file)

    unmapped_rows = []
    coverage_rows = []
    errors = []

    total_recipes = len(recipes)
    logging.info(f"Starting analysis of {total_recipes} recipes...")

    for i, recipe_dict in enumerate(recipes, 1):
        rec_code = recipe_dict["id"]
        rec_name = recipe_dict["dish"]

        try:
            result = analyse_recipe(recipe_dict, setting="urban", risk="general")
        except Exception as exc:
            logging.error(f"Error processing recipe {rec_code} ({rec_name}): {exc}")
            errors.append((rec_code, rec_name, str(exc)))
            coverage_rows.append({
                "recipe_code": rec_code,
                "recipe_name": rec_name,
                "lines_total": len(recipe_dict.get("lines", [])),
                "lines_included": 0,
                "lines_unmapped": 0,
                "lines_unquantified": 0,
                "included_mass_g": 0.0,
                "mass_implausible": True,
            })
            continue

        lines_out = result.get("lines", [])
        cov = result.get("coverage", {})
        warnings = result.get("warnings", [])
        excluded = cov.get("excluded_by_reason", {})

        # Collect UNMAPPED lines
        for line in lines_out:
            if line.get("exclusion_reason") == "UNMAPPED":
                parsed = line.get("parsed") or {}
                unmapped_rows.append({
                    "recipe_code": rec_code,
                    "recipe_name": rec_name,
                    "raw_line": line.get("raw"),
                    "parsed_name": parsed.get("name"),
                })

        mass_implausible = any("MASS_IMPLAUSIBLE" in w for w in warnings)

        coverage_rows.append({
            "recipe_code": rec_code,
            "recipe_name": rec_name,
            "lines_total": cov.get("lines_total", len(lines_out)),
            "lines_included": cov.get("lines_included", 0),
            "lines_unmapped": excluded.get("UNMAPPED", 0),
            "lines_unquantified": excluded.get("UNQUANTIFIED", 0),
            "included_mass_g": cov.get("included_mass_g", 0.0),
            "mass_implausible": mass_implausible,
        })

        if i % 100 == 0 or i == total_recipes:
            logging.info(f"Processed {i}/{total_recipes} recipes ({len(unmapped_rows)} unmapped lines so far)")

    # Save CSVs
    df_unmapped = pd.DataFrame(unmapped_rows, columns=["recipe_code", "recipe_name", "raw_line", "parsed_name"])
    df_unmapped.to_csv(unmapped_csv_path, index=False)
    logging.info(f"Saved {len(df_unmapped)} UNMAPPED lines to {unmapped_csv_path}")

    df_coverage = pd.DataFrame(
        coverage_rows,
        columns=[
            "recipe_code",
            "recipe_name",
            "lines_total",
            "lines_included",
            "lines_unmapped",
            "lines_unquantified",
            "included_mass_g",
            "mass_implausible",
        ],
    )
    df_coverage.to_csv(coverage_csv_path, index=False)
    logging.info(f"Saved {len(df_coverage)} recipe coverage rows to {coverage_csv_path}")

    if errors:
        logging.warning(f"{len(errors)} recipes failed with errors during processing.")
    else:
        logging.info("All recipes processed without error!")


if __name__ == "__main__":
    main()
