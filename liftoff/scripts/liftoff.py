#!/usr/bin/env python3
"""liftoff - build Grok Bot templates people keep using, and ship them safely.

Zero dependencies. Python 3.8+.

A template is a folder:
  BOT.md                          identity, rules, first message
  ROUTINES.md                     schedules (optional, but you want one)
  skills/<category>/<slug>/SKILL.md

Commands
  score DIR             Stickiness Score (0-100): will people come back to this bot?
  scan DIR              Leak Scan: secrets and personal data that would ship with the share link
  post FILE             Launch Check: is the X launch post ready to go?
  check DIR [--post F]  All of the above in one report (exit 1 if anything blocks sharing)
  pack DIR [-o OUT]     Build TEMPLATE_CARD.md: every block to paste into Grok Bot, in order
  new NAME [-o DIR]     Scaffold a new template that already passes the structure checks

Add --json to score, scan, post or check for machine output.
"""

import argparse
import json
import os
import re
import shutil
import signal
import sys

# ---------------------------------------------------------------- terminal ---

USE_COLOR = (sys.stdout.isatty() or os.environ.get("FORCE_COLOR")) and os.environ.get("NO_COLOR") is None


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(t): return c(t, "1")
def dim(t): return c(t, "2")
def red(t): return c(t, "31")
def green(t): return c(t, "32")
def yellow(t): return c(t, "33")
def cyan(t): return c(t, "36")
def magenta(t): return c(t, "35")


CROSS, CHECK, WARN, ARROW = "✗", "✓", "!", "→"


def bar(value, total, width=24):
    filled = round(width * value / total) if total else 0
    paint = green if value == total else yellow if value else red
    return paint("\u2588" * filled) + dim("\u2591" * (width - filled))


def tone(score):
    return green if score >= 80 else yellow if score >= 60 else red

