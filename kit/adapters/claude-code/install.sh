#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Claude Code adapter. Called by tools/install.sh with SDLC, WORK, NAME and STAMP set.
# Verify the hook event names against the Claude Code version recorded in sdlc.yml.
set -euo pipefail

# Instructions: CLAUDE.md in the working folder imports the neutral AGENTS.md files.
MARK="<!-- sdlc:$NAME -->"
if ! grep -qF "$MARK" "$WORK/CLAUDE.md" 2>/dev/null; then
  if [ -e "$WORK/CLAUDE.md" ]; then cp -p "$WORK/CLAUDE.md" "$WORK/CLAUDE.md.bak-$STAMP"; fi
  {
    echo ""
    echo "$MARK"
    echo "@$NAME/AGENTS.md"
    echo "@$NAME/personal/profile.md"
    echo "@$NAME/personal/preferences.md"
  } >> "$WORK/CLAUDE.md"
fi

# Skills: linked one by one, so the person's own skills stay untouched.
mkdir -p "$WORK/.claude/skills"
for dir in "$SDLC"/skills/*/; do
  [ -f "$dir/SKILL.md" ] || continue
  skill="$(basename "$dir")"
  [ -e "$WORK/.claude/skills/$skill" ] || ln -s "$dir" "$WORK/.claude/skills/$skill" 2>/dev/null \
    || cp -R "$dir" "$WORK/.claude/skills/$skill"
done

# Guards: merged into the working folder's settings, never duplicated.
SETTINGS="$WORK/.claude/settings.json"
python3 - "$SETTINGS" "$SDLC" "$STAMP" <<'PY'
import io, json, os, shlex, shutil, sys
path, sdlc, stamp = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {}
before = json.dumps(data, sort_keys=True)
hooks = data.setdefault("hooks", {})
guards = os.path.join(sdlc, "tools", "guards")
q = lambda name: shlex.quote(os.path.join(guards, name))
wanted = {
    "SessionStart": (None, "python3 %s" % q("session_start.py")),
    "UserPromptSubmit": (None, "python3 %s" % q("log_reminder.py")),
    "PreToolUse": ("Bash|mcp__.*|Write|Edit|MultiEdit|NotebookEdit", "python3 %s check --format claude" % q("permissions.py")),
}
for event, (matcher, command) in wanted.items():
    entries = hooks.setdefault(event, [])
    if any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
        continue
    entry = {"hooks": [{"type": "command", "command": command}]}
    if matcher:
        entry["matcher"] = matcher
    entries.append(entry)
if json.dumps(data, sort_keys=True) != before:
    if os.path.exists(path):
        shutil.copy2(path, "%s.bak-%s" % (path, stamp))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2) + "\n")
PY
echo "OK  Claude Code adapter: CLAUDE.md, skills and guards in $WORK"
