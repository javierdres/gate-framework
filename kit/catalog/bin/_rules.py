# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Shared reading of the catalog, so the validator, the generator and the other scripts never
disagree.

The frontmatter of a rule is a small, strict subset of YAML: `key: value`, `key: [a, b]`, and
lists written one `  - item` per line under an empty `key:`. Quotes around a value are removed.

Two layouts are accepted under rules/, never mixed in one catalog:

- by severity: rules/hard/HR-NNNN-*.md, rules/soft/SR-NNNN-*.md, rules/recommended/RC-NNNN-*.md
- by scope:    rules/<scope>/<PREFIX>-NNNN-*.md and rules/groups/<group>/<PREFIX>-NNNN-*.md,
               with each prefix declared in scopes.md and a false-positives.md beside the rules
"""
import datetime
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "rules")
SEEDS = os.path.join(ROOT, "seeds")
SCOPES_FILE = os.path.join(ROOT, "scopes.md")
NOT_ADOPTED_FILE = os.path.join(ROOT, "calibration", "not-adopted.md")

SEVERITY_DIRS = {"hard": "HR", "soft": "SR", "recommended": "RC"}
DIRS = SEVERITY_DIRS  # the name the first version of these scripts used
SEVERITIES = tuple(SEVERITY_DIRS)
STATUSES = ("candidate", "in force", "deprecated")
VERIFICATIONS = ("auto", "auto-backlog", "manual")
DETECTED_BY = ("pipeline", "self-review", "review")
LISTS = ("scope", "projects", "tags", "origin", "approved_by", "supersedes", "applies_when")
NOT_RULES = ("false-positives.md", "README.md")
ID = re.compile(r"^[A-Z][A-Z0-9]{0,7}-\d{4}$")
CONDITION = re.compile(r"^([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*)\s*(!=|=|~)\s*([^\s,]+)$")


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def parse_text(text):
    """Return (front, body) from a rule's text, or (None, None) when there is no frontmatter."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, None
    front, key = {}, None
    for line in m.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s*(.*)$", line)
        if item and key:
            if not isinstance(front.get(key), list):
                front[key] = []
            value = unquote(item.group(1))
            if value:
                front[key].append(value)
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            key, v = k.strip(), v.strip()
            if v.startswith("[") and v.endswith("]"):
                front[key] = [unquote(x) for x in v[1:-1].split(",") if unquote(x)]
            elif v == "":
                front[key] = []
            elif v in ("null", "~"):
                front[key] = None
            else:
                front[key] = unquote(v)
    for f in LISTS:
        if f in front and front[f] is not None and not isinstance(front[f], list):
            front[f] = [front[f]]
    return front, m.group(2)


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def parse(path):
    """Return (front, body) from a rule file, or (None, None) when there is no frontmatter."""
    return parse_text(read(path))


# ───────────────────────────── scopes.md ─────────────────────────────────────

DUPLICATE_SCOPES = set()


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_scopes(path=None):
    """Every scope and group declared in scopes.md, as {key: {...}}. None if there is no file.

    Any Markdown table whose first column holds a lowercase key counts. Columns are found by
    their header, so a table without a Prefix or Version column is still read: `Prefix` is the
    id prefix of the scope's folder, `Version` the scope's standard version, and in a table whose
    first header is `Group`, `Remote path prefix` says which repositories the group covers.
    """
    path = path or SCOPES_FILE
    if not os.path.exists(path):
        return None
    scopes, header = {}, None
    for line in read(path).split("\n"):
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if header is None:
            header = [c.lower().strip("`* ") for c in cells]
            continue
        if all(re.match(r"^:?-+:?$", c) for c in cells if c):
            continue
        key = cells[0].strip("` ")
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", key) or key in ("scope", "group"):
            continue

        def col(name):
            for i, h in enumerate(header):
                if h.startswith(name) and i < len(cells):
                    return cells[i].strip("` ")
            return ""

        is_group = header[0] == "group"
        prefix, version = col("prefix"), col("version")
        if key in scopes:
            DUPLICATE_SCOPES.add(key)
        scopes[key] = {
            "kind": "group" if is_group else "scope",
            "prefix": prefix if re.match(r"^[A-Z][A-Z0-9]{0,7}$", prefix) else "",
            "version": version if re.match(r"^\d+\.\d+\.\d+$", version) else "",
            "remote": col("remote").strip("/") if is_group else "",
            "custodian": col("custodian"),
        }
    return scopes or None


