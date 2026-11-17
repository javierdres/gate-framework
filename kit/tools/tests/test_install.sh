#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Tests for tools/install.sh, tools/lib.sh and tools/adapters_check.py, on throwaway working
# folders with a throwaway home folder.
#
#   bash tools/tests/test_install.sh
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
# The checks that follow need that adapter. bootstrap.py keeps only the one the organisation chose,
# so in a scaffolded system the others are skipped rather than failed.
needs() { if [ -z "$1" ] || [ -d "$S/adapters/$1" ]; then skipping=""; else skipping="$1"; fi; }
for v in $(env | grep -E '^(CLAUDE|GEMINI|KIRO_|CODEX|SDLC_)[A-Za-z_]*=' | cut -d= -f1); do unset "$v"; done
export HOME="$T/home" GIT_CONFIG_GLOBAL="$T/home/.gitconfig" GIT_CONFIG_NOSYSTEM=1 TERM_PROGRAM=
mkdir -p "$HOME"
digest() { (cd "$1" && find . -path ./sdlc-acme/personal/backups -prune -o \( -type f -o -type l \) -print \
  | LC_ALL=C sort | while read -r f; do printf '%s ' "$f"; if [ -L "$f" ]; then readlink "$f"; else cksum < "$f"; fi; done); }

W="$T/work"
mkdir -p "$W"
cp -R "$KIT" "$W/sdlc-acme"
rm -rf "$W/sdlc-acme/personal"
printf 'organisation:\n  name: "Acme"\n  short_name: "acme"\n' > "$W/sdlc-acme/sdlc.yml"
printf 'tracker-key\n' >> "$W/sdlc-acme/tools/clients/credentials"
S="$W/sdlc-acme"

# lib.sh
. "$S/tools/lib.sh"
mkdir -p "$T/bin"; printf '#!/bin/sh\nexit 1\n' > "$T/bin/python3"; chmod +x "$T/bin/python3"
check "finds a Python that runs, skipping one that only exists" sh -c \
  "PATH='$T/bin:$PATH' bash -c '. \"$S/tools/lib.sh\"; [ \"\$(sdlc_python)\" != python3 ]'"
check "tells the assistant from its environment" sh -c \
  "[ \"\$(CLAUDECODE=1 bash -c '. \"$S/tools/lib.sh\"; sdlc_assistant')\" = claude-code ]"
check "an explicit SDLC_ASSISTANT wins" sh -c \
  "[ \"\$(CLAUDECODE=1 SDLC_ASSISTANT=kiro bash -c '. \"$S/tools/lib.sh\"; sdlc_assistant')\" = kiro ]"

# What an older installer, and the person, left in the working folder.
needs claude-code
printf 'old\n' > "$HOME/.tracker-key"
printf '# Mine\n\n<!-- sdlc:sdlc-acme -->\n@sdlc-acme/AGENTS.md\n@sdlc-acme/personal/profile.md\n' > "$W/CLAUDE.md"
printf 'x\n' > "$W/CLAUDE.md.bak-20260101000000"
mkdir -p "$W/.claude/skills/onboard" "$W/.claude/skills/mine" "$W/.claude/skills/retired"
printf 'my own onboard\n' > "$W/.claude/skills/onboard/SKILL.md"
printf 'mine\n' > "$W/.claude/skills/mine/SKILL.md"
: > "$W/.claude/skills/retired/.sdlc-copy"
ln -s ../../sdlc-acme/skills/gone "$W/.claude/skills/gone"
cat > "$W/.claude/settings.json" <<EOF
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
  {"type": "command", "command": "python3 '$S/tools/guards/permissions.py' check --format claude"},
  {"type": "command", "command": "my-own-hook"}]}]},
 "permissions": {"ask": ["Bash(rm -rf *)"]},
 "statusLine": {"type": "command", "command": "python3 '$S/tools/guards/usage.py' status"}}
EOF

check "refuses to guess the assistant" sh -c "! bash '$S/tools/install.sh' && [ ! -e '$W/AGENTS.md' ]"
out="$(CLAUDECODE=1 bash "$S/tools/install.sh" 2>&1)"
check "installs for the assistant it runs inside" test -f "$S/personal/.installed-claude-code"
check "writes the fingerprint session start compares" sh -c \
  "[ \"\$(cat '$S/personal/.installed-claude-code')\" = \"\$(python3 '$S/tools/guards/session_start.py' --fingerprint claude-code)\" ]"
