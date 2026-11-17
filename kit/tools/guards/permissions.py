#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Permissions guard for a system built on GATE. Neutral: any assistant can call it.

    permissions.py check [--format claude|json|exit]   read the action on stdin, decide
    permissions.py grant <session> repo <path>          authorise a repository for a session
    permissions.py grant <session> tracker <KEY>        authorise a tracker project
    permissions.py show <session>
    permissions.py grant <session> autonomous           autonomous mode, only where sdlc.yml allows it
    permissions.py revoke <session> [repo <path> | tracker <KEY> | autonomous]

Three levels. Local work is not this guard's business and passes untouched. Outward writes ask
until their scope is authorised for the session. A short list always asks, whatever was
authorised: pushes to the default branch or to a remote the repository does not declare;
forced, mirrored, pruning, deleting and all-branch pushes; merges; approving a change request,
which a person gives and never the assistant; deletions; infrastructure tools, except their
read-only subcommands; credentials; and anything that touches the authorisations themselves.

Authorising a repository also records its path on the code platform, taken from its origin
(`group/sub/name`, whatever the host), so a change request or an API write that names the
repository instead of running inside it (`gh pr create -R`, `glab mr create --repo`,
`gh api repos/<owner>/<name>/...`, `glab api projects/<group%2Fname>/...`) is covered too. The
home folder is never authorised as a repository, even when it is one.

Autonomous mode is an opt-in of the organisation: `permissions.autonomous_allowed: true` in
sdlc.yml. Only then, and only when the person asks for it explicitly, `grant <session>
autonomous` records it, and from there the guard protects nothing but the authorisations
themselves; the assistant's own permission mode decides the rest, merges and deletions
included. Granting goes through the person's confirmation like any other grant, so the assistant
can never give it to itself, and if the organisation withdraws the opt-in, a recorded grant
stops counting.

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

Assistants that can only block get the person's OK another way. Their per-message guard runs
`log_reminder.py --passes`, which records a pass when the person's message is an OK ("ok",
"go ahead", "dale"...). With `--format exit`, the next action that would ask spends the pass and
goes through: one OK, one action, valid for 15 minutes and deleted when used or found stale.
Registering or revoking an authorisation can use the pass, since the person's OK was for that;
writing the authorisations or the passes directly, or recording an OK on the person's behalf, is
blocked even with one.

Tool names from other assistants are brought to one classification first: shell tools
(execute_bash, run_shell_command...) or any tool whose input carries a `command` are shell
commands; file tools (fs_write, write_file, str_replace...) are file writes; and connector tools
named `server___tool`, `server/tool`, `@server/tool` or `mcp_server_tool` are read as
`mcp__server__tool`.

