#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Checks the requirements and the access one or more profiles need, one line each.
#
#   tools/check-access.sh requirements                  only what the machine needs before installing
#   tools/check-access.sh <profile>[,<profile>...]      full report: requirements, everyone's, the profiles'
#   tools/check-access.sh --summary <profile>[,...]     one line, for the session start guard
#
# The checks live in tools/access-checks.tsv: one per line, profile, name, command and, optionally,
# a cheap local test that the access is configured, separated by tabs. `requirements` and `all`
# apply to everyone; several profiles get the union of their checks. A check passes when its
# command exits 0. When it fails and its configured test passes, the access is "configured but
# not answering": expired, revoked or offline. Never put a credential in that file.
#
# Every check runs at the same time, under a hard deadline (GATE_ACCESS_DEADLINE, 8 seconds by
# default): whatever is still running then is stopped with every process it started, and fails.
set -uo pipefail

SUMMARY=0
if [ "${1:-}" = "--summary" ]; then SUMMARY=1; shift; fi
PROFILES="${1:-}"
DIR="$(cd "$(dirname "$0")" && pwd)"
CHECKS="$DIR/access-checks.tsv"
DEADLINE="${GATE_ACCESS_DEADLINE:-${SDLC_ACCESS_DEADLINE:-8}}"   # SDLC_: the older name

if [ -z "$PROFILES" ] || [ ! -f "$CHECKS" ]; then
  sed -n '4,18p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi
TMP="$(mktemp -d 2>/dev/null || { mkdir -p "/tmp/gate-access-$$" && echo "/tmp/gate-access-$$"; })"
trap 'rm -rf "$TMP"' EXIT

applies() {  # applies <profile of the check>
  [ "$1" = requirements ] && return 0
  [ "$PROFILES" = requirements ] && return 1
  [ "$1" = all ] && return 0
  case ",$PROFILES," in *",$1,"*) return 0 ;; esac
  return 1
}
# Stops a process and everything it started, where pgrep exists; elsewhere, the process itself.
kill_tree() {
  local child
  if command -v pgrep >/dev/null 2>&1; then
    for child in $(pgrep -P "$1" 2>/dev/null); do kill_tree "$child"; done
  fi
  kill "$1" 2>/dev/null
}

n=0; pids=""
: > "$TMP/names"
while IFS=$'\t' read -r who name cmd configured; do
  case "$who" in ''|\#*) continue ;; esac
  applies "$who" || continue
  grep -Fxq "$name" "$TMP/names" && continue
  printf '%s\n' "$name" >> "$TMP/names"
  n=$((n + 1))
  printf '%s' "$name" > "$TMP/$n.name"
  printf '%s' "${configured:-}" > "$TMP/$n.configured"
  ( cd "$DIR/.." && bash -c "$cmd" ) </dev/null >/dev/null 2>&1 && : > "$TMP/$n.ok" &
  pids="$pids $!"
done < "$CHECKS"

if [ -n "$pids" ]; then
  ( sleep "$DEADLINE"; for p in $pids; do kill_tree "$p"; done ) >/dev/null 2>&1 &
  watchdog=$!
  for p in $pids; do wait "$p" 2>/dev/null; done
  kill_tree "$watchdog"; wait "$watchdog" 2>/dev/null
fi

ok=0; fail=0; silent=""; report=""
i=0
while [ "$i" -lt "$n" ]; do
  i=$((i + 1))
  name="$(cat "$TMP/$i.name")"
  if [ -e "$TMP/$i.ok" ]; then
    ok=$((ok + 1)); report="$report  ✓  $name\n"; continue
  fi
  fail=$((fail + 1))
  configured="$(cat "$TMP/$i.configured")"
  if [ -n "$configured" ] && ( cd "$DIR/.." && bash -c "$configured" ) </dev/null >/dev/null 2>&1; then
    silent="$silent${silent:+, }$name"; report="$report  !  $name: configured but not answering\n"
  else
    report="$report  ✗  $name\n"
  fi
done

if [ "$SUMMARY" = 1 ]; then
  if [ "$fail" = 0 ]; then echo "$ok of $n checks green for $PROFILES"
  else
    echo "$fail of $n checks failing for $PROFILES: run tools/check-access.sh $PROFILES${silent:+ (configured but not answering, expired or offline: $silent)}"
  fi
else
  printf '  ACCESS · %s\n' "$PROFILES"
  printf '  ──────────────────────────────────────────────────────────\n'
  printf "%b" "$report"
  printf '  ✓ works   ✗ missing   ! configured but not answering\n'
fi
[ "$fail" = 0 ]
