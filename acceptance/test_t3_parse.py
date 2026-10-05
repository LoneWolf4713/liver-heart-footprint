"""T3: lhf.parse.parse_line on hand-labelled real lines (gold) + invariants on all 1,339 sample lines."""
from _common import check, close, finish, gold, rate, samples

from lhf.parse import parse_line  # noqa: E402

KEYS = {"raw", "status", "qty", "qty_min", "qty_max", "unit", "size", "stated_g", "stated_ml", "optional", "name"}
UNITS = {"tsp", "tbsp", "cup", "g", "kg", "mg", "ml", "l", "oz", "lb", "pinch", "dash", "piece", "clove", "inch", "cm", "sprig",
         "stick", "strand", "leaf", "bunch", "cube", "slice", "floret", "ball", "blade", "pat"}
G = gold()
ok = {k: 0 for k in ("status", "qty", "range", "unit", "size", "stated", "optional", "name")}
nq = 0
for g in G:
    p = parse_line(g["line"])
    if not check(set(p) == KEYS, f"{g['gid']}: keys {sorted(p)} != {sorted(KEYS)}"):
        continue
    ok["status"] += p["status"] == g["status"]
    ok["optional"] += p["optional"] == g["optional"]
    ok["name"] += any(k.lower() in (p["name"] or "").lower() for k in g["name_any"])
    if g["status"] == "QUANTIFIED":
        nq += 1
        ok["qty"] += close(p["qty"], g["qty"], rel=0.01)
        ok["range"] += close(p["qty_min"], g["qty_min"], rel=0.01) and close(p["qty_max"], g["qty_max"], rel=0.01)
        units = g["unit"] if isinstance(g["unit"], list) else [g["unit"]]
        ok["unit"] += p["unit"] in units
        ok["size"] += p["size"] == g["size"]
        ok["stated"] += close(p["stated_g"], g["stated_g"], rel=0.01) and close(p["stated_ml"], g["stated_ml"], rel=0.01)
n = len(G)
print(f"  gold lines: {n} ({nq} quantified)")
rate("status", ok["status"], n, 0.95)
rate("optional", ok["optional"], n, 0.90)
rate("name keyword", ok["name"], n, 0.90)
rate("qty", ok["qty"], nq, 0.95)
rate("range min/max", ok["range"], nq, 0.95)
rate("unit", ok["unit"], nq, 0.90)
rate("size", ok["size"], nq, 0.90)
rate("stated g/ml", ok["stated"], nq, 0.95)

# invariants on every real sample line
lines = [l for r in samples() for l in r["lines"]]
crash = 0
for l in lines:
    try:
        p = parse_line(l)
    except Exception as e:  # noqa: BLE001
        crash += 1; check(False, f"crash on {l[:50]!r}: {e!r}"); continue
    check(p["raw"] == l, f"raw must equal input: {l[:50]!r}")
    check(p["status"] in ("QUANTIFIED", "UNQUANTIFIED", "WATER"), f"bad status {p['status']!r}")
    check(p["unit"] is None or p["unit"] in UNITS, f"non-canonical unit {p['unit']!r} for {l[:50]!r}")
    if p["status"] == "QUANTIFIED":
        check(p["qty"] is not None and p["qty"] > 0, f"QUANTIFIED needs qty > 0: {l[:50]!r}")
        if p["qty"] is not None and p["qty_min"] is not None and p["qty_max"] is not None:
            check(p["qty_min"] <= p["qty"] <= p["qty_max"], f"range order wrong: {l[:50]!r}")
    if p["status"] == "UNQUANTIFIED":
        check(p["qty"] is None and p["stated_g"] is None and p["stated_ml"] is None, f"UNQUANTIFIED must have no qty: {l[:50]!r}")
    check(p["stated_g"] is None or p["stated_g"] > 0, f"stated_g must be > 0: {l[:50]!r}")
    check(p["size"] in (None, "small", "medium", "large"), f"bad size {p['size']!r}")
    check(isinstance(p["name"], str) and p["name"] == p["name"].lower(), f"name must be lower-case str: {l[:50]!r}")
print(f"  sample lines parsed: {len(lines)}, crashes: {crash}")
# targeted edge cases (not from gold)
e = parse_line("1½ lbs (700 grams) chicken")
check(close(e["stated_g"], 700) and close(e["qty"], 1.5) and e["unit"] == "lb", "'1½ lbs (700 grams) chicken' -> qty 1.5 lb, stated_g 700")
e = parse_line("1 1/2 cups rice")
check(close(e["qty"], 1.5) and e["unit"] == "cup", "'1 1/2 cups rice' -> 1.5 cup")
e = parse_line("1 kg mutton")
check(e["unit"] == "kg" and close(e["stated_g"], 1000), "'1 kg mutton' -> unit kg, stated_g 1000")
e = parse_line("Salt to taste")
check(e["status"] == "UNQUANTIFIED" and e["qty"] is None, "'Salt to taste' -> UNQUANTIFIED")
e = parse_line("ice cubes as needed")
check(e["status"] == "WATER", "'ice cubes as needed' -> WATER")
finish("T3 parse")