Environment: SDLC_GRANTS_DIR moves the grants folder and SDLC_CONFIG the sdlc.yml it reads,
both for tests.
"""
import io
import json
import os
import re
import shlex
import subprocess
import sys
import time
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRANTS = os.environ.get("SDLC_GRANTS_DIR") or os.path.join(ROOT, "personal", "grants")
CONFIG = os.environ.get("SDLC_CONFIG") or os.path.join(ROOT, "sdlc.yml")
TTL = 3 * 24 * 3600
PASS_TTL = 15 * 60
FORMATS = ("claude", "json", "exit")

# What changes the authorisations or gives an OK in the person's name. Judged before anything
# else, so nothing chained to it hides it; it asks even in autonomous mode, and a pass never
# covers it.
# Level "person": writing the grants or the passes directly; nothing covers it, not even a pass.
# Level "authorise": the grant and revoke commands; a pass, the person's typed OK, covers them.
GRANTS_TOUCH = [
    (r"personal/grants\b", "person", "the authorisations can only change through the person's own confirmation"),
    (r"log_reminder\.py\b", "person", "an OK can only come from the person"),
    (r"permissions\.py\b.*\b(grant|revoke)\b", "authorise", "an authorisation must pass the person's own confirmation"),
]
PROTECTED = ("person", "authorise")

# Judged on the command with its quotes and backslashes removed, so quoting cannot hide them.
NEVER = [
    (r"\b(gh\s+pr|glab\s+mr)\s+merge\b", "merge"),
    (r"\b(gh|glab|curl)\b.*\bmerge\b", "merge"),
    (r"(^|\s)(-X|--method|--request)\s*=?\s*delete\b", "deletion"),
    (r"\b(gh|glab)\s+(repo|release|issue|mr|pr|api)\b.*\bdelete\b", "deletion"),
    (r"\b(cdk\s+deploy|serverless\s+deploy|sam\s+deploy)\b", "infrastructure or production tool"),
    (r"\b(token|tokens|personal_access_tokens|deploy[-_]keys?)\b.*\b(create|new|add)\b", "credentials"),
    (r"\b(gh|glab)\s+auth\s+token\b", "credentials"),
    (r"\bgh\s+pr\s+review\b.*(--approve|(^|\s)-a\b)", "approval of a change request"),
    (r"\bglab\s+mr\s+(approve|unapprove|revoke)\b", "approval of a change request"),
    (r"\b(gh|glab|curl)\b.*\breviews\b.*\bapprove\b", "approval of a change request"),
    (r"(\b(gh|glab|curl)\b|tools/clients/).*/(un)?approve\b", "approval of a change request"),
]
# Infrastructure tools always ask, except for the subcommands below, which only read. Reading a
# secret is still credentials, and asks.
INFRA = re.compile(r"(?:^|(?<=[\s/(`=]))(kubectl|helm|terraform|pulumi)(?=\s|$)", re.I)
INFRA_READS = {
    "kubectl": {"get", "describe", "logs", "top", "explain", "version", "api-resources", "api-versions",
                "cluster-info", "events", "auth can-i", "auth whoami", "config view",
                "config get-contexts", "config current-context"},
    "helm": {"list", "ls", "status", "get", "history", "show", "search", "template", "lint", "version"},
    "terraform": {"version", "validate", "providers"},
    "pulumi": {"version", "whoami", "about"},
}
INFRA_VALUE_FLAGS = {"-n", "--namespace", "--context", "--kube-context", "--kubeconfig", "--cluster",
                     "--user", "-s", "--server", "--stack", "-C", "--cwd"}
INFRA_END = re.compile(r"&&|\|\||;|\||\n|&|\)|`")
SECRETS = re.compile(r"\bsecrets?\b", re.I)
# Each organisation's API clients live in tools/clients/ and take the HTTP method first:
# `tools/clients/<system>.sh GET <path>`. GET and HEAD only read; anything else, including a call
# with no method, is an outward write.
CLIENT = re.compile(r"(\S*tools/clients/\S+)\s*(\S*)(.*)")
# A GraphQL API takes every call as a POST, so its client takes the intent instead: QUERY reads
# and MUTATION writes.
CLIENT_READS = ("GET", "HEAD", "QUERY")
TICKET_KEY = re.compile(r"\b([A-Z][A-Z0-9]+)-\d+\b")

# Constructs the guard does not parse: a write inside them always asks.
OPAQUE = re.compile(r"(\$\(|`|<\(|>\(|\beval\b|\b(sh|bash|zsh|dash|ksh|fish|pwsh|powershell)\s+(-\w*c|-c)\b|"
                    r"\bxargs\b|\bexec\b|\bsource\b|^\s*\.\s|\bpython\d?\s+-c\b|\bperl\s+-e\b|\bnode\s+-e\b|"
                    r"\bruby\s+-e\b|\benv\s+\S+=)", re.I)
WRITE_HINT = re.compile(r"\bgit\b.*(?<!stash )\bpush\b|tools/clients/|"
                        r"\b(gh|glab)\b.*(\b(create|merge|delete|close|edit|comment|review|transfer|archive)\b|"
                        r"(-X|--method|--request)\s*=?\s*(post|put|patch|delete)\b|\s(-f|-F|--field|--raw-field|--input)(\s|=))|"
                        r"\bcurl\b.*((-X|--request)\s*=?\s*(post|put|patch|delete)\b|\s(-d|--data\S*|-F|--form)(\s|=))", re.I)
WRITE_METHOD = re.compile(r"(^|\s)(-X|--method|--request)\s*=?\s*(post|put|patch)\b", re.I)
IMPLICIT_POST = re.compile(r"(^|\s)(-f|-F|--field|--raw-field|--input)(\s|=)")
CURL_DATA = re.compile(r"(^|\s)(-d|--data\S*|-F|--form)(\s|=)")

READ_VERBS = re.compile(r"(get|list|search|read|fetch|query|view|show|describe|lookup|find|info|whoami|"
                        r"discover|status|count|preview|help|ping|"
                        r"resources|atlassianuserinfo|accessible)", re.I)
WRITE_VERBS = re.compile(r"(create|edit|update|comment|transition|move|assign|add|link|push|open|close|"
                         r"approve|label|write|execute|post|put|patch|set|upload|publish|send|merge|save|"
                         r"delete|remove|destroy|archive)", re.I)
DESTRUCTIVE = re.compile(r"(merge|delete|remove|destroy|archive|executedestructive)", re.I)
TRACKER_TOOL = re.compile(r"(jira|issue|ticket|tracker|linear|youtrack|shortcut|clickup)", re.I)
CODE_TOOL = re.compile(r"(github|gitlab|bitbucket|pull_?request|merge_?request|\bpr\b|\bmr\b|repo|branch|commit)", re.I)
FILE_TOOLS = ("write", "edit", "multiedit", "notebookedit", "str_replace_editor", "create_file", "replace",
              "write_file", "fs_write", "str_replace", "edit_file", "append", "append_file", "fs_append",
              "write_to_file")
FILE_HINT = re.compile(r"(write|append|replace|edit|create|patch)", re.I)
PATH_KEYS = ("file_path", "path", "notebook_path", "filePath", "target_file")
SHELL_TOOLS = ("bash", "shell", "execute_bash", "executebash", "run_shell_command", "run_command",
               "execute_command", "run_terminal_cmd", "shell_command", "terminal", "exec")
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
        return {"repo": [], "tracker": [], "platforms": {}}
    with io.open(p, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("repo", [])
    data.setdefault("tracker", [])
    data.setdefault("platforms", {})
    return data


def save(session, data):
    os.makedirs(GRANTS, exist_ok=True)
    path = grants_path(session)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2))
    os.chmod(path, 0o600)


def pass_path(session):
    return os.path.join(GRANTS, re.sub(r"[^A-Za-z0-9_.-]", "_", session or "default") + ".pass")


def spend_pass(session):
    """True when the person's OK for one action is waiting and fresh. Used or stale, it goes."""
    p = pass_path(session)
    try:
        with io.open(p, encoding="utf-8") as f:
            stamp = float(f.read().strip() or 0)
    except (OSError, ValueError):
        stamp = 0
    try:
        os.remove(p)
    except OSError:
        return False
    return 0 <= time.time() - stamp <= PASS_TTL


