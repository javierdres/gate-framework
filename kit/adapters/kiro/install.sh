#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Kiro adapter. Called by tools/install.sh with SYSTEM, WORK, NAME, STAMP, BACKUPS and PY set.
# Taken from Kiro's public documentation (steering, hooks, skills) and not yet verified on a real
# installation: check every name against the Kiro version recorded in system.yml.
#
# Kiro's hooks can only let an action through or block it, so the permissions guard runs with
# `--format exit` and the per-message guard records the person's typed OK (`--passes`).
set -euo pipefail
SYSTEM="${SYSTEM:-$SDLC}"
. "$SYSTEM/tools/lib.sh"
HERE="$SYSTEM/adapters/kiro"
KIRO="$WORK/.kiro"
mkdir -p "$KIRO/steering" "$KIRO/skills" "$KIRO/hooks"

# Writes a file of the system's own from a template, with the system's name and the Python command.
# A file with the same name that the system did not write (no gate marker) is left alone.
place() {  # place <template> <destination> <marker that proves it is ours>
  local tmp="$2.gate-new"
  sed -e "s#__NAME__#$NAME#g" -e "s#__PY__#$PY#g" "$1" > "$tmp"
  if [ -f "$2" ] && ! grep -q "$3" "$2"; then
    rm -f "$tmp"; echo "! ${2#"$WORK"/} in the working folder is not $NAME's; left untouched"; return 0
  fi
  if [ -f "$2" ] && cmp -s "$tmp" "$2"; then rm -f "$tmp"; return 0; fi
  [ -f "$2" ] && gate_backup "$SYSTEM" "$WORK" "$2" "$STAMP"
  mv "$tmp" "$2"
  echo "OK  ${2#"$WORK"/} written"
}

# An older installer wrote sdlc.md and sdlc.json. Each goes away only when it carries the kit's
# marker; anything else with that name is the person's.
retire() {  # retire <older file> <marker that proves it was ours>
  [ -f "$1" ] && grep -q "$2" "$1" || return 0
  gate_backup "$SYSTEM" "$WORK" "$1" "$STAMP"
  rm -f "$1"
  echo "OK  ${1#"$WORK"/} replaced by its gate.* file"
}

# Instructions: a steering file that loads AGENTS.md and the person's files in every session.
place "$HERE/steering.md" "$KIRO/steering/gate.md" 'gate:begin'
retire "$KIRO/steering/sdlc.md" 'sdlc:begin'

# Skills, linked like the other assistants'.
for dir in "$SYSTEM"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  skill="$(basename "$dir")"
  set +e; gate_skill "$dir" "$KIRO/skills/$skill" "../../$NAME/skills/$skill"; r=$?; set -e
  case "$r" in
    0) ;;
    2) echo "! .kiro/skills/$skill in the working folder is not $NAME's; left untouched" ;;
    *) echo "! Could not install the skill $skill" ;;
  esac
done
for skill in $(gate_prune_skills "$SYSTEM" "$KIRO/skills"); do
  echo "OK  skill $skill removed: $NAME no longer has it"
done

# Hooks: a file of the system's own, rewritten on every install. On Windows, Kiro runs hooks with
# cmd.exe, where the first bash on the PATH may be WSL's, which sees neither the person's tools
# nor their credentials: Git Bash goes first on the hooks' PATH.
hooks="$HERE/hooks.json"
if [ "$(gate_os)" = windows ] && command -v cygpath >/dev/null 2>&1; then
  hooks="$BACKUPS/.kiro-hooks.json.tmp"
  # shellcheck disable=SC2086
  GITBASH="$(cygpath -w "$(dirname "$(command -v bash)")")" $PY - "$HERE/hooks.json" "$hooks" <<'PY'
import io, json, os, sys
with io.open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
prefix = 'set "PATH=%s;%%PATH%%" && ' % os.environ["GITBASH"]
for h in data.get("hooks", []):
    action = h.get("action", {})
    if action.get("command", "").startswith("bash -c "):
        action["command"] = prefix + action["command"]
with io.open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(data, indent=2) + "\n")
PY
fi
place "$hooks" "$KIRO/hooks/gate.json" 'tools/guards/session_start.py'
retire "$KIRO/hooks/sdlc.json" 'tools/guards/session_start.py'
rm -f "$BACKUPS/.kiro-hooks.json.tmp"

echo "OK  Kiro adapter: steering, skills and hooks in $WORK/.kiro"
