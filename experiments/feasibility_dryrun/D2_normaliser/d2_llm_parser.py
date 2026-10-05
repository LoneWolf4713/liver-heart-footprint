#!/usr/bin/env python3
"""
D2 LLM-Assisted Parser (Simulated LLM pipeline).
Applies contextual recipe NER rules, structured unit decomposition,
and ingredient-specific density mapping without seeing gold labels.
"""

import csv
import re

INGREDIENT_DENSITY_MAP = {
    # Ingredient-specific weight factors (g/unit)
    ("butter", "tbsp"): 14.2,
    ("butter", "tsp"): 4.7,
    ("butter", "cup"): 227.0,
    ("ghee", "tbsp"): 13.65,
    ("ghee", "tsp"): 4.55,
    ("ghee", "cup"): 218.0,
    ("oil", "tbsp"): 13.8,
    ("oil", "tsp"): 4.6,
    ("oil", "cup"): 220.0,
    ("cream", "tbsp"): 15.0,
    ("cream", "cup"): 240.0,
    ("sugar", "tbsp"): 12.5,
    ("sugar", "tsp"): 4.2,
    ("sugar", "cup"): 200.0,
    ("salt", "tsp"): 6.0,
    ("salt", "pinch"): 0.5,
    ("maida", "cup"): 125.0,
    ("atta", "cup"): 120.0,
    ("flour", "cup"): 125.0,
    ("poha", "cup"): 60.0,
    ("rice", "cup"): 185.0,
    ("dal", "cup"): 200.0,
    ("chana", "cup"): 180.0,
    ("paneer", "cube"): 15.0,
    ("paneer", "cup"): 150.0,
    ("onion", "medium"): 80.0,
    ("onion", "large"): 110.0,
    ("onion", "small"): 50.0,
    ("tomato", "medium"): 90.0,
    ("tomato", "large"): 120.0,
    ("potato", "medium"): 120.0,
    ("chili", "piece"): 4.0,
    ("chilli", "piece"): 4.0,
    ("clove", "piece"): 0.1,
    ("cardamom", "piece"): 0.3,
    ("ginger", "inch"): 6.0
}

STANDARD_UNITS = {
    "tsp": 5.0,
    "teaspoon": 5.0,
    "teaspoons": 5.0,
    "tbsp": 15.0,
    "tablespoon": 15.0,
    "tablespoons": 15.0,
    "cup": 240.0,
    "cups": 240.0,
    "katori": 150.0,
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

def parse_llm_style(line):
    line_clean = line.strip()
    line_lower = line_clean.lower()

    # Vague detection
    if any(vt in line_lower for vt in ["to taste", "as required", "for frying", "as needed", "few sprigs", "some", "optional"]):
        if not re.search(r"^\s*\d+", line_clean):
            name = re.sub(r"\b(to taste|as required|for frying|as needed|optional)\b", "", line_lower).strip()
            name = re.sub(r"[\(\),]", "", name).strip()
            return {
                "parsed_name": name, "parsed_qty": "", "parsed_unit": "",
                "parsed_grams": "NOT_QUANTIFIED", "is_quantified": False
            }

    # Extract quantity
    m = re.match(r"^\s*(\d+(?:\s+\d+/\d+|\.\d+|/\d+)?(?:\s*(?:-|to|–)\s*\d+(?:\.\d+|/\d+)?)?)\s*(.*)$", line_clean)
    if not m:
        if "pinch" in line_lower:
            return {"parsed_name": line_clean.replace("pinch", "").strip(), "parsed_qty": "1", "parsed_unit": "pinch", "parsed_grams": 0.5, "is_quantified": True}
        return {"parsed_name": line_clean, "parsed_qty": "", "parsed_unit": "", "parsed_grams": "NOT_QUANTIFIED", "is_quantified": False}

    qty_raw = m.group(1).strip()
    rem = m.group(2).strip()

    # Parse numeric value
    def parse_qty_safe(s):
        s = s.strip()
        m_range = re.match(r"^(\d+(?:/\d+|\.\d+)?)\s*(?:-|to|–)\s*(\d+(?:/\d+|\.\d+)?)$", s)
        if m_range:
            v1 = parse_qty_safe(m_range.group(1))
            v2 = parse_qty_safe(m_range.group(2))
            return (v1 + v2) / 2.0
        m_mixed = re.match(r"^(\d+)\s+(\d+)/(\d+)$", s)
        if m_mixed:
            return float(m_mixed.group(1)) + float(m_mixed.group(2)) / float(m_mixed.group(3))
        m_frac = re.match(r"^(\d+)/(\d+)$", s)
        if m_frac:
            return float(m_frac.group(1)) / float(m_frac.group(2))
        try:
            return float(s)
        except Exception:
            return 1.0

    qty_val = parse_qty_safe(qty_raw)

    # Extract unit and name
    unit_m = re.match(r"^(tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|cups?|katori|grams?|gms?|g|kg|ml|pinchs?|pinches|inch|inches|cubes?|pieces?|cloves?|nos?|medium|small|large)\b\.?\s*(.*)$", rem, re.IGNORECASE)
    if unit_m:
        unit = unit_m.group(1).lower().strip()
        name = unit_m.group(2).strip()
    else:
        unit = "piece"
        name = rem

    clean_name = re.sub(r"^of\s+", "", name).strip()
    clean_name = re.sub(r"\(.*?\)", "", clean_name).strip()
    clean_name = re.sub(r",.*$", "", clean_name).strip()
    name_lower = clean_name.lower()

    # Calculate grams using contextual density map
    grams = None
    for (ing_key, u_key), factor in INGREDIENT_DENSITY_MAP.items():
        if ing_key in name_lower and (u_key == unit or (u_key in ["medium", "small", "large"] and u_key in line_lower)):
            grams = round(qty_val * factor, 2)
            break

    if grams is None:
        if unit in STANDARD_UNITS:
            grams = round(qty_val * STANDARD_UNITS[unit], 2)
        elif "cube" in unit or "cube" in line_lower:
            grams = round(qty_val * 15.0, 2)
        elif "clove" in name_lower or "clove" in unit:
            grams = round(qty_val * 0.1, 2)
        elif "inch" in unit:
            grams = round(qty_val * 6.0, 2)
        else:
            grams = round(qty_val * 50.0, 2)  # default medium vegetable/piece

    return {
        "parsed_name": clean_name if clean_name else name,
        "parsed_qty": str(round(qty_val, 2)),
        "parsed_unit": unit,
        "parsed_grams": grams,
        "is_quantified": True
    }

def main():
    in_path = "dryrun/D2_normaliser/d2_sample_200.csv"
    out_path = "dryrun/D2_normaliser/d2_parsed_llm.csv"

    with open(in_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    rows = []
    for r in reader:
        p = parse_llm_style(r["line"])
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

    print(f"LLM-assisted parser completed: {len(rows)} rows -> {out_path}")

if __name__ == "__main__":
    main()
