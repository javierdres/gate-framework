#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Validate the rule files: naming, ids, frontmatter, values and required sections.

    python3 bin/validate.py

It rejects what the format forbids and accepts what the format allows; tests in tests/ cover
both directions.
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rules import DIRS, allowed_scopes, parse, rule_files  # noqa: E402

FILENAME = re.compile(r"^(HR|SR)-(\d{4})-[a-z0-9]+(-[a-z0-9]+)*\.md$")
ID = re.compile(r"^(HR|SR)-\d{4}$")
FIELDS = ["id", "title", "severity", "status", "scope", "projects", "tags", "origin",
          "approved_by", "created", "updated", "supersedes", "superseded_by"]
SECTIONS = ["## Do not", "## Do instead", "## Why", "## How it is checked"]
STATUSES = ("candidate", "in force", "deprecated")


def date(value):
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def check(sev, name, path, seen, scopes, errors):
    where = "rules/%s/%s" % (sev, name)

    def error(msg):
        errors.append("%s: %s" % (where, msg))

    if not FILENAME.match(name):
        error("invalid filename (expected HR-NNNN-slug.md in rules/hard/, or SR-NNNN-slug.md in rules/soft/)")
    front, body = parse(path)
    if front is None:
        error("no frontmatter")
        return
    for f in FIELDS:
        if f not in front:
            error("missing field '%s'" % f)

    rid = str(front.get("id") or "")
    if not ID.match(rid):
        error("invalid id '%s'" % rid)
    if not name.startswith(rid + "-"):
        error("the filename does not start with the id '%s'" % rid)
    if not rid.startswith(DIRS[sev]):
        error("id prefix does not match rules/%s/ (expected '%s')" % (sev, DIRS[sev]))
    if rid.endswith("0000"):
        error("0000 is reserved for the template")
    if rid in seen:
        error("duplicate id '%s', already used by %s" % (rid, seen[rid]))
    seen[rid] = where

    if front.get("severity") != sev:
        error("severity '%s' does not match its directory rules/%s/" % (front.get("severity"), sev))
    status = front.get("status")
    if status not in STATUSES:
        error("status '%s' is not one of: %s" % (status, ", ".join(STATUSES)))
    if not str(front.get("title") or "").strip():
        error("empty title")

    for f in ("scope", "projects", "tags", "origin", "approved_by", "supersedes"):
        if f in front and not isinstance(front[f], list):
            error("'%s' must be a list" % f)
    if not front.get("scope"):
        error("scope is empty")
    elif scopes is not None:
        for s in front["scope"]:
            if s not in scopes:
                error("scope '%s' is not listed in scopes.md" % s)
    if not front.get("projects"):
        error("projects is empty (use cross-cutting for every project)")
    if not front.get("origin"):
        error("origin is empty: every rule shows where it came from")
    if status == "in force" and not front.get("approved_by"):
        error("status is 'in force' but approved_by is empty")
    for other in front.get("supersedes") or []:
        if not ID.match(other):
            error("supersedes '%s' is not a rule id" % other)
    superseded_by = front.get("superseded_by")
    if superseded_by not in (None, "") and not ID.match(str(superseded_by)):
        error("superseded_by '%s' is not a rule id" % superseded_by)
    if status == "deprecated" and not superseded_by:
        error("status is 'deprecated' but superseded_by is empty")

    created, updated = date(front.get("created")), date(front.get("updated"))
    if "created" in front and not created:
        error("created '%s' is not a date (YYYY-MM-DD)" % front.get("created"))
    if "updated" in front and not updated:
        error("updated '%s' is not a date (YYYY-MM-DD)" % front.get("updated"))
    if created and updated and updated < created:
        error("updated is earlier than created")

    for s in SECTIONS:
        if body is not None and s not in body:
            error("missing section '%s'" % s)
    if sev == "hard" and body is not None and "## Exceptions" not in body:
        error("a hard rule needs '## Exceptions', even if it only says there are none")


def main():
    errors, seen, total = [], {}, 0
    scopes = allowed_scopes()
    for sev, name, path in rule_files():
        total += 1
        check(sev, name, path, seen, scopes, errors)
    for e in errors:
        print("x %s" % e)
    if errors:
        print("\nx %d error(s) across %d rule(s)." % (len(errors), total))
        return 1
    if total == 0:
        print("OK  0 rules.")
        print("    The catalog is empty, which is the expected starting state. See README.md.")
    else:
        print("OK  %d rule(s) valid." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
