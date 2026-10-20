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

CATALOG_README = """# Standards

Code standards for this organisation, in Markdown, written to be read by people and consumed
mechanically by the GATE review skills.

Built with [GATE](https://github.com/javierdres/gate-framework).

## It starts empty on purpose

There are no rules yet, and that is not a pending task: it is the design.

A rule set written in one sitting, before there are real cases, does not describe the
organisation. It describes whoever copied it. Here **every rule has to show which discussion or
incident it came from** — the `origin` field is required and validated.

The catalog fills up through use, from the discussions in reviews and the root causes of
incidents. Until it does, review is not left without a bar: it leans on the industry baseline,
OWASP, SOLID and Clean Code, and on each project's own conventions. This repository sits on top
of that baseline, it does not replace it.

## Two severities

| Level | Directory | What belongs there | How review reports it |
|---|---|---|---|
| **Hard rule** | `rules/hard/` | Non-negotiable security: hardcoded secrets, injection, access control, insecure configuration | **Blocking** |
| **Soft rule** | `rules/soft/` | SOLID, clean code, readability | **Suggestion** |

A rule in `candidate` status never blocks, whatever its severity.

## This repository is the organisation

Within GATE, two projects reading this catalog are, by construction, the same organisation.
Nothing else defines that relationship.

## How a rule gets in

It is harvested, not written. `/harvest` runs on every pass of `/review` and on the closing of
every incident, and proposes candidates traceable to a real decision. Promoting a candidate to
`in force` is a human decision. See [GOVERNANCE.md](GOVERNANCE.md).

## Checks

```
python3 bin/validate.py          # rule format, ids, sections
python3 bin/generate_catalog.py  # rebuild catalog.json
```

`catalog.json` is generated. Do not edit it by hand.
"""

CATALOG_GOVERNANCE = """# Governance

## A rule's life

```
candidate ──► in force ──► deprecated
    │
    └──► (rejected: the merge request is closed, no file is left)
```

| Status | What it means | Effect on review |
|---|---|---|
| `candidate` | Formulated from a real decision, not yet approved | Reported as a **suggestion**, whatever its severity. Never blocks. |
| `in force` | Approved | Hard → **blocking**. Soft → suggestion. |
| `deprecated` | Superseded or dropped | Ignored. The file is **not** deleted. |

**Deprecated rule files are not deleted.** An old review may cite `HR-0007`; if the id
disappears that comment is orphaned. Mark `status: deprecated` and `superseded_by: <id>`, and
never reuse an id.

## Who approves

Promoting a candidate to `in force` requires approval on the merge request.

For **soft** rules, one reviewer who did not write it.

For **hard** rules, the group this organisation names as custodians. Define it before the first
hard rule, not during the argument about it. With more than one project this stops being a
single person.

## What does not go in this repository

**How a particular project is built.** Its patterns, its stack, its deliberate exceptions.
That belongs in that project's own documentation, and GATE points at it through
`project.definition` in the project's `.gate/config.yml`.

**Generic good practice with no decision of our own behind it.** The industry baseline already
covers it, and adding it here drowns out the signal.

## False positives

`calibration/false-positives.md` does not follow the life cycle above: it is not approved, not
versioned, and the validator does not look at it. An entry there blocks nothing — it only tells
review that a finding was already discussed and dismissed.

That is deliberate. If recording a false positive cost a merge request with approval, nobody
would record one, and calibration would go back to living only in conversation.

What does go through this governance: if the false positive comes from a **badly written rule**,
the rule gets fixed, by merge request, like any other change.
"""

