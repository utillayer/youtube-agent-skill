# Changelog

## 1.1.0

- Filler detection now knows Hindi and Nepali, romanised and Devanagari, next to English and Spanish.
- Caption annotations like `[Music]` and `[Applause]` are dropped on load, so they no longer show up
  as chapter titles or as the first line of a Short.
- `shorts.py` says when a transcript has no punctuation (YouTube auto-captions) and its sentence
  ends are guesses. `--json` now returns `{"punctuated": ..., "spans": [...]}`.
- Skills pre-approve their own bundled tools through `allowed-tools`, so Claude Code stops asking
  before every run.
- `/yt-edit`, `/yt-shorts` and `/yt-chapters` show the one-line `yt-dlp` command that fetches a
  video's captions.
- The hook panel is described as what it is: hand-set heuristics, not a model trained on views.

## 1.0.0

First release.

- Eleven skills: script, package, edit, shorts, chapters, seo, comment, plan, viral, retention, audit.
- Seven standard-library Python tools: `hookscore.py`, `title.py`, `deadair.py`, `chapters.py`,
  `retention.py`, `swipe.py`, `shorts.py`.
- Transcripts in `.srt`, `.vtt` (YouTube auto-captions included) and whisper `.json`, any script.
- Retention exports in seconds, `m:ss`, percent or 0-1 ratio, with the unit read from the header.
- `swipe.py` reads `yt-dlp` output directly and medians Shorts and long videos separately.
- Regression tests and CI.
