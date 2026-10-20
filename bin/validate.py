#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Validate that every skill declares a complete, coherent contract.

For each skill it checks that the frontmatter carries every field, that the
required sections exist, and that the trigger chain closes both ways: if A says
it triggers B, B has to say it is triggered by A.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")

FIELDS = ["skill", "stage", "name", "triggers", "gate", "gate_owner",
          "writes_outside", "consults"]
SECTIONS = ["## Purpose", "## Preconditions", "## What it does",
            "## What it does NOT do", "## Gate", "## Dossier"]
# valid origins that are not another skill
EXTERNAL = {"person", "alert"}

errors = []


def error(where, msg):
    errors.append("%s: %s" % (where, msg))


def as_list(value):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [x.strip() for x in value.split(",") if x.strip()]


def read_skill(path):
    text = io.open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, None
    front = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            front[k.strip()] = v.strip()
    return front, m.group(2)


def main():
    if not os.path.isdir(SKILLS):
        print("skills/ not found", file=sys.stderr)
        return 1

    names = sorted(d for d in os.listdir(SKILLS)
                   if os.path.isdir(os.path.join(SKILLS, d)))
    fronts = {}

    for n in names:
        path = os.path.join(SKILLS, n, "SKILL.md")
        where = "skills/%s/SKILL.md" % n
        if not os.path.exists(path):
            error("skills/%s" % n, "SKILL.md missing")
            continue
        front, body = read_skill(path)
        if front is None:
            error(where, "no frontmatter")
            continue
        fronts[n] = front

        for f in FIELDS:
            if f not in front:
                error(where, "missing field '%s'" % f)
        if front.get("skill") != n:
            error(where, "skill field ('%s') does not match its directory"
                  % front.get("skill"))
        for s in SECTIONS:
            if s not in body:
                error(where, "missing section '%s'" % s)

        stage = front.get("stage", "")
        cross = stage == "cross-cutting"
        foundation = stage in ("foundation", "support")
        if not cross and not foundation and not (stage.isdigit() and 0 <= int(stage) <= 12):
            error(where, "invalid stage: '%s' (0 to 12, 'foundation', 'support' or 'cross-cutting')" % stage)
        if front.get("gate") != "none" and front.get("gate_owner", "—") == "—":
            error(where, "declares a gate but no owner for it")
        if front.get("gate") == "none" and front.get("gate_owner", "—") != "—":
            error(where, "declares no gate but does declare an owner")

        if cross:
            if "consulted_by" not in front:
                error(where, "a cross-cutting skill declares consulted_by, not triggered_by")
            if as_list(front.get("triggered_by", "")):
                error(where, "a cross-cutting skill is not triggered: it is consulted")
        elif "triggered_by" not in front:
            error(where, "missing field 'triggered_by'")

    # the chain has to close in both directions
    for n, front in fronts.items():
        where = "skills/%s/SKILL.md" % n
        for target in as_list(front.get("triggers", "")):
            if target not in fronts:
                error(where, "triggers '%s', which does not exist" % target)
            elif n not in as_list(fronts[target].get("triggered_by", "")):
                error(where, "triggers '%s', but '%s' does not list it in triggered_by"
                      % (target, target))
        for reader in as_list(front.get("consulted_by", "")):
            if reader not in fronts:
                error(where, "says it is consulted by '%s', which does not exist" % reader)
        for origin in as_list(front.get("triggered_by", "")):
            if origin in EXTERNAL:
                continue
            if origin not in fronts:
                error(where, "says it is triggered by '%s', which does not exist" % origin)
            elif n not in as_list(fronts[origin].get("triggers", "")):
                error(where, "says it is triggered by '%s', but '%s' does not list it in triggers"
                      % (origin, origin))

    for e in errors:
        print("x %s" % e)
    if errors:
        print("\nx %d problem(s) across %d skill(s)." % (len(errors), len(names)))
        return 1

    print("OK  %d skills valid, trigger chain closes." % len(names))
    human = [n for n, f in fronts.items()
             if "person" in as_list(f.get("triggered_by", ""))]
    print("    Human invocation: %s" % ", ".join("/%s" % h for h in sorted(human)))
    order = {"foundation": -1, "support": 98}
    gates = [(int(f["stage"]) if f["stage"].isdigit() else order.get(f["stage"], 99),
              n, f["gate"], f["gate_owner"])
             for n, f in fronts.items() if f.get("gate") != "none"]
    print("    Gates: %d" % len(gates))
    for _, n, g, owner in sorted(gates):
        print("      /%-20s %-22s %s" % (n, g, owner))
    return 0


if __name__ == "__main__":
    sys.exit(main())
