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
    method: ssh-signing   the person signs a fresh nonce with the key in `git config
                          user.signingkey`, and the signature must verify against the SDLC's
                          allowed_signers: holding the private key is what proves it
    method: declared      git's user.email, reported as not verified
When the declared method does not verify the person, `identity.tracker_command` (a command that
prints their tracker account) is tried next; failing both, the assistant is told to verify them
through the tracker connector before any menu. Accounts matching `identity.bot_pattern` are never
taken for a person. The profiles a person declares never widen the ones GOVERNANCE.md enables.

    session_start.py [--guards block]       the context; `block` for assistants whose hooks can
                                            only let through or block
    session_start.py --fingerprint <id>     what the installer stamps for that assistant

The update never hangs and never leaves the repository half done: no prompt, bounded network
calls, a fast-forward of the default branch without switching branches, and a rebase with the
local changes set aside only when they do not touch the incoming files.
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
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAL = os.path.join(ROOT, "personal")
SKILL_FOLDERS = (".claude/skills", ".kiro/skills", ".gemini/skills", ".agents/skills", ".codex/skills")
OPEN_HEADINGS = re.compile(r"^##\s+(open|abierto|abiertos|pendiente|pendientes|en curso)\b", re.I | re.M)


def read(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def run(args, timeout=10, cwd=ROOT, env=None):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env,
                           stdin=subprocess.DEVNULL)
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def config_value(key, section=None):
    """A flat read of sdlc.yml, enough for the few keys this guard needs.

    A value may be bare, in single quotes, or in double quotes with backslash escapes; a `#`
    starts a comment only outside quotes.
    """
    text = read(os.path.join(ROOT, "sdlc.yml"))
    if section:
        m = re.search(r"^%s:\n((?:[ \t]+.*\n?|\s*\n)*)" % re.escape(section), text, re.M)
        text = m.group(1) if m else ""
    m = re.search(r"^\s*%s:[ \t]*(.*)$" % re.escape(key), text, re.M)
    if not m:
        return ""
    raw = m.group(1).strip()
    if raw.startswith('"'):
        q = re.match(r'"((?:[^"\\]|\\.)*)"', raw)
        return re.sub(r"\\(.)", r"\1", q.group(1)) if q else ""
    if raw.startswith("'"):
        q = re.match(r"'((?:[^']|'')*)'", raw)
        return q.group(1).replace("''", "'") if q else ""
    return raw.split(" #", 1)[0].split("\t#", 1)[0].strip()


# Every network call of the update is bounded: no password prompt, no SSH question, and a slow
# connection gives up instead of holding the session.
QUIET = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never",
         "GIT_SSH_COMMAND": "ssh -o BatchMode=yes -o ConnectTimeout=4 -o ServerAliveInterval=2 "
                            "-o ServerAliveCountMax=2"}
BOUNDED = ["-c", "http.lowSpeedLimit=1000", "-c", "http.lowSpeedTime=4"]
VERSION = re.compile(r"^##\s+(\d+\.\d+\.\d+)\b", re.M)


def git(*args, **kw):
    return run(["git"] + list(args), env=dict(os.environ, **QUIET), **kw)


def default_branch():
    code, head = git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if code == 0 and head.startswith("origin/"):
        return head[len("origin/"):]
    for name in ("main", "master"):
        if git("rev-parse", "--verify", "--quiet", "refs/heads/" + name)[0] == 0:
            return name
    return "main"


def versions(ref):
    _, text = git("show", "%s:CHANGELOG.md" % ref)
    return VERSION.findall(text)


def in_progress():
    _, gitdir = git("rev-parse", "--absolute-git-dir")
    return any(os.path.exists(os.path.join(gitdir, f))
               for f in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "REVERT_HEAD"))


