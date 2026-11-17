#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Claude Code adapter. Called by tools/install.sh with SDLC, WORK, NAME, STAMP, BACKUPS and PY
# set. Verify the hook event names against the Claude Code version recorded in sdlc.yml.
set -euo pipefail
. "$SDLC/tools/lib.sh"

# Instructions: CLAUDE.md in the working folder imports the neutral AGENTS.md and the person's
# files. The block between the sdlc markers is rewritten on every install.
# shellcheck disable=SC2086
result="$($PY "$SDLC/tools/instructions_block.py" "$WORK/CLAUDE.md" "$BACKUPS/CLAUDE.md.$STAMP" <<EOF
@$NAME/AGENTS.md
@$NAME/personal/profile.md
@$NAME/personal/preferences.md
EOF
)"
[ "$result" = unchanged ] || echo "OK  CLAUDE.md in the working folder: $NAME block $result"

# Skills: linked one by one, so the person's own skills stay untouched. A folder of the person's
# with the same name as one of the system's is left alone, with a warning.
mkdir -p "$WORK/.claude/skills"
linked=0; copied=0
for dir in "$SDLC"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  skill="$(basename "$dir")"
  dest="$WORK/.claude/skills/$skill"
  set +e; sdlc_skill "$dir" "$dest" "../../$NAME/skills/$skill"; r=$?; set -e
  case "$r" in
    0) if [ -L "$dest" ]; then linked=$((linked + 1)); else copied=$((copied + 1)); fi ;;
    2) echo "! .claude/skills/$skill in the working folder is not $NAME's; left untouched. Rename yours to use the one from $NAME." ;;
    *) echo "! Could not install the skill $skill" ;;
  esac
done
for skill in $(sdlc_prune_skills "$SDLC" "$WORK/.claude/skills"); do
  echo "OK  skill $skill removed: $NAME no longer has it"
done
[ "$copied" = 0 ] || echo "OK  $copied skills copied, as links are not available here; each session refreshes them"

# Guards and base permission rules, merged into the working folder's settings.
# shellcheck disable=SC2086
$PY - "$WORK/.claude/settings.json" "$NAME" "$PY" "$BACKUPS/.claude__settings.json.$STAMP" \
  "$SDLC/adapters/claude-code/settings.json" <<'PY'
import io, json, os, shutil, sys
path, name, py, backup, base_path = sys.argv[1:6]
try:
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f) if os.path.getsize(path) else {}
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
except FileNotFoundError:
    data = {}
except ValueError as e:
    print("! .claude/settings.json in the working folder is not valid JSON (%s); left untouched. "
          "Fix it and run the installer again." % e)
    sys.exit(0)
before = json.dumps(data, sort_keys=True)
hooks = data.setdefault("hooks", {})
guard = '%s "$CLAUDE_PROJECT_DIR/%s/tools/guards/%%s"' % (py, name)
# Hooks go through the project folder Claude Code was opened in, so moving or renaming the
# working folder does not break them. A branch of the system without the script never breaks the
# session: the tolerant ones end in `|| true`, and the permissions guard steps aside when its
# script is missing. `shell` keeps Claude Code on Windows from running them in PowerShell.
tolerant = lambda script, args="": "%s%s 2>/dev/null || true" % (guard % script, args)
WANTED = (
    ("SessionStart", None, "session_start.py", tolerant("session_start.py"), 30),
    ("UserPromptSubmit", None, "log_reminder.py", tolerant("log_reminder.py"), 5),
    ("UserPromptSubmit", None, "usage.py", tolerant("usage.py", " check --format claude"), 5),
    ("PreToolUse", "Bash|mcp__.*|Write|Edit|MultiEdit|NotebookEdit", "permissions.py",
     '[ -f "$CLAUDE_PROJECT_DIR/%s/tools/guards/permissions.py" ] || exit 0; %s check --format claude'
     % (name, guard % "permissions.py"), 10),
)
ours = lambda command, script: ("tools/guards/" + script) in command.replace("\\", "/")
scripts = {w[2] for w in WANTED}
# A guard an older installer registered on an event it no longer belongs to goes away.
for event, entries in hooks.items():
    for e in entries:
        e["hooks"] = [h for h in e.get("hooks", []) if not any(
            ours(h.get("command", ""), s) and (event, s) not in {(w[0], w[2]) for w in WANTED} for s in scripts)]
    entries[:] = [e for e in entries if e.get("hooks")]
for event, matcher, script, command, timeout in WANTED:
    entries = hooks.setdefault(event, [])
    hook = {"type": "command", "command": command, "timeout": timeout, "shell": "bash"}
    placed = False
    for e in entries:
        kept = []
        for h in e.get("hooks", []):
            if not ours(h.get("command", ""), script):
                kept.append(h)
            elif not placed:
                # Replaced in place, which also brings older absolute-path entries up to date.
                kept.append(hook)
                placed = True
                if matcher:
                    e["matcher"] = matcher
        e["hooks"] = kept
    entries[:] = [e for e in entries if e.get("hooks")]
    if not placed:
        entries.append(dict({"matcher": matcher} if matcher else {}, hooks=[hook]))
# Base rules that always ask, merged with the person's own. RETIRED lists rules an older base
# asked for and the permissions guard decides now: left in place, they would ask even after a
# session authorisation.
RETIRED = set()
with io.open(base_path, encoding="utf-8") as f:
    base = json.load(f).get("permissions", {}).get("ask", [])
ask = data.setdefault("permissions", {}).setdefault("ask", [])
ask[:] = [r for r in ask if r not in RETIRED or r in base]
ask += [r for r in base if r not in ask]
# The usage status line; session.py also refreshes it at every session start.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(base_path))
import session
session.register(data, name, py)
if json.dumps(data, sort_keys=True) != before:
    if os.path.exists(path):
        os.makedirs(os.path.dirname(backup), exist_ok=True)
        shutil.copy2(path, backup)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("OK  .claude/settings.json in the working folder: guards, base rules and status line up to date")
PY

echo "OK  Claude Code adapter: CLAUDE.md, skills and guards in $WORK"
