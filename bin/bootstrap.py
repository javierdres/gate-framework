#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Scaffold what an organisation needs before it can run GATE for the first time.

Three subcommands:

    bootstrap.py sdlc <path> [--assistant <id>] [--org <short name>]
                                   create the organisation's SDLC repository
    bootstrap.py catalog <path>    create a standalone standards catalog repository
    bootstrap.py config <path>     drop .gate/config.yml into a project

`sdlc` is where an orchestrator starts: it writes the whole skeleton that
/establish then fills in from the interview, with the empty catalog inside it,
the neutral guards and the adapter for the chosen assistant (claude-code,
gemini-cli, kiro, codex or other). The catalog is identical for anyone starting
out, so there is no reason to build it by hand. The config is filled in with
whatever can be read off the repository, and leaves the rest for /init to ask
about.
"""
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ───────────────────────────── the catalog scaffold ─────────────────────────

KIT = os.path.join(HERE, "kit")


def copy_tree(src_dir, target):
    """Copy a folder of the kit, keeping file modes. Returns the number of files."""
    count = 0
    for base, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            src = os.path.join(base, f)
            dst = os.path.join(target, os.path.relpath(src, src_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            io.open(dst, "wb").write(io.open(src, "rb").read())
            os.chmod(dst, os.stat(src).st_mode)
            count += 1
    return count


def scaffold_catalog(target):
    """A standalone catalog repository, for an organisation that keeps it outside its SDLC."""
    if os.path.exists(target) and os.listdir(target):
        print("x %s exists and is not empty. Refusing to write over it." % target)
        return 1
    count = copy_tree(os.path.join(KIT, "catalog"), target)
    print("OK  standards catalog scaffolded at %s (%d files, empty of rules)" % (target, count))
    print()
    print("    Next:")
    print("      cd %s" % target)
    print("      git init && git add -A && git commit -m 'Standards catalog, empty by design'")
    print("      python3 bin/validate.py && python3 tests/test_catalog.py")
    print()
    print("    Then point your project's .gate/config.yml at it:")
    print("      organisation.catalog:         <this repository's URL>")
    print("      organisation.false_positives: <that URL>/calibration/false-positives.md")
    return 0


# ───────────────────────────── the organisation's SDLC ──────────────────────

ASSISTANTS = ("claude-code", "gemini-cli", "kiro", "codex", "other")

SDLC_TEMPLATES = {
    "AGENTS.md": "agents.md",
    "GOVERNANCE.md": "governance.md",
    "PLAN.md": "plan.md",
    "products/_template/README.md": "product.md",
    "products/_template/business-rules.md": "business-rules.md",
    "products/_template/use-cases.md": "use-cases.md",
    "method/templates/dossier.md": "dossier.md",
    "method/templates/design-decision.md": "design-decision.md",
    "method/templates/postmortem.md": "postmortem.md",
    "method/templates/qa-script.md": "qa-script.md",
    "method/templates/session-log.md": "session-log.md",
    "method/templates/profile.md": "profile.md",
    "method/templates/ticket.md": "ticket.md",
    "method/templates/rule.md": "rule.md",
}

SDLC_README = """# {org} SDLC

