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
    r"\b(?:finely|roughly|thinly|thickly|coarsely)?\s*(?:chopped|diced|sliced|grated|minced|crushed|shredded|mashed|pureed|puree|paste|julienne|juliennes|slit|ground)\b",
    r"\b(?:cut into|cut in)\s+(?:pieces|cubes|small pieces|uniform size|small size pieces)(?:\s+of\s+uniform\s+size)?\b",
    r"\b(?:boiled|fried|roasted|toasted|soaked|blanched|melted|softened|peeled|halved|quartered|torn|broken|pounded)\b",
    r"\b(?:for smoking|to knead|for frying|for tempering|for garnishing|to taste|as needed|as required|optional)\b",
    r"\b(?:stick|sticks|piece|pieces|pod|pods|strands|bag|bags)\b",
    r"\b(?:medium-sized|medium sized|large|small|medium|big)\b",
    r"\b(?:fresh|freshly|dried|dry|raw|ripe|warm|cold|hot|whole)\b",
]
PREP_RE = re.compile("|".join(PREP_PATTERNS), re.IGNORECASE)
JUNK_LEAD_RE = re.compile(
    r"^(?:[&+*\"']|\b(?:and|or|of|to|pinch|inch|tablespoons?|teaspoons?|tbsps?|tsps?|cups?)\b|[0-9½⅓⅔¼¾⅛⅜⅝⅞./\s\-–—&+=*\"'])+",
    re.IGNORECASE,
)
EXTRA_PREP_RE = re.compile(
    r"\b(?:shelled|cut lengthwise|lengthwise|pounded coarsely|pounded|coarsely|and diced small|sized|medium-sized|thin)\b",
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


def _get_variants(text: str) -> list[str]:
    variants = []
    t = text.lower().strip()
    t = t.replace("&amp;", "&").replace("&nbsp;", " ")
    t = re.sub(r"\(.*?\)", " ", t)
    t = t.strip("\"' \t\r\n.,;:!*~")

    # Remove leading junk (symbols, fractions, units)
    t = JUNK_LEAD_RE.sub("", t).strip("\"' \t\r\n.,;:!*~")

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
        p_clean = re.sub(r"\s+", " ", p_clean).strip()
        if p_clean and p_clean not in seen:
            seen.add(p_clean)
            variants.append(p_clean)

        prep_c = _clean_prep(p_clean)
        prep_c = EXTRA_PREP_RE.sub("", prep_c)
        prep_c = JUNK_LEAD_RE.sub("", prep_c).strip("\"' \t\r\n.,;:!*~")
        prep_c = re.sub(r"\s+", " ", prep_c).strip()
        if prep_c and prep_c not in seen:
            seen.add(prep_c)
            variants.append(prep_c)

        for cand in [p_clean, prep_c]:
            if cand.endswith("ies") and len(cand) > 4:
                sing = cand[:-3] + "y"
                if sing not in seen:
                    seen.add(sing)
                    variants.append(sing)
            elif cand.endswith("es") and len(cand) > 3:
                sing = cand[:-2]
                if sing not in seen:
                    seen.add(sing)
                    variants.append(sing)
            elif cand.endswith("s") and not cand.endswith("ss") and len(cand) > 2:
                sing = cand[:-1]
                if sing not in seen:
                    seen.add(sing)
                    variants.append(sing)

    return variants


def match_name(name: str) -> dict:
    """Map a parsed ingredient name to a composition table code or UNMAPPED/NON_FOOD."""
    if not name or not isinstance(name, str):
        return {"code": "UNMAPPED", "method": "none", "score": 0.0}

    alias_map = _load_aliases()
    comp_map, comp_names = _load_comp_lookup()

    variants = _get_variants(name)

    # 1. Alias match
    for v in variants:
        if v in alias_map:
            return {"code": alias_map[v], "method": "alias", "score": 1.0}

    # 2. Exact match against composition names
    for v in variants:
        if v in comp_map:
            return {"code": comp_map[v], "method": "exact", "score": 1.0}

    # 3. Fuzzy match against composition names
    cutoff = constants.get("FUZZY_MATCH_CUTOFF")
    for v in variants:
        matches = difflib.get_close_matches(v, comp_names, n=1, cutoff=cutoff)
        if matches:
            matched_name = matches[0]
            score = difflib.SequenceMatcher(None, v, matched_name).ratio()
            return {"code": comp_map[matched_name], "method": "fuzzy", "score": round(score, 4)}

    # 4. Non-food items (charcoal)
    if "charcoal" in name.lower():
        return {"code": "NON_FOOD", "method": "alias", "score": 1.0}

    # 5. UNMAPPED
    return {"code": "UNMAPPED", "method": "none", "score": 0.0}