CATALOG_CONTRIBUTING = """# Contributing a rule

Rules are harvested by `/harvest`, not written from scratch. This document is the format they
have to meet.

## File naming

```
rules/hard/HR-0001-no-concatenated-input-in-sql.md
rules/soft/SR-0001-extract-a-method-instead-of-a-flag.md
```

- `HR-` for a hard rule, in `rules/hard/`. `SR-` for a soft one, in `rules/soft/`.
- Four digits, sequential and **independent** per prefix. The next free id comes from
  `catalog.json`.
- Slug in lowercase with hyphens. An id is **never** reused, not even once deprecated.

## Frontmatter

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | `HR-NNNN` / `SR-NNNN` | yes | Must match the filename and the directory |
| `title` | text | yes | Names the rule, does not justify it |
| `severity` | `hard` / `soft` | yes | Consistent with the id prefix |
| `status` | `candidate` / `in force` / `deprecated` | yes | See GOVERNANCE.md |
| `scope` | list | yes | `cross-cutting`, or a stack: `php`, `sql`, `js`, `shell`, `iac`, `ci` |
| `projects` | list | yes | `cross-cutting`, or specific project ids |
| `tags` | list | yes, may be empty | Free: `owasp-a03`, `injection`, `secrets` |
| `origin` | list of URLs | yes, not empty | The discussion, note or postmortem it came from |
| `approved_by` | list | yes, empty if candidate | Not empty if `status: in force` |
| `created` | `YYYY-MM-DD` | yes | |
| `updated` | `YYYY-MM-DD` | yes | |
| `supersedes` | list of ids | yes, may be empty | |
| `superseded_by` | id or `null` | yes | Required if `status: deprecated` |

## Required sections

`## Do not`, `## Do instead`, `## Why`, `## How it is checked`.

`## Exceptions`, `## Evidence` and `## History` are optional, except that a hard rule with no
exceptions must say so explicitly.

## Before opening a merge request

```
python3 bin/generate_catalog.py && python3 bin/validate.py
```

Both have to come back clean.
"""

CATALOG_FALSE_POSITIVES = """# Known false positives

Findings that review raises and the team has already rejected, with the reason. The review
skills read this file first so they do not raise them again. Context in
[GOVERNANCE.md](../GOVERNANCE.md).

Entry format:

```markdown
## FP-NNNN — Short title

- **What review raises:** the claim the assistant makes.
- **Why it does not apply:** the reason, in one sentence that will still serve next time.
- **How to avoid it:** what to check before raising it.
- **Origin:** a link to the discussion or the rejected finding.
- **Recorded:** YYYY-MM-DD
```

Sequential numbering, never reused. No validator and no approval: it is added in the same merge
request where the rejection happened.

---

<!-- Nothing recorded yet. The first entry goes above this comment: the file reads top down and
     the most recent is best placed first. -->
"""

CATALOG_RULE_TEMPLATE = """---
id: HR-0000
title: A short phrase naming the rule, not justifying it
severity: hard
status: candidate
scope: [cross-cutting]
projects: [cross-cutting]
tags: []
origin:
  - https://example.com/merge_requests/1#note_1
approved_by: []
created: 2026-01-01
updated: 2026-01-01
supersedes: []
superseded_by: null
---

# HR-0000 — A short phrase naming the rule

## Do not

What is forbidden, concretely. Nameable in code: a function, a pattern, a way of writing
something. If you cannot point at it in a diff, it is not a rule yet.

## Do instead

The concrete alternative that replaces it. With code if it helps.

## Why

What breaks if it is not followed. Real impact, not "it is bad practice".

## How it is checked

The heuristic a person or an agent uses to check this rule against a change. Concrete and
runnable:

```bash
grep -rn "forbidden_pattern" --include="*.ext" .
```

If the check has known false positives, say so here.

## Exceptions

(Optional) Cases where the rule does not apply, and why. If a hard rule has none, write
"None. This is a hard rule."

## Evidence

(Optional) Links to real code, incidents or findings behind the rule.

## History

(Optional) One line per change of status or of demand.

- 2026-01-01 — Created as a candidate from <link to the discussion>.
"""

