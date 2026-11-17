#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Kiro adapter. Called by tools/install.sh with SDLC, WORK, NAME, STAMP, BACKUPS and PY set.
# Taken from Kiro's public documentation (steering, hooks, skills) and not yet verified on a real
# installation: check every name against the Kiro version recorded in sdlc.yml.
#
# Kiro's hooks can only let an action through or block it, so the permissions guard runs with
# `--format exit` and the per-message guard records the person's typed OK (`--passes`).
set -euo pipefail
. "$SDLC/tools/lib.sh"
HERE="$SDLC/adapters/kiro"
KIRO="$WORK/.kiro"
mkdir -p "$KIRO/steering" "$KIRO/skills" "$KIRO/hooks"

# Writes a file of the system's own from a template, with the system's name and the Python command.
# A file with the same name that the system did not write (no sdlc marker) is left alone.
place() {  # place <template> <destination> <marker that proves it is ours>
  local tmp="$2.sdlc-new"
  sed -e "s#__NAME__#$NAME#g" -e "s#__PY__#$PY#g" "$1" > "$tmp"
  if [ -f "$2" ] && ! grep -q "$3" "$2"; then
    rm -f "$tmp"; echo "! ${2#"$WORK"/} in the working folder is not $NAME's; left untouched"; return 0
  fi
  if [ -f "$2" ] && cmp -s "$tmp" "$2"; then rm -f "$tmp"; return 0; fi
  [ -f "$2" ] && sdlc_backup "$SDLC" "$WORK" "$2" "$STAMP"
  mv "$tmp" "$2"
  echo "OK  ${2#"$WORK"/} written"
}

# Instructions: a steering file that loads AGENTS.md and the person's files in every session.
place "$HERE/steering.md" "$KIRO/steering/sdlc.md" 'sdlc:begin'

# Skills, linked like the other assistants'.
for dir in "$SDLC"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  skill="$(basename "$dir")"
  set +e; sdlc_skill "$dir" "$KIRO/skills/$skill" "../../$NAME/skills/$skill"; r=$?; set -e
  case "$r" in
    0) ;;
    2) echo "! .kiro/skills/$skill in the working folder is not $NAME's; left untouched" ;;
    *) echo "! Could not install the skill $skill" ;;
  esac
done
for skill in $(sdlc_prune_skills "$SDLC" "$KIRO/skills"); do
  echo "OK  skill $skill removed: $NAME no longer has it"
done

# Hooks: a file of the system's own, rewritten on every install. On Windows, Kiro runs hooks with
# cmd.exe, where the first bash on the PATH may be WSL's, which sees neither the person's tools
# nor their credentials: Git Bash goes first on the hooks' PATH.
hooks="$HERE/hooks.json"
if [ "$(sdlc_os)" = windows ] && command -v cygpath >/dev/null 2>&1; then
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
place "$hooks" "$KIRO/hooks/sdlc.json" 'tools/guards/session_start.py'
rm -f "$BACKUPS/.kiro-hooks.json.tmp"

echo "OK  Kiro adapter: steering, skills and hooks in $WORK/.kiro"
