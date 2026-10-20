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
authorised: pushes to the default branch or to a remote the repository does not declare;
forced, mirrored, pruning, deleting and all-branch pushes; merges; deletions; infrastructure
tools; credentials; and anything that touches the authorisations themselves.

The guard is conservative by design. A session authorisation only covers a simple command the
guard fully understands: a push or a change request that is the whole of its segment. A write
hidden inside `sh -c`, `eval`, a subshell, a command substitution or any other construct the
guard does not parse always asks. Every segment of a chained command is judged, the working
directory is followed across `cd`, and whatever goes wrong while deciding, the answer is ask:
this guard never fails open.

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
GRANTS = os.environ.get("SDLC_GRANTS_DIR") or os.path.join(ROOT, "personal", "grants")
TTL = 3 * 24 * 3600
FORMATS = ("claude", "json", "exit")

# Judged on the command with its quotes and backslashes removed, so quoting cannot hide them.
NEVER = [
    (r"\b(gh\s+pr|glab\s+mr)\s+merge\b", "merge"),
    (r"\b(gh|glab|curl)\b.*\bmerge\b", "merge"),
    (r"(^|\s)(-X|--method|--request)\s*=?\s*delete\b", "deletion"),
    (r"\b(gh|glab)\s+(repo|release|issue|mr|pr|api)\b.*\bdelete\b", "deletion"),
    (r"\b(kubectl|helm|terraform|pulumi|cdk\s+deploy|serverless\s+deploy|sam\s+deploy)\b",
     "infrastructure or production tool"),
    (r"\b(token|tokens|personal_access_tokens|deploy[-_]keys?)\b.*\b(create|new|add)\b", "credentials"),
    (r"\b(gh|glab)\s+auth\s+token\b", "credentials"),
    (r"permissions\.py\b.*\b(grant|revoke)\b", "an authorisation must pass the person's own confirmation"),
    (r"personal/grants\b", "the authorisations can only change through the person's own confirmation"),
]
# Constructs the guard does not parse: a write inside them always asks.
OPAQUE = re.compile(r"(\$\(|`|<\(|>\(|\beval\b|\b(sh|bash|zsh|dash|ksh|fish|pwsh|powershell)\s+(-\w*c|-c)\b|"
                    r"\bxargs\b|\bexec\b|\bsource\b|^\s*\.\s|\bpython\d?\s+-c\b|\bperl\s+-e\b|\bnode\s+-e\b|"
                    r"\bruby\s+-e\b|\benv\s+\S+=)", re.I)
WRITE_HINT = re.compile(r"\bgit\b.*(?<!stash )\bpush\b|"
                        r"\b(gh|glab)\b.*(\b(create|merge|delete|close|edit|comment|review|transfer|archive)\b|"
                        r"(-X|--method|--request)\s*=?\s*(post|put|patch|delete)\b|\s(-f|-F|--field|--raw-field|--input)(\s|=))|"
                        r"\bcurl\b.*((-X|--request)\s*=?\s*(post|put|patch|delete)\b|\s(-d|--data\S*|-F|--form)(\s|=))", re.I)
WRITE_METHOD = re.compile(r"(^|\s)(-X|--method|--request)\s*=?\s*(post|put|patch)\b", re.I)
IMPLICIT_POST = re.compile(r"(^|\s)(-f|-F|--field|--raw-field|--input)(\s|=)")
CURL_DATA = re.compile(r"(^|\s)(-d|--data\S*|-F|--form)(\s|=)")

READ_VERBS = re.compile(r"(get|list|search|read|fetch|query|view|show|describe|lookup|find|info|whoami|"
                        r"resources|atlassianuserinfo|accessible)", re.I)
WRITE_VERBS = re.compile(r"(create|edit|update|comment|transition|move|assign|add|link|push|open|close|"
                         r"approve|label|write|execute|post|put|patch|set|upload|publish|send|merge|"
                         r"delete|remove|destroy|archive)", re.I)
DESTRUCTIVE = re.compile(r"(merge|delete|remove|destroy|archive|executedestructive)", re.I)
TRACKER_TOOL = re.compile(r"(jira|issue|ticket|tracker|linear|youtrack)", re.I)
CODE_TOOL = re.compile(r"(github|gitlab|bitbucket|pull_?request|merge_?request|\bpr\b|\bmr\b|repo|branch|commit)", re.I)
FILE_TOOLS = ("write", "edit", "multiedit", "notebookedit", "str_replace_editor", "create_file", "replace",
              "write_file")