def allowed_scopes():
    """The scope and group keys listed in scopes.md. None if there is no file."""
    scopes = read_scopes()
    return set(scopes) if scopes else None


# ───────────────────────────── rule files ────────────────────────────────────

def rule_folders():
    """Yield (folder relative to rules/, kind) for every folder that may hold rules.

    kind is 'severity' for hard, soft and recommended, and 'scope' for anything else,
    groups/<group> included.
    """
    if not os.path.isdir(RULES):
        return
    for d in sorted(os.listdir(RULES)):
        full = os.path.join(RULES, d)
        if not os.path.isdir(full) or d.startswith((".", "_")):
            continue
        if d in SEVERITY_DIRS:
            yield d, "severity"
        elif d == "groups":
            for g in sorted(os.listdir(full)):
                if os.path.isdir(os.path.join(full, g)) and not g.startswith((".", "_")):
                    yield "groups/" + g, "scope"
        else:
            yield d, "scope"


def folder_key(folder):
    """The scope or group key a folder stands for: 'security' -> 'security', 'groups/x' -> 'x'."""
    return folder.split("/", 1)[1] if folder.startswith("groups/") else folder


def rule_files():
    """Yield (folder, filename, path) for every rule, skipping templates and calibration files."""
    for folder, _ in rule_folders():
        d = os.path.join(RULES, folder)
        for name in sorted(os.listdir(d)):
            if name.endswith(".md") and not name.startswith("_") and name not in NOT_RULES:
                yield folder, name, os.path.join(d, name)


def derogated_ids():
    """Ids listed in the derogated table of calibration/not-adopted.md."""
    if not os.path.exists(NOT_ADOPTED_FILE):
        return set()
    text = read(NOT_ADOPTED_FILE)
    part = text.split("## Derogated", 1)
    if len(part) < 2:
        return set()
    ids = set()
    for line in part[1].split("\n"):
        if line.lstrip().startswith("|"):
            first = _cells(line)[0].strip("` ")
            if ID.match(first):
                ids.add(first)
    return ids


def version_is_draft(version):
    return bool(version) and version.startswith("0.")


def reported_as(rule, scopes):
    """How review reports a rule: blocking, required, suggestion or ignored.

    A rule blocks only when it is hard, in force, and none of its scopes is a draft standard
    (version 0.x). A candidate is always a suggestion.
    """
    status, sev = rule.get("status"), rule.get("severity")
    if status == "deprecated":
        return "ignored"
    if status != "in force" or sev == "recommended":
        return "suggestion"
    if sev == "soft":
        return "required"
    draft = any(version_is_draft((scopes or {}).get(s, {}).get("version", ""))
                for s in rule.get("scope") or [])
    return "required" if draft else "blocking"


def load_rules():
    """Every rule as a dict, with its path, its severity and how review reports it."""
    scopes = read_scopes() or {}
    rules = []
    for folder, name, path in rule_files():
        front, _ = parse(path)
        if not front or str(front.get("id", "")).endswith("0000"):
            continue
        if folder in SEVERITY_DIRS:
            front["severity"] = folder
        front["path"] = "rules/%s/%s" % (folder, name)
        front["waivable"] = str(front.get("waivable", "true")).lower() != "false"
        front["reported_as"] = reported_as(front, scopes)
        rules.append(front)
    return rules


# ───────────────────────────── project profile ───────────────────────────────

def _strip_comment(line):
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [unquote(x) for x in v[1:-1].split(",") if unquote(x)]
    if v.startswith("{") and v.endswith("}"):
        d = {}
        for part in v[1:-1].split(","):
            if ":" in part:
                k, val = part.split(":", 1)
                d[k.strip()] = _scalar(val)
        return d
    if v in ("null", "~", ""):
        return None
    return unquote(v)


