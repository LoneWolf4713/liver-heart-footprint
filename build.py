#!/usr/bin/env python3
"""build.py: the state + gate tool for coding packages (builds whose code nobody will read).

Copy this file UNCHANGED into the project. The architect writes order.json (the tasks, their allowed files and
their acceptance checks) and the acceptance tests. The builder session writes the code. This tool decides
whether a task is done. It runs the checks itself, so "it works" is never self-reported.

Gates for `done`, all run by the tool:
  1. protected files (acceptance tests, order.json, build.py) are unchanged
  2. the task changed only files matching its allowed globs
  3. no forbidden pattern was added
  4. the task's acceptance commands pass
  5. every earlier finished task's acceptance commands, and the full test command, still pass
A task gets `max_attempts` tries at `done` (default 2), then it is recorded as FAILED and the build moves on.

Commands: init | next | check | done | note | status | report
Stdlib only. Needs git.
"""
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ORDER = os.path.join(ROOT, "order.json")
STATE_DIR = os.path.join(ROOT, ".build")
STATE = os.path.join(STATE_DIR, "state.json")
REPORT = os.path.join(ROOT, "BUILD_REPORT.md")
TOOL = "python3 build.py"


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load_order():
    try:
        with open(ORDER) as f:
            o = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        die(f"cannot read order.json: {e}")
    o.setdefault("max_attempts", 2)
    o.setdefault("timeout", 600)
    o.setdefault("forbidden", [])
    o.setdefault("protected", [])
    o["protected"] = sorted(set(o["protected"]) | {"order.json", "build.py"})
    return o


def load_state():
    if not os.path.exists(STATE):
        die(f"not initialised. Run: {TOOL} init")
    with open(STATE) as f:
        return json.load(f)


