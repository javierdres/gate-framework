#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Which rules apply to one project, and how review reports each one.

    python3 bin/applicable.py --profile <project>/AGENTS.md [--remote <url>] [--project <id>] [--json]

It reads the project profile (the YAML block under '## Project profile' in the project's
instructions file, see project-profile.md), resolves the project's groups from its remote by
longest path prefix, and filters the rules by status, scope, projects and applies_when. It also
checks the profile's exceptions: each names a rule that exists and admits one, and none has
expired.

A rule whose applies_when reads a key the profile does not declare is listed as undetermined,
not dropped: the profile is incomplete, and saying so is the point.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rules import evaluate, expired, groups_for, load_rules, read_profile, read_scopes  # noqa: E402

ALWAYS = ("cross-cutting",)


def git_remote(directory):
    try:
        out = subprocess.run(["git", "-C", directory, "remote", "get-url", "origin"],
                             capture_output=True, text=True)
        return out.stdout.strip() if out.returncode == 0 else ""
    except OSError:
        return ""


def resolve(rules, scopes, profile, remote, project):
    groups = groups_for(remote, scopes) if remote else []
    group_keys = {k for k, s in (scopes or {}).items() if s.get("kind") == "group"}
    declared = profile.get("scopes") if isinstance(profile.get("scopes"), list) else None
    applies, skipped, undetermined = [], [], []
    for r in rules:
        if r.get("status") == "deprecated":
            continue
        rscopes = set(r.get("scope") or [])
        if rscopes & group_keys:
            in_scope = bool(rscopes & set(groups))
        elif declared is None:
            in_scope = True
        else:
            in_scope = bool(rscopes & (set(declared) | set(ALWAYS)))
        projects = set(r.get("projects") or [])
        in_project = "cross-cutting" in projects or (project and project in projects)
        if not (in_scope and in_project):
            skipped.append((r, "scope or project"))
            continue
        results = [(c, evaluate(c, profile)) for c in r.get("applies_when") or []]
        if any(v is False for _, v in results):
            skipped.append((r, "applies_when: " + ", ".join(c for c, v in results if v is False)))
        elif any(v is None for _, v in results):
            undetermined.append((r, ", ".join(c for c, v in results if v is None)))
        else:
            applies.append(r)
    return groups, applies, skipped, undetermined


def check_exceptions(profile, rules, today=None):
    problems = []
    by_id = {r["id"]: r for r in rules}
    for e in profile.get("exceptions") or []:
        if not isinstance(e, dict):
            problems.append("an exception is not a mapping with rule, reason, authorised_by, ticket and expires")
            continue
        rid = e.get("rule")
        for f in ("rule", "reason", "authorised_by", "expires"):
            if not e.get(f):
                problems.append("exception for %s has no '%s'" % (rid or "?", f))
        if rid and rid not in by_id:
            problems.append("exception for %s: no such rule in the catalog" % rid)
        elif rid and not by_id[rid]["waivable"]:
            problems.append("exception for %s: that rule never admits one" % rid)
        if e.get("expires") and expired(e["expires"], today) is None:
            problems.append("exception for %s: expires '%s' is not YYYY-MM or YYYY-MM-DD" % (rid, e["expires"]))
        elif e.get("expires") and expired(e["expires"], today):
            problems.append("exception for %s expired on %s" % (rid, e["expires"]))
    return problems


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--profile", required=True, help="the project's instructions file with its profile")
    p.add_argument("--remote", help="the project's remote (default: git remote of the profile's folder)")
    p.add_argument("--project", help="the project id (default: project.id in the profile)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    profile = read_profile(args.profile)
    if profile is None:
        print("x %s has no '## Project profile' with a yaml block. See project-profile.md." % args.profile)
        return 1
    remote = args.remote if args.remote is not None else git_remote(os.path.dirname(os.path.abspath(args.profile)))
    project = args.project
    if not project and isinstance(profile.get("project"), dict):
        project = profile["project"].get("id")
    scopes = read_scopes() or {}
    rules = load_rules()
    groups, applies, skipped, undetermined = resolve(rules, scopes, profile, remote, project)
    problems = check_exceptions(profile, rules)

    if args.json:
        print(json.dumps({
            "groups": groups,
            "applies": [{"id": r["id"], "title": r["title"], "reported_as": r["reported_as"]} for r in applies],
            "undetermined": [{"id": r["id"], "missing": why} for r, why in undetermined],
            "problems": problems,
        }, indent=2, ensure_ascii=False))
    else:
        if groups:
            print("Group: %s%s" % (groups[0], " (and %s)" % ", ".join(groups[1:]) if groups[1:] else ""))
        print("%d rule(s) apply:" % len(applies))
        for r in applies:
            print("  %-10s %-10s %s" % (r["id"], r["reported_as"], r["title"]))
        if undetermined:
            print("\n%d rule(s) undetermined, the profile does not declare what they read:" % len(undetermined))
            for r, why in undetermined:
                print("  %-10s %s" % (r["id"], why))
        for msg in problems:
            print("x %s" % msg)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