# ---------------------------------------------------------------- template ---


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def frontmatter(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fields = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip("\"'")
    return fields, text[end + 4:]


class Template:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        if not os.path.isdir(self.root):
            sys.exit(f"liftoff: {root} is not a folder")
        self.bot = self._opt("BOT.md")
        self.routines = self._opt("ROUTINES.md")
        self.skills = []
        skills_dir = os.path.join(self.root, "skills")
        for dirpath, _, files in sorted(os.walk(skills_dir)):
            if "SKILL.md" in files:
                path = os.path.join(dirpath, "SKILL.md")
                fm, body = frontmatter(read(path))
                self.skills.append({
                    "path": os.path.relpath(path, self.root),
                    "slug": os.path.basename(dirpath),
                    "fm": fm or {},
                    "has_fm": fm is not None,
                    "body": body,
                })

    def _opt(self, name):
        path = os.path.join(self.root, name)
        return read(path) if os.path.isfile(path) else ""

    def files(self):
        for dirpath, _, files in sorted(os.walk(self.root)):
            for name in sorted(files):
                if name.endswith((".md", ".txt", ".json", ".yaml", ".yml")):
                    path = os.path.join(dirpath, name)
                    yield os.path.relpath(path, self.root), read(path)

    def all_text(self):
        return "\n".join([self.bot, self.routines] + [s["body"] + "\n" + json.dumps(s["fm"]) for s in self.skills])

    def first_message(self):
        m = re.search(r"^#+\s*first message\s*$(.*?)(?=^#+\s|\Z)", self.bot, re.I | re.M | re.S)
        return m.group(1).strip() if m else ""

# ------------------------------------------------------- Stickiness Score ---
# Grok Bot Creator Rewards look at how many people use a template and how
# consistently they keep using it. Each check below is one habit of bots that
# people come back to. It is a heuristic, not X's formula.

SCHEDULE_RE = re.compile(
    r"\b(daily|every\s+(day|morning|evening|night|hour|week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"|weekly|hourly|weekdays?|mondays?|tuesdays?|wednesdays?|thursdays?|fridays?|saturdays?|sundays?|cron"
    r"|\d{1,2}:\d{2}|t-\s?\d+|before (each|every|any)|after (each|every|any))\b", re.I)
FREQUENT_RE = re.compile(r"\b(daily|every\s+(day|morning|evening|night|hour)|hourly|weekdays?|\d{1,2}:\d{2}|t-\s?\d+)\b", re.I)
LIVE_RE = re.compile(r"\b(web search|x search|live search|search live|real[- ]time|latest|breaking|fresh|today'?s|right now|news|prices?|live)\b", re.I)
MEMORY_RE = re.compile(r"\b(remember|memory|memories|preferences?|next time|learns?|keep track|history of)\b", re.I)
OFF_RE = re.compile(r"\b(opt[- ]in|opt[- ]out|mute|turn (it )?off|unsubscribe|pause|send less|less often|only if|spam)\b"
                    r"|\bsays? [\"\u201c]?(less|stop|fewer)\b", re.I)
TRIGGER_RE = re.compile(r"\buse (it )?when\b|\bwhen the user\b", re.I)
EXAMPLE_RE = re.compile(r"\btry\b|[\"“][^\"”]{6,}[\"”]", re.I)
NO_TRAVEL = [
    (re.compile(r"\bmcp server\b(?!s? (don'?t|do not|won'?t))", re.I), "depends on an MCP server (private ones don't travel)"),
    (re.compile(r"\b(localhost|127\.0\.0\.1)\b", re.I), "points at localhost (won't exist for other people)"),
    (re.compile(r"\b(my computer|my laptop|my desktop|my machine)\b", re.I), "depends on your computer"),
    (re.compile(r"\b(log ?in to|logged[- ]in|my account|sign in to)\b", re.I), "depends on a login (logins don't travel)"),
    (re.compile(r"\b(run|execute) (the |my )?(script|\w+\.py|\w+\.sh)\b", re.I), "depends on custom code (doesn't travel)"),
]


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def score_template(t):
    checks = []

    def add(key, name, got, total, ok_msg, fix):
        checks.append({"key": key, "name": name, "points": got, "max": total,
                       "ok": got == total, "detail": ok_msg if got == total else fix})

    sched = SCHEDULE_RE.findall(t.routines)
    frequent = FREQUENT_RE.search(t.routines)
    got = (15 if sched else 0) + (10 if frequent else 0)
    add("routine", "Comes back on its own", got, 25,
        "has a daily-or-more routine" if got == 25 else "",
        "add a daily routine in ROUTINES.md"
        if not sched else "routines are weekly or rarer: add a daily one")

    live = set(m.lower() if isinstance(m, str) else m[0].lower() for m in LIVE_RE.findall(t.all_text()))
    got = 15 if len(live) >= 2 else 8 if live else 0
    add("live", "Fresh every day", got, 15, "uses live data",
        "pull live web/X data so every day is new")

    # Full points for 2+ memory cues, or one cue that names what to remember.
    mem = MEMORY_RE.findall(t.bot)
    specific = any(MEMORY_RE.search(s) and (s.count(",") >= 2 or " and " in s)
                   for s in re.split(r"(?<=[.!?])\s|\n", t.bot))
    got = 15 if len(mem) >= 2 or specific else 8 if mem else 0
    add("memory", "Remembers the user", got, 15, "keeps user preferences",
        "say what to remember: timezone, interests...")

    fm = t.first_message()
    got = (10 if fm else 0) + (5 if fm and "?" in fm and EXAMPLE_RE.search(fm) else 0)
    add("first", "30-second first win", got, 15, "first message asks + shows a prompt to try",
        "add a '## First message' section" if not fm else "first message: ask 1 question + 1 prompt to try")

    n = len(t.skills)
    got = 10 if 1 <= n <= 3 else 5 if 4 <= n <= 5 else 0
    add("focus", "Does one job well", got, 10, f"{n} focused skill{'s' if n != 1 else ''}",
        "add 1-3 skills" if n == 0 else f"{n} skills: cut to 1-3")

    if t.skills:
        good = sum(1 for s in t.skills if len(s["fm"].get("description", "")) >= 40
                   and (s["fm"].get("when-to-use") or TRIGGER_RE.search(s["fm"].get("description", ""))))
        got = round(10 * good / len(t.skills))
    else:
        good, got = 0, 0
    add("triggers", "Skills trigger reliably", got, 10, "every skill says when to use it",
        "no skills to trigger yet" if not t.skills else
        f"{len(t.skills) - good} skill(s) don't say when to use them")

    got = 5 if OFF_RE.search(t.all_text()) else 0
    add("off", "Easy to turn down", got, 5, "users can mute alerts",
        "let users mute alerts or ask for less")

    wc = len(words(t.bot))
    got = 5 if 0 < wc <= 500 else 2 if 0 < wc <= 800 else 0
    add("brief", "Short instructions", got, 5, f"BOT.md is {wc} words",
        "add BOT.md" if wc == 0 else f"BOT.md is {wc} words: cut to 500")

    penalties = []
    for rel, text in [("BOT.md", t.bot), ("ROUTINES.md", t.routines)] + [(s["path"], s["body"]) for s in t.skills]:
        for rx, why in NO_TRAVEL:
            if rx.search(text):
                penalties.append({"file": rel, "why": why})
    penalty = min(20, 10 * len(penalties))

    unfilled = sum(text.count("[FILL:") for text in [t.bot, t.routines] + [s["body"] + json.dumps(s["fm"]) for s in t.skills])
    total = max(0, sum(ch["points"] for ch in checks) - penalty)
    if unfilled:
        total = min(total, 40)
    verdict = ("Unfinished: fill the [FILL] blanks" if unfilled else "Built to stick" if total >= 80 else "Close: fix the misses" if total >= 60
               else "One-and-done risk")
    return {"score": total, "verdict": verdict, "checks": checks, "penalties": penalties, "penalty": penalty,
            "unfilled": unfilled}


def print_score(t, r):
    print()
    print(bold("  STICKINESS SCORE  ") + tone(r["score"])(bold(f"{r['score']}/100")) + "  " + tone(r["score"])(r["verdict"]))
    print(dim(f"  {os.path.basename(t.root)}  {ARROW}  will people come back tomorrow?"))
    print()
    for ch in r["checks"]:
        mark = green(CHECK) if ch["ok"] else (yellow(WARN) if ch["points"] else red(CROSS))
        print(f"  {mark} {ch['name']:<26} {bar(ch['points'], ch['max'], 12)} {ch['points']:>2}/{ch['max']:<2}  "
              + (dim(ch["detail"]) if ch["ok"] else ch["detail"]))
    for p in r["penalties"]:
        print(f"  {red(CROSS)} {'Won’t travel':<26} {' ' * 12} {red('-10')}    {p['file']}: {p['why']}")
    if r["unfilled"]:
        print(f"  {red(CROSS)} {'Unfinished':<26} {' ' * 12} {red('max 40')} {r['unfilled']} [FILL: …] blank(s) left")
    print()

# ---------------------------------------------------------------- Leak Scan ---

LEAKS = [
    ("api key", re.compile(r"\b(?:sk|xai|sk-ant|sk-proj)-[A-Za-z0-9_-]{16,}")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("aws key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack token", re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}")),
    ("bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}")),
    ("secret value", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*['\"]?[A-Za-z0-9._/+-]{10,}")),
    ("webhook url", re.compile(r"https://(?:hooks\.slack\.com|discord(?:app)?\.com/api/webhooks)/\S+")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")),
    ("phone number", re.compile(r"(?<![\w.])\+?\d{1,3}[ .-]?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")),
    ("private address", re.compile(r"\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")),
    ("private doc link", re.compile(r"https://(?:docs\.google\.com|drive\.google\.com|www\.notion\.so|[\w-]+\.notion\.site)/\S+")),
]
SAFE_EMAIL = re.compile(r"@(example\.(com|org)|users\.noreply\.github\.com)$", re.I)


def mask(s):
    m = re.match(r"https?://([^/]+)", s)
    if m:
        return m.group(1) + "/\u2026"
    return s[:4] + "\u2026" if len(s) > 6 else "\u2026"


def scan_template(t):
    hits = []
    for rel, text in t.files():
        in_code = False
        for n, line in enumerate(text.splitlines(), 1):
            for kind, rx in LEAKS:
                for m in rx.finditer(line):
                    val = m.group(0)
                    if kind == "email" and SAFE_EMAIL.search(val):
                        continue
                    hits.append({"file": rel, "line": n, "kind": kind, "preview": mask(val)})
    for p in score_template(t)["penalties"]:
        hits.append({"file": p["file"], "line": 0, "kind": "won't travel", "preview": p["why"], "warn": True})
    blocking = [h for h in hits if not h.get("warn")]
    return {"safe": not blocking, "leaks": len(blocking), "warnings": len(hits) - len(blocking), "hits": hits}


def print_scan(t, r):
    print()
    if r["safe"]:
        print(bold("  LEAK SCAN  ") + green(bold(f"{CHECK} SAFE TO SHARE")) + dim(f"  ({sum(1 for _ in t.files())} files checked)"))
    else:
        print(bold("  LEAK SCAN  ") + red(bold(f"{CROSS} FIX FIRST: {r['leaks']} leak{'s' if r['leaks'] != 1 else ''}")))
        print(dim("  everything below ships inside the share link unless you remove it"))
    print()
    for h in r["hits"]:
        where = f"{h['file']}:{h['line']}" if h["line"] else h["file"]
        if h.get("warn"):
            print(f"  {yellow(WARN)} {where:<38} {yellow(h['kind'].ljust(14))} {h['preview']}")
        else:
            print(f"  {red(CROSS)} {where:<38} {red(h['kind'].ljust(14))} {h['preview']}")
    if r["hits"]:
        print()

# ------------------------------------------------------------- Launch Check ---

HYPE = re.compile(r"\b(game[- ]?changer|revolutionary|unlock|leverage|delve|seamless|cutting[- ]edge|insane|crazy|guaranteed|passive income|get rich|10x your)\b", re.I)
MONEY = re.compile(r"\$\s?\d[\d,.]*\s?[kKmM]?|\b\d[\d,.]*\s?(dollars|usd)\b", re.I)
URL = re.compile(r"https?://\S+|\b(?:x\.ai|grok\.com|x\.com)/\S+", re.I)
PLACEHOLDER = re.compile(r"\[(?:NEED|TODO|LINK|SHARE[_ ]LINK)[^\]]*\]", re.I)


def check_post(text):
    lines = [l for l in text.strip().splitlines()]
    first = lines[0].strip() if lines else ""
    items = []

    def add(name, ok, detail, blocking=True):
        items.append({"name": name, "ok": ok, "detail": detail, "blocking": blocking})

    add("Share link in the post", bool(URL.search(text)) and not PLACEHOLDER.search(text),
        "found" if URL.search(text) and not PLACEHOLDER.search(text) else
        "program rule: the public post must include the template's share link")
    add("Hook under 110 chars", 0 < len(first) <= 110, f"{len(first)} chars")
    dash = "—" in text or " – " in text
    add("No em dashes", not dash, "use a period, colon or → instead" if dash else "clean")
    hype = sorted(set(m.lower() for m in HYPE.findall(text)))
    add("No hype words", not hype, "clean" if not hype else "remove: " + ", ".join(hype))
    money = MONEY.findall(text)
    add("Money claims have proof", not money,
        "none" if not money else f"{len(money)} money figure(s): attach a screenshot or cut them", blocking=False)
    add("Paid partnership label", None, "turn it on in X before posting (program rule, can't be checked from text)", blocking=False)
    ready = all(i["ok"] for i in items if i["blocking"])
    return {"ready": ready, "items": items}


def print_post(r):
    print()
    print(bold("  LAUNCH CHECK  ") + (green(bold(f"{CHECK} READY TO POST")) if r["ready"] else red(bold(f"{CROSS} NOT YET"))))
    print()
    for i in r["items"]:
        mark = cyan(ARROW) if i["ok"] is None else green(CHECK) if i["ok"] else (red(CROSS) if i["blocking"] else yellow(WARN))
        print(f"  {mark} {i['name']:<26} " + (dim(i["detail"]) if i["ok"] else i["detail"]))
    print()

# --------------------------------------------------------------------- pack ---


def pack(t, out):
    lines = [f"# Template card: {os.path.basename(t.root)}", "",
             "Paste these into Grok Bot in order. Generated by liftoff.", ""]
    lines += ["## 1. Instructions (paste into the bot)", "", "```markdown", t.bot.strip(), "```", ""]
    lines += ["## 2. Skills (add each as its own skill)", ""]
    for s in t.skills:
        lines += [f"### /{s['slug']}", "", f"`{s['path']}`", "", "```markdown", read(os.path.join(t.root, s["path"])).strip(), "```", ""]
    if t.routines:
        lines += ["## 3. Routines", ""]
        prompts = re.findall(r"\*\*(.+?)\*\*\s*\n```\w*\n(.*?)```", t.routines, re.S)
        if prompts:
            for name, body in prompts:
                lines += [f"### {name}", "", "```", body.strip(), "```", ""]
        else:
            lines += [t.routines.strip(), ""]
    r, s = score_template(t), scan_template(t)
    lines += ["## 4. Before you share", "",
              f"- Stickiness Score: **{r['score']}/100** ({r['verdict']})",
              f"- Leak Scan: **{'safe to share' if s['safe'] else 'FIX FIRST'}**",
              "- Settings, Share as template, Create public link",
              "- Post it publicly on X with the link, and turn on the paid partnership label", ""]
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "TEMPLATE_CARD.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path, s["safe"]

# ---------------------------------------------------------------------- new ---

NEW_BOT = """# {name}

You are **{name}**, a Grok Bot that [FILL: ONE JOB, ONE SENTENCE].

## Who you serve

[FILL: Who uses this and what they want without having to ask.]

## What you do

1. **[FILL: Main job].** Use `/{slug}` to [FILL: do the job] with live web and X search.
2. **Daily brief.** When the routine runs, send the brief from ROUTINES.md.

## Rules

- Remember the user's preferences ([FILL: timezone, interests, voice]) and use them next time.
- Never invent facts. Use live search and name your source.
- Short by default. Lead with the answer.
- If the user says "less", send less often. Never spam.

## First message

> {name} here. [FILL: What you do in one line.]
> Quick question: [FILL: the one preference you need]?
> Then try: "[FILL: an example prompt]"
"""
NEW_ROUTINES = """# {name} routines

**Daily brief**
```
Every day at 08:00 my time, run /{slug} and send a short brief: [FILL: what goes in it]. If there's nothing new, say so in one line.
```
"""
NEW_SKILL = """---
name: {slug}
description: [FILL: What this skill does]. Use when the user asks [FILL: trigger phrases] or when the daily routine runs.
when-to-use: "[FILL: phrase 1]", "[FILL: phrase 2]"
---

# {name}

## Steps

1. Search live (web + X). Prefer official sources.
2. [FILL: Do the job.]
3. Answer in the format below. Lead with the most important item.

## Format

```
[FILL: output format]
```
"""


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "my-bot"


def new(name, out):
    slug = slugify(name)
    root = os.path.join(out, slug)
    if os.path.exists(root):
        sys.exit(f"liftoff: {root} already exists")
    skill_dir = os.path.join(root, "skills", "core", slug)
    os.makedirs(skill_dir)
    for path, tpl in [(os.path.join(root, "BOT.md"), NEW_BOT), (os.path.join(root, "ROUTINES.md"), NEW_ROUTINES),
                      (os.path.join(skill_dir, "SKILL.md"), NEW_SKILL)]:
        with open(path, "w", encoding="utf-8") as f:
            f.write(tpl.format(name=name, slug=slug))
    return root

# --------------------------------------------------------------------- main ---


def main(argv=None):
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser(prog="liftoff", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("score", "scan"):
        p = sub.add_parser(cmd)
        p.add_argument("dir")
        p.add_argument("--json", action="store_true")
    p = sub.add_parser("post")
    p.add_argument("file")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("check")
    p.add_argument("dir")
    p.add_argument("--post")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("pack")
    p.add_argument("dir")
    p.add_argument("-o", "--out")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("new")
    p.add_argument("name")
    p.add_argument("-o", "--out", default=".")
    a = ap.parse_args(argv)

    if a.cmd == "score":
        t = Template(a.dir)
        r = score_template(t)
        print(json.dumps(r, indent=2)) if a.json else print_score(t, r)
        return 0
    if a.cmd == "scan":
        t = Template(a.dir)
        r = scan_template(t)
        print(json.dumps(r, indent=2)) if a.json else print_scan(t, r)
        return 0 if r["safe"] else 1
    if a.cmd == "post":
        r = check_post(read(a.file))
        print(json.dumps(r, indent=2)) if a.json else print_post(r)
        return 0 if r["ready"] else 1
    if a.cmd == "check":
        t = Template(a.dir)
        sc, sn = score_template(t), scan_template(t)
        po = check_post(read(a.post)) if a.post else None
        if a.json:
            print(json.dumps({"score": sc, "scan": sn, "post": po}, indent=2))
        else:
            print_score(t, sc)
            print_scan(t, sn)
            if po:
                print_post(po)
        return 0 if sn["safe"] and (po is None or po["ready"]) else 1
    if a.cmd == "pack":
        t = Template(a.dir)
        if not scan_template(t)["safe"] and not a.force:
            print_scan(t, scan_template(t))
            print(red("  not packing: fix the leaks first (or --force)"))
            return 1
        path, _ = pack(t, a.out or t.root)
        print(f"  {green(CHECK)} wrote {path}")
        return 0
    if a.cmd == "new":
        root = new(a.name, a.out)
        print(f"  {green(CHECK)} created {root}")
        print(dim(f"  fill every [FILL: …], then: liftoff.py check {root}"))
        return 0


if __name__ == "__main__":
    sys.exit(main())
