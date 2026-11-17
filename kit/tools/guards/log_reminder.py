#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Per-message guard. One short reminder, so the log survives long sessions.

    log_reminder.py              prints the reminder
    log_reminder.py --passes     also reads the message event on standard input and, when the
                                 person's message is an OK, records a pass for permissions.py

The second form is for assistants whose hooks can only let through or block: there, the person
gives their OK by replying "ok" and the next action that would ask spends the pass (see
permissions.py). A pass is single-use and lasts 15 minutes. Only a short message that starts
with an OK counts, in English or Spanish; a bare "yes" or "sí" counts only on its own, so "si
quieres..." is not an OK. Never fails: whatever goes wrong, the reminder still prints.
"""
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "personal", "sessions")
GRANTS = (os.environ.get("GATE_GRANTS_DIR") or os.environ.get("SDLC_GRANTS_DIR")
          or os.path.join(ROOT, "personal", "grants"))
OK = re.compile(r"^(ok|okay|okey|go ahead|proceed|approved|do it|dale|adelante|procede|hazlo|confirmo|"
                r"autorizo|apruebo|de acuerdo)(\W|$)|^(yes|s[ií])\s*[,.!]*\s*$", re.I)


def is_ok(prompt):
    prompt = (prompt or "").strip()
    return 0 < len(prompt) <= 80 and bool(OK.match(prompt))


def record_pass(raw):
    event = json.loads(raw) if raw.strip() else {}
    event = event if isinstance(event, dict) else {}
    prompt = event.get("prompt") or event.get("user_prompt") or event.get("userPrompt") or \
        os.environ.get("USER_PROMPT", "")
    if not is_ok(str(prompt)):
        return
    session = str(event.get("session_id") or event.get("sessionId") or os.environ.get("GATE_SESSION")
                  or os.environ.get("SDLC_SESSION", ""))
    os.makedirs(GRANTS, exist_ok=True)
    path = os.path.join(GRANTS, re.sub(r"[^A-Za-z0-9_.-]", "_", session or "default") + ".pass")
    with open(path, "w", encoding="utf-8") as f:
        f.write("%d\n" % time.time())
    os.chmod(path, 0o600)


if "--passes" in sys.argv[1:]:
    try:
        record_pass(sys.stdin.read())
    except Exception:
        pass

print("Log: if this message leaves a decision, a closed step, a discard, something critical, a "
      "pending item or a pause, update the topic's summary in %s and its README.md index, "
      "following method/sessions.md, and say so in one line. A one-off question leaves no "
      "summary." % LOG)
sys.exit(0)
