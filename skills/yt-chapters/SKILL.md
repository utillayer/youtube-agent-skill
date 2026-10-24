---
name: yt-chapters
description: >-
  Write YouTube chapters from a transcript, validated against YouTube's own
  rules so they actually render. Use for "add chapters", "timestamps",
  "break this video into sections".
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/chapters.py *)
---

# yt-chapters

```bash
python3 ${CLAUDE_SKILL_DIR}/chapters.py transcript.srt --target 8
```

The tools live in this skill's folder. `${CLAUDE_SKILL_DIR}` is that folder in Claude Code; anywhere
it does not expand (claude.ai, Codex), use the folder this SKILL.md was loaded from.

It reads transcripts with `../yt-edit/deadair.py`, so install the two together.

Have a link but no transcript? YouTube's own captions, in one line:

```bash
yt-dlp --skip-download --write-auto-subs --sub-langs en --sub-format vtt -o transcript "<video url>"
```

That writes `transcript.en.vtt`. Swap `en` for the video's language. Auto-captions have no
punctuation; a `whisper` transcript does, and gives cleaner sentence boundaries.

## Before you write

Read `~/.claude/youtube/voice.md` if it exists - the titles you write go in the user's words, not
yours. If it does not exist, retitle plainly and say the voice file would sharpen them.

## The rules, which are not optional

A chapter list that breaks any of these silently does not become chapters at all - the block just
sits in the description doing nothing:

- The first entry must be **00:00**.
- There must be **at least three**.
- Each must be **at least 10 seconds** long.
- They must be in **ascending order**.

Some channels also have to turn on advanced features in Studio before chapters show at all. If a
valid list does not render, that is the first thing to check.

The tool checks all three and tells you when a list is invalid rather than letting you paste it.

## Retitle every line

`chapters.py` finds the BOUNDARIES well - it scores the pauses you actually took by how much the
vocabulary shifts across them. The titles it emits are the topic words, and they are a draft. A
chapter called "Thumbnails Titles Packaging" is a placeholder. Rewrite each one as the promise of
that section, in the user's voice, three to five words.

Chapters are also a retention diagnostic: if a section cannot be named in five words, it is two
sections or it is filler.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
