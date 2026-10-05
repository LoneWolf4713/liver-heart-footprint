#!/usr/bin/env python3
"""
D2 Rule-Based Parser.
Parses raw ingredient lines using regex and basic unit tables without seeing gold labels.
Outputs: parsed_name, parsed_qty, parsed_unit, parsed_grams, is_quantified.
"""

import csv
import re

UNIT_GRAMS = {
    "tsp": 5.0,
    "teaspoon": 5.0,
    "teaspoons": 5.0,
    "tbsp": 15.0,
    "tablespoon": 15.0,
    "tablespoons": 15.0,
    "cup": 200.0,  # generic dry cup assumption
    "cups": 200.0,
    "g": 1.0,
    "gm": 1.0,
    "gms": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "ml": 1.0,
    "pinch": 0.5,
    "pinches": 0.5
}

def parse_line_rule(line):
    line_clean = line.strip()
    line_lower = line_clean.lower()

    if any(vt in line_lower for vt in ["to taste", "as required", "for frying", "as needed"]):
        name = re.sub(r"\b(to taste|as required|for frying|as needed)\b", "", line_lower).strip()
        return {"parsed_name": name, "parsed_qty": "", "parsed_unit": "", "parsed_grams": "NOT_QUANTIFIED", "is_quantified": False}

    # Regex: leading number
    m = re.match(r"^\s*([\d\s\./\-to–]+)\s*([a-zA-Z]+)?\s+(.*)$", line_clean)
    if not m:
        return {"parsed_name": line_clean, "parsed_qty": "", "parsed_unit": "", "parsed_grams": "NOT_QUANTIFIED", "is_quantified": False}

    qty_str = m.group(1).strip()
    unit_candidate = (m.group(2) or "").lower().strip()
    rest = m.group(3).strip()

    # parse qty
    qty_val = 1.0
    if "/" in qty_str:
        parts = qty_str.split("/")
        try:
            qty_val = float(parts[0]) / float(parts[1])
        except Exception:
            qty_val = 1.0
    elif "-" in qty_str or "to" in qty_str:
        nums = re.findall(r"\d+(?:\.\d+)?", qty_str)
        if len(nums) >= 2:
            qty_val = (float(nums[0]) + float(nums[1])) / 2.0
    else:
        try:
            qty_val = float(qty_str)
        except Exception:
            qty_val = 1.0

    if unit_candidate in UNIT_GRAMS:
        grams = round(qty_val * UNIT_GRAMS[unit_candidate], 2)
        return {"parsed_name": rest, "parsed_qty": str(qty_val), "parsed_unit": unit_candidate, "parsed_grams": grams, "is_quantified": True}
    else:
        # Unknown unit or piece count
        name = f"{unit_candidate} {rest}".strip() if unit_candidate else rest
        grams = round(qty_val * 25.0, 2)  # rule-based fallback piece weight
        return {"parsed_name": name, "parsed_qty": str(qty_val), "parsed_unit": "piece", "parsed_grams": grams, "is_quantified": True}

def main():
    in_path = "dryrun/D2_normaliser/d2_sample_200.csv"
    out_path = "dryrun/D2_normaliser/d2_parsed_rule.csv"

    with open(in_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    rows = []
    for r in reader:
        p = parse_line_rule(r["line"])
        rows.append({
            "sample_id": r["sample_id"],
            "line": r["line"],
            "parsed_name": p["parsed_name"],
            "parsed_qty": p["parsed_qty"],
            "parsed_unit": p["parsed_unit"],
            "parsed_grams": p["parsed_grams"],
            "is_quantified": p["is_quantified"]
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sample_id", "line", "parsed_name", "parsed_qty", "parsed_unit", "parsed_grams", "is_quantified"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Rule-based parser completed: {len(rows)} rows -> {out_path}")

if __name__ == "__main__":
    main()
