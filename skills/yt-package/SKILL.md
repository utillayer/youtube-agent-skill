---
name: yt-package
description: >-
  Write and lint the title and thumbnail for a YouTube video as one pairing,
  checking truncation, duplication and vagueness before publish. Use for
  "title ideas", "what should I call this", "thumbnail text", "my CTR is
  bad", packaging, or any request to rename or repackage an existing video.
---

# yt-package

The title and the thumbnail are ONE unit. Writing them separately is why most packaging fails: the
thumbnail repeats the title, and half the click surface says the same thing twice.

```bash
python3 ${CLAUDE_SKILL_DIR}/title.py --title "..." --thumb "AI RAN IT"
python3 ${CLAUDE_SKILL_DIR}/title.py titles.txt --thumb "AI RAN IT"   # one per line, ranked
```

The tools live in this skill's folder. `${CLAUDE_SKILL_DIR}` is that folder in Claude Code; anywhere
it does not expand (claude.ai, Codex), use the folder this SKILL.md was loaded from.


## Before you write

1. Read `~/.claude/youtube/voice.md` if it exists. That is the user's voice profile: how they talk
   on camera, the words they never use, who they are talking to, what they will not claim. If it
   does not exist, ask for **three of their own videos**, read or transcribe them, infer the voice,
   and write the file. A script in the wrong voice is worse than no script, because they have to
   read it out loud.
2. Never invent a number, a result or a source. If a figure would strengthen it and you do not have
   one, ask for it or write the line without it.

## Rules the tool enforces, and why

- **About 60 characters** survives desktop search, **about 40** a mobile home feed. YouTube publishes
  neither number - truncation is by pixel width and varies by surface - so treat them as the safe
  side of a blur, not a rule. Both are reported because they fail differently: a desktop cut loses
  the tail, a mobile cut can lose the subject. 100 is the hard limit, and `<` `>` are not allowed.
- **The thumbnail must not repeat the title.** Different words, same promise.
- **Three words maximum on the thumbnail.** At feed size a fourth word is a grey smear.
- **A number, a name or a date** beats every adjective available to you.
- **Two all-caps words is the ceiling** before a title reads as spam.

## Write ten, keep two

Generate ten titles, run them all through `title.py`, show the user the top three with their scores
and the specific issue on each. For the winner, write the thumbnail brief: the expression, the
framing, the three words, and what the background has to do to hold contrast at feed size.

## Then let YouTube decide

Studio can A/B test up to three titles, three thumbnails, or both, and picks by watch time share.
It runs on desktop Studio, needs advanced features turned on, takes up to two weeks, and does not
work on Shorts. If the top two are close, say so and hand over both for a test instead of
pretending the linter can tell them apart. The score is a lint, not a prediction.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
