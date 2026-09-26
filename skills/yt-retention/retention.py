#!/usr/bin/env python3
"""retention.py - read a YouTube Studio audience-retention export and find the leaks.

    python3 retention.py retention.csv
    python3 retention.py retention.csv --transcript transcript.srt   # names what was said at each drop
    python3 retention.py retention.csv --duration 612 --json   # percent axis -> cliffs in seconds

Get the file from Studio: Analytics -> a video -> Engagement -> the audience-retention chart ->
the download icon -> "Audience retention". Two columns, a position (percent or seconds) and a
percentage still watching.

It reports three things, because they are three different problems with three different fixes:
  HOOK LEAK    what you lost in the first 30 seconds
  CLIFFS       single steep drops - a specific moment people left at
  SLIDE        the steady bleed rate across the flat middle

With --transcript it prints what you were saying at each cliff, which is the only version of this
report you can act on without scrubbing the video yourself.
"""
import argparse, csv, json, os, sys

def unit_of(header):
    """What the position column counts, read off the header when the export has one."""
    h = header.casefold()
    if "%" in h or "percent" in h or "ratio" in h: return "percent"
    if any(w in h for w in ("second", "sec)", "(s)", "time")): return "seconds"
    return None

def clock(c):
    """'1:05' or '0:01:05' as seconds - some exports and hand-copied charts give the position that way."""
    secs = 0.0
    for part in c.split(":"): secs = secs * 60 + float(part)
    return secs

def load_csv(path):
    """(position, percent still watching) rows, plus the position unit if the header names it.
    Both columns are normalised to 0-100 when the file holds 0-1 ratios, as the Analytics API does."""
    rows, unit = [], None
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for r in csv.reader(fh):
            nums = []
            for c in r:
                c = c.strip().replace("%", "").replace(",", "")
                try: nums.append(clock(c) if ":" in c else float(c))
                except ValueError: nums.append(None)
            if any(":" in c for c in r[:1]) and unit is None: unit = "seconds"
            vals = [n for n in nums if n is not None]
            if len(vals) >= 2: rows.append((vals[0], vals[1]))
            elif not rows and r and unit is None: unit = unit_of(r[0])
    if rows and max(x for x, _ in rows) <= 1.0 and max(y for _, y in rows) <= 1.5:
        rows = [(x * 100, y * 100) for x, y in rows]
        unit = "percent"
    return rows, unit

def analyse(rows, unit=None, dur=None):
    xs = [r[0] for r in rows]; ys = [r[1] for r in rows]
    pct_axis = unit == "percent" if unit else max(xs) <= 100.5
    def at(x): return (x / 100.0 * dur) if (pct_axis and dur) else x
    start = ys[0] or 100.0
    # HOOK: the first 30 seconds, or the first 10% when the axis is a percentage and we have no duration
    cutoff = 30.0 if not pct_axis else (30.0 / dur * 100 if dur else 10.0)
    hook_end = min((y for x, y in rows if x <= cutoff), default=start)
    hook_leak = start - hook_end
    drops = []
    for i in range(1, len(rows)):
        d = ys[i - 1] - ys[i]
        span = xs[i] - xs[i - 1] or 1
        drops.append((d / span, xs[i - 1], xs[i], d))
    drops.sort(reverse=True)
    cliffs = [{"from": round(a1, 2), "to": round(b1, 2), "lost": round(d, 2),
               "at_seconds": round(at(a1), 1) if (not pct_axis or dur) else None}
              for _, a1, b1, d in drops[:5] if d > 0.8]
    mid = [rate for rate, x0, _, _ in drops if x0 > cutoff]
    slide = sum(mid) / len(mid) if mid else 0
    per = "second" if not pct_axis else ("1% of the video" if not dur else f"1% of the video ({dur / 100:.1f}s)")
    return {"points": len(rows), "axis": "percent" if pct_axis else "seconds", "start": start,
            "hook_leak": round(hook_leak, 2), "end": ys[-1], "cliffs": cliffs,
            "slide_per_unit": round(slide, 3), "slide_unit": per}

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--transcript", help="srt, vtt or whisper json, to print what was said at each cliff")
    p.add_argument("--duration", type=float, help="video length in seconds, when the export is in percent")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    if not os.path.exists(a.csv): p.error(f"no such file: {a.csv}")
    rows, unit = load_csv(a.csv)
    if len(rows) < 8: print("could not read at least 8 data points from that csv"); sys.exit(1)
    out = analyse(rows, unit, a.duration)
    cliffs, said = out["cliffs"], {}
    if a.transcript and os.path.exists(a.transcript):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "yt-edit"))
        from deadair import load as load_cues
        cues = load_cues(a.transcript)
        for c in cliffs:
            if c["at_seconds"] is None: continue
            t = c["at_seconds"]
            near = [q[2] for q in cues if q[0] <= t + 4 and q[1] >= t - 4]
            said[str(c["from"])] = " ".join(near)[:140]
    out["said"] = said
    if a.json: print(json.dumps(out, indent=1, ensure_ascii=False)); return
    ys = [r[1] for r in rows]; hook_leak = out["hook_leak"]
    print(f"\n  {a.csv}   {len(rows)} points   {ys[0]:.1f}% -> {ys[-1]:.1f}%\n")
    verdict = "healthy" if hook_leak < 25 else "leaking" if hook_leak < 40 else "severe"
    print(f"  HOOK LEAK   {hook_leak:.1f}% lost in the opening   [{verdict}]")
    print(f"              under 25 is healthy. Fix the first line before anything else.\n")
    print("  CLIFFS      the moments people actually left")
    for c in cliffs:
        where = f"{c['at_seconds']:.0f}s" if c["at_seconds"] is not None else f"{c['from']}%"
        print(f"    -{c['lost']:5.1f}%  at {where:>8}" + (f"   \"{said.get(str(c['from']),'')}\"" if said else ""))
    if not cliffs: print("    none steeper than 0.8% - the loss is all slide, not moments")
    if out["axis"] == "percent" and not a.duration and a.transcript:
        print("    (pass --duration to turn these into seconds and match them to the transcript)")
    print(f"\n  SLIDE       {out['slide_per_unit']:.3f}% lost per {out['slide_unit']} across the middle")
    print( "              a flat slide is pacing, not content. Cut the middle, do not rewrite it.\n")

if __name__ == "__main__":
    main()
