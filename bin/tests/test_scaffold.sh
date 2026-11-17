#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Tests for bin/bootstrap.py: a freshly scaffolded system, for each automated adapter, installs
# with the neutral names only and passes its own kit tests. On throwaway folders.
#
#   bash bin/tests/test_scaffold.sh
#
# Prints one line per case and exits non-zero if any case behaves differently from what it should.
set -uo pipefail

GATE="$(cd "$(dirname "$0")/../.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
check() {  # check <description> <command...>
  local what="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  ✓  $what"; else echo "  ✗  $what"; fail=1; fi
}
for v in $(env | grep -E '^(CLAUDE|GEMINI|KIRO_|CODEX|GATE_|SDLC_)[A-Za-z_]*=' | cut -d= -f1); do unset "$v"; done
export HOME="$T/home" GIT_CONFIG_GLOBAL="$T/home/.gitconfig" GIT_CONFIG_NOSYSTEM=1 TERM_PROGRAM=
mkdir -p "$HOME"

check "names proposes deskmate-<org> first" sh -c \
  "python3 '$GATE/bin/bootstrap.py' names acme | grep -m1 '^  \*' | grep -q 'deskmate-acme'"

for a in claude-code kiro; do
  W="$T/$a"; S="$W/deskmate-acme"
  mkdir -p "$W"
  python3 "$GATE/bin/bootstrap.py" system "$S" --assistant "$a" --org acme --name Acme >/dev/null
  (cd "$S" && git init -q -b main && git add -A && git -c user.email=a@x -c user.name=a commit -qm init)
  bash "$S/tools/install.sh" "$a" >/dev/null 2>&1
  check "$a: scaffolds system.yml, never sdlc.yml" sh -c "[ -f '$S/system.yml' ] && [ ! -e '$S/sdlc.yml' ]"
  check "$a: system.yml carries the name and a reach beyond software" sh -c \
    "grep -q 'name: \"deskmate-acme\"' '$S/system.yml' && grep -q 'reach: \"beyond-software\"' '$S/system.yml'"
  check "$a: installs" test -f "$S/personal/.installed-$a"
  check "$a: nothing in the working folder carries an older name" sh -c \
    "! grep -rIl --exclude-dir=deskmate-acme -e 'sdlc:' -e 'SDLC_' -e 'sdlc.json' -e '.sdlc-copy' '$W'"
  check "$a: the log is marked the new way" grep -qx '<!-- gate:open -->' "$S/personal/sessions/README.md"
  check "$a: the session start has nothing older to point out" sh -c \
    "! python3 '$S/tools/guards/session_start.py' 2>&1 | grep -qE 'migrate.sh|Older names'"
  for t in "$S"/tools/tests/*.sh; do
    check "$a: its own $(basename "$t") passes" bash "$t"
  done
done

W="$T/alias"; mkdir -p "$W"
check "the older subcommand, sdlc, still scaffolds" sh -c \
  "python3 '$GATE/bin/bootstrap.py' sdlc '$W/deskmate-acme' --assistant claude-code --org acme && [ -f '$W/deskmate-acme/system.yml' ]"

exit $fail
