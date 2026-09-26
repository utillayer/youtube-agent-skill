---
name: yt-retention
description: >-
  Read a YouTube Studio audience-retention export and find where viewers
  actually leave, then say what to change. Use for "why do people stop
  watching", "my retention is bad", a pasted retention chart or CSV, or "fix
  my pacing".
---

# yt-retention

The retention graph is the only honest feedback YouTube gives you. Almost nobody exports it.

```bash
python3 ${CLAUDE_SKILL_DIR}/retention.py retention.csv --duration 600
python3 ${CLAUDE_SKILL_DIR}/retention.py retention.csv --duration 600 --transcript transcript.srt
```

The tools live in this skill's folder. `${CLAUDE_SKILL_DIR}` is that folder in Claude Code; anywhere
it does not expand (claude.ai, Codex), use the folder this SKILL.md was loaded from.

Getting the file: Studio -> a video -> Analytics -> Engagement -> the audience-retention chart ->
the download icon -> "Audience retention".

What it reads: two columns, a position and the share still watching. The position can be seconds,
`m:ss`, a percent of the video, or a 0-1 ratio as the Analytics API returns it; the header decides
when it names the unit, and otherwise anything up to 100 is read as percent. **If the position is a
percent, always pass `--duration`** (the video length in seconds) - without it the cliffs have no
timestamps and `--transcript` cannot say what was being said there. Ask for the length rather than
guess it. The transcript reader is `../yt-edit/deadair.py`, so install the two together.

## Three different problems

- **HOOK LEAK** - what is lost in the first 30 seconds. Under 25% is healthy. This is always the
  first thing to fix and it is always the first fifteen seconds of script, never the edit.
- **CLIFFS** - single steep drops. A cliff is a moment: a topic change with no signposting, a
  sponsor read, a long setup. With `--transcript` the tool prints what was being said there, which
  is what makes the report actionable instead of interesting.
- **SLIDE** - the steady bleed across the middle. A flat slide is pacing. The fix is cutting, not
  rewriting.

## What to hand back

Name the single biggest leak and one change for it. Not a list of five. Then, only if asked, the
rest. And if the hook leak is healthy and the slide is flat, say the video is fine and the problem
is packaging - send them to `/yt-package`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