_KEY = re.compile(r"^([A-Za-z0-9_.-]+):(?:\s+(.*)|)$")


def _block(lines, i, indent):
    """Parse the block of `lines` starting at i whose items sit at `indent`."""
    if i < len(lines) and lines[i][1].startswith("- "):
        out = []
        while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
            item = lines[i][1][2:].strip()
            j = i + 1
            while j < len(lines) and lines[j][0] > indent:
                j += 1
            if _KEY.match(item):
                value, _ = _block([(indent + 2, item)] + lines[i + 1:j], 0, indent + 2)
                out.append(value)
            else:
                out.append(_scalar(item))
            i = j
        return out, i
    out = {}
    while i < len(lines) and lines[i][0] == indent:
        m = _KEY.match(lines[i][1])
        i += 1
        if not m:
            continue
        key, rest = m.group(1), (m.group(2) or "").strip()
        if rest:
            out[key] = _scalar(rest)
        elif i < len(lines) and lines[i][0] > indent:
            out[key], i = _block(lines, i, lines[i][0])
        elif i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
            out[key], i = _block(lines, i, indent)
        else:
            out[key] = None
    return out, i


def parse_yaml(text):
    """A small YAML reader for the project profile: nested mappings by indentation, lists of
    scalars or of mappings, inline [lists] and {maps}. Enough for the profile, no more."""
    lines = []
    for raw in text.split("\n"):
        line = _strip_comment(raw)
        if line.strip():
            lines.append((len(line) - len(line.lstrip(" ")), line.strip()))
    if not lines:
        return {}
    value, _ = _block(lines, 0, lines[0][0])
    return value if isinstance(value, dict) else {}


def read_profile(path):
    """The project profile: the first ```yaml block under a '## Project profile' heading.

    Returns None when the file has no such block."""
    text = read(path)
    m = re.search(r"^##\s+Project profile\s*$(.*?)^```ya?ml\s*$(.*?)^```", text, re.S | re.M)
    if not m or re.search(r"^## ", m.group(1), re.M):
        return None
    return parse_yaml(m.group(2))


def lookup(profile, path):
    node = profile
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None, False
        node = node[part]
    return node, True


def evaluate(condition, profile):
    """True, False, or None when the profile does not declare the key the condition reads.

    `key = value` holds when the key is exactly that value, `key != value` when it is not it
    and does not contain it, and `key ~ value` when it is that value or a list containing it.
    """
    m = CONDITION.match(condition.strip())
    if not m:
        return None
    path, op, expected = m.groups()
    value, found = lookup(profile, path)
    if not found or value is None:
        return None
    values = [str(v) for v in value] if isinstance(value, list) else [str(value)]
    if op == "=":
        return values == [expected]
    if op == "!=":
        return expected not in values
    return expected in values


def remote_path(remote):
    """'git@host:group/sub/repo.git' or 'https://host/group/sub/repo' -> 'group/sub/repo'."""
    r = re.sub(r"\.git$", "", remote.strip())
    m = re.match(r"^[\w.+-]+://[^/]+/(.*)$", r) or re.match(r"^[^@/]+@[^:]+:(.*)$", r)
    return (m.group(1) if m else r).strip("/")


def groups_for(remote, scopes):
    """Every group whose remote path prefix contains the repository, most specific first.

    The first one is the repository's group, by longest prefix; its parents keep applying."""
    path = remote_path(remote)
    found = []
    for key, s in (scopes or {}).items():
        prefix = s.get("remote", "")
        if s.get("kind") == "group" and prefix and (path == prefix or path.startswith(prefix + "/")):
            found.append((len(prefix), key))
    return [k for _, k in sorted(found, reverse=True)]


def expired(value, today=None):
    """True once an expiry written YYYY-MM or YYYY-MM-DD is past; None if it is not a date."""
    today = today or datetime.date.today()
    s = str(value or "")
    try:
        if re.match(r"^\d{4}-\d{2}$", s):
            y, m = map(int, s.split("-"))
            return (today.year, today.month) > (y, m)
        return today > datetime.date.fromisoformat(s)
    except ValueError:
        return None
