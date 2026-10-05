"""Global rules, run at every `done`:
1. src/lhf/*.py has no numeric literals other than 0-12, 100, 1000 (e.g. 0.5 or 37 are refused; numbers come from data/curated).
2. No network, randomness or subprocess imports in src/.
3. src/ never imports from acceptance/ and never reads acceptance/gold.
4. No whole gold line text appears in src/ or data/curated/aliases.csv (no hard-coding test answers)."""
import ast
import glob
import os
from _common import REPO, check, finish, gold

ALLOWED_INTS = set(range(0, 13)) | {100, 1000}
BANNED_IMPORTS = {"requests", "urllib", "httpx", "socket", "http", "aiohttp", "random", "subprocess", "secrets"}
files = sorted(glob.glob(os.path.join(REPO, "src", "**", "*.py"), recursive=True))
for f in files:
    rel = os.path.relpath(f, REPO)
    src = open(f, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        check(False, f"{rel}: syntax error {e}")
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float) and not isinstance(node.value, bool):
            v = node.value
            if v not in ALLOWED_INTS:  # 0.0/1.0/100.0 count as 0/1/100
                check(False, f"{rel}:{node.lineno}: numeric literal {v!r} not allowed (put it in data/curated with a source)")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for n in names:
                top = n.split(".")[0]
                check(top not in BANNED_IMPORTS, f"{rel}:{node.lineno}: import of '{n}' is not allowed")
                check(top != "acceptance" and top != "_common", f"{rel}:{node.lineno}: src must not import acceptance code")
    check("acceptance/gold" not in src and "gold_public" not in src and "gold_holdout" not in src,
          f"{rel}: must not reference the gold files")

texts = []
for f in files:
    texts.append(open(f, encoding="utf-8").read())
alias = os.path.join(REPO, "data", "curated", "aliases.csv")
if os.path.exists(alias):
    texts.append(open(alias, encoding="utf-8").read())
blob = "\n".join(texts)
for g in gold():
    line = g["line"].strip()
    if len(line) >= 12:
        check(line not in blob, f"gold line copied into src/aliases: {line[:60]!r}")
print(f"  scanned {len(files)} source file(s)")
finish("rules")
