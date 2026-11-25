"""Recipe URL scraper extracting schema.org/Recipe JSON-LD (with recipe-scrapers fallback)."""

from __future__ import annotations

import html
import ipaddress
import json
import re
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class RecipeScrapeError(Exception):
    """Structured error raised when a URL cannot be scraped into recipe lines."""

    def __init__(self, message: str, status_code: int = 422, reason: str = "SCRAPE_FAILED"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.reason = reason


def validate_public_http_url(url: str) -> str:
    """Validate that url is a public http/https URL (rejects local/private targets)."""
    cleaned = (url or "").strip()
    if not cleaned:
        raise RecipeScrapeError("Please enter a recipe URL.", status_code=422, reason="INVALID_URL")

    parsed = urlparse(cleaned)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise RecipeScrapeError(
            "URL must start with http:// or https:// and include a domain name.",
            status_code=422,
            reason="INVALID_URL",
        )

    host = (parsed.hostname or "").strip().lower()
    if not host or host in ("localhost", "127.0.0.1", "::1") or host.endswith(".local"):
        raise RecipeScrapeError("Local or private network URLs are not permitted.", status_code=422, reason="INVALID_URL")

    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise RecipeScrapeError("Private IP URLs are not permitted.", status_code=422, reason="INVALID_URL")
    except ValueError:
        # Hostname, resolve safely to reject loopback/private DNS targets
        try:
            resolved = socket.getaddrinfo(host, None)
            for _, _, _, _, sockaddr in resolved:
                candidate = ipaddress.ip_address(sockaddr[0])
                if candidate.is_private or candidate.is_loopback or candidate.is_link_local:
                    raise RecipeScrapeError(
                        "Target host resolves to a private network address.",
                        status_code=422,
                        reason="INVALID_URL",
                    )
        except socket.gaierror:
            # Let downstream HTTP request produce a clear DNS/fetch message if needed
            pass

    return cleaned


def _clean_text(value: str) -> str:
    """Decode HTML entities and collapse internal whitespace."""
    return " ".join(html.unescape(str(value or "")).split())


def parse_servings(raw_yield) -> tuple[float | None, str]:
    """Parse schema.org recipeYield (int, str, or list) into (float_servings, raw_text)."""
    if raw_yield is None or isinstance(raw_yield, bool):
        return None, ""

    if isinstance(raw_yield, (int, float)):
        val = float(raw_yield)
        return (val if val > 0 else None), str(raw_yield)

    if isinstance(raw_yield, list):
        raw_text = ", ".join(_clean_text(x) for x in raw_yield if x is not None).strip()
        for item in raw_yield:
            parsed, _ = parse_servings(item)
            if parsed is not None:
                return parsed, raw_text
        return None, raw_text

    text = _clean_text(str(raw_yield))
    if not text:
        return None, ""

    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None, text
    try:
        val = float(match.group(1))
        return (val if val > 0 else None), text
    except (ValueError, TypeError):
        return None, text


def _is_recipe_type(type_val) -> bool:
    """Return True if JSON-LD @type represents schema.org Recipe."""
    if isinstance(type_val, str):
        return type_val.strip().lower().endswith("recipe")
    if isinstance(type_val, list):
        return any(_is_recipe_type(t) for t in type_val)
    return False


def _extract_jsonld_recipes(soup: BeautifulSoup) -> list[dict]:
    """Collect all schema.org Recipe dicts across ld+json blocks and @graph trees."""
    found: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw_json = script.string or script.get_text() or ""
        if not raw_json.strip():
            continue
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            continue

        stack = [payload]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(reversed(node))
            elif isinstance(node, dict):
                if _is_recipe_type(node.get("@type")):
                    found.append(node)
                graph = node.get("@graph")
                if isinstance(graph, list):
                    stack.extend(reversed(graph))
                elif isinstance(graph, dict):
                    stack.append(graph)
    return found


def _extract_instructions_text(inst_obj) -> str:
    """Flatten schema.org recipeInstructions (str, list of strings, HowToStep, or HowToSection)."""
    if not inst_obj:
        return ""
    if isinstance(inst_obj, str):
        return _clean_text(inst_obj)
    chunks: list[str] = []
    if isinstance(inst_obj, list):
        for item in inst_obj:
            chunks.append(_extract_instructions_text(item))
    elif isinstance(inst_obj, dict):
        if "text" in inst_obj:
            chunks.append(_clean_text(inst_obj.get("text") or ""))
        if "itemListElement" in inst_obj:
            chunks.append(_extract_instructions_text(inst_obj.get("itemListElement")))
    return " ".join(c for c in chunks if c)


def _detect_deep_frying_hint(instructions_text: str, lines: list[str], dish_name: str) -> tuple[bool, str | None]:
    """Infer whether recipe involves deep-frying from instructions text or unquantified lines."""
    title_l = (dish_name or "").lower()
    if any(b in title_l for b in ("baked", "air fry", "air-fry", "air fryer", "steamed", "roasted")):
        return False, None

    inst_l = (instructions_text or "").lower()
    for pat in ("deep fry", "deep-fry", "deep frying", "hot oil and fry", "fry until golden"):
        if pat in inst_l:
            return True, f"instructions ({pat})"

    for line in lines:
        low = line.lower()
        if any(p in low for p in ("for deep frying", "to deep fry", "for frying", "to fry")) and any(
            f in low for f in ("oil", "ghee", "fat", "vanaspati")
        ):
            return True, "ingredient_frying_phrase"

    return False, None


def extract_recipe_from_html(html_text: str, url: str = "") -> dict:
    """Parse HTML into an LHF-ready recipe dict from JSON-LD or recipe-scrapers."""
    if not html_text or not html_text.strip():
        raise RecipeScrapeError("Empty HTML document returned by target page.", reason="EMPTY_PAGE")

    soup = BeautifulSoup(html_text, "html.parser")
    page_title = _clean_text(soup.title.get_text()) if soup.title else ""
    netloc = urlparse(url).netloc if url else ""

    # Tier 1: schema.org/Recipe JSON-LD
    for node in _extract_jsonld_recipes(soup):
        raw_ings = node.get("recipeIngredient") or node.get("ingredients") or []
        if isinstance(raw_ings, str):
            raw_ings = [ln.strip() for ln in raw_ings.splitlines() if ln.strip()]
        lines = [_clean_text(item) for item in raw_ings if isinstance(item, str) and _clean_text(item)]
        if lines:
            title = _clean_text(node.get("name") or page_title or "Scraped Recipe")
            servings, servings_raw = parse_servings(node.get("recipeYield"))
            inst_text = _extract_instructions_text(node.get("recipeInstructions"))
            deep_fried_hint, deep_fry_evidence = _detect_deep_frying_hint(inst_text, lines, title)
            return {
                "id": "web-live",
                "url": url or None,
                "dish": title,
                "servings": servings,
                "servings_raw": servings_raw,
                "lines": lines,
                "deep_fried_hint": deep_fried_hint,
                "deep_fry_evidence": deep_fry_evidence,
                "scrape_meta": {
                    "source": "json-ld",
                    "site": netloc,
                    "lines_extracted": len(lines),
                    "deep_fried_hint": deep_fried_hint,
                    "deep_fry_evidence": deep_fry_evidence,
                },
            }

    # Tier 2: recipe-scrapers HTML extraction fallback
    try:
        from recipe_scrapers import scrape_html

        scraper = scrape_html(html=html_text, org_url=url or "https://example.com/", supported_only=False)
        lines = [_clean_text(x) for x in (scraper.ingredients() or []) if _clean_text(x)]
        if lines:
            title = _clean_text(scraper.title() or page_title or "Scraped Recipe")
            yield_raw = scraper.yields() if hasattr(scraper, "yields") else ""
            servings, servings_raw = parse_servings(yield_raw)
            inst_text = _clean_text(scraper.instructions() or "") if hasattr(scraper, "instructions") else ""
            deep_fried_hint, deep_fry_evidence = _detect_deep_frying_hint(inst_text, lines, title)
            return {
                "id": "web-live",
                "url": url or None,
                "dish": title,
                "servings": servings,
                "servings_raw": servings_raw,
                "lines": lines,
                "deep_fried_hint": deep_fried_hint,
                "deep_fry_evidence": deep_fry_evidence,
                "scrape_meta": {
                    "source": "recipe-scrapers",
                    "site": netloc,
                    "lines_extracted": len(lines),
                    "deep_fried_hint": deep_fried_hint,
                    "deep_fry_evidence": deep_fry_evidence,
                },
            }
    except Exception:
        pass

    raise RecipeScrapeError(
        "No structured schema.org/Recipe JSON-LD ingredient list was found on this page. "
        "Please copy and paste the ingredient lines manually.",
        status_code=422,
        reason="NO_RECIPE_MARKUP",
    )


def scrape_recipe_url(url: str, timeout: int = 15) -> dict:
    """Fetch a public recipe URL and extract its structured recipe dict."""
    target = validate_public_http_url(url)

    try:
        resp = requests.get(target, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
    except requests.Timeout as exc:
        raise RecipeScrapeError(
            f"Timed out after {timeout}s while fetching {target}. Please paste the ingredients directly.",
            status_code=504,
            reason="TIMEOUT",
        ) from exc
    except requests.RequestException as exc:
        raise RecipeScrapeError(
            f"Network error fetching recipe URL ({exc.__class__.__name__}). Try pasting ingredients instead.",
            status_code=502,
            reason="NETWORK_ERROR",
        ) from exc

    body_lower = (resp.text or "")[:8000].lower()
    if resp.status_code in (403, 429, 503) or "challenges.cloudflare.com" in body_lower or "just a moment" in body_lower:
        raise RecipeScrapeError(
            f"Site returned HTTP {resp.status_code} or anti-bot protection. "
            "Respecting site controls — please copy & paste the ingredients instead.",
            status_code=502,
            reason="BLOCKED_BY_SITE",
        )

    if resp.status_code != 200:
        raise RecipeScrapeError(
            f"Target site returned HTTP {resp.status_code}. Please copy & paste the ingredients manually.",
            status_code=502,
            reason=f"HTTP_{resp.status_code}",
        )

    return extract_recipe_from_html(resp.text, url=resp.url or target)
