#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Checks the requirements and the access a profile needs, one line each.
#
#   tools/check-access.sh <profile>             full report
#   tools/check-access.sh --summary <profile>   one line, for the session start guard
#
# The checks live in tools/access-checks.tsv: one per line, profile, name and command,
# separated by tabs. A profile of `all` applies to everyone. A check passes when its
# command exits 0. Never put a credential in that file; commands read each person's own.
set -uo pipefail

SUMMARY=0
if [ "${1:-}" = "--summary" ]; then SUMMARY=1; shift; fi
PROFILE="${1:-}"
DIR="$(cd "$(dirname "$0")" && pwd)"
CHECKS="$DIR/access-checks.tsv"

if [ -z "$PROFILE" ] || [ ! -f "$CHECKS" ]; then
  sed -n '4,12p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

# A time limit that works on Linux, macOS and Git Bash alike.
limited() { if command -v perl >/dev/null 2>&1; then perl -e 'alarm shift; exec @ARGV' 15 "$@"; else "$@"; fi; }

ok=0; fail=0; report=""
while IFS=$'\t' read -r who name cmd; do
  case "$who" in ''|\#*) continue ;; esac
  [ "$who" = "all" ] || [ "$who" = "$PROFILE" ] || continue   # `all` as the profile runs only these
  if ( cd "$DIR/.." && limited bash -c "$cmd" ) </dev/null >/dev/null 2>&1; then
    ok=$((ok + 1)); report="$report  ✓  $name\n"
  else
    fail=$((fail + 1)); report="$report  ✗  $name\n"
  fi
done < "$CHECKS"

if [ "$SUMMARY" = 1 ]; then
  if [ "$fail" = 0 ]; then echo "$ok of $((ok + fail)) checks green for $PROFILE"
  else echo "$fail of $((ok + fail)) checks failing for $PROFILE: run tools/check-access.sh $PROFILE"; fi
else
  printf '  ACCESS · profile %s\n' "$PROFILE"
  printf '  ──────────────────────────────────────────────────────────\n'
  printf "%b" "$report"
  printf '  ✓ works   ✗ missing\n'
fi
[ "$fail" = 0 ]
