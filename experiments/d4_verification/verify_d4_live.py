"""Deliverable 4 (D4) Live 10+ URL Verification Script.

Sends real Indian recipe URLs across multiple portals to the running FastAPI endpoints
POST /api/scrape and POST /api/scrape-and-analyze, compares per-serving outputs against
a direct Python call to lhf.pipeline.analyse_recipe, and writes JSON + Markdown reports.
"""

from __future__ import annotations

import json
import math
import urllib.request
from pathlib import Path

from lhf.pipeline import analyse_recipe

OUT_DIR = Path(__file__).resolve().parent
BASE_API = "http://127.0.0.1:8001"

TEST_URLS = [
    ("indianhealthyrecipes.com", "https://www.indianhealthyrecipes.com/samosa-recipe-make-samosa/"),
    ("indianhealthyrecipes.com", "https://www.indianhealthyrecipes.com/paneer-butter-masala-restaurant-style/"),
    ("indianhealthyrecipes.com", "https://www.indianhealthyrecipes.com/chole/"),
    ("indianhealthyrecipes.com", "https://www.indianhealthyrecipes.com/chicken-biryani-recipe/"),
    ("hebbarskitchen.com", "https://hebbarskitchen.com/paneer-butter-masala-recipe/"),
    ("hebbarskitchen.com", "https://hebbarskitchen.com/punjabi-dal-makhani-recipe/"),
    ("hebbarskitchen.com", "https://hebbarskitchen.com/milk-powder-gulab-jamun-recipe/"),
    ("cookwithmanali.com", "https://www.cookwithmanali.com/paneer-butter-masala/"),
    ("cookwithmanali.com", "https://www.cookwithmanali.com/punjabi-chole-chickpeas-curry/"),
    ("archanaskitchen.com", "https://www.archanaskitchen.com/recipe/restaurant-style-paneer-butter-masala-recipe-paneer-makhani-recipe"),
    ("archanaskitchen.com", "https://www.archanaskitchen.com/recipe/calcutta-style-chicken-biryani-recipe"),
    ("pipingpotcurry.com", "https://pipingpotcurry.com/paneer-butter-masala/"),
    ("pipingpotcurry.com", "https://pipingpotcurry.com/chicken-biryani/"),
]


def _post_json(path: str, payload: dict, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_API}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _same_num(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(float(a), float(b), rel_tol=1e-6, abs_tol=1e-6)


def main() -> None:
    results = []
    passed = 0
    sites_passed = set()

    for site, target_url in TEST_URLS:
        entry = {"site": site, "url": target_url, "ok": False}
        try:
            scraped = _post_json("/api/scrape", {"url": target_url})
            api_res = _post_json(
                "/api/scrape-and-analyze",
                {"url": target_url, "setting": "urban", "risk": "general", "frying_setting": "auto"},
            )
            servings_for_direct = scraped.get("servings")
            if api_res.get("recipe", {}).get("servings_missing"):
                servings_for_direct = 1.0

            recipe_dict = {
                "id": "live-recipe",
                "url": target_url,
                "dish": scraped["dish"],
                "servings": servings_for_direct,
                "lines": scraped["lines"],
                "deep_fried_hint": bool(scraped.get("deep_fried_hint", False)),
                "deep_fry_evidence": scraped.get("deep_fry_evidence"),
            }
            direct_res = analyse_recipe(recipe_dict, setting="urban", risk="general", frying_setting="auto")

            axes_match = True
            for ax in ("energy_kcal", "fat_g", "sfa_g", "added_sugar_g", "sodium_mg", "refined_carb_g"):
                a = api_res["footprint"]["axes"][ax]["amount"]
                b = direct_res["footprint"]["axes"][ax]["amount"]
                if not _same_num(a, b):
                    axes_match = False

            entry.update(
                {
                    "ok": axes_match,
                    "title": api_res["recipe"].get("dish") or scraped["dish"],
                    "servings": api_res["recipe"].get("servings"),
                    "lines_total": len(scraped.get("lines") or []),
                    "lines_included": api_res["coverage"]["lines_included"],
                    "frying_applied": bool((api_res.get("frying_correction") or {}).get("applied")),
                    "energy_kcal": round(api_res["footprint"]["axes"]["energy_kcal"]["amount"], 1),
                    "sfa_g": round(api_res["footprint"]["axes"]["sfa_g"]["amount"], 1),
                    "sodium_mg": round(api_res["footprint"]["axes"]["sodium_mg"]["amount"], 1),
                    "engine_parity": axes_match,
                }
            )
            if axes_match:
                passed += 1
                sites_passed.add(site)
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
        results.append(entry)
        print(f"  [{'PASS' if entry['ok'] else 'FAIL'}] {site}: {entry.get('title') or target_url}")

    payload = {
        "tested_count": len(results),
        "passed_count": passed,
        "sites_passed": sorted(sites_passed),
        "results": results,
    }
    (OUT_DIR / "d4_live_verification_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# Deliverable 4 (D4) · Live Web App 10+ URL Verification Report",
        "",
        f"- **Endpoint tested:** `POST {BASE_API}/api/scrape-and-analyze`",
        f"- **URLs passed:** **{passed} / {len(results)}** across **{len(sites_passed)} distinct recipe websites** (`{', '.join(sorted(sites_passed))}`)",
        "- **Engine parity check:** Every passing URL compared per-serving outputs (`energy_kcal`, `fat_g`, `sfa_g`, `added_sugar_g`, `sodium_mg`, `refined_carb_g`) directly against `lhf.pipeline.analyse_recipe` with exact match.",
        "",
        "| Site | Dish Title | Servings | Lines (Inc/Tot) | Frying Fix | Kcal / Serv | SFA / Serv | Engine Parity |",
        "|---|---|---:|---:|---|---:|---:|---|",
    ]
    for r in results:
        if r["ok"]:
            fry = "Applied" if r["frying_applied"] else "No"
            md.append(
                f"| {r['site']} | {r['title']} | {r['servings']} | {r['lines_included']}/{r['lines_total']} | "
                f"{fry} | {r['energy_kcal']} | {r['sfa_g']} g | Exact Match |"
            )
        else:
            md.append(f"| {r['site']} | `{r['url']}` | — | — | — | — | — | Error: {r.get('error', 'unknown')} |")

    (OUT_DIR / "D4_VERIFICATION_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"D4 Live Verification Complete: {passed}/{len(results)} URLs passed across {len(sites_passed)} websites")


if __name__ == "__main__":
    main()
