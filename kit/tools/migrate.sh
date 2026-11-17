#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Moves this system's repository to the neutral names, once, run by the orchestrator. Everything
# keeps working before it runs: the kit reads the older names too, for the window CONTRIBUTING.md
# sets in GATE.
#
#   tools/migrate.sh
#
# Renames sdlc.yml to system.yml with git, so the change goes up as one change request, and
# lists what it cannot change on its own. It commits nothing. Each person's working folder is
# migrated by the installer, not here. Idempotent: a second run changes nothing.
set -euo pipefail

SYSTEM="$(cd "$(dirname "$0")/.." && pwd)"
NAME="$(basename "$SYSTEM")"
cd "$SYSTEM"

if [ -f sdlc.yml ] && [ ! -f system.yml ]; then
  if git ls-files --error-unmatch sdlc.yml >/dev/null 2>&1; then git mv sdlc.yml system.yml; else mv sdlc.yml system.yml; fi
  echo "OK  sdlc.yml renamed to system.yml"
elif [ -f sdlc.yml ]; then
  echo "! Both sdlc.yml and system.yml exist. system.yml is the one read; remove sdlc.yml once"
  echo "  nothing in it is missing from system.yml."
else
  echo "OK  the config is already system.yml"
fi

# What the kit shipped defines the older names as aliases; anything else that uses them was
# written here. It keeps working: this is only so the orchestrator knows where they are.
KIT='^(tools/(lib|install|migrate|rename|check-access)\.sh|tools/guards/|tools/tests/|tools/clients/README\.md|tools/adapters_check\.py|adapters/|e2e/support/|gate-reference/)'
mentions="$(git grep -lE 'sdlc\.yml|\$SDLC|\$\{SDLC|sdlc_[a-z]|SDLC_[A-Z]' -- . 2>/dev/null \
  | grep -vE "$KIT" | grep -vx 'CHANGELOG.md' || true)"
if [ -n "$mentions" ]; then
  echo "! These files still use an older name. They keep working; update them when convenient:"
  printf '%s\n' "$mentions" | sed 's/^/    /'
fi

echo "! On the code platform, if the server-side hook is installed: the formulation key is now"
echo "  gate.formulation. sdlc.formulation is still read while the new one is not set."

if git diff --cached --quiet 2>/dev/null; then
  echo "Nothing to commit for $NAME."
else
  echo
  echo "Next: commit this on a branch and open a change request. Once it is merged, each person"
  echo "runs the installer again when the session start offers it."
fi
