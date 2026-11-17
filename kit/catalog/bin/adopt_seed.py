#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Adopt GATE seed rules into this catalog, as candidates with the organisation's own ids.

    python3 bin/adopt_seed.py --list
    python3 bin/adopt_seed.py SEED-SEC-01 SEED-BACK-02 [--scope backend] [--projects a,b] [--dry-run]
    python3 bin/adopt_seed.py --check

A seed is a rule GATE offers, born from a lesson another organisation paid for. Adopting one
copies it into rules/ as a candidate: the next free id of its folder, the lesson and the seed id
as its origin, approved_by empty. It blocks nothing until its custodian approves it, like any
other candidate. Seeds already adopted are skipped, so running it twice changes nothing.

The layout follows the catalog: rules/hard|soft|recommended/ by default, or rules/<scope>/ when
the catalog already keeps its rules by scope (or with --layout scope).
"""
import argparse
import datetime
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rules import (RULES, SEEDS, SEVERITY_DIRS, derogated_ids, parse,  # noqa: E402
                    parse_text, read_scopes, rule_files, rule_folders)

SEED_ID = re.compile(r"^SEED-[A-Z]+-\d{2}$")
SEED_FIELDS = ["seed_id", "kind", "lesson", "title", "severity", "scope", "projects", "tags",
               "verification", "detected_by"]
ORDER = ["id", "title", "severity", "status", "scope", "projects", "tags", "verification",
         "detected_by", "applies_when", "waivable", "origin", "approved_by", "created", "updated",
         "supersedes", "superseded_by", "seeded_from"]


def seed_files():
    """Yield (seed id, path) for every seed, in id order."""
    found = []
    if os.path.isdir(SEEDS):
        for base, _, files in os.walk(SEEDS):
            for name in files:
                m = re.match(r"^(SEED-[A-Z]+-\d{2})-[a-z0-9-]+\.md$", name)
                if m:
                    found.append((m.group(1), os.path.join(base, name)))
    return sorted(found)


def adopted():
    """{seed id: rule path} for every seed already in rules/."""
    out = {}
    for folder, name, path in rule_files():
        front, _ = parse(path)
        if front and front.get("seeded_from"):
            out[front["seeded_from"]] = "rules/%s/%s" % (folder, name)
    return out


def used_ids():
    ids = set(derogated_ids())
    for _, name, _ in rule_files():
        m = re.match(r"^([A-Z][A-Z0-9]*-\d{4})-", name)
        if m:
            ids.add(m.group(1))
    return ids


def next_id(prefix, taken):
    numbers = [int(i.split("-")[1]) for i in taken if i.startswith(prefix + "-")]
    return "%s-%04d" % (prefix, max(numbers + [0]) + 1)


def layout(requested):
    if requested:
        return requested
    for folder, kind in rule_folders():
        if kind == "scope":
            return "scope"
    return "severity"


def fmt(key, value):
    if isinstance(value, list):
        if key == "origin" or any(len(v) > 40 for v in value):
            return "%s:\n%s" % (key, "\n".join("  - %s" % v for v in value)) if value else "%s: []" % key
        return "%s: [%s]" % (key, ", ".join(value))
    if value is None:
        return "%s: null" % key
    return "%s: %s" % (key, value)


def check_seed(sid, path):
    """Problems with one seed file, as a list of messages."""
    problems = []
    front, body = parse(path)
    if front is None:
        return ["no frontmatter"]
    for f in SEED_FIELDS:
        if not front.get(f):
            problems.append("missing or empty field '%s'" % f)
    if front.get("seed_id") != sid:
        problems.append("seed_id '%s' does not match the filename" % front.get("seed_id"))
    if front.get("kind") not in ("lesson", "baseline"):
        problems.append("kind '%s' is not lesson or baseline" % front.get("kind"))
    if "id" in front or "origin" in front or "status" in front:
        problems.append("a seed carries no id, origin or status: adoption writes them")
    if not body or not body.lstrip().startswith("# %s · " % sid):
        problems.append("the body does not start with '# %s · <title>'" % sid)
    folder = os.path.basename(os.path.dirname(path))
    if front.get("scope") and folder not in front["scope"]:
        problems.append("it sits in seeds/%s/ but its scope is %s" % (folder, front["scope"]))
    return problems


def build(sid, path, target_scope, projects, today):
    front, body = parse(path)
    rule = {
        "title": front["title"],
        "severity": front["severity"],
        "status": "candidate",
        "scope": [target_scope],
        "projects": projects or front.get("projects") or ["cross-cutting"],
        "tags": front.get("tags") or [],
        "verification": front.get("verification"),
        "detected_by": front.get("detected_by"),
        "applies_when": front.get("applies_when") or [],
        "origin": [front["lesson"],
                   "Seeded from GATE %s (%s seed), adopted %s" % (sid, front["kind"], today)],
        "approved_by": [],
        "created": today,
        "updated": today,
        "supersedes": [],
        "superseded_by": None,
        "seeded_from": sid,
    }
    if "waivable" in front:
        rule["waivable"] = front["waivable"]
    if not rule["applies_when"]:
        del rule["applies_when"]
    history = "- %s · Adopted as a candidate from GATE seed %s. Awaits its custodian." % (today, sid)
    if "## History" in body:
        body = body.rstrip() + "\n" + history + "\n"
    else:
        body = body.rstrip() + "\n\n## History\n\n" + history + "\n"
    return rule, body


def write_rule(rule, body, rid, folder, slug, dry_run):
    rule = dict(rule, id=rid)
    body = re.sub(r"^\s*# SEED-[A-Z]+-\d{2} · ", "# %s · " % rid, body, count=1)
    front = "\n".join(fmt(k, rule[k]) for k in ORDER if k in rule)
    text = "---\n%s\n---\n\n%s" % (front, body.lstrip("\n"))
    rel = "rules/%s/%s-%s.md" % (folder, rid, slug)
    if parse_text(text)[0] is None:
        raise SystemExit("x could not write a readable rule for %s" % rid)
    if not dry_run:
        path = os.path.join(RULES, folder, "%s-%s.md" % (rid, slug))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="utf-8").write(text)
    return rel


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("seeds", nargs="*", help="seed ids to adopt, such as SEED-SEC-01")
    p.add_argument("--list", action="store_true", help="list the seeds and which are adopted")
    p.add_argument("--check", action="store_true", help="check that every seed is well formed")
    p.add_argument("--scope", help="the catalog scope to adopt into, when it differs from the seed's")
    p.add_argument("--projects", help="comma-separated project ids (default: the seed's, cross-cutting)")
    p.add_argument("--layout", choices=("severity", "scope"), help="force the layout of rules/")
    p.add_argument("--dry-run", action="store_true", help="say what would be written, write nothing")
    args = p.parse_args(argv)

    seeds = dict(seed_files())
    if args.check:
        bad = 0
        for sid, path in sorted(seeds.items()):
            for problem in check_seed(sid, path):
                print("x %s: %s" % (os.path.relpath(path, os.path.dirname(SEEDS)), problem))
                bad += 1
        if bad:
            return 1
        print("OK  %d seed(s) well formed." % len(seeds))
        return 0

    done = adopted()
    if args.list or not args.seeds:
        if not seeds:
            print("No seeds in seeds/.")
            return 0
        print("%-14s %-9s %-11s %s" % ("seed", "kind", "severity", "title"))
        for sid, path in sorted(seeds.items()):
            front, _ = parse(path)
            mark = "  (adopted as %s)" % done[sid] if sid in done else ""
            print("%-14s %-9s %-11s %s%s" % (sid, front.get("kind"), front.get("severity"),
                                             front.get("title"), mark))
        return 0

    scopes = read_scopes()
    today = datetime.date.today().isoformat()
    projects = [x.strip() for x in args.projects.split(",") if x.strip()] if args.projects else None
    mode = layout(args.layout)
    taken = used_ids()
    status = 0
    for sid in args.seeds:
        if not SEED_ID.match(sid) or sid not in seeds:
            print("x %s: no such seed. See: python3 bin/adopt_seed.py --list" % sid)
            status = 1
            continue
        if sid in done:
            print("–  %s already adopted as %s" % (sid, done[sid]))
            continue
        problems = check_seed(sid, seeds[sid])
        if problems:
            print("x %s: %s" % (sid, "; ".join(problems)))
            status = 1
            continue
        seed_front, _ = parse(seeds[sid])
        target = args.scope or seed_front["scope"][0]
        if scopes is not None and target not in scopes:
            print("x %s: scope '%s' is not in scopes.md. Add its row, or pass --scope with one "
                  "that is." % (sid, target))
            status = 1
            continue
        rule, body = build(sid, seeds[sid], target, projects, today)
        if mode == "severity":
            folder, prefix = rule["severity"], SEVERITY_DIRS[rule["severity"]]
        else:
            declared = (scopes or {}).get(target, {})
            prefix = declared.get("prefix")
            if not prefix:
                print("x %s: scope '%s' has no Prefix in scopes.md, so its rules cannot be "
                      "named." % (sid, target))
                status = 1
                continue
            folder = ("groups/" + target) if declared.get("kind") == "group" else target
        rid = next_id(prefix, taken)
        taken.add(rid)
        slug = re.sub(r"^SEED-[A-Z]+-\d{2}-", "", os.path.basename(seeds[sid]))[:-3]
        rel = write_rule(rule, body, rid, folder, slug, args.dry_run)
        custodian = ((scopes or {}).get(target) or {}).get("custodian") or "its custodian"
        verb = "would adopt" if args.dry_run else "adopted"
        print("OK  %s %s as %s (candidate; needs %s)" % (sid, verb, rel, custodian))
        done[sid] = rel
    if status == 0 and not args.dry_run:
        print("\n    Next: python3 bin/validate.py && python3 bin/generate_catalog.py")
    return status


if __name__ == "__main__":
    sys.exit(main())
