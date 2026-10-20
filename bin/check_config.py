#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Check a project's .gate/config.yml and report what is missing, by stage.

Run it with no arguments to check ./.gate/config.yml, or pass a path.

It never fails for an empty optional field: leaving one empty is a valid
declaration that the stage depending on it is not in use yet. It fails only
when a field required to start is missing, because without those the cycle
cannot resolve traceability or know which catalog to read.
"""
import io
import os
import sys

try:
    import yaml
except ImportError:
    print("this check needs pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# field -> (stage that needs it, blocks the start)
REQUIRED = {
    "organisation.name": (0, True),
    "organisation.catalog": (0, True),
    "organisation.false_positives": (0, True),
    "organisation.hard_rule_approvers": (12, False),
    "organisation.regulatory_context": (1, False),
    "project.id": (0, True),
    "project.repositories": (0, True),
    "project.branch_convention": (0, True),
    "project.tracker": (0, True),
    "project.dossiers": (0, True),
    "project.definition": (3, False),
    "tooling.lint": (6, False),
    "tooling.static_analysis": (6, False),
    "tooling.tests": (6, False),
    "tooling.extra_checks": (6, False),
    "data_sources.application_logs": (10, False),
    "data_sources.infrastructure_logs": (10, False),
    "data_sources.metrics": (10, False),
    "data_sources.traces": (10, False),
    "data_sources.audit_trail": (10, False),
    "data_sources.external_dependencies": (10, False),
    "data_sources.correlation_id": (10, False),
    "data_sources.retention": (10, False),
    "operations.rollback_procedure": (9, False),
    "operations.rollback_last_exercised": (9, False),
    "operations.recovery_time_objective": (2, False),
    "operations.recovery_point_objective": (2, False),
    "gates.product": (1, False),
    "gates.engineering": (3, False),
    "gates.design": (4, False),
    "gates.review": (7, False),
    "gates.qa": (8, False),
    "gates.deployment": (9, False),
}

STAGE_NAMES = {
    0: "start", 1: "definition", 2: "requirements", 3: "refinement", 4: "design",
    6: "pre-review", 7: "change review", 8: "verification", 9: "deployment",
    10: "operations", 12: "learning",
}


def get(data, path):
    node = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def empty(value):
    return value is None or value == "" or value == [] or value == {}


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("usage: check_config.py [path to .gate/config.yml]\n\nReports what is filled, what blocks "
              "the start, and which stage is waiting on each gap.")
        return 0
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(".gate", "config.yml")
    if not os.path.exists(path):
        print("x no config at %s" % path)
        print("  copy templates/gate-config.yml there and run /init again.")
        return 1

    try:
        data = yaml.safe_load(io.open(path, encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print("x %s is not valid YAML: %s" % (path, exc))
        return 1

    blocking, pending = [], {}
    for field, (stage, blocks) in REQUIRED.items():
        if empty(get(data, field)):
            if blocks:
                blocking.append(field)
            else:
                pending.setdefault(stage, []).append(field)

    unknown = []
    for section, content in (data or {}).items():
        if isinstance(content, dict):
            for key in content:
                if "%s.%s" % (section, key) not in REQUIRED:
                    unknown.append("%s.%s" % (section, key))

    filled = len(REQUIRED) - len(blocking) - sum(len(v) for v in pending.values())
    print("%s — %d of %d fields filled" % (path, filled, len(REQUIRED)))

    if blocking:
        print("\nx missing before anything can start:")
        for f in blocking:
            print("    %s" % f)

    if pending:
        print("\n  empty, needed by:")
        for stage in sorted(pending):
            print("    stage %-2d %-16s %s"
                  % (stage, STAGE_NAMES.get(stage, ""), ", ".join(pending[stage])))
        print("\n  An empty field is a valid declaration that the stage using it")
        print("  is not in use yet. Fill it when that stage arrives.")

    if unknown:
        print("\n  not recognised by this version of the framework:")
        for f in unknown:
            print("    %s" % f)

    if blocking:
        print("\nx %d required field(s) missing." % len(blocking))
        return 1
    print("\nOK  ready to start." if not pending else "\nOK  ready to start, with gaps noted above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
