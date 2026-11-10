"""Command-line interface for Phase 1 recipe analysis (SPEC §9)."""

import argparse
import json
import sys
from lhf.pipeline import analyse_recipe


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyse a recipe for liver and heart footprint.")
    parser.add_argument("recipe", help="Path to recipe JSON file")
    parser.add_argument("--setting", default="urban", choices=["urban", "rural"], help="Setting (urban or rural)")
    parser.add_argument("--risk", default="general", choices=["general", "cardiometabolic"], help="Risk level (general or cardiometabolic)")

    args = parser.parse_args(argv)

    try:
        with open(args.recipe, "r", encoding="utf-8") as f:
            recipe_data = json.load(f)
    except Exception as e:
        sys.stderr.write(f"Error: unable to read recipe file '{args.recipe}': {e}\n")
        sys.exit(2)

    try:
        out = analyse_recipe(recipe_data, setting=args.setting, risk=args.risk)
    except Exception as e:
        sys.stderr.write(f"Error analysing recipe: {e}\n")
        sys.exit(1)

    print(json.dumps(out, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
