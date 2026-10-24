# youtube-agent-skill

Eleven Claude skills that run a YouTube channel. Free, MIT, no signup, no API key, nothing to
connect.

One of them writes your script off 21 hook formulas and scores the hook before you waste a take on
it. One lints the title and the thumbnail as a single pairing, because writing them separately is
why half of your click surface says the same thing twice. One reads your audience-retention export
and tells you the exact second people left and what you were saying when they did. One turns a
transcript into an edit decision list. One finds the Shorts already hiding inside a long video. One
goes and finds what is working in your niche and ranks it by how far each video beat its own
channel, not by how big the channel is.

**Nothing gets published until you do it.** These skills write. You upload. Nothing here connects to
your channel either: you bring the transcript, the retention export or the titles, and the skills
work on those.

## Install

This is built for **Claude Code**, the terminal and IDE version of Claude, because seven of the
skills run a small Python tool. It also works on claude.ai and in Codex, with the differences below.

### Claude Code

Paste this into Claude Code. A claude.ai chat cannot clone a repo, so this line does nothing there:

```
https://github.com/utillayer/youtube-agent-skill

Install this skill, then confirm /yt-script works.
```

Or do it yourself:

```bash
git clone https://github.com/utillayer/youtube-agent-skill.git
cp -r youtube-agent-skill/skills/yt-* ~/.claude/skills/
```

Or as a plugin:

```
/plugin marketplace add utillayer/youtube-agent-skill
/plugin install youtube-agent-skill@utillayer
```

Project-local instead of global: copy the same folders into your repo's `.claude/skills/`. Copy all
of them, not one: `/yt-chapters`, `/yt-retention`, `/yt-shorts`, `/yt-viral` and `/yt-audit` borrow
tools from their neighbours. If the `/yt-` commands do not show up, start a new session.

### claude.ai (web and desktop)

Turn on code execution (Settings > Capabilities), then zip each skill folder - the zip holds the
folder, not the loose files - and upload it under Customize > Skills. The tools run in Claude's
sandbox. Upload the neighbours too: `yt-shorts` needs `yt-edit` and `yt-script` beside it.

Or paste any single `SKILL.md` at the top of a chat and it runs as a mode. You lose the Python tools,
which is most of the point of `/yt-script`, `/yt-retention`, `/yt-edit` and `/yt-shorts`, but the rest
works.

### Codex and other agents

The skills are plain `SKILL.md` folders, the format Codex reads too. Copy the `yt-*` folders into
`~/.agents/skills/` (or `.agents/skills/` in a project). `~/.claude/youtube/voice.md` is still where
the voice file lives; tell the agent if you keep it somewhere else.

Then spend ten minutes on [`templates/voice.md`](templates/voice.md). Copy it to
`~/.claude/youtube/voice.md` and fill it in, or send Claude three of your own videos and say "write
my voice.md from these". Every skill reads that file. It matters more here than anywhere else,
because you have to say the words out loud.

## The eleven

| command | what it does |
| --- | --- |
| `/yt-script` | One idea into a script. Five hooks off [21 formulas](skills/yt-script/hooks.json), scored, then the spoken script with the retention beats marked. |
| `/yt-package` | Title and thumbnail as one pairing, linted for truncation, duplication and vagueness. |
| `/yt-edit` | A transcript into an edit decision list: dead air, filler cues, retakes, with timecodes. |
| `/yt-comment` | The comment section triaged into four piles, then replies in your voice. Says which one to pin. |
| `/yt-plan` | A week that fits the hours you actually have. One anchor, one cheap one, three Shorts. |
| `/yt-viral` | What is working in your niche, ranked by multiple over each channel's own median. |
| `/yt-retention` | Your retention export read properly: hook leak, the cliffs, the slide, and what to change. |
| `/yt-shorts` | The Shorts already inside a long video, found by timing and hook score, with a new first line written for each. |
| `/yt-seo` | The description, the tags that are worth having, and the three queries this should win. |
| `/yt-chapters` | Chapters from a transcript, validated against YouTube's own rules so they render. |
| `/yt-audit` | The whole channel, ending in ONE fix rather than twenty. |

## The seven tools

Every one of these runs on a clean Python 3.8+ with no dependencies. They are the reason the skills
are not just prompts.

```bash
python3 skills/yt-script/hookscore.py --hook "one line"        # 5-property hook panel
python3 skills/yt-package/title.py --title "..." --thumb "..." # title + thumbnail linter
python3 skills/yt-edit/deadair.py transcript.srt               # edit decision list
python3 skills/yt-chapters/chapters.py transcript.srt          # validated chapters
python3 skills/yt-retention/retention.py retention.csv         # where they left, and why
python3 skills/yt-viral/swipe.py collected.json --min 2.0      # outliers by own-channel multiple
python3 skills/yt-shorts/shorts.py transcript.srt              # spans that stand alone as Shorts
```

Transcripts can be `.srt`, `.vtt` (YouTube's auto-captions included) or whisper `.json`, in any
language. The word lists behind filler detection and the hook panel are English, with a Spanish
filler list; other languages get the timing-based checks and say so.

To check a change to any of them:

```bash
python3 -m unittest discover -s tests -v
```

## The fine print

The part most packs leave out.

**It does not publish.** YouTube's Data API would allow it with your own OAuth. It is still not
built here: every skill ends in a block you copy and a question — ship it, or change it?
Anything that claims to run your channel unattended should be read with that distinction in mind.

**`hookscore.py` is a heuristic, not a predictor.** The panel was built and calibrated against 74
real short-form hooks (the first 15 seconds of auto-captions, top-8 and bottom-8 by views across
five channels). It separates deliberately bad hooks from real ones well. It separates a given
creator's hits from their own misses barely at all. A low score is a reason to look again; a high
score is not a promise.

**The formula classifier is about the words, not the result.** When `/yt-viral` says a title used
The Statistic, that is a judgement about the title you can see, not a claim about why the video got
its views.

**`/yt-viral` reads, it does not scrape.** Public listings only. It never logs in as you and never
touches your credentials.

**Tags barely matter** and this pack says so instead of selling you a tag generator.

**The 60 and 40 character title limits are rules of thumb.** YouTube publishes no truncation
numbers; they come from what survives on screen, and `title.py` reports them as that.

**No AI label needed for what this writes.** YouTube's disclosure rule covers realistic synthetic
people, places and events, and explicitly exempts AI help with scripts, titles, thumbnails and
ideas.

**Nothing invents a number.** If a skill wants a figure it does not have, it asks you for it or
writes the line without it.

## Licence

MIT. Use it, change it, ship it.
