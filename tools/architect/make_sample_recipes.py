"""Architect tool: build data/samples/recipes_phase1.jsonl from the two genuine sample sets (no network)."""
import ast, json, os, re
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
S = os.path.join(REPO, "data", "samples")


def first_int(x):
    m = re.search(r"\d+", str(x))
    return int(m.group()) if m else None


out = []
r = pd.read_csv(os.path.join(S, "dryrun_recipes", "d1_recipes.csv"))
lines = pd.read_csv(os.path.join(S, "dryrun_recipes", "d1_ingredient_lines.csv"))
for i, rec in enumerate(r[r.status == "FETCHED_OK"].itertuples(), 1):
    ls = lines[lines.url == rec.url].line.tolist()
    raw = rec.servings if isinstance(rec.servings, str) else None
    serv = None
    if raw:
        try:
            serv = first_int(ast.literal_eval(raw)[0])
        except Exception:
            serv = first_int(raw)
    out.append({"id": f"D1-{i:02d}", "set": "dryrun_d1", "dish": rec.dish, "site": rec.site, "url": rec.url,
                "servings": serv, "servings_raw": raw, "lines": ls})
v = pd.read_csv(os.path.join(S, "validation_v2", "recipes.csv"))
for rec in v.itertuples():
    y = None
    try:
        y = ast.literal_eval(rec._6)
    except Exception:
        pass
    raw = str(y) if y is not None else None
    serv = first_int(y[0]) if isinstance(y, list) and y else None
    site = re.sub(r"^www\.", "", re.search(r"//([^/]+)", rec.url).group(1))
    out.append({"id": f"V2-{rec.rid}", "set": "validation_v2", "dish": rec.dish, "site": site, "url": rec.url,
                "title": rec.title, "servings": serv, "servings_raw": raw,
                "lines": [l.strip() for l in rec.raw_ingredient_lines.split("||") if l.strip()]})
with open(os.path.join(S, "recipes_phase1.jsonl"), "w") as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")
print(len(out), "recipes,", sum(len(o["lines"]) for o in out), "lines,", sum(o["servings"] is None for o in out), "without servings")
