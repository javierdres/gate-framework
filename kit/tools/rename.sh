#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Renames this system in the person's working folder, once, after the orchestrator changed its
# name in sdlc.yml. Run it in a terminal with the assistant closed: the assistant runs from this
# folder, and moving it under an open session breaks that session.
#
#   tools/rename.sh                 takes the new name from system.name in sdlc.yml
#   tools/rename.sh <new name>      the orchestrator, renaming it before changing sdlc.yml
#
# Moves the folder, rewrites what the installer wrote in the working folder for the old name
# (the instructions block, the assistant's hooks and status line, the skill links), points the
# remote at the new repository name and installs again. Backs up every file it rewrites.
# Idempotent: with the folder already renamed it only repairs the working folder.
set -euo pipefail

OLD_SDLC="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(dirname "$OLD_SDLC")"
OLD="$(basename "$OLD_SDLC")"
STAMP="$(date +%Y%m%d%H%M%S)"

NEW="${1:-}"
if [ -z "$NEW" ]; then
  NEW="$(sed -n '/^system:/,/^[^ ]/s/^  name:[ ]*"\{0,1\}\([a-z0-9-]*\)"\{0,1\}.*/\1/p' "$OLD_SDLC/sdlc.yml" 2>/dev/null | head -1)"
fi
if [ -z "$NEW" ]; then
  sed -n '4,15p' "$0" | sed 's/^# \{0,1\}//'
  echo "x sdlc.yml declares no system.name, and no new name was given."
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

# The assistant the person installed for, to install again under the new name.
ASSISTANT="$(cut -d' ' -f2 "$OLD_SDLC/personal/.installed" 2>/dev/null || true)"

# 1. The folder. personal/ (profile, log, grants) travels with it.
mv "$WORK/$OLD" "$WORK/$NEW"
SDLC="$WORK/$NEW"
echo "OK  $OLD moved to $NEW"

# 2. What the installer wrote in the working folder for the old name. Only the lines that point
#    into the old folder change; whatever the person wrote stays as it was.
python3 - "$WORK" "$OLD" "$NEW" "$STAMP" <<'PY'
import io, os, re, shutil, sys
work, old, new, stamp = sys.argv[1:5]
pattern = re.compile(r"(?<![\w.-])%s(?=/)|(?<=<!-- sdlc:)%s(?= -->)" % (re.escape(old), re.escape(old)))
candidates = [os.path.join(work, f) for f in os.listdir(work) if f.endswith(".md")]
for folder in (".claude", ".gemini", ".kiro", ".codex", ".agents"):
    base = os.path.join(work, folder)
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("skills", "projects", "cache")]
        candidates += [os.path.join(root, f) for f in files
                       if f.endswith((".json", ".md", ".toml", ".yml", ".yaml")) and ".bak-" not in f]
changed = []
for path in candidates:
    try:
        text = io.open(path, encoding="utf-8").read()
    except Exception:
        continue
    out = pattern.sub(new, text)
    if out != text:
        shutil.copy2(path, "%s.bak-%s" % (path, stamp))
        io.open(path, "w", encoding="utf-8").write(out)
        changed.append(os.path.relpath(path, work))
print("OK  rewritten for the new name: %s" % (", ".join(changed) if changed else "nothing pointed at the old one"))
PY

# 3. Skill links that pointed into the old folder are dangling now; the installer recreates them.
for base in "$WORK"/.claude/skills "$WORK"/.gemini/skills "$WORK"/.kiro/skills "$WORK"/.agents/skills; do
  [ -d "$base" ] || continue
  for link in "$base"/*; do
    if [ -L "$link" ] && [ ! -e "$link" ]; then rm "$link"; fi
  done
done

# 4. The remote. Code platforms redirect a renamed repository for a while, not forever.
URL="$(git -C "$SDLC" remote get-url origin 2>/dev/null || true)"
if [ -n "$URL" ] && printf '%s' "$URL" | grep -q "/$OLD\(\.git\)\{0,1\}$"; then
  NEW_URL="$(printf '%s' "$URL" | sed "s#/$OLD\(\.git\)\{0,1\}\$#/$NEW\1#")"
  git -C "$SDLC" remote set-url origin "$NEW_URL"
  echo "OK  remote now $NEW_URL"
fi

# 5. Install again, so links, hooks and the install stamp all carry the new name.
if [ -n "$ASSISTANT" ] && [ -x "$SDLC/tools/install.sh" ]; then
  "$SDLC/tools/install.sh" "$ASSISTANT"
else
  echo "! Not installed before. Run $NEW/tools/install.sh <assistant> when ready."
fi

echo
echo "Done. Open your assistant in $WORK again and say hello: it now loads $NEW."
echo "The backups end in .bak-$STAMP; delete them once everything works."