CATALOG_VALIDATE = '''#!/usr/bin/env python3
"""Validate the rule files: naming, ids, frontmatter and required sections."""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "rules")
FILENAME = re.compile(r"^(HR|SR)-(\\d{4})-[a-z0-9]+(-[a-z0-9]+)*\\.md$")
FIELDS = ["id", "title", "severity", "status", "scope", "projects", "tags",
          "origin", "approved_by", "created", "updated", "supersedes", "superseded_by"]
SECTIONS = ["## Do not", "## Do instead", "## Why", "## How it is checked"]
DIRS = {"hard": "HR", "soft": "SR"}
errors = []


def error(where, msg):
    errors.append("%s: %s" % (where, msg))


def read(path):
    text = io.open(path, encoding="utf-8").read()
    m = re.match(r"^---\\n(.*?)\\n---\\n(.*)$", text, re.S)
    if not m:
        return None, None
    front = {}
    for line in m.group(1).split("\\n"):
        if ":" in line and not line.startswith("  "):
            k, v = line.split(":", 1)
            front[k.strip()] = v.strip()
    return front, m.group(2)


def main():
    seen, total = {}, 0
    for sev, prefix in DIRS.items():
        d = os.path.join(RULES, sev)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md") or name.startswith("_"):
                continue
            total += 1
            path = os.path.join(d, name)
            where = "rules/%s/%s" % (sev, name)
            if not FILENAME.match(name):
                error(where, "invalid filename (expected HR-NNNN-slug.md in rules/hard/, "
                             "or SR-NNNN-slug.md in rules/soft/)")
            front, body = read(path)
            if front is None:
                error(where, "no frontmatter")
                continue
            for f in FIELDS:
                if f not in front:
                    error(where, "missing field '%s'" % f)
            rid = front.get("id", "")
            if not name.startswith(rid):
                error(where, "the filename does not start with the id '%s'" % rid)
            if not rid.startswith(prefix):
                error(where, "id prefix does not match rules/%s/ (expected '%s')" % (sev, prefix))
            if rid.endswith("0000"):
                error(where, "0000 is reserved for the template")
            if rid in seen:
                error(where, "duplicate id '%s', already used by %s" % (rid, seen[rid]))
            seen[rid] = where
            if front.get("status") == "in force" and front.get("approved_by", "[]") in ("[]", ""):
                error(where, "status is 'in force' but approved_by is empty")
            if front.get("status") == "deprecated" and front.get("superseded_by", "null") == "null":
                error(where, "status is 'deprecated' but superseded_by is null")
            for s in SECTIONS:
                if body and s not in body:
                    error(where, "missing section '%s'" % s)

    for e in errors:
        print("x %s" % e)
    if errors:
        print("\\nx %d error(s) across %d rule(s)." % (len(errors), total))
        return 1
    if total == 0:
        print("OK  0 rules.")
        print("    The catalog is empty, which is the expected starting state. See README.md.")
    else:
        print("OK  %d rule(s) valid." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

CATALOG_GENERATE = '''#!/usr/bin/env python3
"""Rebuild catalog.json from the rule files. Do not edit catalog.json by hand."""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "rules")
OUT = os.path.join(ROOT, "catalog.json")
LIST = ("scope", "projects", "tags", "origin", "approved_by", "supersedes")


def parse(path):
    text = io.open(path, encoding="utf-8").read()
    m = re.match(r"^---\\n(.*?)\\n---", text, re.S)
    if not m:
        return None
    front, key = {}, None
    for line in m.group(1).split("\\n"):
        if line.startswith("  - ") and key:
            front.setdefault(key, [])
            front[key].append(line[4:].strip())
        elif ":" in line:
            k, v = line.split(":", 1)
            key, v = k.strip(), v.strip()
            if v.startswith("[") and v.endswith("]"):
                inner = v[1:-1].strip()
                front[key] = [x.strip() for x in inner.split(",") if x.strip()]
            elif v == "":
                front[key] = []
            elif v == "null":
                front[key] = None
            else:
                front[key] = v
    for f in LIST:
        if f in front and not isinstance(front[f], list):
            front[f] = [front[f]]
    return front


