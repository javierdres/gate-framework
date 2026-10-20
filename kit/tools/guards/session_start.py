#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Session start guard. Prints the context the assistant needs before the person's first message.

It reports the setup stage, brings the SDLC up to date when that is safe, checks whether the
installation is older than the SDLC, identifies the person and hands over the profiles enabled
for them, runs the access check and lists what is still open in their log. It never fails the
session: whatever it cannot check, it says.

Identity, declared in sdlc.yml under `identity:`:
    method: platform      runs identity.command (for example `gh api user --jq .login`) and
                          looks the answer up in the profiles table of GOVERNANCE.md
    method: ssh-signing   the key in `git config user.signingkey` must appear in the SDLC's
                          allowed_signers file next to the person's identity
    method: declared      git's user.email, reported as not verified
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAL = os.path.join(ROOT, "personal")
OPEN_HEADINGS = re.compile(r"^##\s+(open|abierto|abiertos|pendiente|pendientes|en curso)\b", re.I | re.M)


def read(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def run(args, timeout=10, cwd=ROOT):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def config_value(key, section=None):
    """A flat read of sdlc.yml, enough for the few keys this guard needs."""
    text = read(os.path.join(ROOT, "sdlc.yml"))
    if section:
        m = re.search(r"^%s:\n((?:[ \t]+.*\n?|\s*\n)*)" % re.escape(section), text, re.M)
        text = m.group(1) if m else ""
    m = re.search(r"^\s*%s:\s*\"?([^\"\n#]*)" % re.escape(key), text, re.M)
    return m.group(1).strip() if m else ""


def update():
    code, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code:
        return "not a git repository yet"
    code, upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if code:
        return ("no upstream yet: once the SDLC exists on the code platform, push it once with "
                "`git push -u origin %s`" % branch)
    _, dirty = run(["git", "status", "--porcelain", "--untracked-files=no"])
    if dirty:
        return "not updated: there are local changes on %s" % branch
    code, _ = run(["git", "pull", "--ff-only", "--quiet"], timeout=20)
    return "up to date with %s" % upstream if code == 0 else "could not update from %s" % upstream


def installation():
    stamp = read(os.path.join(PERSONAL, ".installed")).strip()
    if not stamp:
        return None, "not installed: run tools/install.sh <assistant> from this repository"
    _, last = run(["git", "log", "-1", "--format=%H", "--", "skills", "adapters", "tools/install.sh",
                   "tools/guards"])
    commit = stamp.split()[0]
    if last and commit != last:
        _, newer = run(["git", "merge-base", "--is-ancestor", commit, last])
        return stamp, ("outdated: skills, adapters or guards changed since it was installed; run "
                       "tools/install.sh %s again" % (stamp.split()[1] if len(stamp.split()) > 1 else "<assistant>"))
    return stamp, "current"


def identity():
    method = config_value("method", "identity") or "declared"
    if method == "platform":
        command = config_value("command", "identity")
        if command:
            code, out = run(["sh", "-c", command], timeout=15)
            if code == 0 and out:
                return out.splitlines()[0].strip(), True, "platform account"
        return None, False, "the platform command did not answer; check the platform login"
    if method == "ssh-signing":
        _, key = run(["git", "config", "user.signingkey"])
        if key and os.path.exists(os.path.expanduser(key)):
            key = read(os.path.expanduser(key)).strip()
        key_body = key.split()[1] if len(key.split()) > 1 else key
        for line in read(os.path.join(ROOT, "allowed_signers")).splitlines():
            parts = line.split()
            if len(parts) >= 3 and not line.startswith("#") and key_body and key_body in parts:
                return parts[0], True, "ssh signing key listed in allowed_signers"
        return None, False, "the signing key is not in allowed_signers"
    _, email = run(["git", "config", "user.email"])
    return email or None, False, "declared in git, not verified"


def profiles_for(who):
    text = read(os.path.join(ROOT, "GOVERNANCE.md"))
    m = re.search(r"^##\s+Profiles enabled.*?\n(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    table = m.group(1) if m else ""
    fallback = None
    for line in table.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or set(cells[0]) <= {"-", " ", ":"}:
            continue
        if who and any(who.lower() == c.lower() for c in cells[1:-1]):
            return cells[-1], cells[0]
        if cells[1] in ("—", "-", "") and cells[0].lower().startswith(("everyone", "todas", "todos")):
            fallback = cells[-1]
    return fallback, None


def open_items():
    index = read(os.path.join(PERSONAL, "sessions", "README.md"))
    start = index.find("<!-- sdlc:open -->")
    if start < 0:
        m = OPEN_HEADINGS.search(index)
        start = m.end() if m else -1
    if start < 0:
        return []
    rest = index[start:].split("\n", 1)[1] if "\n" in index[start:] else ""
    section = re.split(r"^##\s", rest, maxsplit=1, flags=re.M)[0]
    return [l for l in section.splitlines() if l.strip().startswith("-")]


def main():
    lines = ["SDLC context"]
    lines.append("- GATE version: %s" % (config_value("version", "gate") or "not declared"))
    if not config_value("built"):
        lines.append("- The SDLC is not built yet: offer the establish skill before anything else.")
    lines.append("- SDLC repository: %s" % update())

    stamp, state = installation()
    lines.append("- Installation: %s" % state)
    profile = read(os.path.join(PERSONAL, "profile.md"))
    if stamp is None:
        stage = "installation"
    elif not profile.strip():
        stage = "profile"
    elif not re.search(r"^ready:\s*\S", profile, re.M):
        stage = "access or welcome"
    else:
        stage = None
    if stage:
        lines.append("- Setup stage: %s. Continue with the onboard skill from there." % stage)

    who, verified, how = identity()
    if who:
        lines.append("- Identity: %s (%s)" % (who, how))
    else:
        lines.append("- Identity: unknown (%s). Offer only what needs no profile." % how)
    enabled, row = profiles_for(who if verified else None)
    if enabled:
        lines.append("- Profiles enabled%s: %s" % ("" if verified else ", by default because the identity is not verified", enabled))
    if profile.strip():
        lines.append("- Profile: " + " · ".join(l.strip() for l in profile.splitlines() if l.strip()))

    checker = os.path.join(ROOT, "tools", "check-access.sh")
    m = re.search(r"^profile:\s*(.+)$", profile, re.M)
    if stamp and m and os.access(checker, os.X_OK):
        code, out = run([checker, "--summary", m.group(1).split(",")[0].strip()], timeout=25)
        lines.append("- Access: %s" % (out.splitlines()[-1] if out else "the checker did not answer"))

    items = open_items()
    if items:
        lines.append("- Log: %s" % os.path.join(PERSONAL, "sessions"))
        lines.append("- Open in the log:")
        lines.extend("  " + l.strip() for l in items)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("SDLC context\n- The session start guard could not finish (%s). Continue, and say so." % type(e).__name__)
        sys.exit(0)
