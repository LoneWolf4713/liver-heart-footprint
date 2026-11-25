"""Ingredient line parser for Phase 1 core engine (SPEC §4)."""

import html
import re
import unicodedata

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

BOUNDARY = r"""(?=$|[\s,.\-–—:;/\(\)\[\]\{\}"'])"""
NUM_BOUNDARY = r"""(?=$|[a-zA-Z\u0900-\u097f\s,.\-–—:;/\(\)\[\]\{\}"'])"""

NUM_ATOM = (
    r"(?:\d+\s*(?:-|&|and)\s*(?:\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])|"
    r"\d+\s+\d+/\d+|\d+\s*[½⅓⅔¼¾⅛⅜⅝⅞]|"
    r"[½⅓⅔¼¾⅛⅜⅝⅞]|\d+/\d+|(?:\d+(?:\.\d+)?|\.\d+))"
)

RANGE_PAT = re.compile(rf"^({NUM_ATOM})\s*(to|–|—|-)\s*({NUM_ATOM}){NUM_BOUNDARY}", re.IGNORECASE)
SINGLE_PAT = re.compile(rf"^({NUM_ATOM}){NUM_BOUNDARY}", re.IGNORECASE)

GRAM_PAT = re.compile(
    rf"(?:^|[(/,\s])([0-9½⅓⅔¼¾⅛⅜⅝⅞.][0-9½⅓⅔¼¾⅛⅜⅝⅞./\s\-–—&to]*?)\s*(kg|kilograms?|किलोग्राम|किग्रा|g|gms?|grams?|ग्राम){BOUNDARY}",
    re.IGNORECASE,
)
ML_PAT = re.compile(
    rf"(?:^|[(/,\s])([0-9½⅓⅔¼¾⅛⅜⅝⅞.][0-9½⅓⅔¼¾⅛⅜⅝⅞./\s\-–—&to]*?)\s*(ml|millilitres?|milliliters?|mls?|मिलीलीटर|मिली|l|litres?|liters?|लीटर){BOUNDARY}",
    re.IGNORECASE,
)

UNIT_DEFS = [
    ("tbsp", re.compile(rf"^(?:tablespoons?|tbsps?|tbs|टेबल\s*स्पून|ब[डड़]\u093c?[ाे]?\s*चम्मच){BOUNDARY}", re.I)),
    ("tsp", re.compile(rf"^(?:teaspoons?|tsps?|टी\s*स्पून|छोटा\s*चम्मच|छोटे\s*चम्मच){BOUNDARY}", re.I)),
    ("cup", re.compile(rf"^(?:cups?|C|कप){BOUNDARY}", re.I)),
    ("kg", re.compile(rf"^(?:kilograms?|kgs?|किलोग्राम|किग्रा){BOUNDARY}", re.I)),
    ("mg", re.compile(rf"^(?:milligrams?|mgs?|मिलीग्राम){BOUNDARY}", re.I)),
    ("g", re.compile(rf"^(?:grams?|gms?|g|ग्राम){BOUNDARY}", re.I)),
    ("ml", re.compile(rf"^(?:millilitres?|milliliters?|mls?|मिलीलीटर|मिली){BOUNDARY}", re.I)),
    ("l", re.compile(rf"^(?:litres?|liters?|l|लीटर){BOUNDARY}", re.I)),
    ("oz", re.compile(rf"^(?:ounces?|oz){BOUNDARY}", re.I)),
    ("lb", re.compile(rf"^(?:pounds?|lbs?){BOUNDARY}", re.I)),
    ("pinch", re.compile(rf"^(?:generous\s+pinch|a\s+pinch|pinches|pinch|चुटकी\s*भर|चुटकी){BOUNDARY}", re.I)),
    ("dash", re.compile(rf"^(?:dashes|dash){BOUNDARY}", re.I)),
    ("clove", re.compile(rf"^(?:cloves?){BOUNDARY}", re.I)),
    ("inch", re.compile(rf'^(?:inches|inch|\"|इंच){BOUNDARY}', re.I)),
    ("cm", re.compile(rf"^(?:centimeters?|centimetres?|cms?|cm|सेमी|सेंटीमीटर){BOUNDARY}", re.I)),
    ("sprig", re.compile(rf"^(?:sprigs?){BOUNDARY}", re.I)),
    ("stick", re.compile(rf"^(?:sticks?){BOUNDARY}", re.I)),
    ("strand", re.compile(rf"^(?:strands?){BOUNDARY}", re.I)),
    ("leaf", re.compile(rf"^(?:leaves|leaf){BOUNDARY}", re.I)),
    ("bunch", re.compile(rf"^(?:bunches|bunch){BOUNDARY}", re.I)),
    ("cube", re.compile(rf"^(?:cubes?){BOUNDARY}", re.I)),
    ("slice", re.compile(rf"^(?:slices?){BOUNDARY}", re.I)),
    ("floret", re.compile(rf"^(?:florets?){BOUNDARY}", re.I)),
    ("ball", re.compile(rf"^(?:balls?){BOUNDARY}", re.I)),
    ("blade", re.compile(rf"^(?:blades?){BOUNDARY}", re.I)),
    ("pat", re.compile(rf"^(?:pats?){BOUNDARY}", re.I)),
    ("piece", re.compile(rf"^(?:pieces?|piece|nos?\.?|number|whole|pods?|bags?|can|cans|tin|tins|bottle|bottles|टुक[डड़]\u093c?[ाे]?){BOUNDARY}", re.I)),
]

