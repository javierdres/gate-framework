# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Shared reading of rule files, so the validator and the generator never disagree.

The frontmatter is a small, strict subset of YAML: `key: value`, `key: [a, b]`, and lists
written one `  - item` per line under an empty `key:`. Quotes around a value are removed.
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(ROOT, "rules")
SCOPES_FILE = os.path.join(ROOT, "scopes.md")
DIRS = {"hard": "HR", "soft": "SR"}
LISTS = ("scope", "projects", "tags", "origin", "approved_by", "supersedes")


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def parse(path):
    """Return (front, body), or (None, None) when there is no frontmatter."""
    text = io.open(path, encoding="utf-8").read()
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


def rule_files():
    """Yield (severity directory, filename, path) for every rule, skipping the template."""
    for sev in DIRS:
        d = os.path.join(RULES, sev)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".md") and not name.startswith("_"):
                yield sev, name, os.path.join(d, name)


def allowed_scopes():
    """The scopes listed in scopes.md, first column of its table. None if there is no file."""
    if not os.path.exists(SCOPES_FILE):
        return None
    scopes = set()
    for line in io.open(SCOPES_FILE, encoding="utf-8"):
        m = re.match(r"^\|\s*`?([a-z0-9][a-z0-9-]*)`?\s*\|", line)
        if m and m.group(1) not in ("scope",):
            scopes.add(m.group(1))
    return scopes or None
