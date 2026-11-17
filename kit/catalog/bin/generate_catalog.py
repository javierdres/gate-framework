#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Build catalog.json from the rule files, for the review skills to read.

    python3 bin/generate_catalog.py

catalog.json is generated on each machine and ignored by version control. Versioning it would
make every two change requests that touch the catalog conflict on it. Seeds are not rules and
never appear in it.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rules import ROOT, SEVERITIES, STATUSES, load_rules, read_scopes  # noqa: E402

OUT = os.path.join(ROOT, "catalog.json")


def main():
    rules = load_rules()
    totals = {sev: {s: 0 for s in STATUSES} for sev in SEVERITIES}
    for r in rules:
        status = r.get("status", "candidate")
        if r.get("severity") in totals and status in totals[r["severity"]]:
            totals[r["severity"]][status] += 1

    scopes = read_scopes() or {}
    payload = {"version": 1, "scopes": scopes, "totals": totals, "rules": rules}
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
