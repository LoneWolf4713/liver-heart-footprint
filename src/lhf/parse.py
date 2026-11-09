"""Ingredient line parser for Phase 1 core engine (SPEC §4)."""

import html
import re

UNICODE_FRAC = {
    "½": 1 / 2,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "¼": 1 / 4,
    "¾": 3 / 4,
    "⅛": 1 / 8,
    "⅜": 3 / 8,
    "⅝": 5 / 8,
    "⅞": 7 / 8,
}

WORD_NUMS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

NUM_ATOM = (
    r"(?:\d+\s*-\s*\d+/\d+|\d+\s*-\s*[½⅓⅔¼¾⅛⅜⅝⅞]|\d+\s+\d+/\d+|\d+\s*[½⅓⅔¼¾⅛⅜⅝⅞]|"
    r"[½⅓⅔¼¾⅛⅜⅝⅞]|\d+/\d+|\d+(?:\.\d+)?)"
)

RANGE_PAT = re.compile(rf"^({NUM_ATOM})\s*(?:to|–|—|-)\s*({NUM_ATOM})\b", re.IGNORECASE)
SINGLE_PAT = re.compile(rf"^({NUM_ATOM})\b", re.IGNORECASE)

GRAM_PAT = re.compile(
    r"(?:^|[(/,\s])([0-9½⅓⅔¼¾⅛⅜⅝⅞][0-9½⅓⅔¼¾⅛⅜⅝⅞./\s\-–—&to]*?)\s*(kg|kilograms?|किलोग्राम|किग्रा|g|gms?|grams?|ग्राम)\b",
    re.IGNORECASE,
)
ML_PAT = re.compile(
    r"(?:^|[(/,\s])([0-9½⅓⅔¼¾⅛⅜⅝⅞][0-9½⅓⅔¼¾⅛⅜⅝⅞./\s\-–—&to]*?)\s*(ml|millilitres?|milliliters?|mls?|मिलीलीटर|मिली|l|litres?|liters?|लीटर)\b",
    re.IGNORECASE,
)

UNIT_DEFS = [
    ("tbsp", re.compile(r"^(?:tablespoons?|tbsps?|tbs|टेबल\s*स्पून|बड़ा\s*चम्मच|बड़े\s*चम्मच)\b", re.I)),
    ("tsp", re.compile(r"^(?:teaspoons?|tsps?|टी\s*स्पून|छोटा\s*चम्मच|छोटे\s*चम्मच)\b", re.I)),
    ("cup", re.compile(r"^(?:cups?|C|कप)\b", re.I)),
    ("kg", re.compile(r"^(?:kilograms?|kgs?|किलोग्राम|किग्रा)\b", re.I)),
    ("mg", re.compile(r"^(?:milligrams?|mgs?|मिलीग्राम)\b", re.I)),
    ("g", re.compile(r"^(?:grams?|gms?|g|ग्राम)\b", re.I)),
    ("ml", re.compile(r"^(?:millilitres?|milliliters?|mls?|मिलीलीटर|मिली)\b", re.I)),
    ("l", re.compile(r"^(?:litres?|liters?|l|लीटर)\b", re.I)),
    ("oz", re.compile(r"^(?:ounces?|oz)\b", re.I)),
    ("lb", re.compile(r"^(?:pounds?|lbs?)\b", re.I)),
    ("pinch", re.compile(r"^(?:generous\s+pinch|a\s+pinch|pinches|pinch|चुटकी\s*भर|चुटकी)\b", re.I)),
    ("dash", re.compile(r"^(?:dashes|dash)\b", re.I)),
    ("clove", re.compile(r"^(?:cloves?)\b", re.I)),
    ("inch", re.compile(r'^(?:inches|inch|\"|इंच)\b', re.I)),
    ("cm", re.compile(r"^(?:centimeters?|centimetres?|cms?|cm|सेमी|सेंटीमीटर)\b", re.I)),
    ("sprig", re.compile(r"^(?:sprigs?)\b", re.I)),
    ("stick", re.compile(r"^(?:sticks?)\b", re.I)),
    ("strand", re.compile(r"^(?:strands?)\b", re.I)),
    ("leaf", re.compile(r"^(?:leaves|leaf)\b", re.I)),
    ("bunch", re.compile(r"^(?:bunches|bunch)\b", re.I)),
    ("cube", re.compile(r"^(?:cubes?)\b", re.I)),
    ("slice", re.compile(r"^(?:slices?)\b", re.I)),
    ("floret", re.compile(r"^(?:florets?)\b", re.I)),
    ("ball", re.compile(r"^(?:balls?)\b", re.I)),
    ("blade", re.compile(r"^(?:blades?)\b", re.I)),
    ("pat", re.compile(r"^(?:pats?)\b", re.I)),
    ("piece", re.compile(r"^(?:pieces?|piece|nos?\.?|number|whole|pods?|bags?|can|cans|tin|tins|bottle|bottles|टुकड़ा|टुकड़े)\b", re.I)),
]

