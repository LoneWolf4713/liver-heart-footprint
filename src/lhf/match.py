"""Ingredient name matcher for Phase 1 core engine (SPEC §5)."""
import csv
import difflib
import os
import re

from lhf import composition, constants
from lhf.paths import DATA_CURATED

_ALIASES = None
_COMP_LOOKUP = None

PREP_PATTERNS = [
    r"\b(?:finely|roughly|thinly|thickly|coarsely)?\s*(?:chopped|diced|sliced|grated|minced|crushed|shredded|mashed|pureed|puree|paste|julienne|juliennes|slit|ground|cut)\b",
    r"\b(?:cut into|cut in)\s+(?:pieces|cubes|small pieces|small size pieces)\b",
    r"\b(?:boiled|fried|roasted|toasted|soaked|blanched|melted|softened|peeled|halved|quartered|torn|broken|pounded)\b",
    r"\b(?:for smoking|to knead|for deep frying|to deep fry|for frying|to fry|for tempering|for garnishing|to taste|as needed|as required|optional)\b",
    r"\b(?:stick|sticks|piece|pieces|pod|pods|strands|bag|bags|bunch|bunches)\b",
    r"\b(?:medium-sized|medium sized|large|small|medium|big)\b",
    r"\b(?:fresh|freshly|dried|dry|raw|ripe|warm|cold|hot|whole|refined|unrefined)\b",
]
PREP_RE = re.compile("|".join(PREP_PATTERNS), re.IGNORECASE)
JUNK_LEAD_RE = re.compile(
    r"^(?:[&+*\"']|\b(?:and|or|of|to|pinch|inch|tablespoons?|teaspoons?|tbsps?|tsps?|cups?)\b|[0-9½⅓⅔¼¾⅛⅜⅝⅞./\s\-–—&+=*\"'])+",
    re.IGNORECASE,
)
EXTRA_PREP_RE = re.compile(
    r"\b(?:lengthwise|pounded|coarsely|sized|medium-sized|thin)\b",
    re.IGNORECASE,
)
JUNK_TRAIL_RE = re.compile(
    r"(?:\s+\b(?:and|or|of|to|for|with)\b|[.,;:!*~\"'’”)\]\s-])+$",
    re.IGNORECASE,
)


def _load_aliases():
    global _ALIASES
    if _ALIASES is None:
        path = os.path.join(DATA_CURATED, "aliases.csv")
        alias_map = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    alias = row.get("alias", "").strip().lower()
                    code = row.get("code", "").strip()
                    if alias and code and alias not in alias_map:
                        alias_map[alias] = code
        _ALIASES = alias_map
    return _ALIASES


def _load_comp_lookup():
    global _COMP_LOOKUP
    if _COMP_LOOKUP is None:
        df = composition.load_table()
        lookup = {}
        for code, row in df.iterrows():
            name = str(row["name"]).strip().lower()
            src = str(row["source"])
            if name not in lookup or src == "IFCT2017":
                lookup[name] = code
        _COMP_LOOKUP = (lookup, list(lookup.keys()))
    return _COMP_LOOKUP


