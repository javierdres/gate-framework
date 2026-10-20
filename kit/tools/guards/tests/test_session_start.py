#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The session start guard: configuration reading, identity and the person's log.

    python3 tools/guards/tests/test_session_start.py

Each test builds a throwaway SDLC with a copy of the guard. The SSH identity test needs
ssh-keygen.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

GUARD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session_start.py")


def sh(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


class SessionStart(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "tools", "guards"))
        os.makedirs(os.path.join(self.root, "personal", "sessions"))
        shutil.copy(GUARD, os.path.join(self.root, "tools", "guards", "session_start.py"))
        sh(["git", "init", "-q", "-b", "main"], self.root)
        self.home = tempfile.mkdtemp()
        self.env = dict(os.environ, HOME=self.home, GIT_CONFIG_GLOBAL=os.path.join(self.home, ".gitconfig"),
                        GIT_CONFIG_NOSYSTEM="1", SSH_AUTH_SOCK="")

    def tearDown(self):
        shutil.rmtree(self.root)
        shutil.rmtree(self.home)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def run_guard(self):
        p = sh([sys.executable, os.path.join(self.root, "tools", "guards", "session_start.py")], self.root, self.env)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def test_reads_escaped_and_commented_values(self):
        self.write("sdlc.yml", 'gate:\n  version: "abc1234"   # pinned\nbuilt: ""\nidentity:\n'
                   '  method: platform\n  command: "printf \\"%s\\" \\"person-1 #x\\""   # a comment\n')
        self.write("GOVERNANCE.md", "## Profiles enabled\n\n| Person | Identity | Profiles |\n| --- | --- | --- |\n"
                   "| Someone | person-1 #x | backend |\n")
        out = self.run_guard()
        self.assertIn("GATE version: abc1234", out)
        self.assertIn("not built yet", out)
        self.assertIn("Identity: person-1 #x (platform account)", out)
        self.assertIn("Profiles enabled: backend", out)

    def test_ssh_identity_needs_the_private_key(self):
        for who in ("a", "b"):
            sh(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", os.path.join(self.home, who), "-C", who], self.home)
        pub = {}
        for w in ("a", "b"):
            with io.open(os.path.join(self.home, w + ".pub")) as f:
                pub[w] = f.read().split()
        self.write("allowed_signers", "a@x namespaces=\"git\" %s %s\nb@x namespaces=\"git\" %s %s\n"
                   % (pub["a"][0], pub["a"][1], pub["b"][0], pub["b"][1]))
        self.write("sdlc.yml", "identity:\n  method: ssh-signing\n")
        self.write("GOVERNANCE.md", "## Profiles enabled\n\n| Person | Identity | Profiles |\n| --- | --- | --- |\n"
                   "| A | a@x | backend |\n| B | b@x | product |\n")
        sh(["git", "config", "user.signingkey", os.path.join(self.home, "a.pub")], self.root, self.env)
        out = self.run_guard()
        self.assertIn("Identity: a@x", out)
        self.assertIn("Profiles enabled: backend", out)
        # someone holding only b's public key cannot become b
        stolen = os.path.join(tempfile.mkdtemp(), "b.pub")
        shutil.copy(os.path.join(self.home, "b.pub"), stolen)
        sh(["git", "config", "user.signingkey", stolen], self.root, self.env)
        out = self.run_guard()
        self.assertNotIn("Identity: b@x", out)
        self.assertIn("could not sign", out)

    def test_open_items_in_any_language(self):
        self.write("sdlc.yml", "built: 2026-10-01\n")
        self.write("personal/sessions/README.md", "# Bitácora\n\n## Abierto\n\n- tema uno\n\n## Por tema\n- x\n")
        self.assertIn("tema uno", self.run_guard())
        self.write("personal/sessions/README.md", "# Log\n\n## Offen\n<!-- sdlc:open -->\n- thema zwei\n\n## Rest\n")
        out = self.run_guard()
        self.assertIn("thema zwei", out)
        self.assertNotIn("not built yet", out)

    def test_stages(self):
        out = self.run_guard()
        self.assertIn("Setup stage: installation", out)
        self.write("personal/.installed", "unknown claude-code\n")
        self.assertIn("Setup stage: profile", self.run_guard())
        self.write("personal/profile.md", "name: X\nprofile: backend\n")
        self.assertIn("Setup stage: access or welcome", self.run_guard())
        self.write("personal/profile.md", "name: X\nprofile: backend\nready: 2026-10-01\n")
        self.assertNotIn("Setup stage", self.run_guard())


if __name__ == "__main__":
    unittest.main(verbosity=1)
