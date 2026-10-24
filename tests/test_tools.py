"""Regression tests for the seven tools. Standard library only, like the tools themselves.

    python3 -m unittest discover -s tests -v
"""
import json, os, subprocess, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
FIX = os.path.join(ROOT, "tests", "fixtures")
for d in ("yt-edit", "yt-script", "yt-package", "yt-chapters", "yt-retention", "yt-viral", "yt-shorts"):
    sys.path.insert(0, os.path.join(SKILLS, d))

import deadair, hookscore, title, chapters, retention, swipe, shorts  # noqa: E402

def run(tool, *args):
    """Run a tool the way a skill does: from somewhere else, by path."""
    r = subprocess.run([sys.executable, os.path.join(SKILLS, tool), *args], capture_output=True,
                       text=True, cwd=FIX, encoding="utf-8")
    return r.returncode, r.stdout, r.stderr

def fixture(name): return os.path.join(FIX, name)

def read(path):
    with open(path, encoding="utf-8") as fh: return fh.read()


class DeadAir(unittest.TestCase):
    def setUp(self):
        self.cues = deadair.load(fixture("talk.srt"))

    def test_finds_each_kind(self):
        kinds = {c["kind"] for c in deadair.edl(self.cues)}
        self.assertEqual(kinds, {"DEAD", "FILLER", "REPEAT"})

    def test_shorter_abandoned_take_is_a_restart(self):
        # the first take is cut off, so it is shorter than five words - the case the old check missed
        self.assertTrue(deadair.restarted("I think the fix is", "I think the fix is to say the promise"))
        self.assertFalse(deadair.restarted("I think so", "I think the fix is"))
        self.assertFalse(deadair.restarted("so", "so"))

    def test_restart_cuts_the_first_take(self):
        rep = [c for c in deadair.edl(self.cues) if c["kind"] == "REPEAT"]
        self.assertEqual(len(rep), 1)
        kept = [c for c in self.cues if c[0] == rep[0]["start"]]
        self.assertEqual(kept[0][2], "I think the fix is")

    def test_youtube_auto_captions_are_clean(self):
        cues = deadair.load(fixture("auto.vtt"))
        text = " ".join(c[2] for c in cues)
        self.assertNotIn("<", text)
        self.assertEqual(len(cues), 4)                # rolling repeats and 10ms cues collapsed
        self.assertTrue(cues[0][2].startswith("Most channels lose"))
        self.assertFalse(any(deadair.restarted(a[2], b[2]) for a, b in zip(cues, cues[1:])))

    def test_unicode_norm(self):
        self.assertEqual(deadair.norm("Déjame ver"), ["déjame", "ver"])
        self.assertEqual(deadair.norm("привет, канал"), ["привет", "канал"])
        self.assertTrue(deadair.FILLER_ONLY.match("bueno, o sea..."))
        self.assertFalse(deadair.FILLER_ONLY.match("bueno saber eso"))

    def test_hindi_and_nepali_fillers(self):
        for s in ("matlab, toh", "अच्छा, तो।", "ठीक है", "ani ta", "khai ke re", "अनि"):
            self.assertTrue(deadair.FILLER_ONLY.match(s), s)
        for s in ("are", "matlab kya hai", "मतलब यह है कि", "tomato"):
            self.assertFalse(deadair.FILLER_ONLY.match(s), s)

    def test_caption_annotations_are_not_speech(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".srt", delete=False, encoding="utf-8") as f:
            f.write("1\n00:00:00,000 --> 00:00:02,000\n[Music]\n\n"
                    "2\n00:00:02,000 --> 00:00:04,000\n[Applause] thank you all\n")
        cues = deadair.load(f.name)
        os.unlink(f.name)
        self.assertEqual(cues, [(2.0, 4.0, "thank you all")])

    def test_overlapping_cuts_counted_once(self):
        cuts = [{"start": 0, "end": 2}, {"start": 1, "end": 3}, {"start": 5, "end": 6}]
        self.assertEqual(deadair.merge(cuts), 4)

    def test_whisper_json_list_and_dict(self):
        import tempfile
        segs = [{"start": 0, "end": 1, "text": " hi"}, {"start": 2, "end": 3, "text": "there"}]
        for payload in (segs, {"segments": segs}):
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
                json.dump(payload, f)
            self.assertEqual(deadair.load(f.name), [(0.0, 1.0, "hi"), (2.0, 3.0, "there")])
            os.unlink(f.name)

    def test_cli_json(self):
        code, out, _ = run("yt-edit/deadair.py", "talk.srt", "--floor", "0.5", "--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertLess(d["out"], d["duration"])


class HookScore(unittest.TestCase):
    def test_units_stay_with_figures(self):
        found = [m.group(0) for m in hookscore.CONCRETE.finditer("$500 in 3 days, 97% and 3x")]
        self.assertEqual(found, ["$500", "3 days", "97%", "3x"])

    def test_bad_hook_below_good_hook(self):
        good = hookscore.score("You are losing 40% of viewers in 30 seconds and the reason is not your topic.")[1]
        bad = hookscore.score("Hey guys welcome back to the channel, today is going to be amazing.")[1]
        self.assertGreater(good, bad)

    def test_classify_tie_goes_to_first_listed(self):
        # "stop" matches both The Mistake and The Warning once each; The Mistake is listed first
        self.assertEqual(hookscore.classify("Stop wasting your mornings")[0], "The Mistake")

    def test_cli_missing_file_fails(self):
        code, _, err = run("yt-script/hookscore.py", "nope.txt")
        self.assertNotEqual(code, 0)
        self.assertIn("no such file", err)

    def test_twenty_one_formulas(self):
        self.assertEqual(len(hookscore.FORMULAS), 21)
        self.assertEqual(len({f["id"] for f in hookscore.FORMULAS}), 21)


class Title(unittest.TestCase):
    def test_four_word_thumbnail_flagged(self):
        r = title.check("Why your 2026 channel stalls", "IT WAS THE HOOK")
        self.assertIn("thumb-length", [k for k, _ in r["issues"]])

    def test_three_word_thumbnail_ok(self):
        r = title.check("Why your 2026 channel stalls", "ONE BAD LINE")
        self.assertNotIn("thumb-length", [k for k, _ in r["issues"]])

    def test_duplicate_words(self):
        r = title.check("I tested 40 titles", "40 TITLES")
        self.assertIn("duplicate", [k for k, _ in r["issues"]])

    def test_arabic(self):
        r = title.check("ليه التطبيق واقع على السيرفر؟", "السيرفر واقع")
        kinds = [k for k, _ in r["issues"]]
        self.assertIn("duplicate", kinds)
        self.assertNotIn("front-load", kinds)
        self.assertIn("open question in the title", r["good"])

    def test_length_bands(self):
        self.assertIn("length", [k for k, _ in title.check("x" * 70)["issues"]])
        self.assertIn("mobile", [k for k, _ in title.check("word " * 10)["issues"]])

    def test_cli_unicode_json(self):
        code, out, _ = run("yt-package/title.py", "--title", "Qué pasó con 3 canales", "--json")
        self.assertEqual(code, 0)
        self.assertIn("Qué", out)


class Chapters(unittest.TestCase):
    def test_valid_and_on_section_breaks(self):
        ch, ok = chapters.chapter(deadair.load(fixture("talk.srt")), target=5)
        self.assertTrue(ok)
        self.assertEqual(ch[0]["label"], "00:00")
        starts = [c["start"] for c in ch]
        self.assertEqual(starts, sorted(starts))
        # the four long pauses in the fixture are the four topic changes
        for want in (15, 54, 79, 117):
            self.assertTrue(any(abs(s - want) < 2 for s in starts), (want, starts))

    def test_unicode_keywords(self):
        self.assertEqual(chapters.keywords("Codificación de scripts"), {"codificación", "scripts"})
        self.assertEqual(chapters.keywords("привет настройка канала"), {"привет", "настройка", "канала"})
        self.assertIn("don't", chapters.keywords("don't stop"))

    def test_hour_labels(self):
        self.assertEqual(chapters.mmss(65), "01:05")
        self.assertEqual(chapters.mmss(3725), "1:02:05")


class Retention(unittest.TestCase):
    def test_header_says_seconds(self):
        rows, unit = retention.load_csv(fixture("retention_seconds.csv"))
        self.assertEqual(unit, "seconds")
        out = retention.analyse(rows, unit)
        self.assertEqual(out["axis"], "seconds")       # max position is 90, which once read as percent
        self.assertEqual(out["cliffs"][0]["at_seconds"], 48.0)

    def test_percent_with_duration(self):
        rows, unit = retention.load_csv(fixture("retention_pct.csv"))
        out = retention.analyse(rows, unit, dur=600)
        self.assertEqual(out["axis"], "percent")
        self.assertEqual(out["cliffs"][0]["from"], 39.0)
        self.assertEqual(out["cliffs"][0]["at_seconds"], 234.0)

    def test_ratio_export_scaled(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("elapsedVideoTimeRatio,audienceWatchRatio\n")
            for i in range(1, 101): f.write(f"{i / 100},{1 - i / 200}\n")
        rows, unit = retention.load_csv(f.name)
        os.unlink(f.name)
        self.assertEqual(unit, "percent")
        self.assertAlmostEqual(rows[-1][0], 100)

    def test_cli_flag_order_does_not_matter(self):
        code, out, _ = run("yt-retention/retention.py", "--duration", "600", "retention_pct.csv", "--json")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["cliffs"][0]["at_seconds"], 234.0)


class Swipe(unittest.TestCase):
    def test_ytdlp_shape_and_missing_views(self):
        data = {"channel": "Small", "entries": [
            {"title": f"Video {i}", "view_count": v, "url": f"u{i}", "duration": 600}
            for i, v in enumerate([1000, 1200, 900, 1100, 9000, None])]}
        rows = list(swipe.videos(data))
        self.assertEqual({r["channel"] for r in rows}, {"Small"})
        out, thin, missing, _ = swipe.rank(rows, lo=2.0)
        self.assertEqual(missing, 1)                  # not counted as zero views
        self.assertEqual([r["title"] for r in out], ["Video 4"])
        self.assertEqual(out[0]["multiple"], 8.18)

    def test_shorts_medianed_apart(self):
        rows = [{"channel": "C", "title": f"L{i}", "views": 1000, "url": "", "duration": 600} for i in range(4)]
        rows += [{"channel": "C", "title": f"S{i}", "views": 50000, "url": "", "duration": 40} for i in range(4)]
        out, _, _, groups = swipe.rank(rows, lo=1.5)
        self.assertEqual(groups, 2)
        self.assertEqual(out, [])                     # a Short is not an outlier against long-form

    def test_thin_channel_skipped(self):
        rows = [{"channel": "T", "title": "x", "views": 10, "url": "", "duration": None}] * 3
        _, thin, _, _ = swipe.rank(rows)
        self.assertEqual(thin, [("T", 3)])

    def test_same_label_as_hookscore(self):
        for t in ("Stop wasting your mornings", "I tried posting daily for 30 days", "Why nobody opens this?"):
            self.assertEqual(swipe.classify(t), hookscore.classify(t)[0])


class Shorts(unittest.TestCase):
    def test_finds_self_contained_spans(self):
        kept = shorts.pick(shorts.candidates(deadair.load(fixture("talk.srt"))), top=5)
        self.assertGreaterEqual(len(kept), 3)
        for a, b in zip(kept, kept[1:]): self.assertLessEqual(a["end"], b["start"])
        for c in kept:
            self.assertTrue(20 <= c["seconds"] <= 55)
            self.assertNotIn(shorts.first_word(c["first_line"]), shorts.DANGLING)

    def test_question_section_found(self):
        kept = shorts.pick(shorts.candidates(deadair.load(fixture("talk.srt"))), top=5)
        self.assertTrue(any(c["first_line"].startswith("Why do viewers leave") for c in kept))

    def test_unpunctuated_transcript_flagged(self):
        self.assertTrue(shorts.unpunctuated(deadair.load(fixture("auto.vtt"))))
        self.assertFalse(shorts.unpunctuated(deadair.load(fixture("talk.srt"))))

    def test_cli_rejects_long_max(self):
        code, _, err = run("yt-shorts/shorts.py", "talk.srt", "--max", "300")
        self.assertNotEqual(code, 0)


class Skills(unittest.TestCase):
    """Every SKILL.md has the frontmatter Claude Code, claude.ai and Codex all need, and every script
    a skill names exists."""
    def test_frontmatter_and_scripts(self):
        import re
        for d in sorted(os.listdir(SKILLS)):
            body = read(os.path.join(SKILLS, d, "SKILL.md"))
            self.assertTrue(body.startswith("---\n"), d)
            self.assertRegex(body, rf"\nname: {d}\n", d)
            self.assertIn("\ndescription:", body, d)
            for rel in re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w./-]+\.(?:py|json))", body):
                self.assertTrue(os.path.exists(os.path.normpath(os.path.join(SKILLS, d, rel))), (d, rel))


if __name__ == "__main__":
    unittest.main()