def bring_in(main, branch):
    """Bring origin/<main> into <main> without ever leaving the repository half done."""
    if branch != main:
        # On another branch, the default branch moves forward without switching to it.
        if git("fetch", "-q", ".", "origin/%s:%s" % (main, main), timeout=20)[0] == 0:
            return "ok"
        exists = git("rev-parse", "--verify", "--quiet", "refs/heads/" + main)[0] == 0
        if exists and git("merge-base", "--is-ancestor", main, "origin/" + main)[0] != 0:
            return "conflict"
        return "locked"
    if in_progress():
        return "in progress"
    _, base = git("merge-base", "HEAD", "origin/" + main)
    _, local = git("diff", "--name-only", "HEAD")
    _, incoming = git("diff", "--name-only", base, "origin/" + main)
    if set(local.split()) & set(incoming.split()):
        return "same files"
    # The autostash commit needs an identity; a person without one gets a neutral one, only here.
    ident = [] if git("config", "user.email")[1] else ["-c", "user.name=sdlc", "-c", "user.email=sdlc@localhost"]
    _, before = git("rev-parse", "-q", "--verify", "refs/stash")
    code, _ = git(*(ident + ["rebase", "-q", "--autostash", "origin/" + main]), timeout=30)
    if code != 0:
        git("rebase", "--abort")
        return "conflict"
    _, after = git("rev-parse", "-q", "--verify", "refs/stash")
    _, unmerged = git("diff", "--name-only", "--diff-filter=U")
    return "stash collided" if unmerged or before != after else "ok"


def update():
    code, _ = git("rev-parse", "--git-dir")
    if code:
        return "not a git repository yet"
    code, _ = git("rev-parse", "--verify", "--quiet", "HEAD")
    if code:
        return "no commits yet"
    code, branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    branch = branch if code == 0 else ""
    if git("remote", "get-url", "origin")[0] != 0:
        return ("no upstream yet: once the SDLC exists on the code platform, push it once with "
                "`git push -u origin %s`" % (branch or "main"))
    main = default_branch()
    reached = git(*(BOUNDED + ["fetch", "-q", "origin", main]), timeout=20)[0] == 0
    if git("rev-parse", "--verify", "--quiet", "refs/remotes/origin/" + main)[0] != 0:
        return ("no upstream yet: once the SDLC exists on the code platform, push it once with "
                "`git push -u origin %s`" % main)
    _, count = git("rev-list", "--count", "%s..origin/%s" % (main, main))
    new = int(count) if count.isdigit() else 0
    if not new:
        return ("up to date with origin/%s" % main if reached else
                "could not reach origin/%s; up to date with what was last fetched" % main)
    _, titles = git("log", "--format=%s", "-5", "%s..origin/%s" % (main, main))
    titles = "; ".join(titles.splitlines())
    had = set(versions(main))
    added = [v for v in versions("origin/" + main) if v not in had]
    state = bring_in(main, branch)
    news = "%d new commit%s on origin/%s (%s)" % (new, "" if new == 1 else "s", main, titles)
    if added:
        news += ", with new SDLC version%s %s" % ("" if len(added) == 1 else "s", ", ".join(added))
    if state == "ok":
        text = ("updated with %s. Tell the person in one line at the greeting; what changed in the "
                "instructions applies in full from the next session." % news)
        if added:
            text += (" At the greeting, or at the end if they came with a direct request, read in "
                     "CHANGELOG.md the entry of each new version and tell them in one or two lines "
                     "what changed and its \"What to do\".")
        if branch != main:
            text += (" They are on %s: %s moved forward and their branch stays as it was."
                     % (branch or "a detached HEAD", main))
        return text
    return {
        "in progress": "%s, not brought in: a merge, rebase or cherry-pick is half done in the SDLC "
                       "repository. Nothing was touched. Offer to finish it, then update." % news,
        "same files": "%s, not brought in: there are uncommitted changes in the same files. Nothing "
                      "was touched. Offer to commit or discard them, then update." % news,
        "stash collided": "%s. Brought in, but putting back the uncommitted changes collided: they "
                          "are safe in the stash (`git stash list`). Tell the person at the greeting "
                          "and offer to resolve it." % news,
        "conflict": "%s, not brought in: they collide with what is on the local %s (own commits or "
                    "untracked files). Nothing was touched. Offer to resolve it before working." % (news, main),
        "locked": "%s, but %s could not move forward (it may be checked out in another worktree). "
                  "Nothing was touched. Offer to look into it." % (news, main),
    }[state]


