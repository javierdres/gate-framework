#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Validate the rule files: naming, ids, frontmatter, values, sections and the links between
rules.

    python3 bin/validate.py

It rejects what the format forbids and accepts what the format allows; tests in tests/ cover
both directions. Seeds in seeds/ are not rules and are not read here: `adopt_seed.py --check`
validates them.
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rules import (CONDITION, DETECTED_BY, DUPLICATE_SCOPES, ID, SEVERITIES,  # noqa: E402
                    SEVERITY_DIRS, STATUSES, VERIFICATIONS, derogated_ids, folder_key, parse,
                    read_scopes, rule_files, rule_folders)

SLUG = r"-[a-z0-9]+(-[a-z0-9]+)*\.md$"
FIELDS = ["id", "title", "severity", "status", "scope", "projects", "tags", "origin",
          "approved_by", "created", "updated", "supersedes", "superseded_by"]
SECTIONS = ["## Do not", "## Do instead", "## Why", "## How it is checked"]
REPEALED = "repealed"


def date(value):
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def check(folder, name, path, seen, scopes, errors, parsed):
    where = "rules/%s/%s" % (folder, name)

    def error(msg):
        errors.append("%s: %s" % (where, msg))

    by_severity = folder in SEVERITY_DIRS
    if by_severity:
        prefix = SEVERITY_DIRS[folder]
    else:
        key = folder_key(folder)
        declared = (scopes or {}).get(key)
        if declared is None:
            error("rules/%s/ is neither a severity folder nor a scope or group listed in scopes.md" % folder)
            return
        if folder.startswith("groups/") and declared["kind"] != "group":
            error("'%s' sits under rules/groups/ but scopes.md lists it as a scope, not a group" % key)
        if not folder.startswith("groups/") and declared["kind"] == "group":
            error("'%s' is a group in scopes.md: its rules go in rules/groups/%s/" % (key, key))
        prefix = declared["prefix"]
        if not prefix:
            error("scope '%s' has no Prefix in scopes.md, so its rules cannot be named" % key)
            return

    if not re.match(r"^%s-\d{4}%s" % (prefix, SLUG), name):
        if by_severity:
            error("invalid filename (expected HR-NNNN-slug.md in rules/hard/, SR-NNNN-slug.md in "
                  "rules/soft/ or RC-NNNN-slug.md in rules/recommended/)")
        else:
            error("invalid filename (expected %s-NNNN-slug.md in rules/%s/)" % (prefix, folder))
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
    if not rid.startswith(prefix + "-"):
        error("id prefix does not match rules/%s/ (expected '%s')" % (folder, prefix))
    if rid.endswith("0000"):
        error("0000 is reserved for the template")
    if rid in seen:
        error("duplicate id '%s', already used by %s" % (rid, seen[rid]))
    seen[rid] = where
    parsed[rid] = (where, front, body or "")

    sev = front.get("severity")
    if by_severity and sev != folder:
        error("severity '%s' does not match its directory rules/%s/" % (sev, folder))
    elif sev not in SEVERITIES:
        error("severity '%s' is not one of: %s" % (sev, ", ".join(SEVERITIES)))
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
    else:
        if scopes is not None:
            for s in front["scope"]:
                if s not in scopes:
                    error("scope '%s' is not listed in scopes.md" % s)
        if not by_severity and folder_key(folder) not in front["scope"]:
            error("a rule in rules/%s/ lists '%s' in its scope" % (folder, folder_key(folder)))
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
    if superseded_by not in (None, "", REPEALED) and not ID.match(str(superseded_by)):
        error("superseded_by '%s' is neither a rule id nor '%s'" % (superseded_by, REPEALED))
    if status == "deprecated" and not superseded_by:
        error("status is 'deprecated' but superseded_by is empty (a rule id, or '%s')" % REPEALED)
    if superseded_by and status != "deprecated":
        error("superseded_by is set but the status is '%s', not 'deprecated'" % status)

    # optional fields: validated when present
    verification, detected_by = front.get("verification"), front.get("detected_by")
    if verification is not None and verification not in VERIFICATIONS:
        error("verification '%s' is not one of: %s" % (verification, ", ".join(VERIFICATIONS)))
    if detected_by is not None and detected_by not in DETECTED_BY:
        error("detected_by '%s' is not one of: %s" % (detected_by, ", ".join(DETECTED_BY)))
    if detected_by == "pipeline" and verification not in (None, "auto"):
        error("detected_by is 'pipeline' but verification is '%s', not 'auto'" % verification)
    if sev == "hard" and verification == "manual" and "business-defect" not in (front.get("tags") or []):
        error("a hard rule with a manual check blocks only for a business defect no tool detects: "
              "automate its check, tag it business-defect, or make it soft")
    for cond in front.get("applies_when") or []:
        if not CONDITION.match(cond):
            error("applies_when '%s' is not 'key = value', 'key != value' or 'key ~ value'" % cond)
    if "waivable" in front and str(front["waivable"]).lower() not in ("true", "false"):
        error("waivable '%s' is not true or false" % front["waivable"])
    if front.get("seeded_from") and not re.match(r"^SEED-[A-Z]+-\d{2}$", str(front["seeded_from"])):
        error("seeded_from '%s' is not a seed id (SEED-SCOPE-NN)" % front["seeded_from"])

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


