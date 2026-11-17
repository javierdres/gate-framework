# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Shared functions for the system's shell scripts, so they behave the same on macOS, Linux and
# Windows (Git Bash or WSL). Load it with `. tools/lib.sh`: it runs nothing on its own.

# The operating system: mac, linux (WSL included), windows (Git Bash, MSYS, Cygwin) or other.
sdlc_os() {
  case "$(uname -s 2>/dev/null)" in
    Darwin)               echo mac ;;
    Linux)                echo linux ;;
    MINGW*|MSYS*|CYGWIN*) echo windows ;;
    *)                    echo other ;;
  esac
}

# The command that runs Python 3.8 or later, or nothing. On Windows it is usually `python` or
# `py -3`, and `python3` may be the Microsoft Store shortcut, which exists but runs nothing: each
# candidate is run, not just looked up.
sdlc_python() {
  local c
  for c in python3 python "py -3"; do
    # shellcheck disable=SC2086
    if $c -c 'import sys; sys.exit(sys.version_info < (3, 8))' >/dev/null 2>&1; then
      echo "$c"; return 0
    fi
  done
  return 1
}

# A Windows path (C:\Users\...) in bash form (/c/Users/...), so two paths can be compared.
# Unchanged on macOS and Linux.
sdlc_path() {
  if command -v cygpath >/dev/null 2>&1; then cygpath -u "$1" 2>/dev/null || echo "$1"
  else echo "$1"; fi
}

# The assistant running this script, from the variables each one sets, or nothing. An adapter's
# hooks may declare it with SDLC_ASSISTANT, which wins. The variables are the ones each
# assistant documents today; check them against the version in use.
sdlc_assistant() {
  if [ -n "${SDLC_ASSISTANT:-}" ]; then echo "$SDLC_ASSISTANT"; return; fi
  if [ -n "${CLAUDECODE:-}${CLAUDE_PROJECT_DIR:-}" ]; then echo claude-code; return; fi
  if [ -n "${GEMINI_CLI:-}" ]; then echo gemini-cli; return; fi
  case "${TERM_PROGRAM:-}" in [Kk]iro*) echo kiro; return ;; esac
  if env 2>/dev/null | grep -q '^KIRO_'; then echo kiro; return; fi
  if [ -n "${CODEX_SANDBOX:-}${CODEX_HOME:-}" ]; then echo codex; return; fi
  return 0
}

# Where the installer and rename.sh keep what they replace: personal/backups/, which version
# control ignores, never next to the person's files in the working folder. The backup is named
# after the file's path in the working folder. Usage: sdlc_backup <sdlc> <work> <file> <stamp>
sdlc_backup() {
  local dir="$1/personal/backups" rel
  [ -e "$3" ] || return 0
  mkdir -p "$dir"
  rel="${3#"$2"/}"
  cp -p "$3" "$dir/$(printf '%s' "$rel" | sed 's#/#__#g').$4"
}

# A skill of the system made available where the assistant looks for skills. It is linked, so each
# update of the system reaches it; the link is relative, so it survives the working folder being
# moved. Where links fail (Windows without developer mode), it is copied and the copy is marked
# with .sdlc-copy, so the session start guard refreshes it. A folder with the same name that did
# not come from the system is never touched: returns 2.
# Usage: sdlc_skill <skill folder in the system> <destination> <relative link target>
sdlc_skill() {
  local src="${1%/}" dest="$2" rel="$3" name
  name="$(basename "$src")"
  if [ -L "$dest" ]; then
    case "$(readlink "$dest")" in
      "$rel") return 0 ;;
      */skills/"$name"|*/skills/"$name"/) rm -f "$dest" ;;
      *) return 2 ;;
    esac
  elif [ -e "$dest/.sdlc-copy" ]; then
    rm -rf "$dest"
  elif [ -e "$dest" ]; then
    return 2
  fi
  if [ "$(sdlc_os)" = windows ]; then
    MSYS=winsymlinks:nativestrict ln -s "$rel" "$dest" 2>/dev/null
  else
    ln -s "$rel" "$dest" 2>/dev/null
  fi
  [ -L "$dest" ] && [ -e "$dest/SKILL.md" ] && return 0
  rm -rf "$dest"
  cp -R "$src" "$dest" && : > "$dest/.sdlc-copy"
}

# Removes the links and marked copies of skills the system no longer has. Anything else in the
# folder is the person's and stays. Prints the name of each one removed.
# Usage: sdlc_prune_skills <sdlc> <skills folder of the assistant>
sdlc_prune_skills() {
  local sdlc="$1" dir="$2" entry name
  [ -d "$dir" ] || return 0
  for entry in "$dir"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    name="$(basename "$entry")"
    [ -f "$sdlc/skills/$name/SKILL.md" ] && continue
    if [ -L "$entry" ]; then
      case "$(readlink "$entry")" in */skills/"$name"|*/skills/"$name"/) rm -f "$entry"; echo "$name" ;; esac
    elif [ -e "$entry/.sdlc-copy" ]; then
      rm -rf "$entry"; echo "$name"
    fi
  done
}

# The organisation's short name from sdlc.yml, used in credential and folder names.
sdlc_org() {
  sed -n '/^organisation:/,/^[^ #]/s/^  short_name:[ ]*"\{0,1\}\([A-Za-z0-9_-]*\)"\{0,1\}.*/\1/p' \
    "$1/sdlc.yml" 2>/dev/null | head -1
}

# Each person's credentials live in their home folder with permissions 0600, named after the
# organisation (~/.<org>-tracker-key), so another organisation's system on the same machine never
# reads them. An older installation may have used the generic name (~/.tracker-key): the new
# name is read first and the old one is the fallback. Usage: sdlc_credential <sdlc> <name>
sdlc_credential() {
  local org
  org="$(sdlc_org "$1")"
  if [ -n "$org" ] && [ -e "$HOME/.$org-$2" ]; then echo "$HOME/.$org-$2"; else echo "$HOME/.$2"; fi
}

# Moves each credential with the old generic name to the organisation's name and leaves a link
# at the old one, so the person's own tools that still read it keep working. On Windows nothing
# moves: Git Bash cannot create links there, and sdlc_credential's fallback is enough. Prints
# each one moved. Usage: sdlc_migrate_credentials <sdlc> <name>...
sdlc_migrate_credentials() {
  local sdlc="$1" org n old new
  shift
  org="$(sdlc_org "$sdlc")"
  [ -n "$org" ] || return 0
  [ "$(sdlc_os)" = windows ] && return 0
  for n in "$@"; do
    old="$HOME/.$n" new="$HOME/.$org-$n"
    if [ -f "$old" ] && [ ! -L "$old" ] && [ ! -e "$new" ]; then
      mv "$old" "$new" && chmod 600 "$new" && ln -s ".$org-$n" "$old" && echo "$n"
    fi
  done
  return 0
}