check "migrates the older single-marker block" sh -c "grep -qx '<!-- sdlc:begin -->' '$W/CLAUDE.md' && ! grep -q 'sdlc:sdlc-acme' '$W/CLAUDE.md'"
check "keeps the person's lines" grep -qx '# Mine' "$W/CLAUDE.md"
check "moves older backups out of the working folder" sh -c "[ ! -e '$W/CLAUDE.md.bak-20260101000000' ] && ls '$S/personal/backups/CLAUDE.md.bak-20260101000000'"
check "backs up what it changes in personal/backups" sh -c "ls '$S'/personal/backups/.claude__settings.json.* '$S'/personal/backups/CLAUDE.md.2*"
check "never overwrites a skill of the person's with the same name" grep -qx 'my own onboard' "$W/.claude/skills/onboard/SKILL.md"
check "and says so" sh -c "printf '%s' \"\$0\" | grep -q 'skills/onboard in the working folder is not sdlc-acme'" "$out"
check "links the system's skills, relative" sh -c "[ \"\$(readlink '$W/.claude/skills/establish')\" = ../../sdlc-acme/skills/establish ]"
check "removes links and copies of skills the system no longer has" sh -c "[ ! -e '$W/.claude/skills/retired' ] && [ ! -L '$W/.claude/skills/gone' ]"
check "leaves the person's own skills alone" test -f "$W/.claude/skills/mine/SKILL.md"
check "replaces the absolute-path guard, without duplicating it" sh -c \
  "[ \"\$(grep -c 'tools/guards/permissions.py' '$W/.claude/settings.json')\" = 1 ] && grep -q 'CLAUDE_PROJECT_DIR/sdlc-acme/tools/guards/permissions.py' '$W/.claude/settings.json'"
check "keeps the person's own hook and rules" sh -c "grep -q my-own-hook '$W/.claude/settings.json' && grep -q 'rm -rf' '$W/.claude/settings.json'"
check "merges the base rules that always ask" grep -q 'gh pr merge' "$W/.claude/settings.json"
check "hooks never break a session" sh -c "grep -q '|| true' '$W/.claude/settings.json' && grep -q '\"timeout\"' '$W/.claude/settings.json'"
check "moves the status line to a project-relative path" sh -c \
  "grep -q 'CLAUDE_PROJECT_DIR:-.}/sdlc-acme/tools/guards/usage.py' '$W/.claude/settings.json' && ! grep -q \"'$S\" '$W/.claude/settings.json'"
check "moves a credential to the organisation's name and links the old one" sh -c \
  "[ -f '$HOME/.acme-tracker-key' ] && [ -L '$HOME/.tracker-key' ] && [ \"\$(cat '$HOME/.tracker-key')\" = old ]"
check "reads the credential under the new name" sh -c \
  "[ \"\$(bash -c '. \"$S/tools/lib.sh\"; sdlc_credential \"$S\" tracker-key')\" = '$HOME/.acme-tracker-key' ]"
before="$(digest "$W")"
bash "$S/tools/install.sh" claude-code >/dev/null 2>&1
check "a second run changes nothing" test "$before" = "$(digest "$W")"
: > "$S/personal/.reinstall-needed"
bash "$S/tools/install.sh" claude-code >/dev/null 2>&1
check "installing again clears the reinstall notice" test ! -e "$S/personal/.reinstall-needed"

printf '{ not json' > "$W/.claude/settings.json"
out="$(bash "$S/tools/install.sh" claude-code 2>&1)"
check "tolerates invalid JSON settings: warns and leaves them" sh -c \
  "[ \"\$(cat '$W/.claude/settings.json')\" = '{ not json' ] && printf '%s' \"\$0\" | grep -q 'not valid JSON'" "$out"

needs kiro
check "kiro: installs alongside" bash "$S/tools/install.sh" kiro
check "kiro: the permissions guard blocks, the message guard records the OK" sh -c \
  "grep -q 'permissions.py check --format exit' '$W/.kiro/hooks/sdlc.json' && grep -q 'log_reminder.py --passes' '$W/.kiro/hooks/sdlc.json'"
check "kiro: its own fingerprint" test -f "$S/personal/.installed-kiro"

# Requirements first: nothing is touched when one is missing.
needs ""
mkdir -p "$T/nossh" "$T/w2"
for c in bash git dirname basename date grep sed uname env cat; do ln -sf "$(command -v $c)" "$T/nossh/$c"; done
ln -sf "$(command -v python3)" "$T/nossh/python3"
cp -R "$KIT" "$T/w2/sdlc-acme"; rm -rf "$T/w2/sdlc-acme/personal"
check "stops before touching anything when a requirement is missing" sh -c \
  "! PATH='$T/nossh' bash '$T/w2/sdlc-acme/tools/install.sh' claude-code && [ ! -e '$T/w2/AGENTS.md' ] && [ ! -e '$T/w2/sdlc-acme/personal' ]"

# The adapters check, on the kit and on a copy where an adapter fell behind.
check "every adapter wires every guard" python3 "$KIT/tools/adapters_check.py"
needs kiro
cp -R "$KIT" "$T/drift"
[ -n "$skipping" ] || python3 - "$T/drift/adapters/kiro/hooks.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
data["hooks"] = [h for h in data["hooks"] if "log_reminder" not in h["action"]["command"]]
json.dump(data, open(sys.argv[1], "w"))
PY
check "an adapter that drops a guard is caught" sh -c \
  "! python3 '$T/drift/tools/adapters_check.py' kiro >/dev/null && python3 '$T/drift/tools/adapters_check.py' kiro | grep -q 'does not run log_reminder.py on message'"

exit $fail
