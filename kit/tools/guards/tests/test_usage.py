#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The usage guard: the status line, the warning when a window runs fast and the way back.

    python3 tools/guards/tests/test_usage.py

The guard runs on every refresh and every message of every session: if it breaks, the person
loses the warning without knowing. Each end-to-end test runs it with a throwaway home folder.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest

GUARD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "usage.py")
sys.path.insert(0, os.path.dirname(GUARD))
import usage  # noqa: E402

NOW = 1_800_000_000
plain = lambda s: re.sub(r"\033\[[0-9;]*m", "", s)  # noqa: E731


def status(used, resets_in, model="claude-opus"):
    return {"model": {"id": model, "display_name": "Opus"}, "context_window": {"used_percentage": 34},
            "rate_limits": {"five_hour": {"used_percentage": used, "resets_at": NOW + resets_in}}}


class StatusLine(unittest.TestCase):
    def test_window_with_reset(self):
        line = plain(usage.status_line(status(20, 7200), NOW))
        self.assertIn("context 34%", line)
        self.assertIn("5 h ▰▰▱▱▱▱▱▱▱▱ 20%", line)
        self.assertIn("(in 2h 00m)", line)
        self.assertNotIn("runs out", line)

    def test_fast_pace(self):
        # 72% two hours into five: gone before the reset.
        self.assertIn("runs out", usage.status_line(status(72, 10800), NOW))

    def test_no_windows(self):
        self.assertEqual(usage.status_line({"model": {"display_name": "Opus"}}, NOW), "Opus")


class Decide(unittest.TestCase):
    def state(self, runs_out, model="claude-opus"):
        return {"model": model, "windows": {"five_hour": {
            "label": "5 h", "pct": 72, "resets_at": NOW + 10800, "runs_out": runs_out}}}

    def test_warns_once_then_restores(self):
        warning, mark = usage.decide(self.state(NOW + 3000), {})
        self.assertEqual(warning, ("save", "five_hour"))
        self.assertIsNone(usage.decide(self.state(NOW + 2900), mark)[0])
        warning, mark = usage.decide({"model": "claude-sonnet", "windows": {}}, mark)
        self.assertEqual(warning, ("restore", "five_hour"))
        self.assertEqual(mark, {"level": "normal"})

    def test_restore_says_nothing_on_the_capable_model(self):
        self.assertEqual(usage.messages(("restore", "five_hour"), self.state(None), NOW), (None, None))


class EndToEnd(unittest.TestCase):
    def run_guard(self, home, args, stdin):
        env = dict(os.environ, HOME=home)
        return subprocess.run([sys.executable, GUARD] + args, input=stdin, capture_output=True,
                              text=True, env=env).stdout

    def test_status_records_and_check_warns_once(self):
        home = tempfile.mkdtemp()
        now = time.time()
        s = {"model": {"id": "claude-opus", "display_name": "Opus"},
             "rate_limits": {"five_hour": {"used_percentage": 72, "resets_at": now + 10800}}}
        self.run_guard(home, ["status"], json.dumps(s))
        first = self.run_guard(home, ["check", "--format", "claude"], '{"session_id": "s1"}')
        second = self.run_guard(home, ["check", "--format", "claude"], '{"session_id": "s1"}')
        self.assertIn("Usage running fast", json.loads(first)["systemMessage"])
        self.assertEqual(second, "")

    def test_broken_input_never_fails(self):
        home = tempfile.mkdtemp()
        self.assertEqual(self.run_guard(home, ["status"], "not json"), "\n")
        self.assertEqual(self.run_guard(home, ["check"], "not json"), "")


if __name__ == "__main__":
    unittest.main()
