#!/usr/bin/env python3
"""swipe.py - rank collected videos by how far each beat its OWN channel, then name the formula.

    python3 swipe.py collected.json
    python3 swipe.py collected.json --min 2.0 --json
    yt-dlp --flat-playlist -J "https://www.youtube.com/@somechannel/videos" > a.json
    python3 swipe.py a.json b.json c.json          # yt-dlp output works as-is, one file per channel

Input is either yt-dlp's JSON or a list you collected - one object per video:

    [{"channel":"Some Channel","title":"...","views":412000,"url":"...","duration":613}, ...]

Raw view counts rank channel size, not ideas. A 400k video on a 2M-subscriber channel is a normal
Tuesday; a 400k video on a channel whose median is 30k is the thing worth studying. So every video
is scored as a MULTIPLE OF ITS OWN CHANNEL'S MEDIAN, which needs at least four videos per channel
to mean anything - the tool says so rather than quietly ranking on noise.

Shorts and long videos are medianed separately. They are different audiences on the same channel,
and a Short at 2M views against a long-form median of 40k is not an outlier, it is a different
format. A video with no view count is left out rather than counted as zero, because a zero drags
the median down and inflates every multiple on that channel.

The formula comes from skills/yt-script/hooks.json, matched against the TITLE. It is a judgement
about the words on screen, not a claim about why the video worked.
"""
import argparse, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "yt-script"))
from hookscore import classify as _classify  # noqa: E402  (one classifier, so both tools agree)

SHORT_MAX = 180  # seconds. YouTube Shorts can run to three minutes.

def classify(title): return _classify(title)[0]

def videos(node, channel=None):
    """Flatten whatever was collected into (channel, title, views, url, duration) rows. yt-dlp nests a
    channel's tabs as playlists of entries and puts the channel name on the parent, not the video."""
    if isinstance(node, list):
        for n in node: yield from videos(n, channel)
        return
    if not isinstance(node, dict): return
    ch = node.get("channel") or node.get("uploader") or node.get("playlist_uploader") or channel
    if "entries" in node or "videos" in node:
        yield from videos(node.get("entries") or node.get("videos") or [], ch)
        return
    views = node.get("views", node.get("view_count"))
    try: views = float(str(views).replace(",", "")) if views is not None else None
    except ValueError: views = None
    yield {"channel": ch or "?", "title": node.get("title") or "", "views": views,
           "url": node.get("url") or node.get("webpage_url") or "", "duration": node.get("duration")}

def fmt(v):
    d = v["duration"]
    if d is None: return "video"
    return "short" if float(d) <= SHORT_MAX else "long"

def rank(rows, lo=1.5):
    by, missing = {}, 0
    for v in rows:
        if v["views"] is None: missing += 1; continue
        by.setdefault((v["channel"], fmt(v)), []).append(v)
    out, thin = [], []
    for (ch, kind), vids in by.items():
        if len(vids) < 4:
            thin.append((ch if kind == "video" else f"{ch} [{kind}s]", len(vids)))
            continue
        med = statistics.median(v["views"] for v in vids)
        for v in vids:
            m = v["views"] / med if med else 0
            out.append({"channel": ch, "format": kind, "title": v["title"], "views": int(v["views"]),
                        "median": int(med), "multiple": round(m, 2), "formula": classify(v["title"]),
                        "url": v["url"]})
    out = [r for r in out if r["multiple"] >= lo]
    out.sort(key=lambda r: -r["multiple"])
    return out, thin, missing, len(by)

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+", help="collected.json, or yt-dlp -J output, one or more")
    p.add_argument("--min", type=float, default=1.5, help="lowest multiple worth showing")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    rows = []
    for f in a.files:
        if not os.path.exists(f): p.error(f"no such file: {f}")
        rows += list(videos(json.load(open(f, encoding="utf-8-sig"))))
    out, thin, missing, groups = rank(rows, a.min)
    if a.json:
        print(json.dumps({"outliers": out, "skipped_thin_channels": thin, "missing_views": missing},
                         indent=1, ensure_ascii=False)); return
    print(f"\n  {len(rows)} videos, {groups} channel groups, outliers at {a.min}x or better\n")
    for r in out[:25]:
        tag = "" if r["format"] == "video" else f"[{r['format']}] "
        print(f"    {r['multiple']:5.2f}x  {r['views']:>9,}  vs {r['median']:>9,} median   {r['channel'][:22]:<22} {tag}{r['title'][:52]}")
        print(f"            {r['formula']}")
    if not out: print("    nothing cleared the threshold - collect more per channel or lower --min")
    if thin:
        print(f"\n  skipped {len(thin)} group(s) with under 4 videos collected - a median off one or")
        print( "  two videos is not a median: " + ", ".join(f"{c} ({n})" for c, n in thin[:6]))
    if missing:
        print(f"\n  left out {missing} video(s) with no view count - flat listings sometimes omit it")
    counts = {}
    for r in out: counts[r["formula"]] = counts.get(r["formula"], 0) + 1
    if counts:
        print("\n  formulas among the outliers")
        for f, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {n:2d}x  {f}")
    print()

if __name__ == "__main__":
    main()
