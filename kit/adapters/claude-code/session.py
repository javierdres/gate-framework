#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""What Claude Code picks up without reinstalling. Run by the installer and by the session start
guard at every session, so a change here reaches everyone with the next update.

    session.py <working folder> <system name> [python command]

Registers the usage status line in the working folder's .claude/settings.json. Its command goes
through the project folder, never an absolute path, so moving or renaming the working folder
does not break it. A status line the person set up themselves is left alone, and so is a
settings file that is not valid JSON. Claude Code reloads its settings when they change, so the
status line shows up in the same session. Prints one line when it changes something.
"""
import io
import json
import os
import shutil
import sys
import time


def register(data, name, python=None):
    """Sets the status line in the settings `data`. True when it changed them."""
    current = data.get("statusLine") or {}
    command = current.get("command", "") if isinstance(current, dict) else ""
    if current and "tools/guards/usage.py" not in command.replace("\\", "/"):
        return False
    # Keep the interpreter the installer chose (python, py -3 on Windows); python3 otherwise.
    python = python or (command.split('"', 1)[0].strip() if '"' in command else "") or "python3"
    wanted = {"type": "command", "refreshInterval": 60,
              "command": '%s "${CLAUDE_PROJECT_DIR:-.}/%s/tools/guards/usage.py" status' % (python, name)}
    if current == wanted:
        return False
    data["statusLine"] = wanted
    return True


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    work, name = argv[0], argv[1]
    path = os.path.join(work, ".claude", "settings.json")
    try:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f) if os.path.getsize(path) else {}
    except FileNotFoundError:
        data = {}
    except (OSError, ValueError):
        print("! .claude/settings.json in the working folder is not valid JSON; the status line was not registered")
        return 0
    if not isinstance(data, dict) or not register(data, name, argv[2] if len(argv) > 2 else None):
        return 0
    if os.path.exists(path):
        backups = os.path.join(work, name, "personal", "backups")
        os.makedirs(backups, exist_ok=True)
        shutil.copy2(path, os.path.join(backups, ".claude__settings.json.%s" % time.strftime("%Y%m%d%H%M%S")))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("OK  usage status line registered in the working folder")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception:
        sys.exit(0)
