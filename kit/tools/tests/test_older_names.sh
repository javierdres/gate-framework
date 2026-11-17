#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Tests for an installation made before the identifiers became neutral: it keeps working, the
# installer moves each person's working folder to the new names, and tools/migrate.sh moves the
# repository. On a throwaway working folder with a throwaway home folder.
#
#   bash tools/tests/test_older_names.sh
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
for v in $(env | grep -E '^(CLAUDE|GEMINI|KIRO_|CODEX|GATE_|SDLC_)[A-Za-z_]*=' | cut -d= -f1); do unset "$v"; done
export HOME="$T/home" GIT_CONFIG_GLOBAL="$T/home/.gitconfig" GIT_CONFIG_NOSYSTEM=1 TERM_PROGRAM=
mkdir -p "$HOME"
digest() { (cd "$1" && find . -path ./sdlc-acme/personal/backups -prune -o -path ./sdlc-acme/.git -prune \
  -o \( -type f -o -type l \) -print | LC_ALL=C sort \
  | while read -r f; do printf '%s ' "$f"; if [ -L "$f" ]; then readlink "$f"; else cksum < "$f"; fi; done); }

# The checks that follow need that adapter. bootstrap.py keeps only the one the organisation chose,
# so in a scaffolded system the others are skipped rather than failed.
needs() { if [ -z "$1" ] || [ -d "$S/adapters/$1" ]; then skipping=""; else skipping="$1"; fi; }
# The assistant the older-style environment names: Kiro where its adapter is here.
OLDER=kiro; [ -d "$KIT/adapters/kiro" ] || OLDER=claude-code

# A system and a working folder as an older kit left them.
W="$T/work"; S="$W/sdlc-acme"
mkdir -p "$W"
cp -R "$KIT" "$S"
rm -rf "${S:?}/personal" "${S:?}/.git" "${S:?}/system.yml"
printf 'organisation:\n  name: "Acme"\n  short_name: "acme"\n' > "$S/sdlc.yml"
printf 'tracker-key\n' >> "$S/tools/clients/credentials"
printf '#!/usr/bin/env bash\n. "$SDLC/tools/lib.sh"\ncat "$(sdlc_credential "$SDLC" tracker-key)"\n' > "$S/tools/clients/tracker.sh"
(cd "$S" && git init -q -b main && git add -A && git -c user.email=a@x -c user.name=a commit -qm init)
printf 'old\n' > "$HOME/.tracker-key"
[ -d "$S/adapters/claude-code" ] \
  && printf '# Mine\n\n<!-- sdlc:begin -->\n@sdlc-acme/AGENTS.md\n<!-- sdlc:end -->\n\nMy own line.\n' > "$W/CLAUDE.md"
printf '<!-- sdlc:begin -->\nRead and follow sdlc-acme/AGENTS.md.\n<!-- sdlc:end -->\n' > "$W/AGENTS.md"
mkdir -p "$W/.kiro/hooks" "$W/.kiro/steering" "$W/.claude/skills/onboard" "$S/personal/sessions"
[ "$OLDER" = kiro ] && printf '{"hooks": [{"action": {"command": "python3 sdlc-acme/tools/guards/session_start.py"}}]}\n' \
  > "$W/.kiro/hooks/sdlc.json"
printf 'my own steering, not the kit'"'"'s\n' > "$W/.kiro/steering/sdlc.md"
if [ -d "$S/adapters/claude-code" ]; then
  printf 'old copy\n' > "$W/.claude/skills/onboard/SKILL.md"
  : > "$W/.claude/skills/onboard/.sdlc-copy"
fi
printf '# Work log\n\n## Open\n<!-- sdlc:open -->\n- topic one\n\n## By topic\n' > "$S/personal/sessions/README.md"

# Before anything moves: the older names still work.
check "the older function names still answer" sh -c \
  "[ \"\$(CLAUDECODE=1 SDLC_ASSISTANT=kiro bash -c '. \"$S/tools/lib.sh\"; sdlc_assistant')\" = kiro ]"
check "GATE_ASSISTANT wins over the older SDLC_ASSISTANT" sh -c \
  "[ \"\$(GATE_ASSISTANT=claude-code SDLC_ASSISTANT=kiro bash -c '. \"$S/tools/lib.sh\"; gate_assistant')\" = claude-code ]"