def _clean_prep(text: str) -> str:
    cleaned = PREP_RE.sub(" ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _expand_stems(cand: str, seen: set) -> list[str]:
    stems = []
    if "leaves" in cand:
        v = re.sub(r"\bleaves\b", "leaf", cand)
        if v not in seen:
            seen.add(v)
            stems.append(v)
    if "leaf" in cand:
        v = re.sub(r"\bleaf\b", "leaves", cand)
        if v not in seen:
            seen.add(v)
            stems.append(v)

    if cand.endswith("ies") and len(cand) > 4:
        for sing in (cand[:-3] + "y", cand[:-3] + "i", cand[:-3] + "ie"):
            if sing not in seen:
                seen.add(sing)
                stems.append(sing)
    elif cand.endswith("es") and len(cand) > 3:
        s1 = cand[:-2]  # tomatoes -> tomato
        if s1 not in seen:
            seen.add(s1)
            stems.append(s1)
        s2 = cand[:-1]  # apples -> apple, grapes -> grape
        if s2 not in seen:
            seen.add(s2)
            stems.append(s2)
    elif cand.endswith("s") and not cand.endswith("ss") and len(cand) > 2:
        sing = cand[:-1]
        if sing not in seen:
            seen.add(sing)
            stems.append(sing)
    return stems


def _get_raw_and_prep_variants(text: str) -> tuple[list[str], list[str]]:
    raw_variants = []
    prep_variants = []
    t = text.lower().strip()
    for q in ("“", "”", "‘", "’"):
        t = t.replace(q, "")
    t = t.replace("&amp;", "&").replace("&nbsp;", " ")
    t = re.sub(r"\(.*?\)", " ", t)
    t = t.strip("\"' \t\r\n.,;:!*~")

    # Remove leading junk (symbols, fractions, units)
    t = JUNK_LEAD_RE.sub("", t).strip("\"' \t\r\n.,;:!*~")
    t = JUNK_TRAIL_RE.sub("", t).strip("\"' \t\r\n.,;:!*~")

    # Deduplicate repeated adjacent words (e.g. 'cloves cloves', 'potatoes potatoes')
    words = t.split()
    dedup = []
    for w in words:
        if not dedup or dedup[-1] != w:
            dedup.append(w)
    t = " ".join(dedup)

    parts = [t]
    if " or " in t:
        parts.extend(p.strip() for p in t.split(" or ") if p.strip())
    if "/" in t:
        parts.extend(p.strip() for p in t.split("/") if p.strip())
    if "," in t:
        parts.extend(p.strip() for p in t.split(",") if p.strip())

    seen = set()
    for p in parts:
        p_clean = JUNK_LEAD_RE.sub("", p).strip("\"' \t\r\n.,;:!*~")
        p_clean = JUNK_TRAIL_RE.sub("", p_clean).strip("\"' \t\r\n.,;:!*~")
        p_clean = re.sub(r"\s+", " ", p_clean).strip()
        if p_clean and p_clean not in seen:
            seen.add(p_clean)
            raw_variants.append(p_clean)

        for s in _expand_stems(p_clean, seen):
            raw_variants.append(s)

        prep_c = _clean_prep(p_clean)
        prep_c = EXTRA_PREP_RE.sub("", prep_c)
        prep_c = JUNK_LEAD_RE.sub("", prep_c)
        prep_c = JUNK_TRAIL_RE.sub("", prep_c).strip("\"' \t\r\n.,;:!*~")
        prep_c = re.sub(r"\s+", " ", prep_c).strip()
        if prep_c and prep_c not in seen:
            seen.add(prep_c)
            prep_variants.append(prep_c)

        for s in _expand_stems(prep_c, seen):
            prep_variants.append(s)

    return raw_variants, prep_variants


def _get_variants(text: str) -> list[str]:
    raw_v, prep_v = _get_raw_and_prep_variants(text)
    return raw_v + prep_v


def _check_priority_variant(v: str, full_name: str) -> str | None:
    """Enforce SPEC §5 priority rules for a single variant."""
    vl = v.lower()
    fnl = full_name.lower()

    # Non-food items
    if "charcoal" in vl:
        return "NON_FOOD"

    # Chicken Rule: Any ingredient containing the token 'chicken' or 'murgh'/'murg'
    # Exclude stock, cube, spices, seasonings, eggs, vegan/plant substitutes (DEF-B2).
    chicken_exclusions = (
        "stock", "cube", "masala", "curry powder", "spice", "powder",
        "seasoning", "egg", "vegan", "plant",
    )
    if any(w in vl for w in ("chicken", "murgh", "murg", "चिकन")):
        if not any(w in fnl for w in chicken_exclusions) and not any(w in vl for w in chicken_exclusions):
            return "N500"

    # Ghee -> T013
    if not any(x in vl for x in ("vanaspati", "dalda")):
        if vl == "ghee" or "clarified butter" in vl or "desi ghee" in vl or "ghee" in vl.split():
            return "T013"

    # Paneer / Cottage Cheese -> L903 (Amul Malai Paneer, fat 23g) (DEF-B3)
    if "paneer" in vl or "cottage cheese" in vl:
        return "L903"

    # Curd / Dahi / Yogurt / Yoghurt -> L902 (or L520 for greek)
    if not ("bean curd" in vl or "tofu" in vl):
        if "greek" in vl and any(k in vl for k in ("yogurt", "yoghurt", "curd", "dahi")):
            return "L520"
        curd_terms = (
            "curd", "dahi", "yogurt", "yoghurt", "plain yogurt",
            "plain curd", "plain dahi", "hung curd", "hung dahi",
        )
        if any(vl == k or vl.startswith(k + " ") or vl.endswith(" " + k) for k in curd_terms):
            return "L902"

    # Butter -> L904 (or T501 for unsalted)
    # Exclude non-dairy butter terms: beans, fruit, paper, cookies, etc.
    non_dairy_butter = (
        "buttermilk", "chaas", "peanut butter", "almond butter", "apple butter",
        "butterfish", "butter beans", "butter bean", "butter fruit", "butter paper",
        "butter cookie", "butter cookies", "butter milk", "cocoa butter", "shea butter",
        "cashew butter",
    )
    if not any(x in vl for x in non_dairy_butter) and not any(x in fnl for x in non_dairy_butter):
        if "unsalted" in vl and "butter" in vl:
            return "T501"
        butter_terms = ("butter", "salted butter", "butter softened", "white butter", "makhan")
        if any(vl == k or vl.startswith(k + " ") or vl.endswith(" " + k) for k in butter_terms):
            return "L904"

    # Milk -> L901 (or L002 for whole, L001 for buffalo)
    non_dairy_milk = (
        "coconut milk", "soy milk", "soya milk", "almond milk",
        "oat milk", "condensed milk", "milk powder", "buttermilk",
        "milkfish", "milk fish",
    )
    if not any(x in vl for x in non_dairy_milk):
        if vl == "milk" or "milk" in vl.split() or vl == "doodh":
            if any(w in vl for w in ("buffalo", "bhains")):
                return "L001"
            if any(w in vl for w in ("whole", "full cream", "cow")):
                return "L002"
            return "L901"

    # Cream / Malai -> L905 (or L512 for heavy/whipping, L906 for malai)
    if not any(x in vl for x in ("ice cream", "sour cream", "coconut cream")):
        if any(w in vl for w in ("heavy cream", "whipping cream", "heavy whipping cream", "double cream")):
            return "L512"
        if vl == "malai" or "malai" in vl.split():
            return "L906"
        cream_terms = ("cream", "fresh cream", "light cream", "single cream")
        if any(vl == k or vl.startswith(k + " ") or vl.endswith(" " + k) for k in cream_terms):
            return "L905"

    # Generic Cooking Oil & Deep-Frying:
    # Cleaned name 'oil', 'cooking oil', 'refined oil', or containing
    # 'for deep frying', 'to deep fry', 'for frying', 'to fry' WITH oil/fat words maps to T508 (DEF-B4).
    named_oils = (
        "mustard", "sarson", "coconut", "nariyal", "sesame", "til", "gingelly",
        "olive", "groundnut", "peanut", "moongphali", "mungphali", "soybean",
        "soya", "canola", "rice bran", "corn", "palm", "safflower", "cottonseed",
    )
    if not any(w in vl for w in named_oils):
        oil_phrases = ("for deep frying", "to deep fry", "for frying", "to fry", "deep fry", "deep frying")
        if any(p in vl for p in oil_phrases) and any(w in vl for w in ("oil", "tel", "fat", "ghee")):
            return "T508"
        generic_oil_terms = ("oil", "cooking oil", "refined oil", "refined cooking oil", "vegetable oil", "neutral oil", "frying oil")
        if any(vl == k or vl.startswith(k + " ") or vl.endswith(" " + k) for k in generic_oil_terms):
            return "T508"

    return None


def match_name(name: str) -> dict:
    """Map a parsed ingredient name to a composition table code or UNMAPPED/NON_FOOD."""
    if not name or not isinstance(name, str):
        return {"code": "UNMAPPED", "method": "none", "score": 0.0}

    alias_map = _load_aliases()
    comp_map, comp_names = _load_comp_lookup()

    raw_variants, prep_variants = _get_raw_and_prep_variants(name)

    # 1. Programmatic Priority Rules on raw variants
    for v in raw_variants:
        priority_code = _check_priority_variant(v, name)
        if priority_code is not None:
            return {"code": priority_code, "method": "alias", "score": 1.0}

    # 2. Alias match on raw/unstripped text
    for v in raw_variants:
        if v in alias_map:
            return {"code": alias_map[v], "method": "alias", "score": 1.0}

    # 3. Exact match against composition names on raw/unstripped text
    for v in raw_variants:
        if v in comp_map:
            return {"code": comp_map[v], "method": "exact", "score": 1.0}

    # 4. Programmatic Priority Rules on prep-stripped variants
    for v in prep_variants:
        priority_code = _check_priority_variant(v, name)
        if priority_code is not None:
            return {"code": priority_code, "method": "alias", "score": 1.0}

    # 5. Exact match against composition names on prep-stripped text
    for v in prep_variants:
        if v in comp_map:
            return {"code": comp_map[v], "method": "exact", "score": 1.0}

    # 6. Alias match on prep-stripped text
    for v in prep_variants:
        if v in alias_map:
            return {"code": alias_map[v], "method": "alias", "score": 1.0}

    # 7. Fuzzy match against composition names
    cutoff = constants.get("FUZZY_MATCH_CUTOFF")
    all_variants = raw_variants + prep_variants
    for v in all_variants:
        matches = difflib.get_close_matches(v, comp_names, n=1, cutoff=cutoff)
        if matches:
            matched_name = matches[0]
            score = difflib.SequenceMatcher(None, v, matched_name).ratio()
            return {"code": comp_map[matched_name], "method": "fuzzy", "score": round(score, 4)}

    # 8. Non-food items (charcoal)
    if "charcoal" in name.lower():
        return {"code": "NON_FOOD", "method": "alias", "score": 1.0}

    # 9. UNMAPPED
    return {"code": "UNMAPPED", "method": "none", "score": 0.0}
