# youtube-agent-skill

**Eleven Claude skills for the parts of YouTube that decide whether anyone watches.**
Hooks, titles, thumbnails, the edit, retention, Shorts, chapters, search. Free, MIT, no signup, no
API key, nothing to connect.

[![test](https://github.com/utillayer/youtube-agent-skill/actions/workflows/test.yml/badge.svg)](https://github.com/utillayer/youtube-agent-skill/actions/workflows/test.yml)
![python](https://img.shields.io/badge/python-3.8%2B-3776ab)
![dependencies](https://img.shields.io/badge/dependencies-none-success)
![license](https://img.shields.io/badge/license-MIT-blue)

Most AI writing help for YouTube is a prompt with opinions. This pack ships seven small Python tools
that actually measure things: they score your hook before you record it, lint your title against
your thumbnail, read your retention export down to the second, and turn a raw transcript into a cut
list. Claude does the writing. The tools keep it honest.

```text
> /yt-script a video about why small channels stall at 30 seconds
```

---

## See it work

### Your hook, scored before you waste a take on it

Every channel's default opening, and one written off the pack's [21 hook formulas](skills/yt-script/hooks.json):

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

The verdict is 60% the average and 40% the weakest property, on purpose. A hook with one dead
property leaks at that property, and an average would hide it.

### Your title and thumbnail, linted as one unit

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

### Your raw recording, as a cut list

```text
  talk.srt   147.72s in, 36 cues, dead-air floor 0.45s

    FILLER      9.35 ->     9.95    0.60s   um
    DEAD       13.83 ->    14.98    1.15s   1.60s gap
    FILLER     39.60 ->    40.37    0.77s   so yeah
    REPEAT     97.88 ->    99.81    1.92s   restart of "i think the fix is"
    ...
  10 cuts, 9.94s removed, 137.77s out (6.7% shorter)
```

Dead air is trimmed from the middle so both sides keep a breath. The abandoned take is the one cut,
even with an "um" between the two attempts. It works on YouTube's own auto-captions as they come.

<details>
<summary><b>Your retention graph, read down to the second</b></summary>

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

Pass the transcript and every cliff comes with what you were saying when people left.

</details>

<details>
<summary><b>The Shorts already hiding in a long video</b></summary>

```text
  3. 1:19 -> 1:55   35s   score 75   hook 44 (The Question)
       first  "Why do viewers leave your videos at thirty seconds?"
       last   "And show them the payoff exists before the minute mark."
```

Spans that open on a fresh thought, close on a finished sentence and never overlap. Claude then
writes each a new first line, because the long video's opening assumes context a Shorts viewer
does not have.

</details>

<details>
<summary><b>Chapters YouTube will actually render</b></summary>

```text
  00:00 Before Change Channels
  00:15 Title Promise Forty
  00:53 Thumbnail Title Word
  01:19 First Open Promise
  01:57 Cliff Middle Retention
```

Boundaries come from the pauses you took and the vocabulary shift across them, checked against
YouTube's rules (00:00 first, three or more, ten seconds each, ascending). The titles are drafts;
Claude rewrites them in your voice.

</details>

---

## The eleven, in the order you need them

**Before you record**

| | |
| --- | --- |
| `/yt-plan` | A week that fits the hours you actually have. One anchor video, one cheap one, three Shorts cut from the anchor. |
| `/yt-viral` | What is working in your niche, ranked by how far each video beat **its own channel's** median, not by raw views. |
| `/yt-script` | One idea into a script: five hooks, scored, the best two kept, then every beat with what is on screen. |
| `/yt-package` | Ten titles linted, the top three shown with their issues, and a thumbnail brief for the winner. |

**After you record**

| | |
| --- | --- |
| `/yt-edit` | The transcript into an edit decision list: dead air, filler, retakes, timecodes, the runtime you land on. |
| `/yt-shorts` | The self-contained moments, ranked, each with a new first line, on-screen text and a loop point. |
| `/yt-chapters` | Chapters drafted from the transcript and validated so they render. |
| `/yt-seo` | The two description lines that show above "...more", tags only where they disambiguate, and the three searches this should win. |

**After you publish**

| | |
| --- | --- |
| `/yt-comment` | The comment section sorted into questions, corrections, praise and bait, replies in your voice, and the one to pin. |
| `/yt-retention` | Hook leak, cliffs and slide from your Studio export, and the single change that matters most. |
| `/yt-audit` | The whole channel, ending in **one** fix rather than twenty. |

---

## Quick start

**1. Install** into Claude Code:

```text
/plugin marketplace add utillayer/youtube-agent-skill
/plugin install youtube-agent-skill@utillayer
```

**2. Give it your voice.** Copy [`templates/voice.md`](templates/voice.md) to
`~/.claude/youtube/voice.md` and fill it in, or send Claude three of your videos and say *"write my
voice.md from these"*. Every skill reads it. On YouTube you say the words out loud, so a script in
someone else's voice is unreadable on camera.

**3. Ask for something.**

```text
> /yt-script a beginner's guide to home espresso, 8 minutes
> /yt-edit ~/Downloads/raw-take.srt
> /yt-retention ~/Downloads/retention.csv, the video is 9:42
> /yt-package I need a title for the espresso video
```

<details>
<summary><b>Other ways to install: by hand, claude.ai, Codex</b></summary>

**By hand, in Claude Code.** Copy all the folders, not one: `/yt-chapters`, `/yt-retention`,
`/yt-shorts`, `/yt-viral` and `/yt-audit` borrow tools from their neighbours.

```bash
git clone https://github.com/utillayer/youtube-agent-skill.git
cp -r youtube-agent-skill/skills/yt-* ~/.claude/skills/        # or your repo's .claude/skills/
```

Or paste the repo URL into Claude Code with *"install this skill, then confirm /yt-script works"*.
If the `/yt-` commands do not show up, start a new session.

**claude.ai (web and desktop).** Turn on code execution (Settings > Capabilities), zip each skill
folder (the zip holds the folder, not loose files) and upload it under Customize > Skills. Upload
the neighbours too: `yt-shorts` needs `yt-edit` and `yt-script` beside it. Pasting a single
`SKILL.md` into a chat also works as a mode, without the tools.

**Codex and other agents.** The skills are plain `SKILL.md` folders. Copy the `yt-*` folders into
`~/.agents/skills/` (or `.agents/skills/` in a project).

</details>

---

## The seven tools

Plain Python 3.8+, standard library only. Use them without Claude if you like.

```bash
python3 skills/yt-script/hookscore.py --hook "one line"        # 5-property hook panel
python3 skills/yt-package/title.py --title "..." --thumb "..." # title + thumbnail linter
python3 skills/yt-edit/deadair.py transcript.srt               # edit decision list
python3 skills/yt-chapters/chapters.py transcript.srt          # validated chapters
python3 skills/yt-retention/retention.py retention.csv         # where they left, and why
python3 skills/yt-shorts/shorts.py transcript.srt              # spans that stand alone as Shorts
python3 skills/yt-viral/swipe.py channel.json --min 2.0        # outliers by own-channel multiple
```

Transcripts can be `.srt`, `.vtt` (YouTube auto-captions included) or whisper `.json`, in any
language. `swipe.py` reads `yt-dlp --flat-playlist -J` output as it is. Every tool takes `--json`.

---

## What it will not do

**Publish.** Every skill ends in a block you copy and one question: *ship it, or change it?* Nothing
here touches your channel, and nothing logs in as you.

**Invent a number.** If a skill wants a figure it does not have, it asks you or writes the line
without it.

**Pretend the score is a prediction.** The hook panel was calibrated on 74 real hooks (top and bottom
eight by views across five channels). It tells a deliberately bad hook from a real one well, and a
creator's hits from their own misses barely at all. A low score means look again. A high score is
not a promise.

**Sell you tags.** YouTube's own help page says tags "play a minimal role" in discovery, so the SEO
skill spends one line on them.

**Treat folk numbers as rules.** The 60 and 40 character title limits are what survives on screen,
not anything YouTube publishes, and the linter says so. When two titles are close, the package
skill tells you to run Studio's built-in A/B test instead of trusting either score.

**Help you copy.** `/yt-viral` hands you the shape of what worked, never the video. Remaking someone
else's outlier with the nouns swapped is what YouTube's inauthentic-content policy demonetises.

The word lists behind filler detection and the hook panel are English, with Spanish fillers too.
Other languages get the timing-based checks, and the tools say so instead of guessing.

---

## Contributing

Bugs and ideas go in [issues](https://github.com/utillayer/youtube-agent-skill/issues). Before a pull
request, run the suite; it takes under a second:

```bash
python3 -m unittest discover -s tests -v
```

## Licence

MIT. Use it, change it, ship it.