PUSH_DANGER = {"--force": "forced push", "-f": "forced push", "--force-with-lease": "forced push",
               "--force-if-includes": "forced push", "--mirror": "mirrored push",
               "--prune": "pruning push", "--delete": "deleting push", "-d": "deleting push",
               "--all": "push of every branch"}


# ───────────────────────────── grants ─────────────────────────────

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
    with io.open(p, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("repo", [])
    data.setdefault("tracker", [])
    return data


def save(session, data):
    os.makedirs(GRANTS, exist_ok=True)
    path = grants_path(session)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2))
    os.chmod(path, 0o600)


# ───────────────────────────── git helpers ─────────────────────────────

def git(args, cwd):
    try:
        out = subprocess.run(["git", "-C", cwd] + args, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def toplevel(path):
    top = git(["rev-parse", "--show-toplevel"], path)
    return os.path.realpath(top) if top else None


def default_branches(repo):
    """The branches a push must never reach without the person's OK."""
    names = {"main", "master"}
    head = git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], repo or ".")
    if head and "/" in head:
        names.add(head.split("/", 1)[1])
    return names


def current_branch(repo):
    return git(["rev-parse", "--abbrev-ref", "HEAD"], repo or ".")


def remotes(repo):
    names = (git(["remote"], repo or ".") or "").split()
    urls = set()
    for name in names:
        url = git(["remote", "get-url", "--push", name], repo or ".")
        if url:
            urls.add(url)
    return set(names), urls


# ───────────────────────────── classification ─────────────────────────────

def segments(command):
    """Split a shell command on the operators that chain separate commands."""
    parts = re.split(r"&&|\|\||;|\||\n|&(?!&)", command)
    return [p.strip() for p in parts if p.strip()]


def words(segment):
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def program(token):
    return os.path.basename(token).lower().replace(".exe", "")


def classify_push(tokens, where):
    """tokens start right after `push`."""
    repo = toplevel(where)
    protected = default_branches(repo)
    for flag in [t for t in tokens if t.startswith("-")]:
        name = flag.split("=", 1)[0]
        if name in PUSH_DANGER:
            return ("never", PUSH_DANGER[name], None)
        if re.fullmatch(r"-[a-zA-Z]{2,}", flag) and ("f" in flag or "d" in flag):
            return ("never", "forced or deleting push", None)
    positional = [t for t in tokens if not t.startswith("-")]
    if positional:
        names, urls = remotes(repo)
        if positional[0] not in names and positional[0] not in urls:
            return ("never", "push to a remote this repository does not declare", None)
    refspecs = positional[1:]
    for spec in refspecs:
        if spec.startswith("+"):
            return ("never", "forced push", None)
        if spec.startswith(":"):
            return ("never", "deleting push", None)
        target = spec.split(":", 1)[1] if ":" in spec else spec
        target = re.sub(r"^refs/heads/", "", target)
        if target in protected or (target == "HEAD" and current_branch(repo) in protected):
            return ("never", "push to the default branch", None)
    if not refspecs and current_branch(repo) in protected:
        return ("never", "push to the default branch", None)
    return ("watched", "outward write to a repository", ("repo", repo))


def classify_segment(segment, where):
    """Return ((level, reason, scope), new working directory)."""
    tokens = words(segment)
    if not tokens:
        return ("local", "", None), where
    first = program(tokens[0])
    if first in ("cd", "pushd") and len(tokens) <= 2:
        target = os.path.expanduser(tokens[1]) if len(tokens) == 2 else os.path.expanduser("~")
        return ("local", "", None), os.path.normpath(os.path.join(where, target))
    if first == "git":
        rest = tokens[1:]
        while rest and rest[0].startswith("-"):
            if rest[0] == "-C" and len(rest) > 1:
                where = os.path.normpath(os.path.join(where, os.path.expanduser(rest[1])))
                rest = rest[2:]
            elif rest[0] == "-c" and len(rest) > 1:
                rest = rest[2:]
            else:
                rest = rest[1:]
        if rest and rest[0] == "push":
            return classify_push(rest[1:], where), where
    if first in ("gh", "glab"):
        if re.search(r"\b(pr|mr)\s+create\b", segment):
            return ("watched", "opening a change request", ("repo", toplevel(where))), where
        if len(tokens) > 1 and tokens[1] == "api" and (WRITE_METHOD.search(segment) or IMPLICIT_POST.search(segment)):
            return ("watched", "write through the code platform API", ("repo", toplevel(where))), where
        if len(tokens) > 1 and tokens[1] not in ("api", "auth", "status", "browse", "help", "version") and \
                re.search(r"\b(create|edit|close|reopen|comment|review|ready|merge|delete|transfer|archive|lock)\b", segment):
            return ("watched", "write to the code platform", ("repo", toplevel(where))), where
    if first == "curl" and (WRITE_METHOD.search(segment) or CURL_DATA.search(segment)):
        return ("watched", "write to an external API", None), where
    return ("local", "", None), where


