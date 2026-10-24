#!/usr/bin/env python3
"""deadair.py - an edit decision list from a timestamped transcript.

    python3 deadair.py transcript.srt            # or .vtt, or whisper .json
    python3 deadair.py transcript.srt --floor 0.35 --json

Finds three things and prints the cuts in timeline order:
  DEAD    gaps between spoken cues longer than the floor
  FILLER  cues that are only filler ("um", "so yeah", "basically", "o sea", "bueno")
  REPEAT  a sentence restarted - the abandoned take before the one you kept

YouTube's own auto-caption .vtt works as-is: the inline word timings and the rolling duplicate lines
it writes are stripped on load.

WHAT IT DOES NOT DO. It does not cut the file. It prints an EDL, the total it would remove, and the
runtime you would land on, and you apply it in whatever editor you use. Nothing here touches media.
"""
import argparse, json, os, re, sys

FILLER_ONLY = re.compile(r"^[\s,.\-?!¿¡…।]*((um+|uh+|er+|ah+|hmm+|so|okay|ok|right|yeah|like|anyway|"
                         r"basically|actually|you know|i mean|let me see|hold on|"
                         # spanish
                         r"eh+|este+|bueno|pues|o sea|osea|digamos|a ver|vale|"
                         r"es decir|d[eé]jame ver|un momento|"
                         # hindi, romanised and devanagari
                         r"matlab|toh|haa?n|ach+h?a|dekho|yaa?r|th[ie]e?k hai|chalo|arr?ey|arre|"
                         r"मतलब|तो|हाँ|हां|अच्छा|देखो|यार|ठीक है|चलो|अरे|"
                         # nepali, romanised and devanagari
                         r"ani|ta|ni|la|khai|hai|haina|hoina|ke re|"
                         r"अनि|त|नि|ल|खै|हैन|होइन|के रे)[\s,.\-?!¿¡…।]*)+$", re.I)
TAG = re.compile(r"<[^>]*>")
# [Music], [Applause], (laughs) - caption annotations, never speech. Left in, they become chapter
# titles and the first line of a Short.
SOUND = re.compile(r"\[[^\]]*\]|\((?:music|applause|laughter|laughs|inaudible)\)", re.I)

def parse_ts(s):
    s = s.strip().replace(",", ".")
    p = s.split(":")
    return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2]) if len(p) == 3 else int(p[0]) * 60 + float(p[1])

def load(path):
    with open(path, encoding="utf-8-sig", errors="replace") as fh: raw = fh.read()
    if path.endswith(".json"):
        d = json.loads(raw)
        segs = d.get("segments", []) if isinstance(d, dict) else d
        segs = [(float(s["start"]), float(s["end"]), SOUND.sub("", s.get("text") or "").strip()) for s in segs]
        return [s for s in segs if s[2]]
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", line)
        if m:
            cur = [parse_ts(m.group(1)), parse_ts(m.group(2)), []]
            cues.append(cur)
        elif not line.strip():
            cur = None    # a blank line ends the cue, so a vtt NOTE or cue id is never read as speech
        elif cur is not None:
            text = " ".join(SOUND.sub("", TAG.sub("", line)).split())
            if text: cur[2].append(text)
    # YouTube auto-captions roll: each cue repeats the line before it, and every few seconds there
    # is a 10ms cue that is nothing but the repeat. Keep only the lines that are new. Only for files
    # carrying YouTube's inline word timings - in a hand-made srt a repeated line is a real retake.
    if not re.search(r"<\d[\d:.]+>|<c>", raw): return [(a, b, " ".join(t)) for a, b, t in cues if t]
    out, prev = [], []
    for a, b, lines in cues:
        new = [l for l in lines if l not in prev]
        if lines: prev = lines
        if new: out.append((a, b, " ".join(new)))
    return out

# Letters and digits in any script. An ASCII-only class turned "déjame" into "djame" and every
# Cyrillic, Arabic or Devanagari word into nothing, which broke the retake check for most languages.
def norm(t): return re.findall(r"[^\W_]+", t.lower())

def restarted(first, second):
    """True when `first` is an abandoned take of `second`: the same opening, at least three words.
    The abandoned take is usually SHORTER than the one kept, so compare on its length, capped at 5."""
    a, b = norm(first)[:5], norm(second)[:5]
    n = min(len(a), len(b))
    return n >= 3 and a[:n] == b[:n]

def merge(cuts):
    """Overlapping cuts are counted once. Auto-captions overlap their cues, so without this the
    'removed' total can count the same second twice."""
    spans = []
    for c in sorted(cuts, key=lambda c: c["start"]):
        if spans and c["start"] < spans[-1][1]: spans[-1][1] = max(spans[-1][1], c["end"])
        else: spans.append([c["start"], c["end"]])
    return sum(e - s for s, e in spans)

def edl(cues, floor=0.45):
    cuts = []
    for i, (s, e, t) in enumerate(cues):
        if FILLER_ONLY.match(t):
            cuts.append({"kind": "FILLER", "start": s, "end": e, "why": t.strip()[:48]})
        if i:
            gap = s - cues[i - 1][1]
            if gap > floor:
                keep = floor / 2
                cuts.append({"kind": "DEAD", "start": round(cues[i - 1][1] + keep, 3),
                             "end": round(s - keep, 3), "why": f"{gap:.2f}s gap"})
        # A restart is compared against the last cue that was actually SPEECH. Comparing against
        # the literal previous cue misses every retake with an "um" between the two attempts, which
        # is most of them.
        if t.strip() and not FILLER_ONLY.match(t):
            j = i - 1
            while j >= 0 and (FILLER_ONLY.match(cues[j][2]) or not cues[j][2].strip()): j -= 1
            if j >= 0 and restarted(cues[j][2], t):
                cuts.append({"kind": "REPEAT", "start": cues[j][0], "end": cues[j][1],
                             "why": f'restart of "{" ".join(norm(cues[j][2])[:5])}"'})
    cuts = [c for c in cuts if c["end"] > c["start"]]
    cuts.sort(key=lambda c: c["start"])
    return cuts

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("transcript")
    p.add_argument("--floor", type=float, default=0.45, help="shortest gap, in seconds, worth cutting")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    if not os.path.exists(a.transcript): p.error(f"no such file: {a.transcript}")
    cues = load(a.transcript)
    if not cues: print("no cues found - is this an srt, vtt or whisper json?"); sys.exit(1)
    dur = cues[-1][1]
    cuts = edl(cues, a.floor)
    removed = merge(cuts)
    if a.json:
        print(json.dumps({"source": a.transcript, "duration": dur, "cuts": cuts, "removed": round(removed, 3),
                          "out": round(dur - removed, 3)}, indent=1, ensure_ascii=False)); return
    print(f"\n  {a.transcript}   {dur:.2f}s in, {len(cues)} cues, dead-air floor {a.floor}s\n")
    for c in cuts:
        print(f"    {c['kind']:<7} {c['start']:8.2f} -> {c['end']:8.2f}   {c['end']-c['start']:5.2f}s   {c['why']}")
    print(f"\n  {len(cuts)} cuts, {removed:.2f}s removed, {dur - removed:.2f}s out "
          f"({removed / dur * 100 if dur else 0:.1f}% shorter)\n")

if __name__ == "__main__":
    main()
