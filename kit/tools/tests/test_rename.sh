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
skipping=""
check() {  # check <description> <command...>
  local what="$1"; shift
  if [ -n "$skipping" ]; then echo "  -  $what (skipped: no $skipping adapter)"; return; fi
  if "$@" >/dev/null 2>&1; then echo "  ✓  $what"; else echo "  ✗  $what"; fail=1; fi
}
unset CLAUDECODE GEMINI_CLI CODEX_SANDBOX

mkdir -p "$T/work"
cp -R "$KIT" "$T/work/deskmate-acme"
rm -rf "${T:?}/work/deskmate-acme/.git" "${T:?}/work/deskmate-acme/personal"
cd "$T/work/deskmate-acme"
# The checks that follow need that adapter. bootstrap.py keeps only the one the organisation chose,
# so in a scaffolded system the others are skipped rather than failed.
needs() { if [ -z "$1" ] || [ -d "$T/work/$2/adapters/$1" ]; then skipping=""; else skipping="$1"; fi; }
CLAUDE=0; [ -d adapters/claude-code ] && CLAUDE=1
printf 'system:\n  name: "deskmate-acme"\n  reach: "software"\n' > system.yml
git init -q -b main && git add -A && git -c user.email=a@x -c user.name=a commit -qm init
git remote add origin git@example.com:acme/deskmate-acme.git
for a in claude-code kiro; do [ -d "adapters/$a" ] && bash tools/install.sh "$a" >/dev/null; done
[ "$CLAUDE" = 1 ] && printf '\nMy own note about deskmate-acme-tools/ stays.\n' >> "$T/work/CLAUDE.md"
# A working folder an older installer wired: the single-marker block, a backup left next to it.
printf '# Mine\n\n<!-- sdlc:deskmate-acme -->\nRead and follow deskmate-acme/AGENTS.md, the system of the organisation.\n\nMy own line.\n' \
  > "$T/work/AGENTS.md"
printf 'old\n' > "$T/work/CLAUDE.md.bak-20260101000000"
printf 'See deskmate-acme/AGENTS.md\n' > "$T/work/NOTES.md"

check "does nothing while the name has not changed" bash tools/rename.sh
check "refuses to run inside an assistant session" sh -c '! CLAUDECODE=1 bash tools/rename.sh acme-next && test -d ../deskmate-acme'
check "refuses a name that is not a folder name" sh -c '! bash tools/rename.sh "Bad Name"'

sed -i.orig 's/"deskmate-acme"/"ai-office-acme"/' system.yml && rm -f system.yml.orig
out="$(bash tools/rename.sh 2>&1)"
cd "$T/work"
check "moves the folder with personal/ inside" test -f ai-office-acme/personal/.installed -a ! -e deskmate-acme
needs claude-code ai-office-acme
check "rewrites the instructions block" grep -qx '@ai-office-acme/AGENTS.md' CLAUDE.md
check "leaves no import of the old name" sh -c '! grep -q "@deskmate-acme/" CLAUDE.md AGENTS.md'
check "keeps what the person wrote" grep -q 'deskmate-acme-tools/ stays' CLAUDE.md
check "points the guards at the new folder" grep -q 'ai-office-acme/tools/guards/permissions.py' .claude/settings.json
check "leaves no guard on the old folder" sh -c '! grep -q "deskmate-acme/tools" .claude/settings.json'
check "relinks the skills" test -e .claude/skills/onboard/SKILL.md
needs "" ai-office-acme
check "points the remote at the new name" sh -c 'git -C ai-office-acme remote get-url origin | grep -q "/ai-office-acme.git$"'
check "backs up what it rewrote inside personal/backups" sh -c 'ls ai-office-acme/personal/backups/AGENTS.md.* >/dev/null'
check "leaves no backup in the working folder" sh -c '! ls CLAUDE.md.bak-* AGENTS.md.bak-* .claude/*.bak-* 2>/dev/null | grep -q .'
check "migrates the older single-marker block" sh -c 'grep -qx "<!-- gate:begin -->" AGENTS.md && ! grep -q "sdlc:deskmate-acme" AGENTS.md'
check "keeps the person's lines around the block" sh -c 'grep -qx "# Mine" AGENTS.md && grep -qx "My own line." AGENTS.md'
check "the block names the new folder" grep -q '^Read and follow ai-office-acme/AGENTS.md' AGENTS.md
needs kiro ai-office-acme
check "installs again for every assistant" sh -c 'grep -q "ai-office-acme/tools/guards/permissions.py" .kiro/hooks/gate.json'
needs "" ai-office-acme
check "points out what it does not rewrite" sh -c 'printf "%s" "$0" | grep -q "NOTES.md"' "$out"
state() { cat AGENTS.md CLAUDE.md .claude/settings.json .kiro/hooks/gate.json 2>/dev/null | shasum; }
before="$(state)"
check "a second run changes nothing" bash ai-office-acme/tools/rename.sh
check "and leaves the files identical" test "$before" = "$(state)"

exit $fail