def check_links(parsed, prefixes, errors):
    """supersedes and superseded_by point at real rules and agree, and every id a rule cites
    exists."""
    derogated = derogated_ids()
    for rid, (where, front, body) in sorted(parsed.items()):
        for other in front.get("supersedes") or []:
            if ID.match(other) and other not in parsed:
                errors.append("%s: supersedes '%s', which is not a rule in this catalog" % (where, other))
            elif other in parsed and parsed[other][1].get("superseded_by") != rid:
                errors.append("%s: supersedes '%s', but that rule's superseded_by is '%s'"
                              % (where, other, parsed[other][1].get("superseded_by")))
        succ = front.get("superseded_by")
        if succ == REPEALED:
            if rid not in derogated:
                errors.append("%s: repealed with no successor, but it is missing from the derogated "
                              "table in calibration/not-adopted.md" % where)
        elif succ and ID.match(str(succ)):
            if succ not in parsed:
                errors.append("%s: superseded_by '%s', which is not a rule in this catalog" % (where, succ))
            elif rid not in (parsed[succ][1].get("supersedes") or []):
                errors.append("%s: superseded_by '%s', but that rule does not list '%s' in supersedes"
                              % (where, succ, rid))
        if prefixes:
            cited = re.findall(r"(?<![A-Z0-9-])((?:%s)-\d{4})(?![0-9])" % "|".join(sorted(prefixes)), body)
            for c in sorted(set(cited)):
                if c not in parsed and not c.endswith("0000"):
                    errors.append("%s: cites '%s', which is not a rule in this catalog" % (where, c))


def main():
    errors, seen, parsed, total = [], {}, {}, 0
    scopes = read_scopes()
    for key in sorted(DUPLICATE_SCOPES):
        errors.append("scopes.md: '%s' is listed more than once" % key)
    prefixes_seen = {}
    for key, s in sorted((scopes or {}).items()):
        if s["prefix"] and s["prefix"] in prefixes_seen:
            errors.append("scopes.md: '%s' and '%s' declare the same prefix %s" % (prefixes_seen[s["prefix"]], key, s["prefix"]))
        prefixes_seen.setdefault(s["prefix"], key)
    kind_of, used = dict(rule_folders()), set()
    for folder, name, path in rule_files():
        total += 1
        check(folder, name, path, seen, scopes, errors, parsed)
        front, _ = parse(path)
        if front and front.get("status") != "deprecated":
            used.add(kind_of[folder])
    if used == {"severity", "scope"}:
        errors.append("rules/: rules in force or candidate sit both in severity folders (hard, soft, "
                      "recommended) and in scope folders. Use one layout; see scopes.md")
    prefixes = set(SEVERITY_DIRS.values()) | {s["prefix"] for s in (scopes or {}).values() if s["prefix"]}
    check_links(parsed, prefixes, errors)

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
