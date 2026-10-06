"""Run: python3 -m unittest discover tests"""
import contextlib
import io
import os
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "liftoff")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import liftoff as lo  # noqa: E402


def T(rel):
    return lo.Template(os.path.join(ROOT, rel))


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a)


class Score(unittest.TestCase):
    def test_flagship_is_built_to_stick(self):
        r = lo.score_template(T("templates/liftoff-spacex"))
        self.assertGreaterEqual(r["score"], 90)

    def test_one_shot_bot_scores_low(self):
        r = lo.score_template(T("examples/logo-bot"))
        self.assertLess(r["score"], 20)
        self.assertEqual(r["verdict"], "One-and-done risk")

    def test_rescued_bot_scores_high(self):
        self.assertGreaterEqual(lo.score_template(T("examples/logo-bot-v2"))["score"], 80)

    def test_login_dependency_is_penalized(self):
        r = lo.score_template(T("examples/leaky-bot"))
        self.assertTrue(any("login" in p["why"] for p in r["penalties"]))

    def test_scaffold_has_structure(self):
        with tempfile.TemporaryDirectory() as d:
            root = quiet(lo.new, "Starlink Watch", d)
            self.assertTrue(os.path.isfile(os.path.join(root, "skills/core/starlink-watch/SKILL.md")))
            r = lo.score_template(lo.Template(root))
            ok = {c["key"] for c in r["checks"] if c["ok"]}
            self.assertTrue({"routine", "first", "focus", "triggers", "off", "brief"} <= ok)
            # an unfilled scaffold must not pass as finished
            self.assertGreater(r["unfilled"], 0)
            self.assertLessEqual(r["score"], 40)


class Scan(unittest.TestCase):
    def test_clean_templates_are_safe(self):
        for rel in ("templates/liftoff-spacex", "examples/logo-bot", "examples/logo-bot-v2"):
            self.assertTrue(lo.scan_template(T(rel))["safe"], rel)

    def test_catches_every_planted_leak(self):
        kinds = {h["kind"] for h in lo.scan_template(T("examples/leaky-bot"))["hits"]}
        self.assertTrue({"email", "phone number", "webhook url", "secret value", "won't travel"} <= kinds)

    def test_never_prints_full_secret(self):
        for h in lo.scan_template(T("examples/leaky-bot"))["hits"]:
            self.assertLessEqual(len(h["preview"]), 60)
            self.assertNotIn("7Hq2LmX9vR4tK8wZ", h["preview"])

    def test_detects_keys(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "BOT.md"), "w") as f:
                f.write("use xai-AbCdEf0123456789xyzQ and ghp_" + "a1" * 15 + "\nmail me at bob@example.com\n")
            kinds = [h["kind"] for h in lo.scan_template(lo.Template(d))["hits"]]
            self.assertIn("api key", kinds)
            self.assertIn("github token", kinds)
            self.assertNotIn("email", kinds)  # example.com is allowed


class Post(unittest.TestCase):
    GOOD = "a grok bot that sends every SpaceX launch in your timezone\n\ncopy it free: https://x.ai/bot/t/abc123\n"

    def test_good_post_is_ready(self):
        self.assertTrue(lo.check_post(self.GOOD)["ready"])

    def test_missing_link_blocks(self):
        self.assertFalse(lo.check_post("my new bot is out\n\ncopy it: [SHARE LINK]")["ready"])

    def test_em_dash_and_hype_block(self):
        r = lo.check_post("this game-changer bot — try it https://x.ai/bot/t/x")
        self.assertFalse(r["ready"])

    def test_money_claim_warns_but_does_not_block(self):
        r = lo.check_post("made $500 with this bot\nhttps://x.ai/bot/t/x")
        self.assertTrue(r["ready"])
        self.assertFalse(next(i for i in r["items"] if i["name"].startswith("Money"))["ok"])


class Pack(unittest.TestCase):
    def test_card_has_every_skill_and_routine(self):
        with tempfile.TemporaryDirectory() as d:
            path, safe = lo.pack(T("templates/liftoff-spacex"), d)
            with open(path) as f:
                card = f.read()
            self.assertTrue(safe)
            for slug in ("launch-desk", "starship-explainer", "launch-post"):
                self.assertIn(f"/{slug}", card)
            self.assertIn("Morning brief", card)

    def test_refuses_to_pack_leaky_bot(self):
        with tempfile.TemporaryDirectory() as d:
            code = quiet(lo.main, ["pack", os.path.join(ROOT, "examples/leaky-bot"), "-o", d])
            self.assertEqual(code, 1)
            self.assertFalse(os.path.exists(os.path.join(d, "TEMPLATE_CARD.md")))


if __name__ == "__main__":
    unittest.main()
