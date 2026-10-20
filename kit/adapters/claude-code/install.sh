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
  [ -e "$WORK/CLAUDE.md" ] && cp -p "$WORK/CLAUDE.md" "$WORK/CLAUDE.md.bak-$STAMP"
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
[ -e "$SETTINGS" ] && cp -p "$SETTINGS" "$SETTINGS.bak-$STAMP"
python3 - "$SETTINGS" "$SDLC" <<'PY'
import io, json, os, sys
path, sdlc = sys.argv[1], sys.argv[2]
data = json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {}
hooks = data.setdefault("hooks", {})
guards = os.path.join(sdlc, "tools", "guards")
wanted = {
    "SessionStart": (None, "python3 %s/session_start.py" % guards),
    "UserPromptSubmit": (None, "python3 %s/log_reminder.py" % guards),
    "PreToolUse": ("Bash|mcp__.*", "python3 %s/permissions.py check --format claude" % guards),
}
for event, (matcher, command) in wanted.items():
    entries = hooks.setdefault(event, [])
    if any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
        continue
    entry = {"hooks": [{"type": "command", "command": command}]}
    if matcher:
        entry["matcher"] = matcher
    entries.append(entry)
io.open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2) + "\n")
PY
echo "OK  Claude Code adapter: CLAUDE.md, skills and guards in $WORK"