def renamed():
    """The orchestrator renamed the system in sdlc.yml and this folder still has the old name."""
    name = config_value("name", "system")
    here = os.path.basename(ROOT)
    if not name or name == here:
        return None
    return ("- Renamed: the orchestrator renamed this system from %s to %s, and this copy still "
            "has the old name. Tell the person once, at the greeting, and give them the "
            "step-by-step to run outside the assistant: close the assistant, open a terminal, "
            "paste `bash \"%s/tools/rename.sh\"`, read its OK lines, then open the assistant "
            "again in %s. It moves the folder with their personal files, rewrites what the "
            "installer wrote and installs again, with backups. Until then everything keeps "
            "working under the old name." % (here, name, ROOT, os.path.dirname(ROOT)))


def assistant_in_use():
    """The assistant this session runs in, from the variables each one sets, or None. An
    adapter's hooks may declare it with SDLC_ASSISTANT, which wins (tools/lib.sh does the same)."""
    env = os.environ
    if env.get("SDLC_ASSISTANT"):
        return env["SDLC_ASSISTANT"]
    if env.get("CLAUDECODE") or env.get("CLAUDE_PROJECT_DIR"):
        return "claude-code"
    if env.get("GEMINI_CLI"):
        return "gemini-cli"
    if env.get("TERM_PROGRAM", "").lower().startswith("kiro") or any(k.startswith("KIRO_") for k in env):
        return "kiro"
    if env.get("CODEX_SANDBOX") or env.get("CODEX_HOME"):
        return "codex"
    return None


def fingerprint(assistant):
    """What an installation for this assistant depends on: the list of skills, the installer and
    its helpers, and the adapter's files. When it changes, only running the installer again
    brings the change to the working folder. Line endings are normalised, so a checkout on
    Windows gives the same fingerprint."""
    h = hashlib.sha1()
    skills = os.path.join(ROOT, "skills")
    names = sorted(d for d in (os.listdir(skills) if os.path.isdir(skills) else [])
                   if os.path.isfile(os.path.join(skills, d, "SKILL.md")))
    h.update(("skills:%s\n" % ",".join(names)).encode("utf-8"))
    files = ["tools/install.sh", "tools/lib.sh", "tools/instructions_block.py"]
    adapter = os.path.join(ROOT, "adapters", assistant)
    for base, dirs, found in os.walk(adapter):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        files += sorted(os.path.relpath(os.path.join(base, f), ROOT).replace(os.sep, "/")
                        for f in found if f != "README.md" and not f.endswith(".pyc"))
    for rel in files:
        try:
            with io.open(os.path.join(ROOT, rel), "rb") as f:
                data = f.read().replace(b"\r\n", b"\n")
        except OSError:
            continue
        h.update(rel.encode("utf-8") + b"\0" + data + b"\0")
    return h.hexdigest()[:16]


def installed():
    """{assistant: fingerprint} of every installation in this copy. personal/.installed holds the
    last one in the older form, `<commit or fingerprint> <assistant>`."""
    found = {}
    legacy = read(os.path.join(PERSONAL, ".installed")).split()
    if len(legacy) >= 2:
        found[legacy[1]] = legacy[0]
    if os.path.isdir(PERSONAL):
        for f in os.listdir(PERSONAL):
            if f.startswith(".installed-"):
                found[f[len(".installed-"):]] = read(os.path.join(PERSONAL, f)).strip()
    return found


def installation(assistant):
    """(installed?, state). The notice file keeps the status line warning until the installer
    runs again, which removes it."""
    notice = os.path.join(PERSONAL, ".reinstall-needed")
    found = installed()
    if not found and not os.path.exists(os.path.join(PERSONAL, ".installed")):
        return False, "not installed: run tools/install.sh <assistant> from this repository"
    which = assistant or (sorted(found)[0] if found else "<assistant>")
    if found.get(which) == fingerprint(which):
        try:
            os.remove(notice)
        except OSError:
            pass
        return True, "current"
    try:
        with io.open(notice, "w", encoding="utf-8") as f:
            f.write(which + "\n")
    except OSError:
        pass
    name = os.path.basename(ROOT)
    why = ("there is no installation for %s yet" % which if which not in found else
           "an update brought skills, an adapter or installer changes that only arrive by running "
           "the installer again, or this installation predates the check")
    return True, ("reinstall needed: %s. At the greeting, or at the end if they came with a direct "
                  "request, tell the person in one line and offer to bring it up to date now. With "
                  "their OK you may run it yourself, from the working folder: `bash %s/tools/install.sh "
                  "%s`. It only writes in the working folder, never duplicates anything and keeps "
                  "backups in %s/personal/backups/. Then ask them to close and reopen the assistant so "
                  "it picks up the changes." % (why, name, which, name))


