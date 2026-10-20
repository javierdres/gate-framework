#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Permissions guard for an SDLC built on GATE. Neutral: any assistant can call it.

    permissions.py check [--format claude|json|exit]   read the action on stdin, decide
    permissions.py grant <session> repo <path>          authorise a repository for a session
    permissions.py grant <session> tracker <KEY>        authorise a tracker project
    permissions.py show <session>
    permissions.py revoke <session> [repo <path> | tracker <KEY>]

Three levels. Local work is not this guard's business and passes untouched. Outward writes ask
until their scope is authorised for the session. A short list always asks, whatever was
authorised: merges, forced or deleting pushes, deletions, production tools, credentials, and
granting itself. If anything fails while deciding, the answer is ask.

Output formats:
    claude  the PreToolUse JSON Claude Code understands
    json    {"decision": "allow|ask|deny", "reason": "..."} for adapters to map
    exit    exit 0 to let through; exit 2 with the reason on stderr when it asks, for
            assistants that cannot ask and only understand blocking
"""
import io
import json
import os
import re
import shlex
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRANTS = os.path.join(ROOT, "personal", "grants")
TTL = 3 * 24 * 3600

NEVER = [
    (r"\bgit\s+(-C\s+\S+\s+)?push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s--delete\b|\s-d\b|\s:\S)", "forced or deleting push"),
    (r"\b(gh\s+pr|glab\s+mr)\s+merge\b", "merge"),
    (r"\b(gh|glab)\s+api\b.*\bmerge\b", "merge"),
    (r"(-X|--method|--request)\s*=?\s*DELETE\b", "deletion"),
    (r"\b(gh\s+repo|glab\s+repo)\s+delete\b", "deletion"),
    (r"\b(kubectl|helm|terraform|pulumi)\b", "infrastructure or production tool"),
    (r"\b(token|tokens|personal_access_tokens)\b.*\b(create|new)\b", "credentials"),
    (r"\bpermissions\.py\s+grant\b", "an authorisation must pass the person's own confirmation"),
]
WRITE_METHOD = r"(-X|--method|--request)\s*=?\s*(POST|PUT|PATCH)\b"
TRACKER_TOOL = re.compile(r"(jira|issue|ticket|tracker|linear|youtrack)", re.I)
TRACKER_WRITE = re.compile(r"(create|edit|update|comment|transition|move|assign|add|delete|remove)", re.I)


def grants_path(session):
    return os.path.join(GRANTS, re.sub(r"[^A-Za-z0-9_.-]", "_", session) + ".json")


def purge():
    if not os.path.isdir(GRANTS):
        return
    now = time.time()
    for f in os.listdir(GRANTS):
        p = os.path.join(GRANTS, f)
        if now - os.path.getmtime(p) > TTL:
            os.remove(p)


def load(session):
    p = grants_path(session)
    if not session or not os.path.exists(p):
        return {"repo": [], "tracker": []}
    return json.load(io.open(p, encoding="utf-8"))


def save(session, data):
    os.makedirs(GRANTS, exist_ok=True)
    io.open(grants_path(session), "w", encoding="utf-8").write(json.dumps(data, indent=2))
    os.chmod(grants_path(session), 0o600)


def toplevel(path):
    try:
        out = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        return os.path.realpath(out.stdout.strip()) if out.returncode == 0 else None
    except Exception:
        return None


def segments(command):
    return [s.strip() for s in re.split(r"&&|\|\||;|\|", command) if s.strip()]


def classify_shell(command, cwd):
    """Return (level, reason, scope) for the riskiest segment of a shell command."""
    worst = ("local", "", None)
    for seg in segments(command):
        for pattern, why in NEVER:
            if re.search(pattern, seg):
                return ("never", why, None)
        where = cwd
        m = re.search(r"\bgit\s+-C\s+(\S+)", seg)
        if m:
            where = os.path.join(cwd, os.path.expanduser(m.group(1)))
        if re.search(r"\bgit\s+(-C\s+\S+\s+)?push\b", seg) or re.search(r"\b(gh\s+pr|glab\s+mr)\s+create\b", seg):
            worst = ("watched", "outward write to a repository", ("repo", toplevel(where)))
        elif re.search(r"\b(gh|glab)\s+api\b", seg) and re.search(WRITE_METHOD, seg):
            worst = ("watched", "write through the code platform API", ("repo", toplevel(where)))
        elif re.search(r"\bcurl\b", seg) and re.search(WRITE_METHOD, seg):
            if worst[0] == "local":
                worst = ("watched", "write to an external API", None)
    return worst


def classify_tool(name, args):
    if TRACKER_TOOL.search(name) and TRACKER_WRITE.search(name):
        if re.search(r"(delete|remove)", name, re.I):
            return ("never", "deletion in the tracker", None)
        key = str(args.get("projectKey") or args.get("project") or args.get("issueKey") or
                  args.get("issueIdOrKey") or "")
        key = key.split("-")[0].upper() or None
        return ("watched", "write to the tracker", ("tracker", key))
    return ("local", "", None)


def decide(event):
    tool = event.get("tool_name") or event.get("toolName") or event.get("tool") or ""
    args = event.get("tool_input") or event.get("toolInput") or event.get("args") or {}
    if isinstance(args, str):
        args = {"command": args}
    session = event.get("session_id") or event.get("sessionId") or os.environ.get("SDLC_SESSION", "")
    cwd = event.get("cwd") or os.getcwd()

    command = args.get("command") if isinstance(args, dict) else None
    if command:
        level, reason, scope = classify_shell(command, cwd)
    else:
        level, reason, scope = classify_tool(str(tool), args if isinstance(args, dict) else {})

    if level == "local":
        return None, ""
    if level == "never":
        return "ask", "Always asks: %s." % reason
    grants = load(session)
    if scope and scope[1]:
        kind, value = scope
        if value in grants.get(kind, []):
            return "allow", "%s authorised for this session." % value
        hint = "permissions.py grant %s %s %s" % (session or "<session>", kind, value)
        return "ask", "%s. To authorise it for the session: %s" % (reason.capitalize(), hint)
    return "ask", "%s, outside any authorised scope." % reason.capitalize()


def emit(decision, reason, fmt):
    if decision is None:
        return 0
    if fmt == "claude":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason}}))
        return 0
    if fmt == "json":
        print(json.dumps({"decision": decision, "reason": reason}))
        return 0
    if decision == "allow":
        return 0
    sys.stderr.write("Needs the person's OK. %s\n" % reason)
    return 2


def main(argv):
    purge()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    action = argv[0]
    if action == "check":
        fmt = "exit"
        if "--format" in argv:
            fmt = argv[argv.index("--format") + 1]
        try:
            event = json.loads(sys.stdin.read() or "{}")
            decision, reason = decide(event)
        except Exception as e:
            decision, reason = "ask", "The guard could not decide (%s), so it asks." % e
        return emit(decision, reason, fmt)

    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    session = argv[1]
    data = load(session)
    if action == "show":
        print(json.dumps(data, indent=2))
        return 0
    if action == "grant" and len(argv) == 4 and argv[2] in ("repo", "tracker"):
        kind, value = argv[2], argv[3]
        value = toplevel(os.path.expanduser(value)) if kind == "repo" else value.upper()
        if not value:
            print("x not a repository: %s" % argv[3])
            return 1
        if value not in data[kind]:
            data[kind].append(value)
        save(session, data)
        print("OK  %s %s authorised for session %s" % (kind, value, session))
        return 0
    if action == "revoke":
        if len(argv) == 4 and argv[2] in ("repo", "tracker"):
            kind = argv[2]
            value = toplevel(os.path.expanduser(argv[3])) if kind == "repo" else argv[3].upper()
            data[kind] = [v for v in data[kind] if v != value]
            save(session, data)
        elif os.path.exists(grants_path(session)):
            os.remove(grants_path(session))
        print("OK  revoked")
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
