#!/usr/bin/env python3
"""
D2 Gold Labeller (Independent).
Blind to parser code. Uses cited conversion standards:
- tsp: 5 ml, tbsp: 15 ml, cup: 240 ml (sensitivity test 200 ml)
- katori: 150 ml (ICMR-NIN standard)
- oil: 0.92 g/ml, ghee: 0.91 g/ml, butter: 0.96 g/ml
- granulated sugar: 0.85 g/ml (1 cup=200g, 1 tbsp=12.5g, 1 tsp=4.2g)
- flours: maida 1 cup=125g, atta 1 cup=120g, besan 1 cup=100g, poha 1 cup=60g
- pieces (INDB Units.xlsx): onion med=80g, tomato med=90g, potato med=120g, chili=4g, clove=3g, ginger 1 inch=6g
- vague/to taste/for frying: gold = "NOT_QUANTIFIED"
"""

import csv
import os
import re

DENSITIES = {
    "oil": 0.92,
    "ghee": 0.91,
    "butter": 0.96,
    "cream": 1.00,
    "fresh cream": 1.00,
    "heavy cream": 1.00,
    "malai": 1.00,
    "milk": 1.03,
    "curd": 1.04,
    "yogurt": 1.04,
    "water": 1.00
}

CUP_GRAMS = {
    "sugar": 200.0,
    "jaggery": 150.0,
    "maida": 125.0,
    "all purpose flour": 125.0,
    "atta": 120.0,
    "whole wheat flour": 120.0,
    "besan": 100.0,
    "gram flour": 100.0,
    "poha": 60.0,
    "flattened rice": 60.0,
    "rice": 185.0,
    "basmati rice": 185.0,
    "paneer": 150.0,
    "chicken": 140.0,
    "onion": 160.0,
    "tomato": 180.0,
    "carrot": 110.0,
    "urad dal": 200.0,
    "chana": 180.0,
    "chickpeas": 180.0
}

PIECE_WEIGHTS = {
    "onion": 80.0,
    "tomato": 90.0,
    "potato": 120.0,
    "carrot": 70.0,
    "green chilli": 4.0,
    "green chili": 4.0,
    "chilli": 4.0,
    "chili": 4.0,
    "garlic": 3.0,
    "ginger": 6.0,
    "bay leaf": 0.5,
    "clove": 0.1,
    "cardamom": 0.3,
    "cinnamon": 1.0
}

def parse_num(s):
    s = s.strip()
    # Mixed fraction e.g. "1 1/2"
    m_mixed = re.match(r"^(\d+)\s+(\d+)/(\d+)$", s)
    if m_mixed:
        return float(m_mixed.group(1)) + float(m_mixed.group(2)) / float(m_mixed.group(3))
    # Simple fraction e.g. "1/2", "3/4"
    m_frac = re.match(r"^(\d+)/(\d+)$", s)
    if m_frac:
        return float(m_frac.group(1)) / float(m_frac.group(2))
    # Range e.g. "1-2", "2 to 3"
    m_range = re.match(r"^(\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(\d+(?:\.\d+)?)$", s)
    if m_range:
        return (float(m_range.group(1)) + float(m_range.group(2))) / 2.0
    try:
        return float(s)
    except ValueError:
        return None