def refresh_copies():
    """Where links could not be made (Windows without developer mode), the installer copied the
    skills and marked each copy with .sdlc-copy. They are copied again at every session, so they
    get what the update brought."""
    work = os.path.dirname(ROOT)
    for folder in SKILL_FOLDERS:
        base = os.path.join(work, folder)
        if not os.path.isdir(base):
            continue
        for name in os.listdir(base):
            dest, src = os.path.join(base, name), os.path.join(ROOT, "skills", name)
            if os.path.islink(dest) or not os.path.exists(os.path.join(dest, ".sdlc-copy")):
                continue
            if not os.path.isfile(os.path.join(src, "SKILL.md")):
                continue
            try:
                shutil.rmtree(dest)
                shutil.copytree(src, dest)
                io.open(os.path.join(dest, ".sdlc-copy"), "w").close()
            except OSError:
                pass


def adapter_session(assistant):
    """An adapter may carry session.py, run here at every session start, for what its assistant
    picks up without reinstalling (Claude Code: the status line)."""
    script = os.path.join(ROOT, "adapters", assistant or "", "session.py")
    if assistant and os.path.isfile(script):
        run([sys.executable, script, os.path.dirname(ROOT), os.path.basename(ROOT)], timeout=10)


def opened_inside(event):
    """The assistant was opened inside the SDLC instead of the working folder."""
    where = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    try:
        return os.path.realpath(where) == os.path.realpath(ROOT)
    except Exception:
        return False