def config_value(key, section):
    """A flat read of one key of one section of sdlc.yml: enough for the opt-in this guard needs."""
    try:
        with io.open(CONFIG, encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return ""
    m = re.search(r"^%s:[^\n]*\n((?:[ \t]+.*\n?|\s*\n)*)" % re.escape(section), text, re.M)
    m = re.search(r"^\s*%s:[ \t]*(.*)$" % re.escape(key), m.group(1), re.M) if m else None
    if not m:
        return ""
    return m.group(1).split("#", 1)[0].strip().strip("\"'")


def autonomous_allowed():
    return config_value("autonomous_allowed", "permissions").lower() in ("true", "yes", "on")


def home():
    return os.path.realpath(os.path.expanduser("~"))


def platform_path(url):
    """`group/sub/name` from an origin URL, whatever the host: scp-like, https or ssh://."""
    url = (url or "").strip().rstrip("/")
    url = url[:-4] if url.endswith(".git") else url
    m = re.match(r"^[a-z][a-z0-9+.-]*://[^/]+/(.+)$", url, re.I) or re.match(r"^[^/:@]+@[^:/]+:(.+)$", url)
    return m.group(1).strip("/") if m else ""


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


def named_repository(tokens):
    """The repository a code platform command names instead of running inside it, as
    ("platform", "group/name"): `-R`/`--repo`, or the path of an API call."""
    for i, t in enumerate(tokens):
        if t in ("-R", "--repo") and i + 1 < len(tokens):
            return ("platform", tokens[i + 1].strip("/"))
        if t.startswith("--repo="):
            return ("platform", t.split("=", 1)[1].strip("/"))
    if len(tokens) > 1 and tokens[1] == "api":
        for t in tokens[2:]:
            m = re.match(r"^/?repos/([^/\s]+/[^/\s?]+)", t)
            if m:
                return ("platform", m.group(1))
            m = re.match(r"^/?projects/([^/\s?]+)", t)
            if m:
                return ("platform", unquote(m.group(1)))
    return None


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
        scope = named_repository(tokens) or ("repo", toplevel(where))
        if re.search(r"\b(pr|mr)\s+create\b", segment):
            return ("watched", "opening a change request", scope), where
        if len(tokens) > 1 and tokens[1] == "api" and (WRITE_METHOD.search(segment) or IMPLICIT_POST.search(segment)):
            return ("watched", "write through the code platform API", scope), where
        if len(tokens) > 1 and tokens[1] not in ("api", "auth", "status", "browse", "help", "version") and \
                re.search(r"\b(create|edit|close|reopen|comment|review|ready|merge|delete|transfer|archive|lock)\b", segment):
            return ("watched", "write to the code platform", scope), where
    if first == "curl" and (WRITE_METHOD.search(segment) or CURL_DATA.search(segment)):
        return ("watched", "write to an external API", None), where
    return ("local", "", None), where


def infra_verdict(flat):
    """Every use of an infrastructure tool, wherever it sits in the command, must be a read."""
    for m in INFRA.finditer(flat):
        tool = m.group(1).lower()
        rest = INFRA_END.split(flat[m.end():], 1)[0].split()
        sub = []
        skip = False
        for t in rest:
            if skip:
                skip = False
                continue
            if t.startswith("-"):
                skip = t in INFRA_VALUE_FLAGS
                continue
            sub.append(t.lower())
        if not any(" ".join(sub[:len(r.split())]) == r for r in INFRA_READS[tool]):
            return ("never", "infrastructure or production tool", None)
        if tool == "kubectl" and SECRETS.search(" ".join(sub[1:])):
            return ("never", "credentials", None)
    return None


def client_verdicts(flat):
    verdicts = []
    for m in CLIENT.finditer(flat):
        if m.group(2).upper() not in CLIENT_READS:
            name = os.path.basename(m.group(1))
            scope = None
            key = TICKET_KEY.search(m.group(3))
            if TRACKER_TOOL.search(name) and key:
                scope = ("tracker", key.group(1))
            verdicts.append(("watched", "write through the API client %s" % name, scope))
    return verdicts


def classify_shell(command, cwd):
    flat = re.sub(r"['\"\\]", "", command)
    grants_dir = os.path.realpath(GRANTS)
    if grants_dir in flat or GRANTS in flat:
        return [("person", "the authorisations can only change through the person's own confirmation", None)]
    for pattern, level, why in GRANTS_TOUCH:
        if re.search(pattern, flat, re.I):
            return [(level, why, None)]
    for pattern, why in NEVER:
        if re.search(pattern, flat, re.I):
            return [("never", why, None)]
    infra = infra_verdict(flat)
    if infra:
        return [infra]
    if OPAQUE.search(command) and WRITE_HINT.search(flat):
        return [("never", "a write inside a construct the guard does not parse", None)]
    verdicts, where = [], cwd
    for seg in segments(command):
        verdict, where = classify_segment(seg, where)
        if verdict[0] == "local" and re.search(r"\bgit\b.*(?<!stash )\bpush\b", re.sub(r"['\"\\]", "", seg)):
            verdict = ("never", "a push the guard could not read with certainty", None)
        verdicts.append(verdict)
    return verdicts + client_verdicts(flat)


def normalise(event):
    """(tool, args) in one vocabulary, whatever assistant sent the event: shell commands carry a
    `command`, file writes are named like the file tools above and connector tools like
    `mcp__server__tool`."""
    tool = str(event.get("tool_name") or event.get("toolName") or event.get("tool") or "")
    args = event.get("tool_input") or event.get("toolInput") or event.get("args") or {}
    if isinstance(args, str):
        try:
            parsed = json.loads(args)
        except ValueError:
            parsed = None
        args = parsed if isinstance(parsed, dict) else {"command": args}
    if not isinstance(args, dict):
        return tool, None
    lname = tool.lower()
    if lname.startswith("mcp__"):
        return tool, args
    if lname in SHELL_TOOLS and not isinstance(args.get("command"), str):
        for key in ("cmd", "script", "commandLine", "command_line"):
            if isinstance(args.get(key), str):
                return "Bash", dict(args, command=args[key])
    if isinstance(args.get("command"), str):
        return "Bash", args
    path = next((args[k] for k in PATH_KEYS if isinstance(args.get(k), str) and args.get(k)), None)
    looks_like_file = FILE_HINT.search(lname) and ("file" in lname or lname.startswith("fs_"))
    if (lname in FILE_TOOLS or looks_like_file) and path and "/" not in tool and "___" not in tool:
        return "Write", dict(args, file_path=path)
    m = re.match(r"^@?([\w.-]+)(?:___|/)([\w.-]+)$", tool)
    if m:
        return "mcp__%s__%s" % (m.group(1), m.group(2)), args
    m = re.match(r"^mcp_([a-z0-9-]+)_(\w+)$", tool, re.I)
    if m:
        return "mcp__%s__%s" % (m.group(1), m.group(2)), args
    return tool, args


def classify_tool(name, args):
    lname = name.lower()
    base = lname.rsplit("__", 1)[-1]
    if base in FILE_TOOLS or lname in FILE_TOOLS:
        path = str(next((args[k] for k in PATH_KEYS if args.get(k)), ""))
        real = os.path.realpath(path) if path else ""
        if "personal/grants" in path.replace("\\", "/") or (real and real.startswith(os.path.realpath(GRANTS))):
            return ("person", "the authorisations can only change through the person's own confirmation", None)
        return ("local", "", None)
    if not lname.startswith("mcp__"):
        return ("local", "", None)
    if "approve" in base:
        return ("never", "approval of a change request through a connector", None)
    if DESTRUCTIVE.search(base):
        return ("never", "a merge or deletion through a connector", None)
    if READ_VERBS.search(base) and not WRITE_VERBS.search(re.sub(r"read|execute", "", base)):
        return ("local", "", None)
    if TRACKER_TOOL.search(lname) and not CODE_TOOL.search(lname):
        key = str(args.get("projectKey") or args.get("project") or args.get("issueKey") or
                  args.get("issueIdOrKey") or args.get("teamKey") or args.get("team") or "")
        if not key:
            ticket = TICKET_KEY.search(" ".join(str(args.get(k) or "") for k in ("identifier", "id", "issueId")))
            key = ticket.group(1) if ticket else ""
        key = key.split("-")[0].upper() or None
        return ("watched", "write to the tracker", ("tracker", key))
    if not WRITE_VERBS.search(base):
        # A connector verb the guard does not know is treated as a write: it never fails open.
        return ("watched", "a connector action the guard does not recognise", None)
    return ("watched", "write through a connector", None)


def covered(scope, grants):
    kind, value = scope
    if not value or value == home():
        return False
    if kind == "platform":
        return value in grants.get("platforms", {}).values()
    return value in grants.get(kind, [])


def judge(event):
    """(decision, reason, level). decision is allow, ask or None; level says what an ask
    protects: "person" and "authorise" for the authorisations, "never", or "watched"."""
    if not isinstance(event, dict) or not event:
        return "ask", "The guard received no action to judge, so it asks.", "never"
    tool, args = normalise(event)
    if args is None:
        return "ask", "The guard could not read the action's arguments, so it asks.", "never"
    session = str(event.get("session_id") or event.get("sessionId") or os.environ.get("SDLC_SESSION", ""))
    cwd = event.get("cwd") or os.getcwd()
    grants = load(session)

    command = args.get("command")
    if command:
        verdicts = classify_shell(str(command), cwd)
    else:
        verdicts = [classify_tool(tool, args)]

    for level, reason, _ in verdicts:
        if level in PROTECTED:
            return "ask", "Always asks: %s." % reason, level
    if grants.get("autonomous") is True and autonomous_allowed():
        # The person chose autonomous mode where the organisation allows it: the assistant's own
        # permission mode decides everything but the authorisations.
        return None, "", None
    pending = []
    for level, reason, scope in verdicts:
        if level == "never":
            return "ask", "Always asks: %s." % reason, "never"
        if level == "watched":
            if scope and covered(scope, grants):
                continue
            pending.append((reason, scope))
    if not pending:
        if any(v[0] == "watched" for v in verdicts):
            return "allow", "Every outward write in this command is authorised for the session.", None
        return None, "", None
    reason, scope = pending[0]
    reason = reason[:1].upper() + reason[1:]
    if scope and scope[0] == "platform" and scope[1]:
        return "ask", "%s in %s. To authorise it for the session, authorise its local clone: permissions.py " \
            "grant %s repo <path>" % (reason, scope[1], session or "<session>"), "watched"
    if scope and scope[1] and scope[1] != home():
        hint = "permissions.py grant %s %s %s" % (session or "<session>", scope[0], scope[1])
        return "ask", "%s. To authorise it for the session: %s" % (reason, hint), "watched"
    return "ask", "%s, outside any authorised scope." % reason, "watched"


def decide(event):
    decision, reason, _ = judge(event)
    return decision, reason


def emit(decision, reason, fmt, level=None):
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
    if level == "person":
        sys.stderr.write("Only the person can do this, not even with an OK: %s Leave it to them.\n" % reason)
        return 2
    sys.stderr.write("Needs the person's OK. %s Show the person what you are about to do and ask them to "
                     "reply \"ok\"; with their reply, try again. One OK covers one action.\n" % reason)
    return 2


def check(argv):
    fmt, level, session = "exit", "never", ""
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
        decision, reason, level = judge(event)
        if isinstance(event, dict):
            session = str(event.get("session_id") or event.get("sessionId") or os.environ.get("SDLC_SESSION", ""))
    except Exception as e:
        decision, reason, level = "ask", "The guard could not decide (%s), so it asks." % type(e).__name__, None
    # An assistant that can only block gets the person's OK as a pass: it covers one action.
    if fmt == "exit" and decision == "ask" and level in ("watched", "never", "authorise"):
        try:
            if spend_pass(session):
                print("The person's OK was used for this action. %s" % reason)
                return 0
        except Exception:
            pass
    try:
        return emit(decision, reason, fmt, level)
    except Exception:
        sys.stderr.write("Needs the person's OK. The guard could not answer.\n")
        return 2


def grant(session, data, kind, value):
    if kind == "autonomous":
        if not autonomous_allowed():
            print("x autonomous mode is not enabled for this organisation: sdlc.yml has no "
                  "permissions.autonomous_allowed: true. Every outward write keeps asking.")
            return 1
        data["autonomous"] = True
        save(session, data)
        print("OK  autonomous mode for session %s: the guard only protects the authorisations; the "
              "assistant's own permission mode decides the rest" % session)
        return 0
    if kind == "repo":
        top = toplevel(os.path.expanduser(value))
        if not top:
            print("x not a repository: %s" % value)
            return 1
        if top == home():
            print("x %s is the home folder: it is never authorised as a repository" % top)
            return 1
        if top not in data["repo"]:
            data["repo"].append(top)
        path = platform_path(git(["remote", "get-url", "origin"], top))
        if path:
            data["platforms"][top] = path
        value = top
    else:
        value = value.upper()
        if value not in data[kind]:
            data[kind].append(value)
    save(session, data)
    print("OK  %s %s authorised for session %s" % (kind, value, session))
    return 0


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
        if data.get("autonomous") is True:
            print("autonomous mode: %s" % ("active" if autonomous_allowed() else
                                           "recorded, but sdlc.yml no longer allows it, so it does not count"))
        return 0
    if action == "grant" and (len(argv) == 4 and argv[2] in ("repo", "tracker") or argv[2:] == ["autonomous"]):
        return grant(session, data, argv[2], argv[3] if len(argv) == 4 else None)
    if action == "revoke":
        if argv[2:] == ["autonomous"]:
            data.pop("autonomous", None)
            save(session, data)
        elif len(argv) == 4 and argv[2] in ("repo", "tracker"):
            kind = argv[2]
            value = (toplevel(os.path.expanduser(argv[3])) or os.path.realpath(argv[3])) if kind == "repo" \
                else argv[3].upper()
            data[kind] = [v for v in data[kind] if v != value]
            data["platforms"].pop(value, None)
            save(session, data)
        elif os.path.exists(grants_path(session)):
            os.remove(grants_path(session))
        print("OK  revoked")
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
