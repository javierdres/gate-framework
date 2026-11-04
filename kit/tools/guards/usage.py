#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Usage guard. Nobody runs out of the assistant without being told first.

Subscription assistants meter use in windows (Claude Code: five hours and seven days) that
reset at a fixed time. This guard has two modes:

    usage.py status                 status line: reads the assistant's status JSON on standard
                                    input, prints the model, the context used and each window
                                    with its reset time, and records the windows in STATE
    usage.py check [--format F]     on every message: reads standard input (the session id) and
                                    STATE, and when a window will run out before it resets at
                                    the current pace, tells the assistant to warn the person,
                                    suggest a lighter model and run its subagents on one. When
                                    that window resets, it suggests going back to the most
                                    capable model. Each warning comes once per session.

Formats for check: `text` (plain context, the default) and `claude` (structured, with a line the
person sees even if the assistant does not mention it). Never fails: on any problem, status
prints what it can and check says nothing.

Only `windows()` knows the assistant's status format. An adapter for another assistant that
exposes its usage maps it there; one that does not, simply has no usage line.
"""
import json
import os
import re
import sys
import time

STATE = os.path.expanduser("~/.cache/gate-usage.json")
MARKS = os.path.expanduser("~/.cache/gate-usage")
FRESH = 1800            # older state says nothing about this session
EARLY = 0.1             # no projection before 10% of a window has passed
LIGHT = ("haiku", "sonnet")  # model names that already use less; adapt to the assistant
GREEN, YELLOW, RED, DIM, END = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def windows(status):
    """{key: (label, length in seconds, used %, reset epoch)} from Claude Code's status JSON."""
    known = {"five_hour": ("5 h", 5 * 3600), "seven_day": ("week", 7 * 86400)}
    found = {}
    for key, w in ((status.get("rate_limits") or {}).items()):
        if key in known and isinstance(w, dict) and w.get("used_percentage") is not None and w.get("resets_at"):
            found[key] = known[key] + (float(w["used_percentage"]), float(w["resets_at"]))
    return found


def runs_out(used, resets_at, length, now):
    """When the window runs out at the pace so far, if that is before it resets; else None."""
    if used >= 100:
        return now
    elapsed = length - (resets_at - now)
    if elapsed < length * EARLY or used <= 0:
        return None
    end = now + (100 - used) / (used / elapsed)
    return end if end < resets_at else None


def clock(epoch, now):
    t = time.localtime(epoch)
    same_day = time.strftime("%Y%m%d", t) == time.strftime("%Y%m%d", time.localtime(now))
    return time.strftime("%H:%M" if same_day else "%a %H:%M", t)


def left(seconds):
    s = max(0, int(seconds))
    d, h, m = s // 86400, s % 86400 // 3600, s % 3600 // 60
    return "%dd %dh" % (d, h) if d else "%dh %02dm" % (h, m) if h else "%dm" % m


def colour(pct):
    return GREEN if pct < 50 else YELLOW if pct < 80 else RED


def status_line(status, now):
    parts = []
    model = (status.get("model") or {}).get("display_name")
    if model:
        parts.append(model)
    ctx = (status.get("context_window") or {}).get("used_percentage")
    if ctx is not None:
        parts.append("context %s%d%%%s" % (colour(float(ctx)), round(float(ctx)), END))
    for key, (label, length, used, resets_at) in windows(status).items():
        bar = "▰" * max(0, min(10, round(used / 10))) + "▱" * (10 - max(0, min(10, round(used / 10))))
        text = "%s %s%s %d%%%s %sresets %s (in %s)%s" % (
            label, colour(used), bar, round(used), END, DIM, clock(resets_at, now), left(resets_at - now), END)
        end = runs_out(used, resets_at, length, now)
        if end is not None:
            text += " " + RED + ("used up" if used >= 100 else "runs out %s at this pace" % clock(end, now)) + END
        parts.append(text)
    return " · ".join(parts)