out="$(python3 "$S/tools/guards/session_start.py" 2>&1)"
check "the session start reads sdlc.yml and points the orchestrator to migrate.sh" sh -c \
  "printf '%s' \"\$0\" | grep -q 'tools/migrate.sh'" "$out"
check "and names the older files in the working folder" sh -c \
  "printf '%s' \"\$0\" | grep -q 'Older names in the working folder (.*AGENTS.md.*the log'" "$out"

# Each person: the installer, told the assistant the older way.
SDLC_ASSISTANT=$OLDER bash "$S/tools/install.sh" >/dev/null 2>&1
check "SDLC_ASSISTANT still tells the installer the assistant" test -f "$S/personal/.installed-$OLDER"
check "migrates the older begin and end markers in AGENTS.md" sh -c \
  "grep -qx '<!-- gate:end -->' '$W/AGENTS.md' && ! grep -q 'sdlc:' '$W/AGENTS.md'"
check "the log's open marker moves, with what it held" sh -c \
  "grep -qx '<!-- gate:open -->' '$S/personal/sessions/README.md' && grep -q 'topic one' '$S/personal/sessions/README.md'"
needs kiro
check "kiro: hooks move to gate.json" sh -c "grep -q 'GATE_ASSISTANT=kiro' '$W/.kiro/hooks/gate.json' && [ ! -e '$W/.kiro/hooks/sdlc.json' ]"
check "kiro: the older hooks file is backed up" sh -c "ls '$S'/personal/backups/.kiro__hooks__sdlc.json.*"
check "kiro: a person's own file under the older name stays" grep -q 'my own steering' "$W/.kiro/steering/sdlc.md"
check "kiro: steering written as gate.md" grep -q 'gate:begin' "$W/.kiro/steering/gate.md"
needs claude-code
[ -d "$S/adapters/claude-code" ] && bash "$S/tools/install.sh" claude-code >/dev/null 2>&1
check "migrates the older begin and end markers in CLAUDE.md" sh -c \
  "grep -qx '<!-- gate:begin -->' '$W/CLAUDE.md' && ! grep -q 'sdlc:' '$W/CLAUDE.md' && grep -qx 'My own line.' '$W/CLAUDE.md'"
check "a skill copy marked the older way is replaced by the link" test -L "$W/.claude/skills/onboard"
needs ""
check "the organisation's name is read from sdlc.yml" sh -c "[ -f '$HOME/.acme-tracker-key' ] && [ -L '$HOME/.tracker-key' ]"
check "a client written with \$SDLC and sdlc_credential keeps working" sh -c \
  "[ \"\$(SDLC='$S' bash '$S/tools/clients/tracker.sh')\" = old ]"
out="$(python3 "$S/tools/guards/session_start.py" 2>&1)"
check "nothing older is left in the working folder" sh -c "! printf '%s' \"\$0\" | grep -q 'Older names in the working folder'" "$out"
before="$(digest "$W")"
SDLC_ASSISTANT=$OLDER bash "$S/tools/install.sh" >/dev/null 2>&1
[ -d "$S/adapters/claude-code" ] && bash "$S/tools/install.sh" claude-code >/dev/null 2>&1
check "a second install changes nothing" test "$before" = "$(digest "$W")"

# The orchestrator, once: tools/migrate.sh.
out="$(bash "$S/tools/migrate.sh" 2>&1)"
check "migrate.sh renames sdlc.yml to system.yml" sh -c "[ -f '$S/system.yml' ] && [ ! -e '$S/sdlc.yml' ]"
check "as a staged rename, committing nothing" sh -c \
  "git -C '$S' diff --cached --name-status | grep -q '^R.*sdlc.yml.*system.yml' && [ \"\$(git -C '$S' rev-list --count HEAD)\" = 1 ]"
check "lists the organisation's own files that use an older name" sh -c "printf '%s' \"\$0\" | grep -q 'tools/clients/tracker.sh'" "$out"
check "and not the kit's own" sh -c "! printf '%s' \"\$0\" | grep -qE 'tools/lib.sh|tools/guards/'" "$out"
out="$(python3 "$S/tools/guards/session_start.py" 2>&1)"
check "the session start stops pointing to migrate.sh" sh -c "! printf '%s' \"\$0\" | grep -q 'tools/migrate.sh'" "$out"
check "a second migrate.sh changes nothing" sh -c \
  "bash '$S/tools/migrate.sh' | grep -q 'already system.yml' && git -C '$S' diff --cached --name-status | grep -c . | grep -qx 1"

exit $fail
