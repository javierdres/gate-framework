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
bash tools/install.sh kiro >/dev/null
printf '\nMy own note about sdlc-acme-tools/ stays.\n' >> "$T/work/CLAUDE.md"
# A working folder an older installer wired: the single-marker block, a backup left next to it.
printf '# Mine\n\n<!-- sdlc:sdlc-acme -->\nRead and follow sdlc-acme/AGENTS.md, the system of the organisation.\n\nMy own line.\n' \
  > "$T/work/AGENTS.md"
printf 'old\n' > "$T/work/CLAUDE.md.bak-20260101000000"
printf 'See sdlc-acme/AGENTS.md\n' > "$T/work/NOTES.md"

check "does nothing while the name has not changed" bash tools/rename.sh
check "refuses to run inside an assistant session" sh -c '! CLAUDECODE=1 bash tools/rename.sh acme-next && test -d ../sdlc-acme'
check "refuses a name that is not a folder name" sh -c '! bash tools/rename.sh "Bad Name"'

sed -i.orig 's/"sdlc-acme"/"ai-office-acme"/' sdlc.yml && rm -f sdlc.yml.orig
out="$(bash tools/rename.sh 2>&1)"
cd "$T/work"
check "moves the folder with personal/ inside" test -f ai-office-acme/personal/.installed -a ! -e sdlc-acme
check "rewrites the instructions block" grep -qx '@ai-office-acme/AGENTS.md' CLAUDE.md
check "leaves no import of the old name" sh -c '! grep -q "@sdlc-acme/" CLAUDE.md AGENTS.md'
check "keeps what the person wrote" grep -q 'sdlc-acme-tools/ stays' CLAUDE.md
check "points the guards at the new folder" grep -q 'ai-office-acme/tools/guards/permissions.py' .claude/settings.json
check "leaves no guard on the old folder" sh -c '! grep -q "sdlc-acme/tools" .claude/settings.json'
check "relinks the skills" test -e .claude/skills/onboard/SKILL.md
check "points the remote at the new name" sh -c 'git -C ai-office-acme remote get-url origin | grep -q "/ai-office-acme.git$"'
check "backs up what it rewrote inside personal/backups" sh -c 'ls ai-office-acme/personal/backups/CLAUDE.md.* >/dev/null'
check "leaves no backup in the working folder" sh -c '! ls CLAUDE.md.bak-* AGENTS.md.bak-* .claude/*.bak-* 2>/dev/null | grep -q .'
check "migrates the older single-marker block" sh -c 'grep -qx "<!-- sdlc:begin -->" AGENTS.md && ! grep -q "sdlc:sdlc-acme" AGENTS.md'
check "keeps the person's lines around the block" sh -c 'grep -qx "# Mine" AGENTS.md && grep -qx "My own line." AGENTS.md'
check "the block names the new folder" grep -q '^Read and follow ai-office-acme/AGENTS.md' AGENTS.md
check "installs again for every assistant" sh -c 'grep -q "ai-office-acme/tools/guards/permissions.py" .kiro/hooks/sdlc.json'
check "points out what it does not rewrite" sh -c 'printf "%s" "$0" | grep -q "NOTES.md"' "$out"
before="$(cat CLAUDE.md .claude/settings.json | shasum)"
check "a second run changes nothing" bash ai-office-acme/tools/rename.sh
check "and leaves the files identical" test "$before" = "$(cat CLAUDE.md .claude/settings.json | shasum)"

exit $fail
