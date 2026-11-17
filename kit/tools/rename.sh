#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Renames this system in the person's working folder, once, after the orchestrator changed its
# name in system.yml. Run it in a terminal with the assistant closed: the assistant runs from this
# folder, and moving it under an open session breaks that session.
#
#   tools/rename.sh                 takes the new name from system.name in system.yml
#   tools/rename.sh <new name>      the orchestrator, renaming it before changing system.yml
#
# Moves the folder, points the remote at the new repository name and installs again for every
# assistant installed before. The installer does the rest: the instructions block sits between
# name-independent markers and is rewritten, the guards are found by their script and pointed
# at the new folder, and the skill links are made again. Its backups go to personal/backups/.
# Idempotent: with the folder already renamed it only repairs the working folder.
set -euo pipefail

OLD_SYSTEM="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(dirname "$OLD_SYSTEM")"
OLD="$(basename "$OLD_SYSTEM")"

NEW="${1:-}"
if [ -z "$NEW" ]; then
  . "$OLD_SYSTEM/tools/lib.sh"
  NEW="$(sed -n '/^system:/,/^[^ ]/s/^  name:[ ]*"\{0,1\}\([a-z0-9-]*\)"\{0,1\}.*/\1/p' "$(gate_config "$OLD_SYSTEM")" \
    2>/dev/null | head -1)"
fi
if [ -z "$NEW" ]; then
  sed -n '4,16p' "$0" | sed 's/^# \{0,1\}//'
  echo "x system.yml declares no system.name, and no new name was given."
  exit 2
fi
if ! printf '%s' "$NEW" | grep -Eq '^[a-z0-9][a-z0-9-]{1,62}$'; then
  echo "x '$NEW' is not a usable name: lowercase letters, digits and hyphens only."
  exit 2
fi
if [ "$NEW" = "$OLD" ]; then
  echo "OK  this system is already called $NEW. Nothing to do."
  exit 0
fi
if [ -e "$WORK/$NEW" ]; then
  echo "x $WORK/$NEW already exists. Move it out of the way first; nothing was changed."
  exit 1
fi
if [ -n "${CLAUDECODE:-}${GEMINI_CLI:-}${CODEX_SANDBOX:-}" ]; then
  echo "x This looks like a session of the assistant. Close it, open a terminal, and run this again."
  exit 1
fi

# The assistants the person installed for, to install again under the new name.
ASSISTANTS=""
for f in "$OLD_SYSTEM"/personal/.installed-*; do
  [ -f "$f" ] && ASSISTANTS="$ASSISTANTS ${f##*/.installed-}"
done
[ -n "$ASSISTANTS" ] || ASSISTANTS="$(cut -d' ' -f2 "$OLD_SYSTEM/personal/.installed" 2>/dev/null || true)"

# 1. The folder. personal/ (profile, log, grants, backups) travels with it.
mv "$WORK/$OLD" "$WORK/$NEW"
SYSTEM="$WORK/$NEW"
echo "OK  $OLD moved to $NEW"

# 2. Skill links that pointed into the old folder are dangling now; the installer makes them
#    again, and for an assistant without an automatic adapter they would only mislead.
for base in "$WORK"/.claude/skills "$WORK"/.gemini/skills "$WORK"/.kiro/skills "$WORK"/.agents/skills "$WORK"/.codex/skills; do
  [ -d "$base" ] || continue
  for link in "$base"/*; do
    if [ -L "$link" ] && [ ! -e "$link" ]; then rm "$link"; fi
  done
done

# 3. The remote. Code platforms redirect a renamed repository for a while, not forever.
URL="$(git -C "$SYSTEM" remote get-url origin 2>/dev/null || true)"
if [ -n "$URL" ] && printf '%s' "$URL" | grep -q "/$OLD\(\.git\)\{0,1\}$"; then
  NEW_URL="$(printf '%s' "$URL" | sed "s#/$OLD\(\.git\)\{0,1\}\$#/$NEW\1#")"
  git -C "$SYSTEM" remote set-url origin "$NEW_URL"
  echo "OK  remote now $NEW_URL"
fi

# 4. Install again, so the instructions block, the guards, the status line and the skills all
#    carry the new name.
if [ -n "$ASSISTANTS" ] && [ -f "$SYSTEM/tools/install.sh" ]; then
  for assistant in $ASSISTANTS; do
    bash "$SYSTEM/tools/install.sh" "$assistant"
  done
else
  echo "! Not installed before. Run $NEW/tools/install.sh <assistant> when ready."
fi

# 5. Whatever still names the old folder was written by hand or by an adapter that is not
#    automated yet. It is not rewritten: the person fixes it, knowing where.
left="$(cd "$WORK" && grep -rlsF "$OLD/" --exclude-dir=skills --exclude-dir=projects --exclude-dir=cache \
  ./*.md .claude .gemini .kiro .codex .agents 2>/dev/null | sed 's#^\./##' || true)"
if [ -n "$left" ]; then
  echo "! These files still name $OLD/; update them by hand:"
  printf '%s\n' "$left" | sed 's/^/    /'
fi

echo
echo "Done. Open your assistant in $WORK again and say hello: it now loads $NEW."
echo "What the installer replaced is in $NEW/personal/backups/; delete it once everything works."
