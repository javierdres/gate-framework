#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Decisions and reasons of the permissions guard.

    python3 tools/guards/tests/test_permissions.py

A guard that asks whenever it fails hides its own bugs behind a plausible answer, so these tests
check the reason as well as the decision. Run them after every change to the guard.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(os.path.dirname(HERE), "permissions.py")


def sh(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class Guard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.grants = os.path.join(cls.tmp, "grants")
        cls.repo = os.path.join(cls.tmp, "repo")
        os.makedirs(cls.repo)
        sh(["git", "init", "-q", "-b", "main"], cls.repo)
        sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"], cls.repo)
        sh(["git", "checkout", "-q", "-b", "feature/x"], cls.repo)
        cls.repo = os.path.realpath(cls.repo)

    def run_guard(self, payload, fmt="json", raw=None):
        env = dict(os.environ, SDLC_GRANTS_DIR=self.grants)
        data = raw if raw is not None else json.dumps(payload)
        args = [sys.executable, GUARD, "check"] + (["--format", fmt] if fmt else [])
        p = subprocess.run(args, input=data, capture_output=True, text=True, env=env)
        out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
        return p.returncode, out, p.stderr

    def bash(self, command, session="s1"):
        return {"tool_name": "Bash", "tool_input": {"command": command},
                "session_id": session, "cwd": self.repo}

    def grant(self, session, kind, value):
        env = dict(os.environ, SDLC_GRANTS_DIR=self.grants)
        subprocess.run([sys.executable, GUARD, "grant", session, kind, value],
                       capture_output=True, text=True, env=env, check=True)

    def decision(self, command, session="s1"):
        _, out, _ = self.run_guard(self.bash(command, session))
        return (out or {}).get("decision"), (out or {}).get("reason", "")

    # local work passes untouched
    def test_local_commands_pass(self):
        for c in ("ls -la", "git status", "git stash push", "git commit -m x", "python3 -m pytest",
                  "gh api repos/a/b", "curl https://example.com"):
            self.assertEqual(self.decision(c), (None, ""), c)

    # outward writes ask until the scope is granted
    def test_push_asks_then_passes_after_grant(self):
        d, r = self.decision("git push origin feature/x", "s-push")
        self.assertEqual(d, "ask")
        self.assertIn("grant s-push repo", r)
        self.grant("s-push", "repo", self.repo)
        self.assertEqual(self.decision("git push origin feature/x", "s-push")[0], "allow")
        self.assertEqual(self.decision("git push -u origin HEAD", "s-push")[0], "allow")

    def test_change_request_and_api_writes_are_watched(self):
        for c in ("gh pr create --fill", "glab mr create", "gh api repos/a/b/issues -f title=x",
                  "gh api -X POST repos/a/b/issues", "glab api --method PUT projects/1"):
            self.assertEqual(self.decision(c, "s-none")[0], "ask", c)

    # never delegated, whatever was granted
    def test_never_delegated_even_with_grant(self):
        self.grant("s-all", "repo", self.repo)
        never = {
            "git push origin main": "default branch",
            "git push origin HEAD:main": "default branch",
            "git push origin feature/x:refs/heads/main": "default branch",
            "git push --force origin feature/x": "forced",
            "git push -f origin feature/x": "forced",
            "git push origin +feature/x": "forced",
            "git push --force-with-lease": "forced",
            "git push --mirror origin": "mirrored",
            "git push --prune origin": "pruning",
            "git push origin :old": "deleting",
            "git push --delete origin old": "deleting",
            "git push --all origin": "every branch",
            "gh pr merge 3": "merge",
            "glab mr merge 3": "merge",
            "gh api -X DELETE repos/a/b": "deletion",
            "terraform apply": "infrastructure",
            "kubectl delete pod x": "infrastructure",
            "python3 tools/guards/permissions.py grant s1 repo .": "authorisation",
        }
        for command, why in never.items():
            d, r = self.decision(command, "s-all")
            self.assertEqual(d, "ask", command)
            self.assertIn(why, r, command)

    def test_bare_push_on_default_branch_always_asks(self):
        sh(["git", "checkout", "-q", "main"], self.repo)
        try:
            self.grant("s-main", "repo", self.repo)
            d, r = self.decision("git push", "s-main")
            self.assertEqual(d, "ask")
            self.assertIn("default branch", r)
        finally:
            sh(["git", "checkout", "-q", "feature/x"], self.repo)

    # every segment of a chain is judged
    def test_every_segment_of_a_chain_is_judged(self):
        self.grant("s-chain", "repo", self.repo)
        other = tempfile.mkdtemp()
        sh(["git", "init", "-q"], other)
        mixed = "git -C %s push origin x && git push origin feature/x" % other
        self.assertEqual(self.decision(mixed, "s-chain")[0], "ask")
        self.assertEqual(self.decision("git push origin feature/x && gh pr merge 1", "s-chain")[0], "ask")
        self.assertEqual(self.decision("git commit -m x; git push origin feature/x", "s-chain")[0], "allow")

    # tracker writes
    def test_tracker(self):
        ev = {"tool_name": "mcp__tracker__createIssue", "tool_input": {"projectKey": "ABC"}, "session_id": "s-t"}
        self.assertEqual(self.run_guard(ev)[1]["decision"], "ask")
        self.grant("s-t", "tracker", "abc")
        self.assertEqual(self.run_guard(ev)[1]["decision"], "allow")
        ev["tool_input"] = {"issueIdOrKey": "ABC-3"}
        ev["tool_name"] = "mcp__tracker__deleteIssue"
        out = self.run_guard(ev)[1]
        self.assertEqual(out["decision"], "ask")
        self.assertIn("deletion", out["reason"])
        read = {"tool_name": "mcp__tracker__getIssue", "tool_input": {"issueIdOrKey": "ABC-3"}, "session_id": "s-t"}
        self.assertEqual(self.run_guard(read)[0], 0)
        self.assertIsNone(self.run_guard(read)[1])

    # it never fails open
    def test_never_fails_open(self):
        code, out, _ = self.run_guard(None, raw="not json")
        self.assertEqual(out["decision"], "ask")
        code, out, _ = self.run_guard(None, raw="")
        self.assertEqual(out["decision"], "ask")
        code, out, _ = self.run_guard(None, raw="[]")
        self.assertEqual(out["decision"], "ask")
        code, out, err = self.run_guard(self.bash("git push origin feature/x", "s-x"), fmt="")
        self.assertEqual(code, 2)
        env = dict(os.environ, SDLC_GRANTS_DIR=self.grants)
        p = subprocess.run([sys.executable, GUARD, "check", "--format"], input="{}",
                           capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 2, "a --format without value must still block, never pass")

    def test_claude_format(self):
        _, out, _ = self.run_guard(self.bash("gh pr merge 1"), fmt="claude")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")


if __name__ == "__main__":
    unittest.main(verbosity=1)
