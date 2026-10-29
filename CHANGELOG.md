# Changelog

## 1.2.0

- New skill, `/yt-research`: research a video from its primary source. A cited brief (events in
  order with section and line numbers, quotes, a careful list of later additions and ambiguities),
  then an independent fact check of the script by an agent that never saw the writing.
- New tool, `sourcekit.py`: index any plain-text source into its books and chapters, find a phrase
  with the line it starts on, and print a section (`"Book III > Canto XLV"`) or a line range.
- New tool, `scriptcheck.py`: checks a script is ready to be spoken - length, one breath per
  paragraph, no characters a narrator trips on, sentences that end, the opening's score, names
  spelled one way, a turn at the middle.
- `/yt-script` rewritten around writing for the ear: paragraphs as breath-groups, numbers as words,
  every paragraph something to show, a turn at the midpoint, and a check before recording.
- `hookscore.py` counts numbers written as words ("ten seconds") as concrete, so a spoken script is
  not penalised for following the rules.
- Every skill, the README, the voice template and the hook formulas rewritten in the pack's own words.

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
