"""FastAPI backend serving the Liver & Heart Footprint Web Application (Deliverable 4)."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent
SRC_DIR = REPO_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lhf import footprint as footprint_mod  # noqa: E402
from lhf import pipeline  # noqa: E402
from lhf.frying import ALLOWED_FRYING_SETTINGS  # noqa: E402
from lhf.paths import DATA_CURATED  # noqa: E402

from app.scraper import RecipeScrapeError, scrape_recipe_url  # noqa: E402


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="Public recipe URL containing schema.org Recipe data")


class AnalyzeRequest(BaseModel):
    id: str = "live-recipe"
    url: str | None = None
    dish: str = Field(..., min_length=1, description="Dish name used for display and fried-food matching")
    servings: float | None = Field(default=None, description="Number of servings; null defaults to 1 with warning")
    lines: list[str] | str = Field(..., description="Ingredient lines as list or newline-delimited string")
    deep_fried_hint: bool = False
    deep_fry_evidence: str | None = None
    setting: str = "urban"
    risk: str = "general"
    frying_setting: str = "auto"


class ScrapeAndAnalyzeRequest(BaseModel):
    url: str
    setting: str = "urban"
    risk: str = "general"
    frying_setting: str = "auto"


app = FastAPI(
    title="Liver & Heart Footprint of Indian Recipes",
    description="BIO544 Computational Gastronomy API (Deliverable 4)",
    version="1.0.0",
)

STATIC_DIR = APP_DIR / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _normalize_lines(raw_lines: list[str] | str) -> list[str]:
    if isinstance(raw_lines, str):
        return [ln.strip() for ln in raw_lines.splitlines() if ln.strip()]
    return [str(ln).strip() for ln in raw_lines if str(ln).strip()]


def _run_safe_analysis(
    recipe_dict: dict[str, Any],
    setting: str = "urban",
    risk: str = "general",
    frying_setting: str = "auto",
) -> dict[str, Any]:
    """Run pipeline.analyse_recipe and guarantee non-null UI-safe per_serving/footprint fallback."""
    if setting not in footprint_mod.ALLOWED_SETTINGS:
        raise HTTPException(status_code=422, detail=f"Invalid demographic setting {setting!r}")
    if risk not in footprint_mod.ALLOWED_RISKS:
        raise HTTPException(status_code=422, detail=f"Invalid clinical risk {risk!r}")
    if frying_setting not in ALLOWED_FRYING_SETTINGS:
        raise HTTPException(status_code=422, detail=f"Invalid frying_setting {frying_setting!r}")

    lines = _normalize_lines(recipe_dict.get("lines") or [])
    if not lines:
        raise HTTPException(status_code=422, detail="At least one non-empty ingredient line is required.")

    deep_fried_hint = bool(recipe_dict.get("deep_fried_hint", False))
    deep_fry_evidence = recipe_dict.get("deep_fry_evidence")
    if not deep_fried_hint:
        for ln in lines:
            low = ln.lower()
            if any(p in low for p in ("for deep frying", "to deep fry", "for frying", "to fry", "deep frying")) and any(
                f in low for f in ("oil", "ghee", "fat", "vanaspati", "shortening")
            ):
                deep_fried_hint = True
                deep_fry_evidence = deep_fry_evidence or "ingredient_frying_phrase"
                break

    normalized = {
        "id": recipe_dict.get("id") or "live-recipe",
        "url": recipe_dict.get("url"),
        "dish": (recipe_dict.get("dish") or "Custom Recipe").strip(),
        "servings": recipe_dict.get("servings"),
        "lines": lines,
        "deep_fried_hint": deep_fried_hint,
        "deep_fry_evidence": deep_fry_evidence,
    }

    res = pipeline.analyse_recipe(
        normalized,
        setting=setting,
        risk=risk,
        frying_setting=frying_setting,
    )

    # Guard UI against null per_serving / footprint when recipeYield is missing (preserving NO_SERVINGS warning)
    if res.get("per_serving") is None or res.get("footprint") is None:
        fallback_recipe = dict(normalized, servings=1.0)
        recomputed = pipeline.analyse_recipe(
            fallback_recipe,
            setting=setting,
            risk=risk,
            frying_setting=frying_setting,
        )
        warnings = list(recomputed.get("warnings") or [])
        if not any(str(w).startswith("NO_SERVINGS") for w in warnings):
            warnings.append("NO_SERVINGS: servings not specified or invalid in recipe; showing whole-recipe totals as 1 serving")
        recomputed["warnings"] = warnings
        recomputed["recipe"]["servings_missing"] = True
        res = recomputed
    else:
        res["recipe"]["servings_missing"] = False

    res["meta"] = {
        "demographic_setting": setting,
        "risk": risk,
        "frying_setting": frying_setting,
    }
    return res


@app.get("/")
def serve_home():
    index_path = APP_DIR / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Frontend app/index.html not found.")
    return FileResponse(str(index_path))


@app.get("/api/health")
def api_health():
    lab_path = os.path.join(DATA_CURATED, "fried_foods_lab.csv")
    lab_count = 0
    if os.path.exists(lab_path):
        with open(lab_path, encoding="utf-8") as f:
            lab_count = max(0, sum(1 for _ in csv.reader(f)) - 1)
    return {
        "status": "ok",
        "engine": "lhf",
        "lab_rows": lab_count,
    }


@app.get("/api/lab-data")
def api_lab_data():
    lab_path = os.path.join(DATA_CURATED, "fried_foods_lab.csv")
    if not os.path.exists(lab_path):
        raise HTTPException(status_code=404, detail="Lab dataset fried_foods_lab.csv not found.")
    with open(lab_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {"count": len(rows), "rows": rows}


@app.post("/api/scrape")
def api_scrape(req: ScrapeRequest):
    try:
        return scrape_recipe_url(req.url)
    except RecipeScrapeError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"reason": exc.reason, "message": exc.message},
        ) from exc


@app.post("/api/analyze")
def api_analyze(req: AnalyzeRequest):
    return _run_safe_analysis(
        req.model_dump(),
        setting=req.setting,
        risk=req.risk,
        frying_setting=req.frying_setting,
    )


@app.post("/api/scrape-and-analyze")
def api_scrape_and_analyze(req: ScrapeAndAnalyzeRequest):
    try:
        scraped = scrape_recipe_url(req.url)
    except RecipeScrapeError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"reason": exc.reason, "message": exc.message},
        ) from exc

    analysis = _run_safe_analysis(
        scraped,
        setting=req.setting,
        risk=req.risk,
        frying_setting=req.frying_setting,
    )
    analysis["scrape_meta"] = scraped.get("scrape_meta")
    return analysis