def save_state(s):
    with open(STATE, "w") as f:
        json.dump(s, f, indent=1)


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        die(f"git {' '.join(args)} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def sh(cmd, timeout):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {timeout}s: {cmd}"


def match(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def all_files():
    out = git("ls-files", "--cached", "--others", "--exclude-standard")
    return sorted(p for p in out.splitlines() if p and not p.startswith(".build/"))


def protected_hashes(order):
    h = {}
    for p in all_files():
        if match(p, order["protected"]):
            with open(os.path.join(ROOT, p), "rb") as f:
                h[p] = hashlib.sha256(f.read()).hexdigest()
    return h


def changed_since(base):
    tracked = git("diff", "--name-only", base).splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted({p for p in tracked + untracked if p and not p.startswith(".build/")})


def added_lines(base, path):
    if path in git("ls-files", "--others", "--exclude-standard").splitlines():
        try:
            with open(os.path.join(ROOT, path), errors="ignore") as f:
                return f.read().splitlines()
        except OSError:
            return []
    diff = git("diff", "-U0", base, "--", path, check=False)
    return [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]


def task_by_id(order, tid):
    for t in order["tasks"]:
        if t["id"] == tid:
            return t
    die(f"unknown task {tid}")


def current(order, s):
    for t in order["tasks"]:
        if s["tasks"].get(t["id"], {}).get("status") not in ("done", "failed"):
            return t
    return None


def tail(text, n=40):
    lines = text.strip().splitlines()
    return "\n".join(lines[-n:])


# ----------------------------------------------------------------- gates

def run_gates(order, s, t):
    """Return a list of (gate, ok, detail)."""
    st = s["tasks"][t["id"]]
    res = []
    # 1. protected files
    now_h = protected_hashes(order)
    touched = sorted(p for p in set(s["protected"]) | set(now_h) if s["protected"].get(p) != now_h.get(p))
    res.append(("protected files unchanged", not touched,
                "modified, added or deleted: " + ", ".join(touched) if touched else "ok"))
    # 2. scope
    changed = changed_since(st["base"])
    allowed = t.get("files", []) + order.get("always_allowed", [])
    outside = [p for p in changed if not match(p, allowed) and p not in s["protected"]]
    res.append(("only this task's files changed", not outside,
                f"outside {allowed}: " + ", ".join(outside) if outside else f"{len(changed)} file(s) changed"))
    # 3. forbidden patterns
    hits = []
    for rule in order["forbidden"]:
        rx = re.compile(rule["pattern"])
        for p in changed:
            if match(p, [rule.get("files", "*")]):
                for line in added_lines(st["base"], p):
                    if rx.search(line):
                        hits.append(f"{p}: {rule['message']} ({line.strip()[:80]})")
    res.append(("no forbidden patterns", not hits, "; ".join(hits[:5]) if hits else "ok"))
    # 4. this task's acceptance
    for a in t.get("accept", []):
        code, out = sh(a["cmd"], order["timeout"])
        ok = code == a.get("expect_exit", 0) and (not a.get("expect_output") or re.search(a["expect_output"], out))
        res.append((f"acceptance: {a['cmd']}", bool(ok), tail(out, 25) if not ok else "passed"))
    # 5. regression: earlier finished tasks + full suite
    for prev in order["tasks"]:
        if s["tasks"].get(prev["id"], {}).get("status") == "done":
            for a in prev.get("accept", []):
                code, out = sh(a["cmd"], order["timeout"])
                ok = code == a.get("expect_exit", 0) and (not a.get("expect_output") or re.search(a["expect_output"], out))
                if not ok:
                    res.append((f"regression ({prev['id']}): {a['cmd']}", False, tail(out, 25)))
    if order.get("test_cmd"):
        code, out = sh(order["test_cmd"], order["timeout"])
        res.append((f"full suite: {order['test_cmd']}", code == 0, tail(out, 25) if code else "passed"))
    return res


def print_gates(res):
    for g, ok, detail in res:
        print(f"  {'PASS' if ok else 'FAIL'}  {g}" + ("" if ok and detail in ("ok", "passed") else f"\n        {detail.replace(chr(10), chr(10) + '        ')}"))


# ----------------------------------------------------------------- commands

def cmd_init(args):
    order = load_order()
    if os.path.exists(STATE):
        die("already initialised (.build/state.json exists)")
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=ROOT, capture_output=True).returncode:
        git("init", "-q")
    os.makedirs(STATE_DIR, exist_ok=True)
    gi = os.path.join(ROOT, ".gitignore")
    lines = open(gi).read().splitlines() if os.path.exists(gi) else []
    missing = [x for x in (".build/", "__pycache__/", "*.pyc") if x not in lines]
    if missing:
        with open(gi, "a") as f:
            f.write(("\n" if lines and lines[-1] else "") + "\n".join(missing) + "\n")
    git("add", "-A")
    git("-c", "user.name=build", "-c", "user.email=build@localhost", "commit", "-q", "--allow-empty", "-m", "build: baseline")
    s = {"started": now(), "protected": protected_hashes(order), "tasks": {}, "notes": []}
    save_state(s)
    print(f"Initialised. {len(order['tasks'])} tasks; {len(s['protected'])} protected files locked. Run: {TOOL} next")


def cmd_next(args):
    order, s = load_order(), load_state()
    t = current(order, s)
    if not t:
        print(f"ALL TASKS FINISHED. Run `{TOOL} report`, then tell the user: 'Build finished — see BUILD_REPORT.md.'")
        return
    st = s["tasks"].setdefault(t["id"], {"status": "in_progress", "attempts": 0, "started": now(),
                                         "base": git("rev-parse", "HEAD").strip()})
    save_state(s)
    P = print
    P("=" * 78 + f"\n{order['name']} — BUILD TASK {t['id']}: {t['title']}\n" + "=" * 78)
    P(f"\n## GOAL OF THE WHOLE BUILD\n{order['goal']}")
    if order.get("rules"):
        P("\n## RULES (non-negotiable)")
        for r in order["rules"]:
            P(f"  - {r}")
    P(f"""
## HOW THIS WORKS
- You do exactly THIS task. Other tasks are listed only so you don't touch their work.
- You may change ONLY files matching: {t.get('files', []) + order.get('always_allowed', [])}
- NEVER edit protected files: {order['protected']}. They define "done"; edit your code, not the tests.
- Read the code that exists before changing it. Never assume a function or file exists; check.
- When you think the task works: `{TOOL} check` (runs every gate, changes nothing), then `{TOOL} done`.
- `done` runs the gates itself. You get {order['max_attempts']} `done` attempts; after that the task is recorded as
  FAILED, honestly, and the build moves on. Don't game the checks; fix the code.
- Write free text through files, never as shell arguments. Save progress with `{TOOL} note --file f.txt`.""")
    P("\n## ALL TASKS")
    for x in order["tasks"]:
        xs = s["tasks"].get(x["id"], {})
        files = f" files: {xs['files']}" if xs.get("files") else ""
        P(f"  {x['id']} [{xs.get('status', 'pending').upper()}] {x['title']}{files}")
    P(f"\n## THIS TASK: {t['id']} — {t['title']}  (attempts used: {st['attempts']}/{order['max_attempts']})\n{t['spec']}")
    if t.get("accept"):
        P("\nDone means these pass (run by the tool):")
        for a in t["accept"]:
            P(f"  $ {a['cmd']}" + (f"   (output must match /{a['expect_output']}/)" if a.get("expect_output") else ""))
    if order.get("test_cmd"):
        P(f"  $ {order['test_cmd']}   (full suite, must stay green)")
    if st.get("last_failure"):
        P("\n## LAST `done` FAILED BECAUSE\n" + st["last_failure"])
    if s["notes"]:
        P("\n## NOTES FROM EARLIER SESSIONS")
        for n in s["notes"][-8:]:
            P(f"  [{n['at']}] {n['task']}: {n['text']}")


def cmd_check(args):
    order, s = load_order(), load_state()
    t = current(order, s)
    if not t or t["id"] not in s["tasks"]:
        die(f"no task in progress. Run: {TOOL} next")
    print(f"Gates for {t['id']} (dry run — nothing is recorded):")
    res = run_gates(order, s, t)
    print_gates(res)
    print("ALL GATES PASS — run `done`." if all(ok for _, ok, _ in res) else "Some gates fail — fix the code, not the tests.")


def cmd_done(args):
    order, s = load_order(), load_state()
    t = current(order, s)
    if not t or t["id"] not in s["tasks"]:
        die(f"no task in progress. Run: {TOOL} next")
    st = s["tasks"][t["id"]]
    st["attempts"] += 1
    res = run_gates(order, s, t)
    print(f"Gates for {t['id']} (attempt {st['attempts']}/{order['max_attempts']}):")
    print_gates(res)
    log = os.path.join(STATE_DIR, f"{t['id']}-attempt{st['attempts']}.txt")
    with open(log, "w") as f:
        f.write("\n".join(f"{'PASS' if ok else 'FAIL'} {g}\n{d}\n" for g, ok, d in res))
    files = changed_since(st["base"])
    if all(ok for _, ok, _ in res):
        st.update(status="done", finished=now(), files=files, gates=[[g, ok] for g, ok, _ in res], last_failure="")
        save_state(s)
        git("add", "-A")
        git("-c", "user.name=build", "-c", "user.email=build@localhost", "commit", "-q", "--allow-empty",
            "-m", f"{t['id']}: {t['title']}")
        print(f"\nTASK {t['id']} DONE and committed.")
    else:
        st["last_failure"] = "\n".join(f"- {g}: {d}" for g, ok, d in res if not ok)[:3000]
        if st["attempts"] >= order["max_attempts"]:
            # Roll the failed work back so it can't break later tasks; keep it as a patch for reference.
            patch = os.path.join(STATE_DIR, f"{t['id']}-failed.patch")
            git("add", "-A")
            with open(patch, "w") as f:
                f.write(git("diff", "--cached", st["base"], check=False))
            git("reset", "-q", "--hard", st["base"])
            git("clean", "-q", "-fd", "-e", ".build")
            st.update(status="failed", finished=now(), files=files, gates=[[g, ok] for g, ok, _ in res])
            save_state(s)
            print(f"\nTASK {t['id']} FAILED after {st['attempts']} attempts. Recorded honestly; its changes were "
                  f"rolled back (kept in .build/{t['id']}-failed.patch). The build moves on.")
        else:
            save_state(s)
            print(f"\nNot done. Fix the code (not the tests) and run `done` again — "
                  f"{order['max_attempts'] - st['attempts']} attempt(s) left.")
            sys.exit(1)
    nxt = current(order, s)
    if not nxt:
        cmd_report(args)
        print("ALL TASKS FINISHED. Tell the user exactly: 'Build finished — see BUILD_REPORT.md.'")
    elif order.get("chain_tasks"):
        print(f"Next: {nxt['id']}. This order chains small tasks: run `{TOOL} next` and continue in this session.")
    else:
        print("STOP NOW — tell the user exactly: 'Task done — open a new session for the next one.'")


def cmd_note(args):
    order, s = load_order(), load_state()
    t = current(order, s)
    text = open(args.file).read().strip() if args.file else (args.text or "")
    if not text:
        die("give the note as text or --file")
    s["notes"].append({"at": now()[:16], "task": t["id"] if t else "-", "text": text[:1000]})
    save_state(s)
    print("note saved")


def cmd_status(args):
    order, s = load_order(), load_state()
    for t in order["tasks"]:
        x = s["tasks"].get(t["id"], {})
        print(f"{t['id']} {x.get('status', 'pending'):<12} attempts {x.get('attempts', 0)}  {t['title']}")


def cmd_report(args):
    order, s = load_order(), load_state()
    L = ["<!-- GENERATED by `python3 build.py report` from .build/ — written by the tool, not the builder. -->\n",
         f"# {order['name']} — build report\n", f"Goal: {order['goal']}\n", "| Task | Status | Attempts | Files changed |",
         "|---|---|---|---|"]
    for t in order["tasks"]:
        x = s["tasks"].get(t["id"], {})
        L.append(f"| {t['id']} {t['title']} | {x.get('status', 'pending').upper()} | {x.get('attempts', 0)} | "
                 f"{', '.join(x.get('files', [])) or '—'} |")
    not_done = [t for t in order["tasks"] if s["tasks"].get(t["id"], {}).get("status") != "done"]
    L.append("\n## Not done\n")
    L += [f"- **{t['id']} {t['title']}** — {s['tasks'].get(t['id'], {}).get('status', 'pending')}: "
          + (s["tasks"].get(t["id"], {}).get("last_failure", "")[:600].replace("\n", " ") or "not started")
          for t in not_done] or ["- nothing"]
    L.append("\n## Gate results (as run by the tool)\n")
    for t in order["tasks"]:
        x = s["tasks"].get(t["id"], {})
        for g, ok in x.get("gates", []):
            L.append(f"- {t['id']}: {'PASS' if ok else 'FAIL'} — {g}")
    L.append("\nRaw gate output per attempt: `.build/<task>-attempt<N>.txt`.")
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"wrote {os.path.basename(REPORT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("init", cmd_init), ("next", cmd_next), ("check", cmd_check), ("done", cmd_done),
                     ("status", cmd_status), ("report", cmd_report)):
        sub.add_parser(name).set_defaults(fn=fn)
    p = sub.add_parser("note"); p.add_argument("text", nargs="?"); p.add_argument("--file"); p.set_defaults(fn=cmd_note)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
