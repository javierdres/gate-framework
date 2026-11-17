#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The catalog's gate for a change request, on any CI platform. Standard library only.

    python3 gate.py --base <target branch or commit> [--counts counts.tsv]
                    [--pinned X.Y.Z | --profile AGENTS.md] [--current X.Y.Z] [--enforce]

It does two things, and neither needs the project to be clean first.

1. Freezes debt. For each pattern in counts.tsv it counts the matches at the merge base with
   the target branch and at the change's head. A rule fails only if its count went up: what was
   already broken blocks nobody, and nothing new gets in.
2. Checks the pinned version. The project declares which version of the standard it follows.
   Behind by a minor or a patch it warns; behind by a major it fails.

Without --enforce, or while the standard is 0.x, every failure is printed as a warning and the
exit code is 0: a draft standard blocks nothing.

counts.tsv, one pattern per line, tab-separated, '#' for comments:

    <rule id>	<extended regex>	[<pathspec> ...]
"""
import argparse
import io
import re
import subprocess
import sys


def git(*args):
    p = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return p.returncode, p.stdout


def read_counts(path):
    patterns = []
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2 or not parts[0].strip() or not parts[1]:
            raise SystemExit("x %s:%d: expected '<rule id><TAB><regex>[<TAB><pathspec>...]'" % (path, n))
        paths = " ".join(parts[2:]).split()
        patterns.append((parts[0].strip(), parts[1], paths))
    return patterns


def count(rev, regex, paths):
    code, out = git("grep", "-c", "-E", "-e", regex, rev, "--", *(paths or ["."]))
    if code not in (0, 1):
        raise SystemExit("x git grep failed for /%s/ at %s" % (regex, rev))
    return sum(int(line.rsplit(":", 1)[1]) for line in out.splitlines() if ":" in line)


def semver(v):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", (v or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def version_lag(pinned, current):
    """'ok', 'warn' (behind by a minor or a patch) or 'fail' (behind by a major, or unreadable)."""
    p, c = semver(pinned), semver(current)
    if p is None or c is None:
        return "fail"
    if p >= c:
        return "ok"
    return "fail" if p[0] < c[0] else "warn"


def pinned_from(profile):
    text = io.open(profile, encoding="utf-8").read()
    m = re.search(r"^\s*catalog_version:\s*[\"']?(v?\d+\.\d+\.\d+)", text, re.M)
    return m.group(1) if m else None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--base", required=True, help="the target branch or commit of the change")
    p.add_argument("--head", default="HEAD")
    p.add_argument("--counts", help="tsv of rule id, regex and pathspecs to freeze")
    p.add_argument("--pinned", help="the standard version the project follows")
    p.add_argument("--profile", help="read the pinned version from catalog_version in this file")
    p.add_argument("--current", help="the latest released version of the standard")
    p.add_argument("--enforce", action="store_true", help="fail instead of warning (ignored while 0.x)")
    args = p.parse_args(argv)

    code, base = git("merge-base", args.base, args.head)
    if code != 0:
        print("x cannot find the merge base of %s and %s. Fetch the target branch with its history." % (args.base, args.head))
        return 1
    base = base.strip()
    failures, notes = [], []

    for rid, regex, paths in read_counts(args.counts) if args.counts else []:
        before, after = count(base, regex, paths), count(args.head, regex, paths)
        line = "%s  %d -> %d" % (rid, before, after)
        if after > before:
            failures.append("%s (+%d): new occurrences of /%s/" % (line, after - before, regex))
        else:
            notes.append(line + ("  (down %d)" % (before - after) if after < before else ""))

    pinned = args.pinned or (pinned_from(args.profile) if args.profile else None)
    current = args.current
    if args.profile and not pinned:
        failures.append("the profile does not declare catalog_version")
    if pinned and current:
        lag = version_lag(pinned, current)
        if lag == "fail":
            failures.append("pinned version %s is a major behind %s (or unreadable)" % (pinned, current))
        elif lag == "warn":
            notes.append("pinned version %s is behind %s: plan the upgrade" % (pinned, current))

    draft = bool(current) and current.lstrip("v").startswith("0.")
    blocking = args.enforce and not draft
    for n in notes:
        print("   %s" % n)
    for f in failures:
        print("%s %s" % ("x" if blocking else "!", f))
    if failures and not blocking:
        why = "the standard is still 0.x" if draft else "run with --enforce to block"
        print("\n!  %d finding(s), reported as warnings: %s." % (len(failures), why))
    elif not failures:
        print("OK  nothing new against %s." % args.base)
    return 1 if (failures and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
