"""T4: lhf.match.match_name maps parsed names (from lhf.parse) to composition codes. Gold = hand-labelled allowed codes."""
import csv
import os
from _common import CUR, check, finish, gold, rate, samples

from lhf import composition  # noqa: E402
from lhf.match import match_name  # noqa: E402
from lhf.parse import parse_line  # noqa: E402

codes = set(composition.load_table().index)
SPECIAL = {"UNMAPPED", "NON_FOOD"}
path = os.path.join(CUR, "aliases.csv")
check(os.path.exists(path), "data/curated/aliases.csv must exist")
if os.path.exists(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    check(rows and set(rows[0]) >= {"alias", "code", "note"}, "aliases.csv needs columns alias,code,note")
    for r in rows:
        check(r["code"] in codes or r["code"] in SPECIAL, f"alias {r['alias']!r} -> unknown code {r['code']!r}")
        check(len(r["alias"]) <= 40 and not any(ch.isdigit() for ch in r["alias"]), f"alias must be a short name without digits: {r['alias']!r}")
    print(f"  aliases: {len(rows)}")

ok = n = 0
for g in gold():
    if g["codes"] is None:
        continue
    n += 1
    name = parse_line(g["line"])["name"]
    m = match_name(name)
    check(set(m) >= {"code", "method", "score"}, f"match_name output keys {sorted(m)}")
    hit = m["code"] in g["codes"]
    ok += hit
    if not hit:
        print(f"    miss {g['gid']}: {name!r} -> {m['code']} (allowed {g['codes'][:4]})")
rate("gold code match", ok, n, 0.85)

total = 0
for r in samples():
    for l in r["lines"]:
        p = parse_line(l)
        if p["status"] != "QUANTIFIED":
            continue
        m = match_name(p["name"])
        total += 1
        check(m["code"] in codes or m["code"] in SPECIAL, f"invalid code {m['code']!r} for {l[:50]!r}")
        check(m["method"] in ("alias", "exact", "fuzzy", "none"), f"bad method {m['method']!r}")
        check(0 <= m["score"] <= 1, f"score out of range for {l[:50]!r}")
print(f"  sample quantified lines matched: {total}")
check(match_name("maida")["code"] == "A018", "maida -> A018")
check(match_name("besan")["code"] == "A504", "besan -> A504")
check(match_name("ghee")["code"] in ("T506", "T013"), "ghee -> T506/T013")
check(match_name("sunflower oil")["code"] in ("T508", "T012"), "sunflower oil -> T508/T012 (UK preferred)")
check(match_name("xqzv blorf")["code"] == "UNMAPPED", "nonsense -> UNMAPPED")
finish("T4 match")
