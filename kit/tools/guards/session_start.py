#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Session start guard. Prints the context the assistant needs before the person's first message.

Brings the SDLC's main branch up to date when it can do so safely, reports the setup stage,
hands over the GATE version, the profile and what is still open in the person's log. It never
fails the session: whatever it cannot check, it says.
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAL = os.path.join(ROOT, "personal")


def read(path):
    try:
        return io.open(path, encoding="utf-8").read()
    except Exception:
        return ""


def pull():
    try:
        branch = subprocess.run(["git", "-C", ROOT, "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, timeout=5).stdout.strip()
        dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, timeout=5).stdout.strip()
        if branch == "main" and not dirty:
            r = subprocess.run(["git", "-C", ROOT, "pull", "--ff-only", "--quiet"],
                               capture_output=True, text=True, timeout=20)
            return "up to date with origin/main" if r.returncode == 0 else "could not pull main"
        return "not pulled (branch %s%s)" % (branch, ", local changes" if dirty else "")
    except Exception:
        return "not pulled (git unavailable)"


def main():
    lines = ["SDLC context"]
    version = re.search(r"^\s*version:\s*\"?([^\"\n]*)", read(os.path.join(ROOT, "sdlc.yml")), re.M)
    lines.append("- GATE version: %s" % ((version.group(1) if version else "") or "not declared"))
    lines.append("- SDLC repository: %s" % pull())

    profile = read(os.path.join(PERSONAL, "profile.md"))
    if not profile.strip():
        lines.append("- Setup stage: profile. Offer /onboard before anything else.")
    elif not re.search(r"^ready:\s*\S", profile, re.M):
        lines.append("- Setup stage: access or welcome. Offer to finish /onboard.")
    else:
        lines.append("- Profile: " + " · ".join(l.strip() for l in profile.splitlines() if l.strip()))

    index = read(os.path.join(PERSONAL, "sessions", "README.md"))
    m = re.search(r"^## Open\s*\n(.*?)(?=^## |\Z)", index, re.M | re.S)
    if m and m.group(1).strip():
        lines.append("- Log: %s" % os.path.join(PERSONAL, "sessions"))
        lines.append("- Open in the log:")
        lines.extend("  " + l for l in m.group(1).strip().splitlines() if l.strip().startswith("-"))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
