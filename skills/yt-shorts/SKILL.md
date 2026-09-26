---
name: yt-shorts
description: >-
  Find the Shorts hiding inside a long video and write them, using the
  transcript to pick self-contained moments. Use for "cut this into shorts",
  "clip this", "repurpose this video", "what should I clip".
---

# yt-shorts

A Short cut out of a long video is not a clip of the best moment. It is a moment that **survives
without the video around it**, which is a much smaller set.

```bash
python3 ${CLAUDE_SKILL_DIR}/shorts.py transcript.srt              # top 5, 20-55s each
python3 ${CLAUDE_SKILL_DIR}/shorts.py transcript.srt --top 8 --max 90 --json
```

The tools live in this skill's folder. `${CLAUDE_SKILL_DIR}` is that folder in Claude Code; anywhere
it does not expand (claude.ai, Codex), use the folder this SKILL.md was loaded from.

It uses `../yt-edit/deadair.py` and `../yt-script/hookscore.py`, so install all three together.

## Before you write

Read `~/.claude/youtube/voice.md` if it exists. The new first line is spoken or captioned in the
user's voice, and the voice file's "what I will not claim" list applies here too.

## Picking

Run `shorts.py` first and read its shortlist rather than the whole transcript. A Short needs all
three of these:

1. It opens on a complete thought. If the first sentence needs the previous minute, it is not a Short.
2. There is a turn in it - a claim, then something that complicates or proves it.
3. It ends on a line, not a trail-off.

The tool can check the first and last, and scores the opening line; only you can check the second.
Read each candidate it returns, drop the ones with no turn, and show the user the top five with
their timecodes and first line, so they can reject one without reading the whole transcript.

On length: Shorts can run to **three minutes** now. 20-55 seconds is a choice, not the limit - short
spans loop and finish better. Go longer with `--max` only when the turn needs the room. **Over 60
seconds, any Content ID claim blocks the Short everywhere**, so a longer span with someone else's
music under it is not a Short at all.

## Writing each one

- **A NEW first line.** The long video's line assumes context this viewer does not have. Write the
  replacement and run it through `${CLAUDE_SKILL_DIR}/../yt-script/hookscore.py`.
- **On-screen text for the first two seconds**, different words from the spoken line.
- **A loop point**: what the last line sets up so the first line answers it.
- Vertical framing note - what gets cropped out of a 16:9 frame and whether that matters.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
