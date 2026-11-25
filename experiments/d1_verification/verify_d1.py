"""Deliverable 1 (D1) Verification Script.

1. Audits provenance completeness across data/curated/fried_foods_lab.csv.
2. Recomputes category-level fat ranges (min, Q1, median, Q3, max, mean).
3. Runs leave-one-source-out (LOSO) holdout validation across the 10 published sources.
4. Writes CSV, JSON, and Markdown verification artifacts.
"""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LAB_CSV = BASE_DIR / "data" / "curated" / "fried_foods_lab.csv"
OUT_DIR = Path(__file__).resolve().parent


def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])


def _summarise(vals: list[float]) -> dict:
    s = sorted(vals)
    return {
        "min": round(s[0], 2),
        "p25": round(_percentile(s, 0.25), 2),
        "median": round(statistics.median(s), 2),
        "p75": round(_percentile(s, 0.75), 2),
        "max": round(s[-1], 2),
        "mean": round(statistics.mean(s), 2),
    }


def main() -> None:
    rows = list(csv.DictReader(LAB_CSV.open(encoding="utf-8")))
    assert len(rows) >= 60, f"Expected >=60 rows, got {len(rows)}"

    missing_prov = [
        r["item"] for r in rows if not r.get("source", "").strip() or not r.get("table_page", "").strip()
    ]
    sources = sorted({r["source"].strip() for r in rows})
    total_samples = sum(int(r["n_samples"]) for r in rows)

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_cat[r["category"].strip()].append(r)

    cat_summary = []
    for cat, cat_rows in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        fats = [float(r["fat_g_100g"]) for r in cat_rows]
        sfas = [float(r["SFA_pct_of_fat"]) for r in cat_rows if r.get("SFA_pct_of_fat", "").strip()]
        stats = _summarise(fats)
        cat_summary.append(
            {
                "category": cat,
                "rows": len(cat_rows),
                "n_samples": sum(int(r["n_samples"]) for r in cat_rows),
                "sources_count": len({r["source"].strip() for r in cat_rows}),
                **stats,
                "sfa_pct_rows": len(sfas),
                "sfa_pct_median": round(statistics.median(sfas), 2) if sfas else None,
            }
        )

    # Save category ranges CSV
    ranges_csv = OUT_DIR / "d1_category_ranges.csv"
    with ranges_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(cat_summary[0].keys()))
        writer.writeheader()
        writer.writerows(cat_summary)

    # Leave-One-Source-Out (LOSO) Holdout Validation
    loso_by_source = []
    total_eval = 0
    total_in_range = 0
    margin_hits_2g = 0
    untestable_singleton_rows = 0

    for src in sources:
        held = [r for r in rows if r["source"].strip() == src]
        train = [r for r in rows if r["source"].strip() != src]
        train_by_cat: dict[str, list[float]] = defaultdict(list)
        for r in train:
            train_by_cat[r["category"].strip()].append(float(r["fat_g_100g"]))

        src_eval = 0
        src_hits = 0
        src_margin = 0
        details = []

        for r in held:
            cat = r["category"].strip()
            val = float(r["fat_g_100g"])
            ref_vals = train_by_cat.get(cat, [])
            if len(ref_vals) < 1:
                untestable_singleton_rows += 1
                continue
            lo, hi = min(ref_vals), max(ref_vals)
            inside = lo <= val <= hi
            near = (lo - 2.0) <= val <= (hi + 2.0)
            src_eval += 1
            total_eval += 1
            if inside:
                src_hits += 1
                total_in_range += 1
            if near:
                src_margin += 1
                margin_hits_2g += 1
            details.append(
                {
                    "item": r["item"],
                    "category": cat,
                    "setting": r["setting"],
                    "val": val,
                    "ref_min": round(lo, 2),
                    "ref_max": round(hi, 2),
                    "in_range": inside,
                }
            )

        loso_by_source.append(
            {
                "source": src,
                "held_rows": len(held),
                "evaluable_rows": src_eval,
                "in_range": src_hits,
                "in_range_pct": round((src_hits / src_eval * 100), 1) if src_eval else None,
                "within_2g_margin": src_margin,
                "details": details,
            }
        )

    payload = {
        "rows_total": len(rows),
        "samples_total": total_samples,
        "sources_count": len(sources),
        "missing_provenance_count": len(missing_prov),
        "categories": cat_summary,
        "loso": {
            "evaluable_rows": total_eval,
            "untestable_singleton_rows": untestable_singleton_rows,
            "in_range_count": total_in_range,
            "in_range_pct": round(total_in_range / total_eval * 100, 1) if total_eval else 0.0,
            "within_2g_margin_count": margin_hits_2g,
            "within_2g_margin_pct": round(margin_hits_2g / total_eval * 100, 1) if total_eval else 0.0,
            "by_source": loso_by_source,
        },
    }

    (OUT_DIR / "d1_verification_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Deliverable 1 (D1) · Dataset Range & Holdout Verification Report",
        "",
        f"- **Dataset:** `data/curated/fried_foods_lab.csv`",
        f"- **Total Rows / Samples:** **{len(rows)} rows** ({total_samples} lab samples) across **{len(sources)} published sources**",
        f"- **Provenance Completeness:** **{len(rows) - len(missing_prov)}/{len(rows)}** rows have non-empty `source` and `table_page` citations (`{len(missing_prov)}` missing)",
        "",
        "## 1. Recomputed Fat Ranges by Category (g fat / 100 g cooked food)",
        "",
        "| Category | Rows | Samples (n) | Sources | Min | Q1 | Median | Q3 | Max | Mean |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in cat_summary:
        lines.append(
            f"| {c['category']} | {c['rows']} | {c['n_samples']} | {c['sources_count']} | "
            f"{c['min']:.2f} | {c['p25']:.2f} | {c['median']:.2f} | {c['p75']:.2f} | {c['max']:.2f} | {c['mean']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## 2. Leave-One-Source-Out (LOSO) Holdout Validation",
            "",
            f"Each study is held out in turn; remaining sources build the `[min, max]` category envelope for every overlapping category.",
            "",
            f"- **Evaluable held-out measurements:** **{total_eval}** (`{untestable_singleton_rows}` held-out row had no other-source category peer)",
            f"- **Exact in-range coverage:** **{total_in_range} / {total_eval} ({payload['loso']['in_range_pct']}%)**",
            f"- **Within ±2.0 g/100g of envelope:** **{margin_hits_2g} / {total_eval} ({payload['loso']['within_2g_margin_pct']}%)**",
            "",
            "| Held-Out Source | Total Rows | Evaluable Rows | Inside Other-Source Range | Coverage % |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for s in loso_by_source:
        pct_str = f"{s['in_range_pct']:.1f}%" if s["in_range_pct"] is not None else "—"
        lines.append(f"| {s['source']} | {s['held_rows']} | {s['evaluable_rows']} | {s['in_range']} | {pct_str} |")

    (OUT_DIR / "D1_VERIFICATION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"D1 Verification OK: {len(rows)} rows, {len(sources)} sources, LOSO={total_in_range}/{total_eval} ({payload['loso']['in_range_pct']}%)")


if __name__ == "__main__":
    main()