How {org} works with an AI assistant across the software life cycle: product, building,
operations, security and leadership. Built on [GATE](https://github.com/javierdres/gate-framework):
the assistant prepares, people decide.

To start, see [ONBOARDING.md](ONBOARDING.md). What is being built now is in [PLAN.md](PLAN.md),
and who approves what is in [GOVERNANCE.md](GOVERNANCE.md).
"""

SDLC_ONBOARDING = """# Onboarding

1. Ask the orchestrator for read access to this repository on the code platform, with your own
   account. Product and other roles that work outside the terminal get the chat-client package
   instead, from `method/chat-client/`.
2. Create a working folder, for example `~/Projects/{org}`, and clone this repository inside it,
   next to the repositories of your products.
3. Open your assistant inside this repository the first time and say hello. `onboard` takes it
   from there: requirements, installation, profile and access, one step at a time. Until the
   installer runs, the guards are not active yet, so that first session only reads and installs.
4. From then on, open the assistant in the working folder, not inside this repository.

You never paste a credential in the chat. Each access has a step-by-step guide in
`tools/guides/`.

## Skills

See [skills/README.md](skills/README.md).
"""

SDLC_GATE_MAP = """# GATE in this SDLC

Implements GATE at commit `{version}`. Moving to a newer one is a change request to this file
that also reviews the departures below.

## What implements what

| GATE | Here |
| --- | --- |
| Section 2, the orchestrator and `/establish` | This repository, `sdlc.yml`, `GOVERNANCE.md` |
| `/onboard` | `skills/onboard`, `tools/install.sh`, `tools/guides/` |
| Permissions principle | `method/permissions.md`, `tools/guards/permissions.py` |
| Environment-enforced controls | `tools/guards/`, `adapters/`, protected main branch |
| The person's level | `personal/`, `method/sessions.md` |
| Stage 2 use cases, stage 8 flows, stage 9 regression | `products/<product>/use-cases.md`, `e2e/`, `skills/e2e` |
| Stage 12 and the catalog | `catalog/`, `skills/harvest` |

## Departures

Each one is a local decision or a lesson GATE has not learned yet. A lesson is proposed to GATE
as a candidate, told as a pattern, with nothing that belongs to the organisation.

| Departure | Why | Proposed to GATE? |
| --- | --- | --- |
"""


REFERENCE_FILES = ("GATE.md", "BUILDING.md", "BUILDING.es.md", "START-HERE.md", "START-HERE.es.md",
                   "README.md", "README.es.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE",
                   "LICENSE-DOCS", "adoption/README.md")
REFERENCE_FOLDERS = ("skills", "templates")


def gate_version():
    v = run(["git", "rev-parse", "--short", "HEAD"], HERE)
    return v or "to be defined"


def scaffold_sdlc(target, assistant, org):
    if os.path.exists(target) and os.listdir(target):
        print("x %s exists and is not empty. Refusing to write over it." % target)
        return 1
    if assistant not in ASSISTANTS:
        print("x unknown assistant '%s'. One of: %s" % (assistant, ", ".join(ASSISTANTS)))
        return 1
    org = org or os.path.basename(os.path.abspath(target)).replace("sdlc-", "") or "org"
    written = copy_tree(KIT, target)

    for dst, tpl in SDLC_TEMPLATES.items():
        src = os.path.join(HERE, "templates", tpl)
        path = os.path.join(target, dst)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = io.open(src, encoding="utf-8").read().replace("<Organisation>", org)
        io.open(path, "w", encoding="utf-8").write(text)
        written += 1

    version = gate_version()
    config = io.open(os.path.join(HERE, "templates", "sdlc.yml"), encoding="utf-8").read()
    config = re.sub(r'^(  version:) ""', r'\1 "%s"' % version, config, count=1, flags=re.M)
    config = re.sub(r'^(  short_name:) ""', r'\1 "%s"' % org, config, count=1, flags=re.M)
    config = re.sub(r'^(  - id:) ""(\s+# claude-code)', r'\1 "%s"\2' % assistant, config, count=1, flags=re.M)
    extra = {
        "sdlc.yml": config,
        "README.md": SDLC_README.format(org=org),
        "ONBOARDING.md": SDLC_ONBOARDING.format(org=org),
        "GATE.md": SDLC_GATE_MAP.format(version=version),
        "CODEOWNERS": "# Translates GOVERNANCE.md. During formulation, the orchestrator owns everything.\n* @<orchestrator>\n",
        ".gitignore": "personal/\n__pycache__/\n.DS_Store\n",
        "method/flows/.gitkeep": "",
        "method/chat-client/README.md": "# Chat-client package\n\nInstructions and context files for roles that work outside the terminal, and where to copy each one.\n",
    }
    for rel, content in extra.items():
        path = os.path.join(target, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="utf-8").write(content)
        written += 1

    # The reference travels with the SDLC, so /establish works offline and against the exact
    # version the SDLC was scaffolded from.
    reference = os.path.join(target, "gate-reference")
    for rel in REFERENCE_FILES:
        src = os.path.join(HERE, rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(os.path.join(reference, rel)), exist_ok=True)
            io.open(os.path.join(reference, rel), "wb").write(io.open(src, "rb").read())
            written += 1
    for folder in REFERENCE_FOLDERS:
        written += copy_tree(os.path.join(HERE, folder), os.path.join(reference, folder))
    io.open(os.path.join(reference, "ABOUT.md"), "w", encoding="utf-8").write(
        "# GATE reference\n\nA read-only copy of GATE at commit `%s`, the version this SDLC was "
        "scaffolded from, with its own paths kept so every link inside it resolves. Moving to a "
        "newer GATE replaces this folder and updates `GATE.md` at the root of the SDLC.\n" % version)
    written += 1

    if assistant == "claude-code":
        # Claude Code finds skills in .claude/skills/ of the folder it is opened in. Linking them
        # here makes /establish and /onboard available before anything is installed.
        io.open(os.path.join(target, "CLAUDE.md"), "w", encoding="utf-8").write("@AGENTS.md\n")
        os.makedirs(os.path.join(target, ".claude", "skills"), exist_ok=True)
        for name in ("establish", "onboard"):
            link = os.path.join(target, ".claude", "skills", name)
            try:
                os.symlink(os.path.join("..", "..", "skills", name), link)
            except OSError:
                src = os.path.join(target, "skills", name, "SKILL.md")
                os.makedirs(link, exist_ok=True)
                io.open(os.path.join(link, "SKILL.md"), "wb").write(io.open(src, "rb").read())
        written += 2

    print("OK  SDLC for %s scaffolded at %s (%d files, GATE %s, assistant %s)"
          % (org, target, written, version, assistant))
    print()
    print("    Next, with your assistant open inside %s:" % target)
    if assistant == "claude-code":
        print("      run /establish. It interviews you, builds every layer following")
        print("      gate-reference/BUILDING.md and closes with the final verification.")
    else:
        print("      ask it to read AGENTS.md and run the establish skill in")
        print("      skills/establish/SKILL.md. If your assistant loads skills from")
        print("      another folder, point it there first; adapters/README.md says how.")
        print("      /establish then writes the adapter for %s from its current" % assistant)
        print("      documentation, and the final verification proves it works.")
    return 0


# ───────────────────────────── the project config ───────────────────────────

def run(cmd, cwd):
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def detect(project):
    """Read off the repository whatever the config can be filled with."""
    found = {}

    remotes = run(["git", "remote", "-v"], project)
    urls = sorted({l.split()[1] for l in remotes.split("\n") if len(l.split()) > 1})
    if urls:
        found["repositories"] = urls
    found.setdefault("id", os.path.basename(os.path.abspath(project)))

    branches = run(["git", "branch", "-a", "--format=%(refname:short)"], project)
    pattern = None
    for b in branches.split("\n"):
        m = re.search(r"^(?:origin/)?((?:feature|feat|fix|hotfix|bugfix)/[A-Z]+-)\d+", b)
        if m:
            pattern = m.group(1) + "<number>"
            break
    if pattern:
        found["branch_convention"] = pattern

    lint, tests = [], []
    pkg = os.path.join(project, "package.json")
    if os.path.exists(pkg):
        try:
            scripts = json.load(io.open(pkg, encoding="utf-8")).get("scripts", {})
            for name, _ in scripts.items():
                if name in ("lint", "eslint"):
                    lint.append("npm run %s" % name)
                if name in ("test", "tests"):
                    tests.append("npm run %s" % name)
        except Exception:
            pass
    if os.path.exists(os.path.join(project, "composer.json")):
        lint.append("php -l on every changed .php file")
    if os.path.exists(os.path.join(project, "pyproject.toml")):
        lint.append("ruff check .")
        tests.append("pytest")
    if os.path.exists(os.path.join(project, "Makefile")):
        mk = io.open(os.path.join(project, "Makefile"), encoding="utf-8", errors="replace").read()
        for target in ("lint", "test"):
            if re.search(r"^%s:" % target, mk, re.M):
                (lint if target == "lint" else tests).append("make %s" % target)
    if lint:
        found["lint"] = sorted(set(lint))
    if tests:
        found["tests"] = sorted(set(tests))

    for candidate in (".ai", "docs/architecture.md", "ARCHITECTURE.md", "CLAUDE.md", "AGENTS.md"):
        if os.path.exists(os.path.join(project, candidate)):
            found["definition"] = candidate
            break

    return found


def scaffold_config(project):
    template = os.path.join(HERE, "templates", "gate-config.yml")
    if not os.path.exists(template):
        print("x templates/gate-config.yml not found next to this script")
        return 1
    target = os.path.join(project, ".gate", "config.yml")
    if os.path.exists(target):
        print("x %s already exists. Run bin/check_config.py to see what is missing." % target)
        return 1

    text = io.open(template, encoding="utf-8").read()
    found = detect(project)

    def put(key, value):
        nonlocal text
        if isinstance(value, list):
            rendered = "\n" + "\n".join("    - %s" % v for v in value)
            text = re.sub(r"^(  %s:) \[\]$" % key, r"\1" + rendered, text, count=1, flags=re.M)
        else:
            text = re.sub(r'^(  %s:) ""$' % key, r'\1 "%s"' % value, text, count=1, flags=re.M)

    for key in ("id", "repositories", "branch_convention", "definition"):
        if key in found:
            put(key, found[key])
    for key in ("lint", "tests"):
        if key in found:
            put(key, found[key])

    os.makedirs(os.path.dirname(target), exist_ok=True)
    io.open(target, "w", encoding="utf-8").write(text)

    print("OK  %s written" % target)
    if found:
        print("\n    Detected from the repository:")
        for k, v in sorted(found.items()):
            print("      %-18s %s" % (k, v if not isinstance(v, list) else ", ".join(v)))
    print("\n    Now run:")
    print("      python3 %s/bin/check_config.py %s" % (HERE, target))
    print("    and fill in what it reports as blocking. /init will ask for the same fields.")
    return 0


def option(name, default=""):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("sdlc", "catalog", "config"):
        print(__doc__.strip())
        return 2
    action, path = sys.argv[1], sys.argv[2]
    if action == "sdlc":
        return scaffold_sdlc(path, option("--assistant", "other"), option("--org"))
    if action == "catalog":
        return scaffold_catalog(path)
    if not os.path.isdir(path):
        print("x %s is not a directory" % path)
        return 1
    return scaffold_config(path)


if __name__ == "__main__":
    sys.exit(main())