MASS_VOLUME_UNITS = {"g", "kg", "mg", "ml", "l", "oz", "lb"}
SIZE_PAT = re.compile(r"^(small|medium-sized|medium-size|medium|med|large|big)\b", re.I)

WATER_ADJ = (
    r"(?:warm|cold|chilled|cool|hot|boiling|lukewarm|filter|filtered|"
    r"clean|tap|fresh|plain|crushed|a\s+little|some|enough|"
    r"ठंडा|ठंडे|ठंडी|गर्म|गुनगुना|गुनगुने|गुनगुनी|साफ|ताज़ा|ताजा)"
)

COMPOUND_WATER_ICE = re.compile(
    r"\b(?:"
    r"pani\s*p[ou]{1,2}r[iy]|panipuri|पानी\s*पूरी|पानीपूरी|"
    r"water\s*chestnuts?|"
    r"water\s*cress|watercress|"
    r"water\s*spinach|"
    r"water\s*melons?|watermelons?|"
    r"water\s*caltrops?|"
    r"ice\s*cream[s]?|आइस\s*क्रीम|"
    r"ice\s*golas?|"
    r"ice\s*pops?|"
    r"ice\s*cand(?:y|ies)|"
    r"ice\s*loll(?:y|ies)|"
    r"ice\s*apples?|"
    r"tamarind\s*water|"
    r"rose\s*water|"
    r"kewra\s*water|"
    r"coconut\s*water|"
    r"rice\s*water|"
    r"dal\s*water|"
    r"tonic\s*water|"
    r"soda\s*water"
    r")\b",
    re.IGNORECASE,
)

PLAIN_WATER_PAT = re.compile(
    rf"^(?:{WATER_ADJ}\s+)*(?:water|ice(?:\s+cubes?)?|pani|paani|पानी|बर्फ){BOUNDARY}",
    re.IGNORECASE,
)


