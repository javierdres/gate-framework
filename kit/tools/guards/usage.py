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

Under the usage, the status line shows the SDLC's notices, only when there is one: the
installation needs running again, what the person authorised for this session, autonomous mode.
An organisation adds its own (change requests waiting for the person's review, a token about to
expire) with tools/notices.py: any script that prints one line. It may call the network, so it
never runs inside the status line: it runs in the background, at most every NOTICES_EVERY
seconds, and the status line reads the line it left in a cache.

    usage.py notices-refresh        what the background run does; not for people
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

STATE = os.path.expanduser("~/.cache/gate-usage.json")
MARKS = os.path.expanduser("~/.cache/gate-usage")
FRESH = 1800            # older state says nothing about this session
EARLY = 0.1             # no projection before 10% of a window has passed
LIGHT = ("haiku", "sonnet")  # model names that already use less; adapt to the assistant
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTICES = os.path.join(ROOT, "tools", "notices.py")
NOTICES_CACHE = os.path.expanduser("~/.cache/gate-notices-%s.json" % hashlib.sha1(ROOT.encode("utf-8")).hexdigest()[:12])
NOTICES_EVERY = 600     # seconds between background runs of tools/notices.py
NOTICES_LOCK = 120      # a run younger than this is still under way
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


def granted(session):
    """What the person authorised for this session, read through the permissions guard."""
    if not session:
        return None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import permissions
    try:
        with open(permissions.grants_path(session), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if data.get("autonomous") is True and permissions.autonomous_allowed():
        return YELLOW + "autonomous mode" + END
    names = [os.path.basename(str(r).rstrip("/\\")) for r in data.get("repo") or []] + list(data.get("tracker") or [])
    names = [n for n in names if n]
    return "authorised: %s" % ", ".join(names) if names else None


def refresh_notices(now):
    """Starts tools/notices.py in the background when the cache is stale and no run is under way.
    Whatever it brings shows from the next refresh on."""
    try:
        with open(NOTICES_CACHE, encoding="utf-8") as f:
            ts = json.load(f).get("ts", 0)
    except (OSError, ValueError):
        ts = 0
    try:
        running = now - os.path.getmtime(NOTICES_CACHE + ".lock") < NOTICES_LOCK
    except OSError:
        running = False
    if now - ts < NOTICES_EVERY or running:
        return
    try:
        os.makedirs(os.path.dirname(NOTICES_CACHE), exist_ok=True)
        open(NOTICES_CACHE + ".lock", "w").close()
        detach = {"creationflags": 0x00000008} if os.name == "nt" else {"start_new_session": True}
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "notices-refresh"], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **detach)
    except Exception:
        pass


def notices_refresh():
    line = ""
    try:
        p = subprocess.run([sys.executable, NOTICES], capture_output=True, text=True, timeout=60,
                           stdin=subprocess.DEVNULL, cwd=ROOT)
        line = " · ".join(l.strip() for l in p.stdout.splitlines() if l.strip()) if p.returncode == 0 else ""
    except Exception:
        pass
    tmp = "%s.%d.tmp" % (NOTICES_CACHE, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"ts": time.time(), "line": line}, f)
    os.replace(tmp, NOTICES_CACHE)
    try:
        os.remove(NOTICES_CACHE + ".lock")
    except OSError:
        pass


def notices(status, now):
    """The SDLC's notices line, or an empty string when there is nothing to say."""
    parts = []
    if os.path.exists(os.path.join(ROOT, "personal", ".reinstall-needed")):
        parts.append(YELLOW + "SDLC: reinstall needed" + END)
    try:
        parts.append(granted(str(status.get("session_id") or "")))
    except Exception:
        pass
    if os.path.isfile(NOTICES):
        refresh_notices(now)
        try:
            with open(NOTICES_CACHE, encoding="utf-8") as f:
                parts.append(json.load(f).get("line"))
        except (OSError, ValueError):
            pass
    return " · ".join(p for p in parts if p)


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
        if mode == "notices-refresh":
            notices_refresh()
            return
        status = json.loads(raw)
        status = status if isinstance(status, dict) else {}
        print("\n".join(l for l in (status_line(status, now), notices(status, now)) if l))
        record(status, now)
    except Exception:
        if mode != "check":
            print("")


if __name__ == "__main__":
    main()
