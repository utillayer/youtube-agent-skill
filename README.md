# youtube-agent-skill

**Twelve Claude skills for the parts of YouTube that decide whether anyone watches** - the research,
the script, the opening, the title and thumbnail, the edit, retention, Shorts, chapters and search.
Free, MIT, no account, no API key, nothing to connect.

[![test](https://github.com/utillayer/youtube-agent-skill/actions/workflows/test.yml/badge.svg)](https://github.com/utillayer/youtube-agent-skill/actions/workflows/test.yml)
![python](https://img.shields.io/badge/python-3.8%2B-3776ab)
![dependencies](https://img.shields.io/badge/dependencies-none-success)
![license](https://img.shields.io/badge/license-MIT-blue)

Most AI help for YouTube is a prompt with opinions. This pack comes with nine small Python tools that
measure instead: they score an opening line before you record it, check a title against its
thumbnail, find the second your viewers left, turn a raw transcript into a cut list, and check a
script is ready to be spoken. Claude writes; the tools keep it honest.

```text
> /yt-script a video about why small channels stall at thirty seconds
```

---

## What it looks like

### An opening line, scored before you record it

A typical channel opening, and one written from the pack's [21 hook formulas](skills/yt-script/hooks.json):

```text
  Hey guys, welcome back to the channel, today is going to be amazing.
    SPECIFICITY    0
    ADDRESS       26  #####
    STAKES        22  ####
    CURIOSITY     24  ####
    BREVITY      100  ####################
    VERDICT       21  WEAK
    formula      Unclassified  (no formula matched - that is usually a summary, not a hook)

  Why do you lose 40% of your viewers before 30 seconds, when the topic is fine?
    SPECIFICITY   78  ###############
    ADDRESS       96  ###################
    STAKES        88  #################
    CURIOSITY     76  ###############
    BREVITY      100  ####################
    VERDICT       83  STRONG
    formula      The Question  (2 patterns matched)
```

The verdict is 60% the average and 40% the weakest score. One dead property is where people leave,
and an average would hide it.

### A title and its thumbnail, checked together

```text
  "The ULTIMATE Guide To Growing Your Channel FAST In 2026 (Insane Results)"   +  thumbnail "GROW YOUR CHANNEL FAST"
  72 chars   score 38/100
    x  length       72 characters - desktop search cuts near 60
    x  mobile       a mobile feed shows about "The ULTIMATE Guide To Growing Your..." - check the subject survives
    x  vague        insane, ultimate - swap for a number, a name or a date
    x  duplicate    thumbnail repeats the title on channel, fast - the thumbnail should say what the title does not
    x  thumb-length 4 words on the thumbnail - three is the ceiling at feed size

  "I Rewrote 40 Titles. 3 Doubled Their Clicks"   +  thumbnail "ONE WORD CHANGED"
  43 chars   score 98/100
    x  mobile       a mobile feed shows about "I Rewrote 40 Titles. 3 Doubled Their..." - check the subject survives
    ok              carries a concrete figure (40, 3)
    ok              thumbnail and title carry different words
```

### A raw recording, as a cut list

```text
  talk.srt   147.72s in, 36 cues, dead-air floor 0.45s

    FILLER      9.35 ->     9.95    0.60s   um
    DEAD       13.83 ->    14.98    1.15s   1.60s gap
    FILLER     39.60 ->    40.37    0.77s   so yeah
    REPEAT     97.88 ->    99.81    1.92s   restart of "i think the fix is"
    ...
  10 cuts, 9.94s removed, 137.77s out (6.7% shorter)
```

Silences are trimmed from the middle so both sides keep a breath, and the abandoned take is the one
cut, even with an "um" between the tries. YouTube's own auto-captions work as they come.

<details>
<summary><b>A script checked before anyone records it</b></summary>

```text
  script.json: 999 words, 18 paragraphs, 1 errors, 1 warnings

    x  opening scores 59 on hookscore.py (need 60): 'You know Vibhishana as the brother who betrayed Ravana. But before he '
    !  paragraph 11: 'King' is capitalised but not in names
```

Length, one breath per paragraph, nothing a narrator trips on (digits, dashes, brackets), sentences
that end, the opening's score, names spelled one way, a turn at the middle.

</details>

<details>
<summary><b>The moment viewers left, to the second</b></summary>

```text
  retention.csv   101 points   100.0% -> 28.0%

  HOOK LEAK   31.5% lost in the opening   [leaking]
              under 25 is healthy. Fix the first line before anything else.

  CLIFFS      the moments people actually left
    - 12.3%  at     234s
    -  6.3%  at      12s   "Today I want to show you exactly why that happens. um And what you can change..."
    ...
  SLIDE       0.428% lost per 1% of the video (6.0s) across the middle
              a flat slide is pacing, not content. Cut the middle, do not rewrite it.
```

Give it the transcript and each drop comes with what was being said.

</details>

<details>
<summary><b>The Shorts already inside a long video</b></summary>

```text
  3. 1:19 -> 1:55   35s   score 79   hook 54 (The Question)
       first  "Why do viewers leave your videos at thirty seconds?"
       last   "And show them the payoff exists before the minute mark."
```

Spans that start on a fresh thought, end on a finished sentence and never overlap. Claude then writes
each a new first line, because the long video's opening relies on context a Shorts viewer never saw.

</details>

<details>
<summary><b>Chapters that YouTube will actually show</b></summary>

```text
  00:00 Before Change Channels
  00:15 Title Promise Forty
  00:53 Thumbnail Title Word
  01:19 First Open Promise
  01:57 Cliff Middle Retention
```

Boundaries come from the pauses taken and the change of vocabulary across them, checked against
YouTube's rules (00:00 first, at least three, ten seconds each, in order). The titles are drafts;
Claude rewrites them in your voice.

</details>

---

## The twelve, in the order you use them

**Before you record**

| | |
| --- | --- |
| `/yt-plan` | A week that fits the hours you really have: one main video, one quick one, Shorts cut from the main one. |
| `/yt-viral` | What's working in your niche, ranked against **each channel's own** normal views, not raw counts. |
| `/yt-research` | For anything that retells a source: a cited brief of what the source says, then an independent fact check of the script. |
| `/yt-script` | Five openings scored, the best kept, then a script written for the ear, with what's on screen, checked before recording. |
| `/yt-package` | Ten titles checked, the best three shown with their issues, and a thumbnail plan for the winner. |

**After you record**

| | |
| --- | --- |
| `/yt-edit` | The transcript as a cut list: silences, filler and false starts, with timecodes and the length you'll end up with. |
| `/yt-shorts` | The moments that stand on their own, ranked, each with a new first line, on-screen text and a loop. |
| `/yt-chapters` | Chapters drafted from the transcript and checked so they appear. |
| `/yt-seo` | The two description lines people see, tags only where they help, and the three searches this should win. |

**After you publish**

| | |
| --- | --- |
| `/yt-comment` | Comments sorted into questions, corrections, praise and bait; short replies in your voice; the one to pin. |
| `/yt-retention` | The opening loss, the drops and the slide from your Studio export, and the one change that matters most. |
| `/yt-audit` | The whole channel, ending in **one** fix rather than twenty. |

---

## Quick start

**1. Install** in Claude Code:

```text
/plugin marketplace add utillayer/youtube-agent-skill
/plugin install youtube-agent-skill@utillayer
```

**2. Tell it how you sound.** Copy [`templates/voice.md`](templates/voice.md) to
`~/.claude/youtube/voice.md` and fill it in, or send Claude three of your videos and say *"write my
voice.md from these"*. Every skill reads it before writing.

**3. Ask.**

```text
> /yt-script a beginner's guide to home espresso, 8 minutes
> /yt-research what does the original text say about the golden deer?
> /yt-edit ~/Downloads/raw-take.srt
> /yt-retention ~/Downloads/retention.csv, the video is 9:42
```

<details>
<summary><b>Other ways to install: by hand, claude.ai, Codex</b></summary>

**By hand in Claude Code.** Copy all the folders, not just one - several skills use their
neighbours' tools.

```bash
git clone https://github.com/utillayer/youtube-agent-skill.git
cp -r youtube-agent-skill/skills/yt-* ~/.claude/skills/        # or your project's .claude/skills/
```

If the `/yt-` commands don't appear, start a new session.

**claude.ai (web and desktop).** Turn on code execution (Settings > Capabilities), zip each skill
folder (the zip holds the folder, not loose files) and upload it under Customize > Skills. Upload
the neighbours too: `yt-shorts` needs `yt-edit` and `yt-script` beside it. Pasting one `SKILL.md`
into a chat also works, without the tools.

**Codex and other agents.** The skills are plain `SKILL.md` folders. Copy the `yt-*` folders into
`~/.agents/skills/` (or `.agents/skills/` in a project).

</details>

---

## The nine tools

Plain Python 3.8+, standard library only. They work without Claude too.

```bash
python3 skills/yt-script/hookscore.py --hook "one line"         # score an opening
python3 skills/yt-script/scriptcheck.py script.json             # is a script ready to be spoken?
python3 skills/yt-package/title.py --title "..." --thumb "..."  # title + thumbnail check
python3 skills/yt-research/sourcekit.py find source.txt "..."   # where a source says it, with line numbers
python3 skills/yt-edit/deadair.py transcript.srt                # cut list
python3 skills/yt-chapters/chapters.py transcript.srt           # chapters that YouTube accepts
python3 skills/yt-retention/retention.py retention.csv          # where they left, and why
python3 skills/yt-shorts/shorts.py transcript.srt               # moments that stand alone as Shorts
python3 skills/yt-viral/swipe.py channel.json --min 2.0         # outliers against each channel's own median
```

Transcripts can be `.srt`, `.vtt` (YouTube auto-captions included) or whisper `.json`, in any
language. No transcript? `yt-dlp --skip-download --write-auto-subs --sub-format vtt -o transcript <url>`
fetches YouTube's own. `swipe.py` reads `yt-dlp --flat-playlist -J` output directly. Every tool
takes `--json`.

---

## What it won't do

**Publish.** Every skill ends with something to copy and one question: *post it as is, or another
pass?* Nothing here touches your channel or logs in as you.

**Invent.** No made-up numbers, results or quotes. If a line needs a figure it doesn't have, it
asks or leaves the figure out. For retellings, `/yt-research` holds the script to its source.

**Pretend the scores predict views.** The hook panel is hand-set rules, not a model trained on
views. It reliably flags openings that waste the first seconds - the greeting, the channel intro,
the adjective with nothing behind it - but it hasn't been shown to pick the winner between two good
ones. A low score means look again. A high score is not a promise.

**Sell you tags.** YouTube's help page says tags "play a minimal role" in discovery, so the SEO skill
gives them one line.

**Treat rules of thumb as rules.** The 60 and 40 character title limits are what tends to fit, not
published numbers, and the checker says so. When two titles are close, `/yt-package` points you to
Studio's own A/B test rather than trusting either score.

**Help you copy.** `/yt-viral` gives you the shape of what worked, never the video. Remaking someone
else's outlier with the names changed is what YouTube's inauthentic-content policy demonetises.

The hook panel's word lists are English. Filler detection knows English, Spanish, Hindi and Nepali.
Other languages get the timing-based checks, and the tools say so instead of guessing.

---

## Contributing

Bugs and ideas go in [issues](https://github.com/utillayer/youtube-agent-skill/issues). Run the tests
before a pull request; they take under a second:

```bash
python3 -m unittest discover -s tests -v
```

## Licence

MIT.
