#!/usr/bin/env python3
"""sourcekit.py - find your way around a long primary source, with line numbers you can cite.

    python3 sourcekit.py index source.txt                      # sections -> source.index.json
    python3 sourcekit.py index source.txt --heading "^CANTO [IVXLC]+"
    python3 sourcekit.py find  source.txt "golden deer"        # every match, with section and line
    python3 sourcekit.py show  source.txt "Canto XLV"          # print one section, numbered
    python3 sourcekit.py show  source.txt 32700-32790          # print a line range, numbered

Works on any plain-text source: a Gutenberg translation, a court transcript, a public-domain
history. Sections are found from heading lines (BOOK, PART, CHAPTER, CANTO, SECTION, ACT, or your
own --heading pattern), so a script can cite "Book III, Canto XLV, lines 32700-32790" and a fact
checker can open exactly those lines.
"""
import argparse, json, os, re, sys

DEFAULT = r"^\s*(BOOK|PART|CHAPTER|CANTO|SECTION|ACT|SCENE|BOOK THE|CHAP\.?)\b[ .]*([IVXLCDM]+|\d+|[A-Z]+)\b.*$"

def read(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh: return fh.read().splitlines()

def index(lines, heading=None):
    """[{title, level, start, end}] with 1-based inclusive line numbers. A section ends where the
    next heading of the same or a higher level begins."""
    rx = re.compile(heading or DEFAULT, re.I if not heading else 0)
    found = [(n, line.strip()) for n, line in enumerate(lines, 1) if line.strip() and len(line.strip()) < 90 and rx.match(line.strip())]
    nonblank = [n for n, l in enumerate(lines, 1) if l.strip()]
    nxt = {a: b for a, b in zip(nonblank, nonblank[1:])}
    starts = {n for n, _ in found}
    heads = []
    for n, s in found:
        # a heading followed straight by another heading is a table-of-contents line, not a section
        if nxt.get(n) in starts and not s.split()[0].upper().rstrip(".") in ("BOOK", "PART"): continue
        word = s.split()[0].upper().rstrip(".")
        level = 0 if word in ("BOOK", "PART") else 1
        heads.append({"title": s, "level": level, "start": n})
    # drop book headings that only head a table of contents (no section of their own follows)
    heads = [h for i, h in enumerate(heads) if h["level"] == 1 or (i + 1 < len(heads) and heads[i + 1]["level"] == 1)]
    for i, h in enumerate(heads):
        end = len(lines)
        for g in heads[i + 1:]:
            if g["level"] <= h["level"]: end = g["start"] - 1; break
        h["end"] = end
        h["words"] = sum(len(l.split()) for l in lines[h["start"] - 1: end])
    return heads

def section_of(heads, n):
    inner = [h for h in heads if h["start"] <= n <= h["end"]]
    return " / ".join(h["title"] for h in sorted(inner, key=lambda h: h["level"])) or "(before the first heading)"

def load_index(path, heading=None):
    ix = os.path.splitext(path)[0] + ".index.json"
    if os.path.exists(ix) and not heading: return json.load(open(ix))
    return index(read(path), heading)

def find(path, phrase, context=1, limit=50):
    lines, heads = read(path), load_index(path)
    words = phrase.lower().split()
    out = []
    # join each line with the next so a phrase broken across a line wrap is still found
    target = " ".join(words)
    for n in range(1, len(lines) + 1):
        here = re.sub(r"\s+", " ", lines[n - 1].lower())
        window = re.sub(r"\s+", " ", " ".join(lines[n - 1: n + 1]).lower())
        nxt_only = n < len(lines) and target in re.sub(r"\s+", " ", lines[n].lower())
        # report the line the phrase starts on; a phrase wrapped across two lines starts on the first
        if (target in here or (target in window and not nxt_only)) and not (out and out[-1]["line"] == n - 1):
            lo, hi = max(1, n - context), min(len(lines), n + context + 1)
            out.append({"line": n, "section": section_of(heads, n), "text": [f"{k}: {lines[k - 1]}" for k in range(lo, hi + 1)]})
            if len(out) >= limit: break
    return out

def show(path, what):
    lines = read(path)
    m = re.match(r"^(\d+)-(\d+)$", what)
    if m: a, b = int(m.group(1)), int(m.group(2))
    else:
        heads = load_index(path)
        parts = [x.strip().lower() for x in what.split(">")]
        hits = []
        for h in heads:
            if parts[-1] not in h["title"].lower(): continue
            path_titles = section_of(heads, h["start"]).lower()
            # "Book III > Canto XLV": every part must appear in the section's path, in that book
            if all(re.search(r"(^|[^a-z])" + re.escape(x) + r"([^a-z]|$)", path_titles) for x in parts): hits.append(h)
        if not hits: sys.exit(f"no section titled like {what!r}; run `index` and look at the titles")
        a, b = hits[0]["start"], hits[0]["end"]
    return [f"{k}: {lines[k - 1]}" for k in range(a, min(b, len(lines)) + 1)]

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("index"); a.add_argument("source"); a.add_argument("--heading")
    b = sub.add_parser("find"); b.add_argument("source"); b.add_argument("phrase"); b.add_argument("--context", type=int, default=1)
    c = sub.add_parser("show"); c.add_argument("source"); c.add_argument("what")
    for x in (a, b, c): x.add_argument("--json", action="store_true")
    args = p.parse_args()
    if not os.path.exists(args.source): p.error(f"no such file: {args.source}")
    if args.cmd == "index":
        heads = index(read(args.source), args.heading)
        out = os.path.splitext(args.source)[0] + ".index.json"
        json.dump(heads, open(out, "w"), indent=1)
        if args.json: print(json.dumps(heads, indent=1)); return
        print(f"\n  {len(heads)} sections -> {out}\n")
        for h in heads[:40]: print(f"  {'  ' * h['level']}{h['title'][:60]:<62} lines {h['start']}-{h['end']}  ({h['words']} words)")
        if len(heads) > 40: print(f"  ... and {len(heads) - 40} more")
        if not heads: print("  no headings found - pass --heading with a regex for this text's section lines")
        print()
    elif args.cmd == "find":
        hits = find(args.source, args.phrase, args.context)
        if args.json: print(json.dumps(hits, indent=1, ensure_ascii=False)); return
        print(f"\n  {len(hits)} match(es) for {args.phrase!r}\n")
        for h in hits:
            print(f"  line {h['line']}  [{h['section']}]")
            for t in h["text"]: print(f"    {t}")
            print()
    else:
        out = show(args.source, args.what)
        if args.json: print(json.dumps(out, indent=1, ensure_ascii=False)); return
        print("\n".join(out))

if __name__ == "__main__":
    main()
