#!/usr/bin/env python3
"""shorts.py - find the spans of a long video that could stand on their own as a Short.

    python3 shorts.py transcript.srt              # or .vtt / whisper .json
    python3 shorts.py transcript.srt --top 8 --max 90 --json

A Short cut from a long video has to survive without the video around it. This checks the three
things the transcript can show:
  OPEN    it starts on a fresh thought - after a pause, not on "and", "so", "but" or "this"
  CLOSE   it ends on a finished sentence or a real pause, not mid-thought
  HOOK    the first line, scored with ../yt-script/hookscore.py

It ranks candidates, keeps the best non-overlapping ones and prints timecodes plus the first and last
line of each, so you can reject one without reading the whole transcript. What it cannot see is
whether the moment is any good. That is still your call - and the first line almost always needs
rewriting, because the long video's opening assumes context a Shorts viewer does not have.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "yt-edit"))
sys.path.insert(0, os.path.join(HERE, "..", "yt-script"))
from deadair import load, FILLER_ONLY  # noqa: E402
from hookscore import score as hookscore  # noqa: E402

# Openers that lean on what came before. A Short that starts on one of these needs the previous minute.
DANGLING = {"and", "but", "so", "because", "which", "that", "this", "these", "those", "it", "they",
            "he", "she", "also", "then", "plus", "or", "anyway", "now", "as", "like", "same"}
END = re.compile(r"[.!?…。？！]['\"”’)]*\s*$")

def mmss(t):
    t = int(t); return f"{t // 60}:{t % 60:02d}"

def first_word(t):
    w = re.findall(r"[^\W\d_]+", t.lower())
    return w[0] if w else ""

def candidates(cues, lo=20.0, hi=55.0):
    out = []
    for i, (s, _, t) in enumerate(cues):
        if FILLER_ONLY.match(t): continue
        gap_before = s - cues[i - 1][1] if i else 99
        fresh = i == 0 or gap_before >= 0.3 or bool(END.search(cues[i - 1][2]))
        opener = first_word(t)
        best = None
        for j in range(i, len(cues)):
            span = cues[j][1] - s
            if span > hi: break
            if span < lo: continue
            gap_after = cues[j + 1][0] - cues[j][1] if j + 1 < len(cues) else 99
            close = (1.0 if END.search(cues[j][2]) else 0) + (0.5 if gap_after >= 0.4 else 0)
            if close and (best is None or close >= best[0]): best = (close, j)
        if best is None: continue
        close, j = best
        text = " ".join(c[2] for c in cues[i:j + 1])
        line = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0][:240]
        _, verdict, formula, _ = hookscore(line)
        open_score = (0.5 if fresh else 0) + (0.5 if opener not in DANGLING else 0)
        total = round(100 * (0.45 * verdict / 100 + 0.30 * open_score + 0.25 * min(close, 1.0)))
        flags = []
        if opener in DANGLING: flags.append(f'opens on "{opener}" - needs a new first line')
        if not fresh: flags.append("no pause before it - may start mid-thought")
        if not END.search(cues[j][2]): flags.append("ends on a pause, not a finished sentence")
        if cues[j][1] - s > 60: flags.append("over 60s - any Content ID claim (music) blocks it everywhere")
        out.append({"start": s, "end": cues[j][1], "seconds": round(cues[j][1] - s, 1), "score": total,
                    "hook": verdict, "formula": formula, "first_line": line,
                    "last_line": cues[j][2][-160:], "flags": flags})
    return out

def pick(cands, top=5):
    """Best first, never two that overlap - two Shorts out of the same 40 seconds is one Short."""
    kept = []
    for c in sorted(cands, key=lambda c: (-c["score"], c["start"])):
        if all(c["end"] <= k["start"] or c["start"] >= k["end"] for k in kept): kept.append(c)
        if len(kept) >= top: break
    return sorted(kept, key=lambda c: c["start"])

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("transcript")
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--min", type=float, default=20.0, help="shortest span, seconds")
    p.add_argument("--max", type=float, default=55.0, help="longest span, seconds (Shorts allow up to 180)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    if not os.path.exists(a.transcript): p.error(f"no such file: {a.transcript}")
    if a.max > 180: p.error("--max over 180s is no longer a Short")
    cues = load(a.transcript)
    if not cues: print("no cues found - is this an srt, vtt or whisper json?"); sys.exit(1)
    kept = pick(candidates(cues, a.min, a.max), a.top)
    if a.json: print(json.dumps(kept, indent=1, ensure_ascii=False)); return
    print(f"\n  {a.transcript}   {len(cues)} cues, spans of {a.min:.0f}-{a.max:.0f}s\n")
    for n, c in enumerate(kept, 1):
        print(f"  {n}. {mmss(c['start'])} -> {mmss(c['end'])}   {c['seconds']:.0f}s   score {c['score']}   "
              f"hook {c['hook']} ({c['formula']})")
        print(f"       first  \"{c['first_line'][:110]}\"")
        print(f"       last   \"{c['last_line'][-110:]}\"")
        for f in c["flags"]: print(f"       !  {f}")
        print()
    if not kept:
        print("  no span opens cleanly and closes on a sentence inside that window -")
        print("  try --min 15 or --max 90, or check the transcript has punctuation or real pauses\n")

if __name__ == "__main__":
    main()
