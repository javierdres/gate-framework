#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Installs the organisation's SDLC in the person's working folder, for the assistant they use.
#
#   tools/install.sh <assistant>      claude-code | gemini-cli | kiro | codex | other
#
# Idempotent: running it twice changes nothing the second time. Backs up whatever it modifies.
# Stops if the SDLC repository sits loose in the home folder.
set -euo pipefail

ASSISTANT="${1:-}"
SDLC="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(dirname "$SDLC")"
NAME="$(basename "$SDLC")"
STAMP="$(date +%Y%m%d%H%M%S)"

if [ -z "$ASSISTANT" ]; then
  sed -n '4,9p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi
if [ "$WORK" = "$HOME" ]; then
  echo "x $NAME sits loose in the home folder. Move it into a working folder first,"
  echo "  for example ~/Projects/<org>/$NAME, and run this again from there."
  exit 1
fi

backup() { [ -e "$1" ] && cp -p "$1" "$1.bak-$STAMP" || true; }

# 1. personal/: profile, preferences, grants and log. Ignored by version control.
mkdir -p "$SDLC/personal/sessions" "$SDLC/personal/grants"
chmod 700 "$SDLC/personal/grants"
[ -e "$SDLC/personal/profile.md" ] || : > "$SDLC/personal/profile.md"
[ -e "$SDLC/personal/preferences.md" ] || printf '# My preferences\n' > "$SDLC/personal/preferences.md"
[ -e "$SDLC/personal/sessions/README.md" ] || printf '# Work log\n\n## Open\n\n## By topic\n' \
  > "$SDLC/personal/sessions/README.md"
grep -qx 'personal/' "$SDLC/.gitignore" 2>/dev/null || echo 'personal/' >> "$SDLC/.gitignore"

# 2. The working folder's AGENTS.md, without touching what it already has.
MARK="<!-- sdlc:$NAME -->"
if ! grep -qF "$MARK" "$WORK/AGENTS.md" 2>/dev/null; then
  backup "$WORK/AGENTS.md"
  {
    echo ""
    echo "$MARK"
    echo "Read and follow $NAME/AGENTS.md, the organisation's SDLC, in every session."
    echo "The person's profile is in $NAME/personal/profile.md and their preferences in"
    echo "$NAME/personal/preferences.md."
  } >> "$WORK/AGENTS.md"
fi

# 3. The adapter for the person's assistant.
ADAPTER="$SDLC/adapters/$ASSISTANT/install.sh"
if [ -x "$ADAPTER" ]; then
  SDLC="$SDLC" WORK="$WORK" NAME="$NAME" STAMP="$STAMP" "$ADAPTER"
else
  echo "! No automatic adapter for '$ASSISTANT' yet."
  echo "  Follow $NAME/adapters/README.md to wire instructions, skills and guards,"
  echo "  then run the final verification."
fi

echo "OK  $NAME installed in $WORK for $ASSISTANT"
echo "    Open your assistant in $WORK (not inside $NAME) and say hello."