def main():
    rules = []
    for sev in ("hard", "soft"):
        d = os.path.join(RULES, sev)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".md") or name.startswith("_"):
                continue
            front = parse(os.path.join(d, name))
            if front and not str(front.get("id", "")).endswith("0000"):
                front["path"] = "rules/%s/%s" % (sev, name)
                rules.append(front)

    totals = {"hard": {"in force": 0, "candidate": 0, "deprecated": 0},
              "soft": {"in force": 0, "candidate": 0, "deprecated": 0}}
    for r in rules:
        sev = r.get("severity", "soft")
        st = r.get("status", "candidate")
        if sev in totals and st in totals[sev]:
            totals[sev][st] += 1

    payload = {"version": 1, "totals": totals, "rules": rules}
    new = json.dumps(payload, indent=2, ensure_ascii=False) + "\\n"
    old = io.open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    if new == old:
        print("OK  catalog.json already up to date")
    else:
        io.open(OUT, "w", encoding="utf-8").write(new)
        print("OK  catalog.json rebuilt (%d rules)" % len(rules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

CATALOG_FILES = {
    "README.md": CATALOG_README,
    "GOVERNANCE.md": CATALOG_GOVERNANCE,
    "CONTRIBUTING.md": CATALOG_CONTRIBUTING,
    "calibration/false-positives.md": CATALOG_FALSE_POSITIVES,
    "rules/_TEMPLATE.md": CATALOG_RULE_TEMPLATE,
    "bin/validate.py": CATALOG_VALIDATE,
    "bin/generate_catalog.py": CATALOG_GENERATE,
    "catalog.json": json.dumps(
        {"version": 1,
         "totals": {"hard": {"in force": 0, "candidate": 0, "deprecated": 0},
                    "soft": {"in force": 0, "candidate": 0, "deprecated": 0}},
         "rules": []}, indent=2) + "\n",
    ".gitignore": "__pycache__/\n.DS_Store\n",
    "rules/hard/.gitkeep": "",
    "rules/soft/.gitkeep": "",
}


def scaffold_catalog(target, quiet=False):
    if os.path.exists(target) and os.listdir(target):
        print("x %s exists and is not empty. Refusing to write over it." % target)
        return 1
    for rel, content in CATALOG_FILES.items():
        path = os.path.join(target, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="utf-8").write(content)
        if rel.startswith("bin/"):
            os.chmod(path, 0o755)
    if quiet:
        return 0
    print("OK  standards catalog scaffolded at %s" % target)
    print()
    print("    %d files. Next:" % len(CATALOG_FILES))
    print("      cd %s" % target)
    print("      git init && git add -A && git commit -m 'Standards catalog, empty by design'")
    print("      python3 bin/validate.py")
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
}

SDLC_README = """# {org} SDLC

How {org} works with an AI assistant across the software life cycle: product, building,
operations, security and leadership. Built on [GATE](https://github.com/javierdres/gate-framework):
the assistant prepares, people decide.

To start, see [ONBOARDING.md](ONBOARDING.md). What is being built now is in [PLAN.md](PLAN.md),
and who approves what is in [GOVERNANCE.md](GOVERNANCE.md).
"""

SDLC_ONBOARDING = """# Onboarding

1. Create a working folder, for example `~/Projects/{org}`, and clone this repository inside it,
   next to the repositories of your products.
2. Open your assistant inside this repository the first time and say hello. `onboard` takes it
   from there: requirements, installation, profile and access, one step at a time.
3. From then on, open the assistant in the working folder, not inside this repository.

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

SDLC_SCOPES = """# Scopes

Every rule declares one scope in its `scope` field. A rule is born in the scope where it was
learned and becomes cross-cutting once it is shown to apply in a second place.

| Scope | Custodian (role) |
| --- | --- |
| cross-cutting | Every custodian |
| product | Custodian of product |
| security | Custodian of security |
| operations | Custodian of operations |
"""


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
    kit = os.path.join(HERE, "kit")
    written = 0

    for base, _, files in os.walk(kit):
        for f in files:
            src = os.path.join(base, f)
            dst = os.path.join(target, os.path.relpath(src, kit))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            io.open(dst, "wb").write(io.open(src, "rb").read())
            os.chmod(dst, os.stat(src).st_mode)
            written += 1

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
    reference = {
        "gate-reference/GATE.md": "GATE.md",
        "gate-reference/BUILDING.md": "BUILDING.md",
        "gate-reference/BUILDING.es.md": "BUILDING.es.md",
    }
    for name in sorted(os.listdir(os.path.join(HERE, "skills"))):
        contract = os.path.join("skills", name, "SKILL.md")
        if os.path.exists(os.path.join(HERE, contract)):
            reference["gate-reference/contracts/%s.md" % name] = contract
    for dst, src in reference.items():
        path = os.path.join(target, dst)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "wb").write(io.open(os.path.join(HERE, src), "rb").read())
        written += 1
    io.open(os.path.join(target, "gate-reference", "README.md"), "w", encoding="utf-8").write(
        "# GATE reference\n\nA copy of GATE at commit `%s`, the version this SDLC was "
        "scaffolded from: the framework, the build guide and the skill contracts. Read only; "
        "moving to a newer GATE replaces this folder and updates `GATE.md` at the root.\n" % version)
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

    scaffold_catalog(os.path.join(target, "catalog"), quiet=True)
    io.open(os.path.join(target, "catalog", "scopes.md"), "w", encoding="utf-8").write(SDLC_SCOPES)
    written += len(CATALOG_FILES) + 1

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
