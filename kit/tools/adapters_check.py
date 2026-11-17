#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Checks that every adapter still wires every guard, so none falls behind when the guards change.

    python3 tools/adapters_check.py [<adapter>...]

For each adapters/<assistant>/install.sh it installs a throwaway copy of the system in a temporary
working folder, with a temporary home, and reads what the assistant would load:

- every guard registered on its event (session start, each message, before each tool), with a
  command that points at a script that exists;
- the skills of skills/ where the assistant looks for them;
- a second install that changes nothing.

An adapter this check has no reader for is reported as "check by hand", not as a failure. Run it
before a change request that touches the guards, an adapter or the installer. Exits 1 with the
list of differences when an adapter fell behind. Nothing outside the temporary folder is touched.
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "gate-check"
# What every adapter registers: the guard and the moment it runs.
REQUIRED = (("session", "session_start.py"), ("message", "log_reminder.py"), ("tool", "permissions.py"))
# Guards an adapter registers only where its assistant supports them.
OPTIONAL = {"claude-code": (("message", "usage.py"),)}
COPY = ("AGENTS.md", "system.yml", "sdlc.yml", "skills", "tools", "adapters")
SCRIPT = re.compile(r"tools/guards/([\w.-]+\.py)")


def claude_code(work):
    """{(moment, script)} and the skills folder, from .claude/settings.json."""
    events = {"SessionStart": "session", "UserPromptSubmit": "message", "PreToolUse": "tool"}
    with io.open(os.path.join(work, ".claude", "settings.json"), encoding="utf-8") as f:
        hooks = json.load(f).get("hooks", {})
    found = set()
    for event, entries in hooks.items():
        for e in entries:
            for h in e.get("hooks", []):
                for script in SCRIPT.findall(h.get("command", "")):
                    found.add((events.get(event, event), script, h.get("command", "")))
    return found, os.path.join(work, ".claude", "skills")


def kiro(work):
    """{(moment, script)} and the skills folder, from .kiro/hooks/*.json."""
    events = {"SessionStart": "session", "UserPromptSubmit": "message", "PreToolUse": "tool"}
    found = set()
    folder = os.path.join(work, ".kiro", "hooks")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        with io.open(os.path.join(folder, name), encoding="utf-8") as f:
            data = json.load(f)
        for h in data.get("hooks", []):
            command = (h.get("action") or {}).get("command", "")
            for script in SCRIPT.findall(command):
                found.add((events.get(h.get("trigger"), h.get("trigger")), script, command))
    return found, os.path.join(work, ".kiro", "skills")


READERS = {"claude-code": claude_code, "kiro": kiro}


def snapshot(work):
    """A digest of every file the installer may write, backups and logs aside."""
    h = hashlib.sha1()
    for base, dirs, files in os.walk(work):
        dirs[:] = sorted(d for d in dirs if d not in ("backups", ".git", "__pycache__"))
        for f in sorted(files):
            p = os.path.join(base, f)
            h.update(os.path.relpath(p, work).encode("utf-8"))
            if os.path.islink(p):
                h.update(os.readlink(p).encode("utf-8"))
            elif os.path.isfile(p):
                with io.open(p, "rb") as data:
                    h.update(data.read())
    return h.hexdigest()


def install(system, adapter, home):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "GEMINI", "KIRO", "CODEX", "GATE_", "SDLC_"))}
    env.update(HOME=home, GIT_CONFIG_GLOBAL=os.path.join(home, ".gitconfig"), GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(["bash", os.path.join(system, "tools", "install.sh"), adapter],
                          capture_output=True, text=True, env=env, timeout=120)


def check(adapter):
    """(problems, notes) for one adapter."""
    tmp = tempfile.mkdtemp()
    try:
        work, home = os.path.join(tmp, "work"), os.path.join(tmp, "home")
        system = os.path.join(work, NAME)
        os.makedirs(home)
        for item in COPY:
            src = os.path.join(ROOT, item)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(system, item), symlinks=True,
                                ignore=shutil.ignore_patterns("__pycache__", "node_modules", "personal"))
            elif os.path.isfile(src):
                os.makedirs(system, exist_ok=True)
                shutil.copy2(src, os.path.join(system, item))
        p = install(system, adapter, home)
        if p.returncode != 0:
            return ["the installer failed: %s" % (p.stdout + p.stderr).strip().splitlines()[-1:]], []
        if adapter not in READERS:
            return [], ["no reader for %s yet: check its registrations by hand" % adapter]
        try:
            found, skills = READERS[adapter](work)
        except (OSError, ValueError) as e:
            return ["could not read what it installed (%s)" % e], []
        problems = []
        moments = {(m, s) for m, s, _ in found}
        for moment, script in REQUIRED + OPTIONAL.get(adapter, ()):
            if (moment, script) not in moments:
                problems.append("does not run %s on %s" % (script, moment))
        for _, script, command in sorted(found):
            if not os.path.isfile(os.path.join(system, "tools", "guards", script)):
                problems.append("runs %s, which tools/guards/ does not have" % script)
            if "%s/tools/guards/" % NAME not in command:
                problems.append("runs %s through a path that does not go through the working folder: %s"
                                % (script, command))
        for skill in sorted(os.listdir(os.path.join(system, "skills"))):
            if os.path.isfile(os.path.join(system, "skills", skill, "SKILL.md")) and \
                    not os.path.isfile(os.path.join(skills, skill, "SKILL.md")):
                problems.append("does not make the skill %s available" % skill)
        before = snapshot(work)
        p = install(system, adapter, home)
        if p.returncode != 0 or snapshot(work) != before:
            problems.append("a second install changes something; it must change nothing")
        return problems, []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    folder = os.path.join(ROOT, "adapters")
    adapters = argv or sorted(d for d in os.listdir(folder) if os.path.isfile(os.path.join(folder, d, "install.sh")))
    failed = False
    for adapter in adapters:
        problems, notes = check(adapter)
        for n in notes:
            print("–  %s: %s" % (adapter, n))
        for p in problems:
            print("x  %s: %s" % (adapter, p))
        if not problems and not notes:
            print("OK %s: every guard on its event, every skill, and a second install changes nothing" % adapter)
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