def _strip_brackets(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _is_plain_water(s: str) -> bool:
    if not s:
        return False
    low = s.strip().lower()
    if COMPOUND_WATER_ICE.search(low):
        return False
    if re.search(r"\b(?:milk|curd|yogurt|dahi)\b", low):
        return False
    return bool(PLAIN_WATER_PAT.search(low))


def _parse_num_val(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    m_mix = re.match(r"^(\d+)\s*(?:-|&|and)\s*(\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])$", s, re.I)
    if m_mix:
        w = float(m_mix.group(1))
        f_str = m_mix.group(2)
        if f_str in UNICODE_FRAC:
            f_val = UNICODE_FRAC[f_str]
        else:
            parts = f_str.split("/")
            denom = float(parts[1])
            if denom == 0:
                return None
            f_val = float(parts[0]) / denom
        return w + f_val
    m_rng = re.match(r"^(.+?)\s*(?:to|–|—|-)\s*(.+)$", s)
    if m_rng:
        v1 = _parse_num_val(m_rng.group(1))
        v2 = _parse_num_val(m_rng.group(2))
        if v1 is not None and v2 is not None:
            return (v1 + v2) / 2
    if s in UNICODE_FRAC:
        return UNICODE_FRAC[s]
    m = re.match(r"^(\d+)(?:\s*(?:&|and)?\s*|\-)?([½⅓⅔¼¾⅛⅜⅝⅞])$", s, re.I)
    if m:
        return float(m.group(1)) + UNICODE_FRAC[m.group(2)]
    m = re.match(r"^(\d+)(?:\s+(?:&|and\s+)?|\-)(\d+)\s*/\s*(\d+)$", s, re.I)
    if m:
        denom = float(m.group(3))
        if denom == 0:
            return None
        return float(m.group(1)) + float(m.group(2)) / denom
    m = re.match(r"^(\d+)\s*/\s*(\d+)$", s)
    if m:
        denom = float(m.group(2))
        if denom == 0:
            return None
        return float(m.group(1)) / denom
    try:
        return float(s)
    except ValueError:
        return None


def parse_line(text: str) -> dict:
    """Parse a single recipe ingredient line into structured attributes (SPEC §4)."""
    raw = text
    optional = bool(re.search(r"\boptional\b", text, re.I))

    s = unicodedata.normalize("NFC", text)
    s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\u200b", " ").replace("\ufeff", " ")
    s = s.translate(str.maketrans("०१२३४५६७८९", "0123456789"))

    # Stated grams / ml anywhere in the line
    sg = None
    mg = GRAM_PAT.search(s)
    if mg:
        val = _parse_num_val(mg.group(1))
        if val is not None and val > 0:
            u = mg.group(2).lower()
            sg = val * 1000 if u in ("kg", "kilogram", "kilograms", "किलोग्राम", "किग्रा") else val

    sml = None
    if sg is None:
        mml = ML_PAT.search(s)
        if mml:
            val = _parse_num_val(mml.group(1))
            if val is not None and val > 0:
                u = mml.group(2).lower()
                sml = val * 1000 if u in ("l", "litre", "litres", "liter", "liters", "लीटर") else val

    # Working string without bracketed notes for main fields
    s_clean = _strip_brackets(s)

    # Word numbers at start
    m_w = re.match(r"^(one|two|three|four|five|six|seven|eight|nine|ten)\b", s_clean, re.I)
    if m_w:
        s_clean = str(WORD_NUMS[m_w.group(1).lower()]) + s_clean[m_w.end():]

    # Check pinch / dash at start without number
    m_pinch = re.match(rf"^(?:generous\s+pinch|a\s+pinch|pinches|pinch|चुटकी\s*भर|चुटकी|a\s+dash|dashes|dash){BOUNDARY}", s_clean, re.I)
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
        matched_word = m_pinch.group(0).lower()
        unit = "dash" if "dash" in matched_word else "pinch"
        rem = s_clean[m_pinch.end():].strip()
    else:
        # Check RANGE_PAT first for range expressions (e.g. 1-1/2 to 2)
        m_rng = RANGE_PAT.match(s_clean)
        is_range = False
        if m_rng:
            a1, sep, a2 = m_rng.group(1), m_rng.group(2), m_rng.group(3)
            # If sep is '-' and a1 is integer and a2 is fraction, this is a mixed number (e.g. 1-1/2), NOT a range!
            if not (sep == "-" and re.match(r"^\d+$", a1.strip()) and (a2.strip() in UNICODE_FRAC or "/" in a2)):
                is_range = True

        if is_range:
            v1 = _parse_num_val(m_rng.group(1))
            v2 = _parse_num_val(m_rng.group(3))
            if v1 is not None and v2 is not None:
                qty_min = min(v1, v2)
                qty_max = max(v1, v2)
                qty = (v1 + v2) / 2
                rem = s_clean[m_rng.end():].strip()
        else:
            # Check mixed fraction like 2-1/2, 2 - 1/2, 1 & 1/2, 1 and 1/2
            m_mix = re.match(r"^(\d+)\s*(?:-|&|and)\s*(\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞]){NUM_BOUNDARY}", s_clean, re.I)
            if m_mix:
                w = float(m_mix.group(1))
                f_str = m_mix.group(2)
                if f_str in UNICODE_FRAC:
                    f_val = UNICODE_FRAC[f_str]
                else:
                    parts = f_str.split("/")
                    denom = float(parts[1])
                    f_val = float(parts[0]) / denom if denom != 0 else None
                if f_val is not None:
                    qty = w + f_val
                    qty_min = qty
                    qty_max = qty
                    rem = s_clean[m_mix.end():].strip()
            if qty is None:
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
                if rem.strip():
                    unit = "leaf"
                else:
                    unit = "piece"
                    rem = u_str + " " + rem
            else:
                unit = u_name
        else:
            # Check for garlic cloves / garlic pods where garlic precedes the unit word
            mg_pod = re.search(r"\bgarlic\s+(?:pods?|cloves?)\b", rem, re.I)
            if mg_pod:
                unit = "clove"
                rem = (rem[:mg_pod.start()] + " garlic " + rem[mg_pod.end():]).strip()
            else:
                unit = "piece"

        if unit in MASS_VOLUME_UNITS:
            size = None

    # Strip leading prepositions and separators from rem
    rem = re.sub(r"^[,\-–—:\.\s/]+", "", rem).strip()
    rem = re.sub(r"^\bof\b\s+", "", rem, flags=re.I).strip()

    water_line = _is_plain_water(rem)

    # Inverted lines: if qty was not found at start but stated mass/volume exists
    if qty is None and not water_line:
        if sg is not None and sg > 0:
            qty = sg
            qty_min = sg
            qty_max = sg
            unit = "g"
        elif sml is not None and sml > 0:
            qty = sml
            qty_min = sml
            qty_max = sml
            unit = "ml"

    # Determine status
    if water_line:
        status = "WATER"
    elif qty is None or qty <= 0:
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
        r"^(?:/\s*|\bor\s+)?\d+[\d\s./½¼¾⅓⅔⅛&to\-]*\s*(?:kg|kilograms?|किलोग्राम|किग्रा|g|gms?|grams?|ग्राम|ml|millilitres?|milliliters?|mls?|मिलीलीटर|मिली|l|litres?|liters?|लीटर)\b",
        " ",
        name_clean,
        flags=re.I,
    )
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
    name_clean = re.sub(
        r"(?:,\s*|\-\s*|\bor\s+|/\s*)?\d+[\d\s./½¼¾⅓⅔⅛&to\-]*\s*(?:kg|kilograms?|किलोग्राम|किग्रा|g|gms?|grams?|ग्राम|ml|millilitres?|milliliters?|mls?|मिलीलीटर|मिली|l|litres?|liters?|लीटर)\b\s*$",
        " ",
        name_clean,
        flags=re.I,
    )
    name_clean = re.sub(r"^[,\-–—:\.\s/]+|[,\-–—:\.\s/]+$", "", name_clean)
    name_clean = re.sub(r"^\bof\b\s+", "", name_clean, flags=re.I)
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