def record(status, now):
    found = windows(status)
    if not found:
        return
    model = status.get("model") or {}
    state = {"ts": now, "model": model.get("id"), "name": model.get("display_name"), "windows": {
        k: {"label": label, "pct": used, "resets_at": resets_at, "runs_out": runs_out(used, resets_at, length, now)}
        for k, (label, length, used, resets_at) in found.items()}}
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = "%s.%d.tmp" % (STATE, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f)
    os.replace(tmp, STATE)


def decide(state, mark):
    """(warning, new mark). warning is None, ("save", window) or ("restore", window)."""
    ws = state.get("windows") or {}
    at_risk = sorted((w["runs_out"], k) for k, w in ws.items() if w.get("runs_out"))
    key = at_risk[0][1] if at_risk else None
    if mark.get("level") != "save":
        if key:
            return ("save", key), {"level": "save", "window": key, "resets_at": ws[key]["resets_at"]}
        return None, mark
    # The assistant drops a window once it resets, or reports a later reset time.
    w = ws.get(mark.get("window"))
    reset = w is None or w["resets_at"] > mark.get("resets_at", 0) + 60
    if reset and not key:
        return ("restore", mark.get("window")), {"level": "normal"}
    if reset:
        return None, {"level": "save", "window": key, "resets_at": ws[key]["resets_at"]}
    return None, mark


def messages(warning, state, now):
    """(context for the assistant, line for the person), or (None, None)."""
    kind, key = warning
    name = state.get("name") or "the current model"
    light = any(m in (state.get("model") or "").lower() for m in LIGHT)
    if kind == "save":
        w = state["windows"][key]
        fact = "the %s usage window is at %d%% and at this pace runs out at %s, before it resets at %s" % (
            w["label"], round(w["pct"]), clock(w["runs_out"], now), clock(w["resets_at"], now))
        if light:
            ask = "The session already runs %s, a lighter model: suggest leaving what is not urgent until the reset." % name
            line = "Usage running fast: %s. You are on a lighter model; leave what is not urgent for later." % fact
        else:
            ask = ("The session runs %s. Suggest switching to a lighter model until the reset (in Claude Code, "
                   "/model)." % name)
            line = "Usage running fast: %s. Suggestion: a lighter model until the reset." % fact
        return ("Usage running fast: %s. Tell the person in one or two lines in this answer, before carrying on, "
                "so nobody runs out without knowing. %s Until the reset, run your subagents on a lighter model "
                "unless the task needs the most capable one. Do not repeat this warning." % (fact, ask)), line
    if not light:
        return None, None
    fact = "the %s usage window has reset" % state["windows"].get(key, {}).get("label", key) \
        if key in (state.get("windows") or {}) else "the usage window has reset"
    return ("Usage restored: %s and the session runs %s. In one line, suggest going back to the most capable "
            "model for complex work, and run subagents on whatever model the task needs." % (fact, name),
            "Usage restored: %s. You can go back to the most capable model." % fact)


def check(raw, fmt, now):
    session = (json.loads(raw or "{}") or {}).get("session_id") or ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", session):
        return
    state = json.load(open(STATE, encoding="utf-8"))
    if now - state.get("ts", 0) > FRESH:
        return
    path = os.path.join(MARKS, session + ".json")
    try:
        mark = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        mark = {}
    warning, new = decide(state, mark)
    if new != mark:
        os.makedirs(MARKS, exist_ok=True)
        json.dump(new, open(path, "w", encoding="utf-8"))
    if not warning:
        return
    context, line = messages(warning, state, now)
    if not context:
        return
    if fmt == "claude":
        print(json.dumps({"systemMessage": line, "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "additionalContext": context}}))
    else:
        print(context)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    fmt = sys.argv[sys.argv.index("--format") + 1] if "--format" in sys.argv[:-1] else "text"
    now = time.time()
    try:
        raw = sys.stdin.read()
        if mode == "check":
            check(raw, fmt, now)
            return
        status = json.loads(raw)
        status = status if isinstance(status, dict) else {}
        print(status_line(status, now))
        record(status, now)
    except Exception:
        if mode != "check":
            print("")


if __name__ == "__main__":
    main()
