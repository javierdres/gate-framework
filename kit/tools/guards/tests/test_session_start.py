#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The session start guard: configuration reading, the update, the installation fingerprint,
identity and the person's log.

    python3 tools/guards/tests/test_session_start.py

Each test builds a throwaway working folder with a system holding a copy of the guard, and a bare
repository as its origin when the update is under test. The SSH identity test needs ssh-keygen.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

GUARD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session_start.py")


def sh(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


class Base(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.root = os.path.join(self.work, "system-test")
        os.makedirs(os.path.join(self.root, "tools", "guards"))
        os.makedirs(os.path.join(self.root, "personal", "sessions"))
        shutil.copy(GUARD, os.path.join(self.root, "tools", "guards", "session_start.py"))
        sh(["git", "init", "-q", "-b", "main"], self.root)
        self.home = tempfile.mkdtemp()
        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith(("CLAUDE", "GEMINI", "KIRO", "CODEX", "GATE_", "SDLC_"))}
        self.env = dict(clean, HOME=self.home, GIT_CONFIG_GLOBAL=os.path.join(self.home, ".gitconfig"),
                        GIT_CONFIG_NOSYSTEM="1", SSH_AUTH_SOCK="", TERM_PROGRAM="")

    def tearDown(self):
        shutil.rmtree(self.work)
        shutil.rmtree(self.home)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def run_guard(self, *args, event=None, env=None, cwd=None):
        p = subprocess.run([sys.executable, os.path.join(self.root, "tools", "guards", "session_start.py")] + list(args),
                           cwd=cwd or self.root, env=dict(self.env, **(env or {})), capture_output=True, text=True,
                           input=json.dumps(event) if event else "")
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def read(self, path):
        with io.open(path, encoding="utf-8") as f:
            return f.read()

    def put(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(text)


class SessionStart(Base):
    def test_reads_escaped_and_commented_values(self):
        self.write("system.yml", 'gate:\n  version: "abc1234"   # pinned\nbuilt: ""\nidentity:\n'
                   '  method: platform\n  command: "printf \\"%s\\" \\"person-1 #x\\""   # a comment\n')
        self.write("GOVERNANCE.md", "## Profiles enabled\n\n| Person | Identity | Profiles |\n| --- | --- | --- |\n"
                   "| Someone | person-1 #x | backend |\n")
        out = self.run_guard()
        self.assertIn("GATE version: abc1234", out)
        self.assertIn("not built yet", out)
        self.assertIn("Identity: person-1 #x (platform account)", out)
        self.assertIn("Profiles enabled: backend", out)

    def test_spanish_headings_keys_and_quoted_commands(self):
        self.write("system.yml", "identity:\n  method: platform\n  command: 'printf ''%s'' persona-1'\n")
        self.write("GOVERNANCE.md", "## Perfiles habilitados\n\n| Persona | Identidad | Perfiles |\n| --- | --- | --- |\n"
                   "| Alguien | persona-1 | `backend`, `leadership` |\n")
        self.write("personal/profile.md", "nombre: Alguien\nperfil: backend\nlisto: 2026-11-10\n")
        out = self.run_guard()
        self.assertIn("Identity: persona-1 (platform account)", out)
        self.assertIn("Profiles enabled: backend, leadership", out)
        self.assertNotIn("Setup stage: profile", out)
        self.assertNotIn("Setup stage: access", out)

    def test_ssh_identity_needs_the_private_key(self):
        for who in ("a", "b"):
            sh(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", os.path.join(self.home, who), "-C", who], self.home)
        pub = {}
        for w in ("a", "b"):
            with io.open(os.path.join(self.home, w + ".pub")) as f:
                pub[w] = f.read().split()
        self.write("allowed_signers", "a@x namespaces=\"git\" %s %s\nb@x namespaces=\"git\" %s %s\n"
                   % (pub["a"][0], pub["a"][1], pub["b"][0], pub["b"][1]))
        self.write("system.yml", "identity:\n  method: ssh-signing\n")
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
        self.write("system.yml", "built: 2026-10-01\n")
        self.write("personal/sessions/README.md", "# Bitácora\n\n## Abierto\n\n- tema uno\n\n## Por tema\n- x\n")
        self.assertIn("tema uno", self.run_guard())
        self.write("personal/sessions/README.md", "# Log\n\n## Offen\n<!-- gate:open -->\n- thema zwei\n\n## Rest\n")
        out = self.run_guard()
        self.assertIn("thema zwei", out)
        self.assertNotIn("not built yet", out)
        self.write("personal/sessions/README.md", "# Log\n\n## Offen\n<!-- sdlc:open -->\n- thema drei\n\n## Rest\n")
        self.assertIn("thema drei", self.run_guard())

    def test_asks_to_rename_once_the_system_is_renamed(self):
        here = os.path.basename(self.root)
        self.write("system.yml", 'system:\n  name: "%s"\n  reach: "software"\n' % here)
        self.assertNotIn("Renamed", self.run_guard())
        self.write("system.yml", 'system:\n  name: "ai-office-acme"   # beyond software\n')
        out = self.run_guard()
        self.assertIn("from %s to ai-office-acme" % here, out)
        self.assertIn("tools/rename.sh", out)

    def test_stages(self):
        out = self.run_guard()
        self.assertIn("Setup stage: installation", out)
        self.write("personal/.installed", "unknown claude-code\n")
        self.assertIn("Setup stage: profile", self.run_guard())
        self.write("personal/profile.md", "name: X\nprofile: backend\n")
        self.assertIn("Setup stage: access or welcome", self.run_guard())
        self.write("personal/profile.md", "name: X\nprofile: backend\nready: 2026-10-01\n")
        self.assertNotIn("Setup stage", self.run_guard())


GIT_ID = ["-c", "user.name=t", "-c", "user.email=t@t"]


class Update(Base):
    """Bringing the system up to date: never hanging, never leaving the repository half done."""

    def setUp(self):
        super().setUp()
        self.remote = os.path.join(self.home, "origin.git")
        sh(["git", "init", "-q", "--bare", "-b", "main", self.remote], self.home)
        self.write("README.md", "one\n")
        self.write("CHANGELOG.md", "# Changes\n\n## 1.0.0 · 2026-01-01\n\n**What to do.** Nothing.\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "first")
        self.git("remote", "add", "origin", self.remote)
        self.git("push", "-q", "-u", "origin", "main")
        self.other = os.path.join(self.home, "other")
        sh(["git", "clone", "-q", self.remote, self.other], self.home)

    def git(self, *args, cwd=None):
        p = sh(["git"] + GIT_ID + list(args), cwd or self.root, self.env)
        return p.stdout.strip()

    def upstream(self, rel, text, title, version=None):
        """A colleague's change, pushed to origin."""
        with io.open(os.path.join(self.other, rel), "w", encoding="utf-8") as f:
            f.write(text)
        if version:
            path = os.path.join(self.other, "CHANGELOG.md")
            self.put(path, self.read(path).replace(
                "# Changes\n\n", "# Changes\n\n## %s · 2026-02-01\n\n**What to do.** Install again.\n\n" % version))
        self.git("add", "-A", cwd=self.other)
        self.git("commit", "-qm", title, cwd=self.other)
        self.git("push", "-q", "origin", "main", cwd=self.other)

    def test_fast_forward_reports_titles_and_versions(self):
        self.upstream("README.md", "two\n", "A clearer readme", version="1.1.0")
        out = self.run_guard()
        self.assertIn("updated with 1 new commit on origin/main (A clearer readme)", out)
        self.assertIn("new %s version 1.1.0" % os.path.basename(self.root), out)
        self.assertIn('"What to do"', out)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.git("rev-parse", "origin/main"))
        self.assertIn("up to date with origin/main", self.run_guard())

    def test_other_branch_moves_main_without_switching(self):
        self.git("checkout", "-q", "-b", "mine")
        self.write("mine.txt", "x\n")
        self.upstream("README.md", "two\n", "Upstream change")
        out = self.run_guard()
        self.assertIn("They are on mine: main moved forward", out)
        self.assertEqual(self.git("symbolic-ref", "--short", "HEAD"), "mine")
        self.assertEqual(self.git("rev-parse", "main"), self.git("rev-parse", "origin/main"))
        self.assertTrue(os.path.exists(os.path.join(self.root, "mine.txt")))

    def test_local_changes_elsewhere_are_kept_through_the_rebase(self):
        self.write("CHANGELOG.md", self.read(os.path.join(self.root, "CHANGELOG.md")) + "local note\n")
        self.upstream("README.md", "two\n", "Upstream change")
        out = self.run_guard()
        self.assertIn("updated with 1 new commit", out)
        self.assertIn("local note", self.read(os.path.join(self.root, "CHANGELOG.md")))
        self.assertEqual(self.read(os.path.join(self.root, "README.md")), "two\n")
        self.assertEqual(self.git("stash", "list"), "")

    def test_local_changes_in_the_same_files_are_left_alone(self):
        self.write("README.md", "mine\n")
        self.upstream("README.md", "two\n", "Upstream change")
        out = self.run_guard()
        self.assertIn("uncommitted changes in the same files", out)
        self.assertEqual(self.read(os.path.join(self.root, "README.md")), "mine\n")
        self.assertNotEqual(self.git("rev-parse", "HEAD"), self.git("rev-parse", "origin/main"))

    def test_own_commits_that_collide_are_left_alone(self):
        self.write("README.md", "mine\n")
        self.git("commit", "-qam", "mine")
        head = self.git("rev-parse", "HEAD")
        self.upstream("README.md", "two\n", "Upstream change")
        out = self.run_guard()
        self.assertIn("they collide with what is on the local main", out)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_an_operation_half_done_is_reported(self):
        self.upstream("README.md", "two\n", "Upstream change")
        self.put(os.path.join(self.root, ".git", "MERGE_HEAD"), self.git("rev-parse", "HEAD") + "\n")
        self.assertIn("half done", self.run_guard())

    def test_main_locked_in_another_worktree(self):
        self.git("checkout", "-q", "-b", "mine")
        self.git("worktree", "add", "-q", os.path.join(self.home, "wt"), "main")
        self.upstream("README.md", "two\n", "Upstream change")
        self.assertIn("could not move forward", self.run_guard())

    def test_an_unreachable_origin_never_hangs(self):
        self.git("remote", "set-url", "origin", "ssh://git@192.0.2.1:22/nowhere.git")
        out = self.run_guard()
        self.assertIn("could not reach origin/main", out)


class Installation(Base):
    """The fingerprint per assistant, the reinstall notice and the copies of skills."""

    def install(self, assistant="claude-code"):
        fp = self.run_guard("--fingerprint", assistant).strip()
        self.write("personal/.installed-%s" % assistant, fp + "\n")
        return fp

    def test_reinstall_needed_until_installed_again(self):
        self.write("adapters/claude-code/install.sh", "echo one\n")
        self.write("skills/a/SKILL.md", "a\n")
        self.install()
        out = self.run_guard(env={"CLAUDECODE": "1"})
        self.assertIn("Installation: current", out)
        notice = os.path.join(self.root, "personal", ".reinstall-needed")
        self.assertFalse(os.path.exists(notice))
        self.write("skills/b/SKILL.md", "b\n")
        out = self.run_guard(env={"CLAUDECODE": "1"})
        self.assertIn("reinstall needed", out)
        self.assertIn("bash system-test/tools/install.sh claude-code", out)
        self.assertTrue(os.path.exists(notice))
        self.install()
        self.assertIn("Installation: current", self.run_guard(env={"CLAUDECODE": "1"}))
        self.assertFalse(os.path.exists(notice))

    def test_each_assistant_has_its_own_fingerprint(self):
        self.write("adapters/claude-code/install.sh", "echo one\n")
        self.write("adapters/kiro/install.sh", "echo two\n")
        self.install("claude-code")
        self.assertIn("no installation for kiro yet", self.run_guard(env={"GATE_ASSISTANT": "kiro"}))
        self.install("kiro")
        self.write("adapters/kiro/hooks.json", "{}\n")
        self.assertIn("Installation: current", self.run_guard(env={"CLAUDECODE": "1"}))
        self.assertIn("reinstall needed", self.run_guard(env={"SDLC_ASSISTANT": "kiro"}))

    def test_copied_skills_are_refreshed(self):
        self.install()
        self.write("skills/a/SKILL.md", "new\n")
        copy = os.path.join(self.work, ".claude", "skills", "a")
        os.makedirs(copy)
        self.put(os.path.join(copy, "SKILL.md"), "old\n")
        self.put(os.path.join(copy, ".sdlc-copy"), "")
        mine = os.path.join(self.work, ".claude", "skills", "mine")
        os.makedirs(mine)
        self.put(os.path.join(mine, "SKILL.md"), "mine\n")
        self.run_guard()
        self.assertEqual(self.read(os.path.join(copy, "SKILL.md")), "new\n")
        self.assertTrue(os.path.exists(os.path.join(copy, ".gate-copy")))
        self.assertEqual(self.read(os.path.join(mine, "SKILL.md")), "mine\n")

    def test_opened_inside_the_system(self):
        self.install()
        self.assertIn("Opened inside the system", self.run_guard())
        self.assertNotIn("Opened inside", self.run_guard(env={"CLAUDE_PROJECT_DIR": self.work}))


class Identity(Base):
    """The chain of identity sources, bot accounts and the profiles a person may use."""

    TABLE = ("## Profiles enabled\n\n| Person | Identity | Profiles |\n| --- | --- | --- |\n"
             "| A | person-a | backend, sre |\n| Everyone else | — | product |\n")

    def test_tracker_command_when_the_platform_does_not_answer(self):
        self.write("system.yml", "identity:\n  method: platform\n  command: \"false\"\n"
                   "  tracker_command: \"echo person-a\"\n")
        self.write("GOVERNANCE.md", self.TABLE)
        out = self.run_guard()
        self.assertIn("Identity: person-a (tracker account)", out)
        self.assertIn("Profiles enabled: backend, sre", out)

    def test_bot_accounts_are_never_a_person(self):
        self.write("system.yml", "identity:\n  method: platform\n  command: \"echo release-bot\"\n")
        self.write("GOVERNANCE.md", self.TABLE.replace("person-a", "release-bot"))
        out = self.run_guard()
        self.assertIn("release-bot is a bot account", out)
        self.assertIn("through the tracker connector", out)
        self.assertIn("by default because the identity is not verified: product", out)

    def test_declared_profiles_never_widen_and_access_covers_the_union(self):
        self.write("system.yml", "identity:\n  method: platform\n  command: \"echo person-a\"\n")
        self.write("GOVERNANCE.md", self.TABLE)
        self.write("personal/.installed-claude-code", "x\n")
        self.write("personal/profile.md", "name: A\nprofile: backend, sre, leadership\nready: 2026-01-01\n")
        self.write("tools/check-access.sh", 'echo "checked $2"\n')
        out = self.run_guard()
        self.assertIn("Declared but not enabled: leadership", out)
        self.assertIn("Access: checked backend,sre", out)

    def test_session_notes(self):
        self.write("system.yml", "permissions:\n  autonomous_allowed: false\n")
        out = self.run_guard(event={"session_id": "s-1"})
        self.assertIn("Session s-1", out)
        self.assertIn("grant s-1 repo", out)
        self.assertNotIn("autonomous", out)
        self.assertNotIn("cannot show a confirmation", out)
        self.write("system.yml", "permissions:\n  autonomous_allowed: true\n")
        out = self.run_guard("--guards", "block", event={"session_id": "s-1"})
        self.assertIn("grant s-1 autonomous", out)
        self.assertIn("cannot show a confirmation", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