MASS_VOLUME_UNITS = {"g", "kg", "mg", "ml", "l", "oz", "lb"}
SIZE_PAT = re.compile(r"^(small|medium-sized|medium-size|medium|med|large|big)\b", re.I)


def _strip_brackets(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _is_plain_water(s_no_brackets: str) -> bool:
    low = s_no_brackets.lower().strip()
    if re.search(r"\b(?:rose|kewra|coconut|rice|dal)\s+water\b", low):
        return False
    if re.search(r"\bmilk\s+or\s+water\b", low):
        return False
    return bool(re.search(r"\b(?:water|ice(?:\s+cubes?)?|पानी|बर्फ)\b", low))


def _parse_num_val(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    m_mix = re.match(r"^(\d+)-(\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])$", s)
    if m_mix:
        w = float(m_mix.group(1))
        f_str = m_mix.group(2)
        if f_str in UNICODE_FRAC:
            f_val = UNICODE_FRAC[f_str]
        else:
            parts = f_str.split("/")
            f_val = float(parts[0]) / float(parts[1])
        return w + f_val
    m_rng = re.match(r"^(.+?)\s*(?:to|–|—|-)\s*(.+)$", s)
    if m_rng:
        v1 = _parse_num_val(m_rng.group(1))
        v2 = _parse_num_val(m_rng.group(2))
        if v1 is not None and v2 is not None:
            return (v1 + v2) / 2
    if s in UNICODE_FRAC:
        return UNICODE_FRAC[s]
    m = re.match(r"^(\d+)(?:\s*(?:&|and)?\s*|\-)?([½⅓⅔¼¾⅛⅜⅝⅞])$", s)
    if m:
        return float(m.group(1)) + UNICODE_FRAC[m.group(2)]
    m = re.match(r"^(\d+)(?:\s+(?:&|and\s+)?|\-)(\d+)\s*/\s*(\d+)$", s)
    if m:
        return float(m.group(1)) + float(m.group(2)) / float(m.group(3))
    m = re.match(r"^(\d+)\s*/\s*(\d+)$", s)
    if m:
        return float(m.group(1)) / float(m.group(2))
    try:
        return float(s)
    except ValueError:
        return None


def parse_line(text: str) -> dict:
    """Parse a single recipe ingredient line into structured attributes (SPEC §4)."""
    raw = text
    optional = bool(re.search(r"\boptional\b", text, re.I))

    s = html.unescape(text)
    s = s.replace("\xa0", " ").replace("\u200b", " ").replace("\ufeff", " ")
    s = s.translate(str.maketrans("०१२३४५६७८९", "0123456789"))

    # Stated grams / ml anywhere in the line
    sg = None
    mg = GRAM_PAT.search(s)
    if mg:
        val = _parse_num_val(mg.group(1))
        if val is not None:
            u = mg.group(2).lower()
            sg = val * 1000 if u in ("kg", "kilogram", "kilograms", "किलोग्राम", "किग्रा") else val

    sml = None
    if sg is None:
        mml = ML_PAT.search(s)
        if mml:
            val = _parse_num_val(mml.group(1))
            if val is not None:
                u = mml.group(2).lower()
                sml = val * 1000 if u in ("l", "litre", "litres", "liter", "liters", "लीटर") else val

    # Working string without bracketed notes for main fields
    s_clean = _strip_brackets(s)
    water_line = _is_plain_water(s_clean)

    # Word numbers at start
    m_w = re.match(r"^(one|two|three|four|five|six|seven|eight|nine|ten)\b", s_clean, re.I)
    if m_w:
        s_clean = str(WORD_NUMS[m_w.group(1).lower()]) + s_clean[m_w.end():]

    # Check pinch / dash at start without number
    m_pinch = re.match(r"^(?:generous\s+pinch|a\s+pinch|pinch|चुटकी\s*भर|चुटकी)\b", s_clean, re.I)
    qty = None
    qty_min = None
    qty_max = None
    unit = None
    size = None
    rem = s_clean

    if m_pinch:
        qty = float(1)
        qty_min = float(1)
        qty_max = float(1)
        unit = "pinch"
        rem = s_clean[m_pinch.end():].strip()
    else:
        # Check mixed fraction first like 2-1/2
        m_mix = re.match(r"^(\d+)-(\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])\b", s_clean)
        if m_mix:
            w = float(m_mix.group(1))
            f_str = m_mix.group(2)
            if f_str in UNICODE_FRAC:
                f_val = UNICODE_FRAC[f_str]
            else:
                parts = f_str.split("/")
                f_val = float(parts[0]) / float(parts[1])
            qty = w + f_val
            qty_min = qty
            qty_max = qty
            rem = s_clean[m_mix.end():].strip()
        else:
            m_rng = RANGE_PAT.match(s_clean)
            if m_rng:
                v1 = _parse_num_val(m_rng.group(1))
                v2 = _parse_num_val(m_rng.group(2))
                if v1 is not None and v2 is not None:
                    qty_min = min(v1, v2)
                    qty_max = max(v1, v2)
                    qty = (v1 + v2) / 2
                    rem = s_clean[m_rng.end():].strip()
            else:
                m_single = SINGLE_PAT.match(s_clean)
                if m_single:
                    v = _parse_num_val(m_single.group(1))
                    if v is not None:
                        qty = v
                        qty_min = v
                        qty_max = v
                        rem = s_clean[m_single.end():].strip()

    # Parse size and unit if quantity was found
    if qty is not None and unit is None:
        # Check size right after quantity
        ms = SIZE_PAT.match(rem)
        if ms:
            sz_str = ms.group(1).lower()
            if sz_str == "small":
                size = "small"
            elif sz_str in ("medium", "medium-sized", "medium-size", "med"):
                size = "medium"
            elif sz_str in ("large", "big"):
                size = "large"
            rem = rem[ms.end():].strip()

        # Check unit right after quantity or size
        matched_unit = None
        for u_name, u_re in UNIT_DEFS:
            mu = u_re.match(rem)
            if mu:
                matched_unit = (u_name, mu.group(0), mu.end())
                break

        if matched_unit:
            u_name, u_str, u_end = matched_unit
            rem = rem[u_end:].strip()
            if size is None:
                ms2 = SIZE_PAT.match(rem)
                if ms2:
                    sz_str = ms2.group(1).lower()
                    if sz_str == "small":
                        size = "small"
                    elif sz_str in ("medium", "medium-sized", "medium-size", "med"):
                        size = "medium"
                    elif sz_str in ("large", "big"):
                        size = "large"
                    rem = rem[ms2.end():].strip()

            has_garlic = "garlic" in s.lower()
            if u_name == "clove":
                if has_garlic:
                    unit = "clove"
                else:
                    unit = "piece"
                    rem = u_str + " " + rem
            elif u_name == "piece" and u_str.lower().startswith("pod") and has_garlic:
                unit = "clove"
            elif u_name == "leaf":
                if re.search(r"\b(bay|curry|methi|fenugreek|coriander|cilantro|mint)\b", s.lower()):
                    unit = "piece"
                    rem = u_str + " " + rem
                else:
                    unit = "leaf"
            else:
                unit = u_name
        else:
            # Check for garlic cloves / garlic pods where garlic precedes the unit word
            mg_pod = re.search(r"\bgarlic\s+(?:pods?|cloves?)\b", rem, re.I)
            if mg_pod:
                unit = "clove"
                rem = (rem[:mg_pod.start()] + " garlic " + rem[mg_pod.end():]).strip()
            else:
                mb = re.search(r"\b(small|medium|large|big)?\s*(bunches|bunch)\b", rem, re.I)
                if mb:
                    unit = "bunch"
                    if mb.group(1):
                        sz_str = mb.group(1).lower()
                        if sz_str == "small":
                            size = "small"
                        elif sz_str in ("medium", "medium-sized", "medium-size", "med"):
                            size = "medium"
                        elif sz_str in ("large", "big"):
                            size = "large"
                    rem = (rem[:mb.start()] + " " + rem[mb.end():]).strip()
                else:
                    unit = "piece"

        if unit in MASS_VOLUME_UNITS:
            size = None

    # Determine status
    if water_line:
        status = "WATER"
    elif qty is None:
        status = "UNQUANTIFIED"
    else:
        status = "QUANTIFIED"

    if status == "UNQUANTIFIED":
        qty = None
        qty_min = None
        qty_max = None
        unit = None
        size = None
        sg = None
        sml = None
    elif status == "WATER" and qty is None:
        unit = None
        size = None
        sg = None
        sml = None

    # Name cleanup
    name_clean = rem
    name_clean = re.sub(
        r"/(?:\s*\d+[\d\s./½¼¾⅓⅔⅛&to\-]*\s*(?:kg|kilograms?|g|gms?|grams?|ml|l)\b)",
        " ",
        name_clean,
        flags=re.I,
    )
    name_clean = re.sub(
        r"\bor\s+\d+[\d\s./½¼¾⅓⅔⅛&to\-]*\s*(?:kg|kilograms?|g|gms?|grams?|ml|l)\b",
        " ",
        name_clean,
        flags=re.I,
    )
    name_clean = re.sub(r"^[,\-–—:\.\s/]+|[,\-–—:\.\s/]+$", "", name_clean)
    name = re.sub(r"\s+", " ", name_clean).strip().lower()
    if not name:
        name = _strip_brackets(s).strip().lower()

    return {
        "raw": raw,
        "status": status,
        "qty": qty,
        "qty_min": qty_min,
        "qty_max": qty_max,
        "unit": unit,
        "size": size,
        "stated_g": sg,
        "stated_ml": sml,
        "optional": optional,
        "name": name,
    }