def classify_shell(command, cwd):
    flat = re.sub(r"['\"\\]", "", command)
    for pattern, why in NEVER:
        if re.search(pattern, flat, re.I):
            return [("never", why, None)]
    if OPAQUE.search(command) and WRITE_HINT.search(flat):
        return [("never", "a write inside a construct the guard does not parse", None)]
    verdicts, where = [], cwd
    for seg in segments(command):
        verdict, where = classify_segment(seg, where)
        if verdict[0] == "local" and re.search(r"\bgit\b.*(?<!stash )\bpush\b", re.sub(r"['\"\\]", "", seg)):
            verdict = ("never", "a push the guard could not read with certainty", None)
        verdicts.append(verdict)
    return verdicts


def classify_tool(name, args):
    lname = name.lower()
    base = lname.rsplit("__", 1)[-1]
    if base in FILE_TOOLS or lname in FILE_TOOLS:
        path = str(args.get("file_path") or args.get("path") or args.get("notebook_path") or "")
        if "personal/grants" in path.replace("\\", "/") or os.path.realpath(path).startswith(os.path.realpath(GRANTS)):
            return ("never", "the authorisations can only change through the person's own confirmation", None)
        return ("local", "", None)
    if not lname.startswith("mcp__"):
        return ("local", "", None)
    if DESTRUCTIVE.search(base):
        return ("never", "a merge or deletion through a connector", None)
    if READ_VERBS.search(base) and not WRITE_VERBS.search(re.sub(r"read|execute", "", base)):
        return ("local", "", None)
    if not WRITE_VERBS.search(base):
        return ("local", "", None)
    if TRACKER_TOOL.search(lname) and not CODE_TOOL.search(lname):
        key = str(args.get("projectKey") or args.get("project") or args.get("issueKey") or
                  args.get("issueIdOrKey") or "")
        key = key.split("-")[0].upper() or None
        return ("watched", "write to the tracker", ("tracker", key))
    return ("watched", "write through a connector", None)


def decide(event):
    if not isinstance(event, dict) or not event:
        return "ask", "The guard received no action to judge, so it asks."
    tool = event.get("tool_name") or event.get("toolName") or event.get("tool") or ""
    args = event.get("tool_input") or event.get("toolInput") or event.get("args") or {}
    if isinstance(args, str):
        args = {"command": args}
    if not isinstance(args, dict):
        return "ask", "The guard could not read the action's arguments, so it asks."
    session = str(event.get("session_id") or event.get("sessionId") or os.environ.get("SDLC_SESSION", ""))
    cwd = event.get("cwd") or os.getcwd()
    grants = load(session)

    command = args.get("command")
    if command:
        verdicts = classify_shell(str(command), cwd)
    else:
        verdicts = [classify_tool(str(tool), args)]

    pending = []
    for level, reason, scope in verdicts:
        if level == "never":
            return "ask", "Always asks: %s." % reason
        if level == "watched":
            if scope and scope[1] and scope[1] in grants.get(scope[0], []):
                continue
            pending.append((reason, scope))
    if not pending:
        if any(v[0] == "watched" for v in verdicts):
            return "allow", "Every outward write in this command is authorised for the session."
        return None, ""
    reason, scope = pending[0]
    if scope and scope[1]:
        hint = "permissions.py grant %s %s %s" % (session or "<session>", scope[0], scope[1])
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


def check(argv):
    fmt = "exit"
    try:
        if "--format" in argv:
            i = argv.index("--format")
            fmt = argv[i + 1] if i + 1 < len(argv) and argv[i + 1] in FORMATS else "exit"
        try:
            purge()
        except Exception:
            pass
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
        decision, reason = decide(event)
    except Exception as e:
        decision, reason = "ask", "The guard could not decide (%s), so it asks." % type(e).__name__
    try:
        return emit(decision, reason, fmt)
    except Exception:
        sys.stderr.write("Needs the person's OK. The guard could not answer.\n")
        return 2


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    action = argv[0]
    if action == "check":
        return check(argv[1:])
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
