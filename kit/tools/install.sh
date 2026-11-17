#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Installs the organisation's system in the person's working folder, for the assistant they use.
#
#   tools/install.sh [<assistant>]    claude-code | gemini-cli | kiro | codex | other
#
# Without an argument, the assistant is the one this runs inside, told by its environment.
# Idempotent: running it twice changes nothing the second time. Checks the requirements before
# touching anything, and keeps a copy of whatever it changes in personal/backups/.
set -euo pipefail

SYSTEM="$(cd "$(dirname "$0")/.." && pwd)"
SDLC="$SYSTEM"   # the older name of the same folder, kept for adapters and scripts that use it
WORK="$(dirname "$SYSTEM")"
NAME="$(basename "$SYSTEM")"
STAMP="$(date +%Y%m%d%H%M%S)"
BACKUPS="$SYSTEM/personal/backups"
. "$SYSTEM/tools/lib.sh"

ASSISTANT="${1:-$(gate_assistant)}"
case "$ASSISTANT" in
  -h|--help) sed -n '4,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  "") sed -n '4,11p' "$0" | sed 's/^# \{0,1\}//'
      echo "x Could not tell which assistant this is. Name it: tools/install.sh <assistant>"
      exit 2 ;;
esac
if ! printf '%s' "$ASSISTANT" | grep -Eq '^[a-z0-9][a-z0-9-]*$'; then
  echo "x '$ASSISTANT' is not an assistant id: lowercase letters, digits and hyphens."
  exit 2
fi

# 0. Before touching anything.
if [ "$WORK" = "$HOME" ] || [ "$WORK" = "/" ]; then
  echo "x $NAME sits loose in $WORK. Move it into a working folder first,"
  echo "  for example ~/Projects/<org>/$NAME, and run this again from there."
  exit 1
fi
missing=""
for c in git ssh; do command -v "$c" >/dev/null 2>&1 || missing="$missing $c"; done
PY="$(gate_python)" || missing="$missing python-3.8-or-later"
if [ -n "$missing" ]; then
  echo "x Missing on this machine:$missing. Install them and run this again; nothing was changed."
  exit 1
fi
export SYSTEM SDLC WORK NAME STAMP BACKUPS PY PYTHONUTF8=1

# The working folder inside another repository (a home folder under version control, say) makes
# the assistant treat every working folder below it as one project, and some assistants share
# their automatic memory across it. Not fatal, but the person has to know (GATE section 8).
ENCLOSING="$(git -C "$WORK" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$ENCLOSING" ]; then
  echo "! $WORK is inside the repository $ENCLOSING."
  echo "  The assistant may share state, such as its memory, with every other folder in it,"
  echo "  including another organisation's system. Move the working folder out, or remove that"
  echo "  repository if it was not meant to be there."
fi

# 1. personal/: profile, preferences, grants, log and backups. Ignored by version control.
mkdir -p "$SYSTEM/personal/sessions" "$SYSTEM/personal/grants" "$BACKUPS"
chmod 700 "$SYSTEM/personal/grants" "$BACKUPS"
[ -e "$SYSTEM/personal/profile.md" ] || : > "$SYSTEM/personal/profile.md"
[ -e "$SYSTEM/personal/preferences.md" ] || printf '# My preferences\n' > "$SYSTEM/personal/preferences.md"
[ -e "$SYSTEM/personal/sessions/README.md" ] || printf '# Work log\n\n## Open\n<!-- gate:open -->\n\n## By topic\n' \
  > "$SYSTEM/personal/sessions/README.md"
# An older installer marked the log's open section with sdlc:open.
if grep -q '<!-- sdlc:open -->' "$SYSTEM/personal/sessions/README.md"; then
  sed 's/<!-- sdlc:open -->/<!-- gate:open -->/' "$SYSTEM/personal/sessions/README.md" > "$BACKUPS/.log.$STAMP" \
    && cat "$BACKUPS/.log.$STAMP" > "$SYSTEM/personal/sessions/README.md" && rm -f "$BACKUPS/.log.$STAMP"
fi
grep -qx 'personal/' "$SYSTEM/.gitignore" 2>/dev/null || echo 'personal/' >> "$SYSTEM/.gitignore"

# Older installers left their backups next to the person's files: they move to personal/backups/.
moved=0
for f in "$WORK"/*.bak-* "$WORK"/.*/*.bak-*; do
  [ -f "$f" ] || continue
  rel="${f#"$WORK"/}"
  mv "$f" "$BACKUPS/$(printf '%s' "$rel" | sed 's#/#__#g')" && moved=$((moved + 1))
done
[ "$moved" = 0 ] || echo "OK  $moved older backups moved to $NAME/personal/backups/"

# 2. The working folder's AGENTS.md. The block between the gate markers belongs to the system
#    and is rewritten on every install; whatever is outside it belongs to the person.
# shellcheck disable=SC2086
result="$($PY "$SYSTEM/tools/instructions_block.py" "$WORK/AGENTS.md" "$BACKUPS/AGENTS.md.$STAMP" <<EOF
Read and follow $NAME/AGENTS.md, the organisation's system, in every session.
The person's profile is in $NAME/personal/profile.md and their preferences in
$NAME/personal/preferences.md.
EOF
)"
[ "$result" = unchanged ] || echo "OK  AGENTS.md in the working folder: $NAME block $result"

# 3. The adapter for the person's assistant.
ADAPTER="$SYSTEM/adapters/$ASSISTANT/install.sh"
if [ -f "$ADAPTER" ]; then
  bash "$ADAPTER"
else
  echo "! No automatic adapter for '$ASSISTANT' yet."
  echo "  Follow $NAME/adapters/README.md to wire instructions, skills and guards,"
  echo "  then run the final verification."
fi

# 4. Credentials carry the organisation's name (tools/clients/README.md).
if [ -f "$SYSTEM/tools/clients/credentials" ]; then
  # shellcheck disable=SC2046
  for n in $(gate_migrate_credentials "$SYSTEM" $(grep -v '^[[:space:]]*#' "$SYSTEM/tools/clients/credentials")); do
    echo "OK  credential ~/.$n moved to the organisation's name; the old name links to it"
  done
fi

# 5. The fingerprint the session start guard compares against, to tell when this install is
#    outdated. personal/.installed keeps the last one in the older form, which rename.sh reads.
# shellcheck disable=SC2086
FP="$($PY "$SYSTEM/tools/guards/session_start.py" --fingerprint "$ASSISTANT")"
printf '%s\n' "$FP" > "$SYSTEM/personal/.installed-$ASSISTANT"
printf '%s %s\n' "$FP" "$ASSISTANT" > "$SYSTEM/personal/.installed"
rm -f "$SYSTEM/personal/.reinstall-needed"

echo "OK  $NAME installed in $WORK for $ASSISTANT"
echo "    Open your assistant in $WORK (not inside $NAME) and say hello."
