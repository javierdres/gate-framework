#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Tests for tools/rename.sh, on a throwaway working folder installed for Claude Code.
#
#   bash tools/tests/test_rename.sh
#
# Prints one line per case and exits non-zero if any case behaves differently from what it should.
set -uo pipefail

KIT="$(cd "$(dirname "$0")/../.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
check() {  # check <description> <command...>
  local what="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  ✓  $what"; else echo "  ✗  $what"; fail=1; fi
}
unset CLAUDECODE GEMINI_CLI CODEX_SANDBOX

mkdir -p "$T/work"
cp -R "$KIT" "$T/work/sdlc-acme"
cd "$T/work/sdlc-acme"
printf 'system:\n  name: "sdlc-acme"\n  reach: "software"\n' > sdlc.yml
git init -q -b main && git add -A && git -c user.email=a@x -c user.name=a commit -qm init
git remote add origin git@example.com:acme/sdlc-acme.git
bash tools/install.sh claude-code >/dev/null
printf '\nMy own note about sdlc-acme-tools/ stays.\n' >> "$T/work/CLAUDE.md"

check "does nothing while the name has not changed" bash tools/rename.sh
check "refuses to run inside an assistant session" sh -c '! CLAUDECODE=1 bash tools/rename.sh acme-next && test -d ../sdlc-acme'
check "refuses a name that is not a folder name" sh -c '! bash tools/rename.sh "Bad Name"'

sed -i.orig 's/"sdlc-acme"/"ai-office-acme"/' sdlc.yml && rm -f sdlc.yml.orig
bash tools/rename.sh >/dev/null 2>&1
cd "$T/work"
check "moves the folder with personal/ inside" test -f ai-office-acme/personal/.installed -a ! -e sdlc-acme
check "rewrites the instructions block" grep -qx '@ai-office-acme/AGENTS.md' CLAUDE.md
check "leaves no import of the old name" sh -c '! grep -q "@sdlc-acme/" CLAUDE.md AGENTS.md'
check "keeps what the person wrote" grep -q 'sdlc-acme-tools/ stays' CLAUDE.md
check "points the guards at the new folder" grep -q 'ai-office-acme/tools/guards/permissions.py' .claude/settings.json
check "leaves no guard on the old folder" sh -c '! grep -q "sdlc-acme/tools" .claude/settings.json'
check "relinks the skills" test -e .claude/skills/onboard/SKILL.md
check "points the remote at the new name" sh -c 'git -C ai-office-acme remote get-url origin | grep -q "/ai-office-acme.git$"'
check "backs up what it rewrote" sh -c 'ls CLAUDE.md.bak-* >/dev/null'
before="$(cat CLAUDE.md .claude/settings.json | shasum)"
check "a second run changes nothing" bash ai-office-acme/tools/rename.sh
check "and leaves the files identical" test "$before" = "$(cat CLAUDE.md .claude/settings.json | shasum)"

exit $fail