def label_ingredient(line):
    line_clean = line.strip()
    line_lower = line_clean.lower()

    # 1. Check for unquantified / vague expressions
    vague_markers = ["to taste", "as required", "as needed", "for deep frying", "for frying", "few sprigs", "some", "optional"]
    if any(vm in line_lower for vm in vague_markers):
        if not re.search(r"^\s*\d+", line_clean):
            # Extract ingredient name
            name = re.sub(r"\b(to taste|as required|as needed|for frying|for deep frying|pinch of|few drops|optional)\b", "", line_lower).strip()
            name = re.sub(r"[\(\),]", "", name).strip()
            return {
                "name": name, "qty": "", "unit": "",
                "grams": "NOT_QUANTIFIED", "is_quantified": False,
                "reasoning": f"Unquantified vague qualifier in '{line_clean}'"
            }

    # 2. Extract leading number/fraction/range
    num_match = re.match(r"^\s*(\d+(?:\s+\d+/\d+|\.\d+|/\d+)?(?:\s*(?:-|to|–)\s*\d+(?:\.\d+|/\d+)?)?)\s*(.*)$", line_clean)
    if not num_match:
        # Check if pinch or salt
        if "pinch" in line_lower:
            return {
                "name": line_clean.replace("pinch of", "").replace("pinch", "").strip(),
                "qty": "1", "unit": "pinch", "grams": 0.5, "is_quantified": True,
                "reasoning": "Standard 1 pinch = 0.5g"
            }
        return {
            "name": line_clean, "qty": "", "unit": "",
            "grams": "NOT_QUANTIFIED", "is_quantified": False,
            "reasoning": "No leading quantity or standard measure found"
        }

    qty_raw = num_match.group(1).strip()
    rem = num_match.group(2).strip()

    qty_val = parse_num(qty_raw)
    if qty_val is None:
        return {
            "name": rem, "qty": qty_raw, "unit": "",
            "grams": "NOT_QUANTIFIED", "is_quantified": False,
            "reasoning": f"Unparseable quantity '{qty_raw}'"
        }

    # 3. Detect Unit
    unit_match = re.match(r"^(tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|cups?|katori|grams?|gms?|g|kg|ml|liters?|litres?|pinchs?|pinches|inch|inches|cubes?|pieces?|cloves?|nos?|medium|small|large)\b\.?\s*(.*)$", rem, re.IGNORECASE)
    
    if unit_match:
        unit_raw = unit_match.group(1).lower().strip()
        name_raw = unit_match.group(2).strip()
    else:
        unit_raw = "piece"
        name_raw = rem

    # Clean name
    clean_name = re.sub(r"^of\s+", "", name_raw).strip()
    clean_name = re.sub(r"\(.*?\)", "", clean_name).strip()
    clean_name = re.sub(r",.*$", "", clean_name).strip()
    clean_name_lower = clean_name.lower()

    # 4. Compute Grams
    grams = None
    reasoning = ""

    # Unit: grams / kg / ml
    if unit_raw in ["g", "gm", "gms", "gram", "grams"]:
        grams = round(qty_val, 2)
        reasoning = f"Direct metric weight: {qty_val} g"
    elif unit_raw in ["kg"]:
        grams = round(qty_val * 1000.0, 2)
        reasoning = f"Metric kg to g: {qty_val} * 1000 = {grams} g"
    elif unit_raw in ["ml"]:
        # Find density
        d = 1.0
        for k, v in DENSITIES.items():
            if k in clean_name_lower:
                d = v
                break
        grams = round(qty_val * d, 2)
        reasoning = f"Volume {qty_val} ml * density {d} g/ml = {grams} g"

    # Unit: tsp (5 ml)
    elif unit_raw in ["tsp", "teaspoon", "teaspoons"]:
        ml = qty_val * 5.0
        d = 1.0
        for k, v in DENSITIES.items():
            if k in clean_name_lower:
                d = v
                break
        if "sugar" in clean_name_lower:
            grams = round(qty_val * 4.2, 2)
            reasoning = f"{qty_val} tsp granulated sugar * 4.2g/tsp = {grams} g"
        elif "salt" in clean_name_lower:
            grams = round(qty_val * 6.0, 2)
            reasoning = f"{qty_val} tsp table salt * 6.0g/tsp = {grams} g"
        elif "chilli" in clean_name_lower or "chili" in clean_name_lower or "masala" in clean_name_lower or "powder" in clean_name_lower:
            grams = round(qty_val * 3.0, 2)
            reasoning = f"{qty_val} tsp spice powder * 3.0g/tsp = {grams} g"
        else:
            grams = round(ml * d, 2)
            reasoning = f"{qty_val} tsp = {ml} ml * density {d} = {grams} g"

    # Unit: tbsp (15 ml)
    elif unit_raw in ["tbsp", "tablespoon", "tablespoons"]:
        ml = qty_val * 15.0
        d = 1.0
        for k, v in DENSITIES.items():
            if k in clean_name_lower:
                d = v
                break
        if "sugar" in clean_name_lower:
            grams = round(qty_val * 12.5, 2)
            reasoning = f"{qty_val} tbsp granulated sugar * 12.5g/tbsp = {grams} g"
        elif "butter" in clean_name_lower:
            grams = round(qty_val * 14.2, 2)
            reasoning = f"{qty_val} tbsp butter * 14.2g/tbsp = {grams} g"
        elif "oil" in clean_name_lower:
            grams = round(qty_val * 13.8, 2)
            reasoning = f"{qty_val} tbsp oil * 13.8g/tbsp = {grams} g"
        elif "ghee" in clean_name_lower:
            grams = round(qty_val * 13.65, 2)
            reasoning = f"{qty_val} tbsp ghee * 13.65g/tbsp = {grams} g"
        else:
            grams = round(ml * d, 2)
            reasoning = f"{qty_val} tbsp = {ml} ml * density {d} = {grams} g"

    # Unit: cup (240 ml)
    elif unit_raw in ["cup", "cups"]:
        factor = None
        for k, v in CUP_GRAMS.items():
            if k in clean_name_lower:
                factor = v
                break
        if factor is not None:
            grams = round(qty_val * factor, 2)
            reasoning = f"{qty_val} cup * {factor} g/cup ({clean_name}) = {grams} g"
        else:
            # Default liquid cup = 240g
            grams = round(qty_val * 240.0, 2)
            reasoning = f"{qty_val} cup * default 240 g/cup = {grams} g"

    # Unit: katori (150 ml)
    elif unit_raw in ["katori"]:
        factor = 150.0
        grams = round(qty_val * factor, 2)
        reasoning = f"{qty_val} katori * NIN standard 150g = {grams} g"

    # Unit: pinch
    elif unit_raw in ["pinch", "pinches"]:
        grams = round(qty_val * 0.5, 2)
        reasoning = f"{qty_val} pinch * 0.5g = {grams} g"

    # Unit: piece / count
    else:
        pw = None
        for k, v in PIECE_WEIGHTS.items():
            if k in clean_name_lower:
                pw = v
                break
        if pw is not None:
            grams = round(qty_val * pw, 2)
            reasoning = f"{qty_val} count * INDB piece weight {pw}g = {grams} g"
        else:
            # If item is like paneer cubes
            if "paneer" in clean_name_lower and ("cube" in unit_raw or "cube" in line_lower):
                grams = round(qty_val * 15.0, 2)
                reasoning = f"{qty_val} paneer cubes * 15g/cube = {grams} g"
            elif "clove" in clean_name_lower or "clove" in unit_raw:
                grams = round(qty_val * 0.1, 2)
                reasoning = f"{qty_val} cloves * 0.1g = {grams} g"
            else:
                grams = round(qty_val * 20.0, 2)
                reasoning = f"{qty_val} default item * estimated 20g = {grams} g"

    return {
        "name": clean_name if clean_name else name_raw,
        "qty": str(qty_val),
        "unit": unit_raw,
        "grams": grams,
        "is_quantified": True,
        "reasoning": reasoning
    }

def main():
    in_path = "dryrun/D2_normaliser/d2_sample_200.csv"
    out_path = "dryrun/D2_normaliser/d2_gold_labels.csv"

    with open(in_path, encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    gold_rows = []
    quant_count = 0
    not_quant_count = 0

    for r in reader:
        res = label_ingredient(r["line"])
        gold_rows.append({
            "sample_id": r["sample_id"],
            "stratum": r["stratum"],
            "line": r["line"],
            "gold_name": res["name"],
            "gold_qty": res["qty"],
            "gold_unit": res["unit"],
            "gold_grams": res["grams"],
            "is_quantified": res["is_quantified"],
            "reasoning": res["reasoning"]
        })
        if res["is_quantified"]:
            quant_count += 1
        else:
            not_quant_count += 1

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sample_id", "stratum", "line", "gold_name", "gold_qty", "gold_unit",
            "gold_grams", "is_quantified", "reasoning"
        ])
        writer.writeheader()
        for g in gold_rows:
            writer.writerow(g)

    print(f"D2 Gold Labelling complete: {len(gold_rows)} rows labelled ({quant_count} quantified, {not_quant_count} NOT_QUANTIFIED) -> {out_path}")

if __name__ == "__main__":
    main()