def read_event():
    """The JSON the assistant passes on standard input, if any. Read in a thread with a short
    limit, so a terminal or an open pipe with nothing in it never holds the session."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    box = []
    t = threading.Thread(target=lambda: box.append(sys.stdin.read()), daemon=True)
    t.start()
    t.join(1.0)
    try:
        event = json.loads(box[0]) if box and box[0].strip() else {}
    except ValueError:
        return {}
    return event if isinstance(event, dict) else {}


def identity():
    """The primary source declared in sdlc.yml: (who, verified, how)."""
    method = config_value("method", "identity") or "declared"
    if method == "platform":
        command = config_value("command", "identity")
        if command:
            code, out = run(["sh", "-c", command], timeout=15)
            if code == 0 and out:
                return out.splitlines()[0].strip(), True, "platform account"
        return None, False, "the platform command did not answer; check the platform login"
    if method == "ssh-signing":
        return ssh_identity()
    _, email = run(["git", "config", "user.email"])
    return email or None, False, "declared in git, not verified"


def identities():
    """The chain of sources, strongest first: the declared method, then the tracker command if
    sdlc.yml declares one (`identity.tracker_command`). A bot account (`identity.bot_pattern`) is
    never a person: it is skipped, and the chain goes on."""
    pattern = config_value("bot_pattern", "identity") or r"(\[bot\]$|[-_.]bot$|^bot[-_.])"
    found = [identity()]
    tracker = config_value("tracker_command", "identity")
    if tracker:
        code, out = run(["sh", "-c", tracker], timeout=15)
        if code == 0 and out:
            found.append((out.splitlines()[0].strip(), True, "tracker account"))
        else:
            found.append((None, False, "the tracker command did not answer"))
    checked = []
    for who, verified, how in found:
        try:
            bot = bool(who and re.search(pattern, who, re.I))
        except re.error:
            bot = False
        checked.append((who, False, "%s is a bot account, not a person" % who) if bot else (who, verified, how))
    return checked


def resolve_identity():
    """(who, verified, how, enabled profiles, row). The first verified account with a row in
    GOVERNANCE.md wins; a verified account without one gets the default row."""
    sources = identities()
    verified = [s for s in sources if s[1]]
    for who, _, how in verified:
        enabled, row = profiles_for(who)
        if row:
            return who, True, how, enabled, row
    if verified:
        who, _, how = verified[0]
        return who, True, how, profiles_for(None)[0], None
    who, _, how = sources[0]
    how = "; ".join(s[2] for s in sources)
    return who, False, how, profiles_for(None)[0], None


def as_profiles(text):
    return [p.strip().strip("`").lower() for p in (text or "").split(",") if p.strip().strip("`")]


def ssh_identity():
    """Prove possession: sign a fresh nonce and verify it against allowed_signers."""
    signers = os.path.join(ROOT, "allowed_signers")
    _, key = run(["git", "config", "user.signingkey"])
    if not key:
        return None, False, "no signing key configured in git"
    if not os.path.exists(signers):
        return None, False, "allowed_signers is missing from the SDLC"
    key = os.path.expanduser(key)
    with tempfile.TemporaryDirectory() as tmp:
        nonce = os.path.join(tmp, "nonce")
        with io.open(nonce, "w") as f:
            f.write("sdlc-identity %s %s\n" % (os.getpid(), os.urandom(16).hex()))
        candidates = [key] + ([key[:-4]] if key.endswith(".pub") else [])
        signed = False
        for k in candidates:
            if os.path.exists(k):
                code, _ = run(["ssh-keygen", "-Y", "sign", "-f", k, "-n", "git", nonce], timeout=10, cwd=tmp)
                if code == 0 and os.path.exists(nonce + ".sig"):
                    signed = True
                    break
        if not signed:
            return None, False, "could not sign with the configured key (no private key or agent)"
        code, principal = run(["ssh-keygen", "-Y", "find-principals", "-s", nonce + ".sig", "-f", signers],
                              timeout=10, cwd=tmp)
        principal = principal.splitlines()[0].strip() if code == 0 and principal else ""
        if not principal:
            return None, False, "the signing key is not in allowed_signers"
        try:
            with io.open(nonce, "rb") as data:
                p = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", signers, "-I", principal, "-n", "git",
                                    "-s", nonce + ".sig"], stdin=data, capture_output=True, timeout=10)
        except Exception:
            return None, False, "the signature could not be verified"
        if p.returncode != 0:
            return None, False, "the signature does not verify against allowed_signers"
        return principal, True, "signed a fresh challenge with a key listed in allowed_signers"


def profiles_for(who):
    text = read(os.path.join(ROOT, "GOVERNANCE.md"))
    # The heading may be translated: the SDLC is written in the organisation's language.
    m = re.search(r"^##\s+(Profiles enabled|Perfiles habilitados).*?\n(.*?)(?=^##\s|\Z)",
                  text, re.M | re.S | re.I)
    table = m.group(2) if m else ""
    fallback = None
    for line in table.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or set(cells[0]) <= {"-", " ", ":"}:
            continue
        if who and any(who.lower() == c.lower() for c in cells[1:-1]):
            return cells[-1].replace("`", ""), cells[0]
        if cells[1] in ("—", "-", "") and cells[0].lower().startswith(("everyone", "todas", "todos")):
            fallback = cells[-1].replace("`", "")
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


def session_notes(session, blocking):
    """How authorisations work in this session, for the assistant."""
    tool = "python3 %s/tools/guards/permissions.py" % os.path.basename(ROOT)
    text = ("- Session %s: outward writes ask until the person authorises their scope. At the first OK in "
            "a repository or a tracker project, ask whether it covers the rest of the session and, if "
            "they say yes, register it with `%s grant %s repo <path>` or `tracker <KEY>`."
            % (session, tool, session))
    if blocking:
        text += (" This assistant cannot show a confirmation: the permissions guard blocks what needs an "
                 "OK. Before an outward write, show the person what you are about to do and ask them to "
                 "answer \"ok\"; with that answer, try again. One OK covers one action.")
    if config_value("autonomous_allowed", "permissions").lower() in ("true", "yes"):
        text += (" The organisation allows autonomous mode: only if the person asks for it explicitly, "
                 "register it with `%s grant %s autonomous`; from then on the SDLC asks for nothing but "
                 "changes to the authorisations, and the assistant's own permission mode decides. Never "
                 "offer it yourself." % (tool, session))
    return text


def main(argv):
    if argv[:1] == ["--fingerprint"] and len(argv) == 2:
        print(fingerprint(argv[1]))
        return 0
    blocking = argv[argv.index("--guards") + 1] == "block" if "--guards" in argv[:-1] else False
    event = read_event()
    assistant = assistant_in_use()
    name, work = os.path.basename(ROOT), os.path.dirname(ROOT)
    lines = ["SDLC context"]
    lines.append("- GATE version: %s" % (config_value("version", "gate") or "not declared"))
    if not config_value("built"):
        lines.append("- The SDLC is not built yet: offer the establish skill before anything else.")
    lines.append("- SDLC repository: %s" % update())
    notice = renamed()
    if notice:
        lines.append(notice)

    stamp, state = installation(assistant)
    if stamp:
        refresh_copies()
        adapter_session(assistant or next(iter(sorted(installed())), None))
        if opened_inside(event):
            lines.append("- Opened inside the SDLC: the assistant was opened in %s, not in the working "
                         "folder %s, so the person's profile, log and the guards wired in the working folder "
                         "do not load here. Ask them to close it and open it again in %s. If they came with "
                         "a request about this repository, attend to it." % (name, work, work))
    lines.append("- Installation: %s" % state)
    profile = read(os.path.join(PERSONAL, "profile.md"))
    if not stamp:
        stage = "installation"
    elif not profile.strip():
        stage = "profile"
    elif not re.search(r"^(ready|listo):\s*\S", profile, re.M):
        stage = "access or welcome"
    else:
        stage = None
    if stage:
        lines.append("- Setup stage: %s. Continue with the onboard skill from there." % stage)

    who, verified, how, enabled, row = resolve_identity()
    if verified:
        lines.append("- Identity: %s (%s)" % (who, how))
    else:
        lines.append("- Identity: %s (%s). Before showing any menu, get their account through the "
                     "tracker connector and look it up in the profiles table of GOVERNANCE.md; offer only "
                     "the profiles that row enables, and none other. If it cannot be verified, only the "
                     "default row applies." % (who or "unknown", how))
    if enabled:
        lines.append("- Profiles enabled%s: %s" % ("" if verified else ", by default because the identity is not verified", enabled))
    if profile.strip():
        lines.append("- Profile: " + " · ".join(l.strip() for l in profile.splitlines() if l.strip()))

    # Declared profiles never widen the enabled ones, and access is checked for all of them.
    m = re.search(r"^(?:profile|profiles|perfil|perfiles):\s*(.+)$", profile, re.M)
    declared = as_profiles(m.group(1)) if m else []
    allowed = as_profiles(enabled)
    if enabled and not set(allowed) & {"all", "any", "everything", "todos", "todas"}:
        excess = [p for p in declared if p not in allowed]
        if excess:
            lines.append("- Declared but not enabled: %s. personal/profile.md declares them, but GOVERNANCE.md "
                         "does not enable them for this person. Work only with the enabled ones and offer to "
                         "correct the profile with the onboard skill." % ", ".join(excess))
        declared = [p for p in declared if p in allowed]
    checker = os.path.join(ROOT, "tools", "check-access.sh")
    if stamp and declared and os.path.isfile(checker):
        code, out = run(["bash", checker, "--summary", ",".join(declared)], timeout=30)
        last = out.splitlines()[-1] if out else "the checker did not answer"
        if "not answering" in last:
            last += (". Tell the person in one line at the greeting and offer to renew them with the "
                     "onboard skill, step by step in a separate terminal")
        lines.append("- Access: %s" % last)

    session = str(event.get("session_id") or event.get("sessionId") or "")
    if re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", session):
        lines.append(session_notes(session, blocking))

    items = open_items()
    if items:
        lines.append("- Log: %s" % os.path.join(PERSONAL, "sessions"))
        lines.append("- Open in the log:")
        lines.extend("  " + l.strip() for l in items)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:
        print("SDLC context\n- The session start guard could not finish (%s). Continue, and say so." % type(e).__name__)
        sys.exit(0)
