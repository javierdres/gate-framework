#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Regenerates a product's use-case index from its detail, one file per module.

    python3 tools/use_cases_index.py products/<product>            rewrite the index
    python3 tools/use_cases_index.py products/<product> --check    fail if it is stale

Reads products/<product>/use-cases/NN-*.md and rewrites, in products/<product>/use-cases.md,
only what sits between `<!-- use-cases:begin -->` and `<!-- use-cases:end -->`: a summary per
module and criticality, and one table per module. Each case in the detail starts like this:

    ### ABC-UC-0001 · Name of the case

    - **Role:** … · **Client:** … · **Layer:** … · **Criticality:** N · **Checks:** … · **Origin:** …
    - **Tags:** @module @other

Criticality is 1 (critical), 2 (important) or 3 (detail); a case whose Checks mention `edge`
counts as an edge case. The optional lines `- **Status:** …` and `- **Flow:** …` give its status
(`proposed` when missing) and its automated flow (`—` when missing). A repeated identifier or an
incomplete data line stops it with the list of problems. Exits 0 when done or up to date, 1
otherwise.
"""
import io
import os
import re
import sys

START, END = "<!-- use-cases:begin -->", "<!-- use-cases:end -->"
CASE = re.compile(r"^### ([A-Z]{3}-UC-\d+) · (.+?)\n(.*?)(?=^### |^## |\Z)", re.M | re.S)
META = re.compile(r"^- \*\*Role:\*\* (.+?) · \*\*Client:\*\* (.+?) · \*\*Layer:\*\* (.+?) · "
                  r"\*\*Criticality:\*\* ([123]) · \*\*Checks:\*\* (.+?) · \*\*Origin:\*\* (.+)$", re.M)
COLUMNS = ("id", "name", "role", "client", "layer", "tags", "criticality", "checks", "origin", "status", "flow")


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def field(body, name, default):
    m = re.search(r"^- \*\*%s:\*\* (.+)$" % name, body, re.M)
    return m.group(1).strip() if m else default


def cell(text):
    return text.replace("|", "\\|").strip()


def modules(product):
    """[(file name, title, [case])] and the problems found."""
    found, errors = [], []
    folder = os.path.join(product, "use-cases")
    names = sorted(n for n in os.listdir(folder) if re.match(r"\d\d-.*\.md$", n)) if os.path.isdir(folder) else []
    for name in names:
        text = read(os.path.join(folder, name))
        title = re.search(r"^# (.+)$", text, re.M)
        cases = []
        for cid, case_name, body in CASE.findall(text):
            meta = META.search(body)
            if not meta:
                errors.append("%s: %s has no complete data line" % (name, cid))
                continue
            role, client, layer, crit, checks, origin = (g.strip() for g in meta.groups())
            cases.append({"id": cid, "name": case_name.strip(), "role": role, "client": client, "layer": layer,
                          "criticality": crit, "checks": checks, "origin": origin,
                          "tags": field(body, "Tags", ""), "status": field(body, "Status", "proposed"),
                          "flow": field(body, "Flow", "—")})
        found.append((name, title.group(1).strip() if title else name, cases))
    ids = [c["id"] for _, _, cases in found for c in cases]
    repeated = sorted({i for i in ids if ids.count(i) > 1})
    if repeated:
        errors.append("repeated identifiers: " + ", ".join(repeated))
    return found, errors


def build(found):
    out = ["", "### Summary", "",
           "| Module | Cases | Critical | Important | Detail | Edge |",
           "| --- | --- | --- | --- | --- | --- |"]
    total = [0] * 5
    for name, title, cases in found:
        row = [len(cases)] + [sum(c["criticality"] == n for c in cases) for n in "123"] + \
              [sum("edge" in c["checks"].lower() for c in cases)]
        total = [a + b for a, b in zip(total, row)]
        out.append("| [%s](use-cases/%s) | %s |" % (title, name, " | ".join(map(str, row))))
    out.append("| **Total** | %s |" % " | ".join("**%d**" % n for n in total))
    for name, title, cases in found:
        out += ["", "### %s · [detail](use-cases/%s)" % (title, name), "",
                "| ID | Case | Role | Client | Layer | Tags | Criticality | Checks | Origin | Status | Flow |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        out += ["| %s |" % " | ".join(cell(c[k]) for k in COLUMNS) for c in cases]
    return "\n".join(out) + "\n\n"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.strip())
        return 2
    product = args[0].rstrip("/\\")
    index = os.path.join(product, "use-cases.md")
    if not os.path.exists(index):
        print("x %s does not exist" % index)
        return 1
    text = read(index)
    if START not in text or END not in text or text.index(START) > text.index(END):
        print("x %s: the markers %s and %s are missing" % (index, START, END))
        return 1
    found, errors = modules(product)
    if errors:
        for e in errors:
            print("x " + e)
        return 1
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    new = head + START + "\n" + build(found) + END + tail
    if "--check" in argv:
        if new != text:
            print("x %s is stale: run python3 tools/use_cases_index.py %s" % (index, product))
            return 1
        print("OK  %s is up to date" % index)
        return 0
    with io.open(index, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("OK  %s regenerated with %d cases" % (index, sum(len(c) for _, _, c in found)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
