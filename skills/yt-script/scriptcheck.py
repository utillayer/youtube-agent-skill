#!/usr/bin/env python3
"""scriptcheck.py - check a narration script is ready to be spoken, before anyone records it.

    python3 scriptcheck.py script.json              # {"text", "names", "sources"} or a plain .txt
    python3 scriptcheck.py script.txt --words 900-1500 --json

Errors (exit 1): length outside the target; a paragraph outside 30-75 words (one paragraph is one
breath-group, and one take for a voice model); characters that trip narrators and captions (digits,
semicolons, brackets, dashes, double quotes); a paragraph that stops mid-sentence; an opening that
scores under 60 on hookscore.py.
Warnings: sentences over 28 words; a capitalised word missing from "names" (often a second spelling
of a name); a name spelled two ways; no midpoint turn (a question or a "but" near the middle);
no sources listed.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hookscore import score as hookscore  # noqa: E402

COMMON = set("""a an and as at but by for from he her his i if in into is it its no nor not of on or our she so that the
their them then there they this those though to was we were what when where which while who why with you your yet
one two three four five six seven eight nine ten twelve twenty hundred thousand first last next now once
years later long before after every each all almost nobody many some here how even only still just""".split())
BAD = re.compile(r"[0-9;()\[\]—–\"“”]|--|(?<=\w)-(?=\s)|(?<=\s)-(?=\w)")

def load(path):
    if path.endswith(".json"):
        d = json.load(open(path, encoding="utf-8"))
        return d.get("text", ""), d.get("names", []), d.get("sources", [])
    return open(path, encoding="utf-8-sig").read(), [], []

def check(text, names=(), sources=(), lo=750, hi=1500, hook_min=60):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    errors, warns = [], []
    total = sum(len(p.split()) for p in paras)
    if not lo <= total <= hi: errors.append(f"length {total} words; target {lo}-{hi} (about {lo // 150}-{hi // 150} minutes)")
    names = set(names)
    seen = {}
    for i, p in enumerate(paras):
        n = len(p.split())
        if not 30 <= n <= 75: errors.append(f"paragraph {i}: {n} words (keep 30-75: one breath-group, one take)")
        bad = sorted(set(m.group(0) for m in BAD.finditer(p)))
        if bad: errors.append(f"paragraph {i}: {' '.join(bad)} - write numbers as words; no dashes, brackets, semicolons or double quotes")
        if not p.rstrip().endswith((".", "?", "!")): errors.append(f"paragraph {i}: ends mid-sentence")
        for s in re.split(r"(?<=[.?!])\s+", p):
            if len(s.split()) > 28: warns.append(f"paragraph {i}: a {len(s.split())}-word sentence - split it for the ear: '{s[:50]}...'")
        for w in re.findall(r"(?<=[a-z,] )([A-Z][a-z']+)", p):
            base = w[:-2] if w.endswith("'s") else w
            if base not in names and base.lower() not in COMMON:
                warns.append(f"paragraph {i}: '{base}' is capitalised but not in names")
            seen.setdefault(base.lower().rstrip("aeh"), set()).add(base)
    for k, forms in seen.items():
        if len(forms) > 1: warns.append(f"spelled more than one way: {', '.join(sorted(forms))}")
    if paras:
        # the hook is the first sentence or two - what is said in the first few seconds - not the paragraph
        hook = []
        for sent in re.split(r"(?<=[.?!])\s+", paras[0]):
            hook.append(sent)
            if len(" ".join(hook).split()) >= 14: break
        _, verdict, formula, _ = hookscore(" ".join(hook))
        if verdict < hook_min: errors.append(f"opening scores {verdict} on hookscore.py (need {hook_min}): '{' '.join(hook)[:70]}'")
        mid = paras[max(1, len(paras) * 2 // 5): max(2, len(paras) * 3 // 5)]
        if not any("?" in p or re.search(r"\b(but|yet|until|then)\b", p, re.I) for p in mid):
            warns.append("no turn near the middle - a question or a reversal around 45% resets attention")
    if not sources: warns.append("no sources listed")
    return {"words": total, "paragraphs": len(paras), "errors": errors, "warnings": warns}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script"); ap.add_argument("--words", default="750-1500", help="target length, e.g. 900-1500")
    ap.add_argument("--hook-min", type=int, default=60); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(a.script): ap.error(f"no such file: {a.script}")
    lo, hi = (int(x) for x in a.words.split("-"))
    text, names, sources = load(a.script)
    r = check(text, names, sources, lo, hi, a.hook_min)
    if a.json: print(json.dumps(r, indent=1)); sys.exit(1 if r["errors"] else 0)
    print(f"\n  {a.script}: {r['words']} words, {r['paragraphs']} paragraphs, {len(r['errors'])} errors, {len(r['warnings'])} warnings\n")
    for e in r["errors"]: print(f"    x  {e}")
    for w in r["warnings"]: print(f"    !  {w}")
    print()
    sys.exit(1 if r["errors"] else 0)

if __name__ == "__main__":
    main()
