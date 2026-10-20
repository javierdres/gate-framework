#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Build catalog.json from the rule files, for the review skills to read.

    python3 bin/generate_catalog.py

catalog.json is generated on each machine and ignored by version control. Versioning it would
make every two change requests that touch the catalog conflict on it.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rules import DIRS, ROOT, parse, rule_files  # noqa: E402

OUT = os.path.join(ROOT, "catalog.json")


def main():
    rules = []
    for sev, name, path in rule_files():
        front, _ = parse(path)
        if front and not str(front.get("id", "")).endswith("0000"):
            front["severity"] = sev
            front["path"] = "rules/%s/%s" % (sev, name)
            rules.append(front)

    totals = {sev: {"in force": 0, "candidate": 0, "deprecated": 0} for sev in DIRS}
    for r in rules:
        status = r.get("status", "candidate")
        if status in totals[r["severity"]]:
            totals[r["severity"]][status] += 1

    payload = {"version": 1, "totals": totals, "rules": rules}
    new = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    old = io.open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    if new == old:
        print("OK  catalog.json already up to date (%d rules)" % len(rules))
    else:
        io.open(OUT, "w", encoding="utf-8").write(new)
        print("OK  catalog.json built (%d rules)" % len(rules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
