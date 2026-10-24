---
name: yt-viral
description: >-
  Find what is actually working in the user's niche on YouTube and rank it
  by how far each video beat its own channel, then name the formula. Use for
  "what's working right now", "find viral videos in my niche", "why did this
  blow up", competitor research, or a swipe file.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/swipe.py *)
---

# yt-viral

Raw view counts rank channel size, not ideas. This ranks by **multiple over each channel's own
median**, which is the only version of the question that is about the video.

```bash
python3 ${CLAUDE_SKILL_DIR}/swipe.py collected.json --min 2.0
yt-dlp --flat-playlist -J "https://www.youtube.com/@channel/videos" > a.json
python3 ${CLAUDE_SKILL_DIR}/swipe.py a.json b.json c.json        # yt-dlp output as-is
```

The tools live in this skill's folder. `${CLAUDE_SKILL_DIR}` is that folder in Claude Code; anywhere
it does not expand (claude.ai, Codex), use the folder this SKILL.md was loaded from.

It reads the formulas from `../yt-script/`, so install the two together.

## Collecting the input

You need at least **four videos per channel** or a median means nothing, and the tool will skip the
channel and tell you it did. Collect them however the user prefers - `yt-dlp --flat-playlist -J`
against a channel's `/videos` page is the fastest and its output goes straight in, the public page
works, a manual list works. Collect ten to thirty per channel, not four.

Shorts and long videos are medianed separately when the durations are there, and videos with no
view count are left out rather than counted as zero. If the tool says it left some out, say so.

```json
[{"channel":"...","title":"...","views":412000,"url":"...","duration":613}]
```

**Read, do not scrape.** Public listings only, never a logged-in session, never the user's own
account credentials.

## Reading the output

The multiple is the signal. The formula line is a judgement about the TITLE, matched against
[the 21 formulas](../yt-script/hooks.json) - it is not a claim about why the video worked, and you
should say so when you present it.

What to hand back: the top five with their multiples, the formula each used, and the ONE structural
thing they share. Then the harder line - which of those the user could actually make this week, in
their voice, with what they have.

A swipe file is for the shape, never the video. Remaking someone else's outlier with the nouns
swapped is the "mass-produced, repetitive" content YouTube's inauthentic-content policy demonetises.
If the user asks for that, say so and give them the structure to fill with their own material.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
