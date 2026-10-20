#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# Tests for the server-side `update` hook, on a throwaway bare repository with two people.
#
#   bash tools/server-hooks/tests/test_update.sh
#
# Needs git 2.34 or later and ssh-keygen. Prints one line per case and exits non-zero if any
# case behaves differently from what it should.
set -uo pipefail

HOOK="$(cd "$(dirname "$0")/.." && pwd)/update"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0

expect() {  # expect <accept|reject> <description>
  local want="$1" what="$2" out
  if out="$(git push origin main 2>&1)"; then got=accept; else got=reject; fi
  if [ "$got" = "$want" ]; then echo "  ✓  $what"; else echo "  ✗  $what (got $got)"; echo "$out" | sed 's/^/       /'; fail=1; fi
  git reset -q --hard origin/main
}

ssh-keygen -q -t ed25519 -N "" -f "$T/a" -C a@x
ssh-keygen -q -t ed25519 -N "" -f "$T/b" -C b@x
git init -q --bare "$T/srv.git"
cp "$HOOK" "$T/srv.git/hooks/update" && chmod +x "$T/srv.git/hooks/update"
git -C "$T/srv.git" config sdlc.formulation true
git clone -q "$T/srv.git" "$T/w" 2>/dev/null
cd "$T/w" && git checkout -q -b main

as() { git config user.email "$1@x"; git config user.name "$1"; git config gpg.format ssh
       git config user.signingkey "$T/$1.pub"; git config commit.gpgsign true; }
as a
{ echo "a@x namespaces=\"git\" $(cut -d' ' -f1,2 "$T/a.pub")"
  echo "b@x namespaces=\"git\" $(cut -d' ' -f1,2 "$T/b.pub")"; } > allowed_signers
git add . && git commit -qm init
echo "  formulation"
expect accept "a signed push while the repository is in formulation"
git push -q origin main 2>/dev/null
git -C "$T/srv.git" config sdlc.formulation false

echo "  operation"
echo x > f && git add f && git commit -qm direct
expect reject "a commit pushed directly to the default branch"

git checkout -q -b feat && echo y > g && git add g && git commit -qm feat && git checkout -q main
git merge -q --no-ff feat -m "merge feat"
expect reject "a merge with no Reviewed-by trailer"

git merge -q --no-ff feat -m "merge feat

Reviewed-by: b@x"
expect reject "a merge naming b as reviewer but signed by a"

git -c user.email=b@x merge -q --no-ff feat -m "merge feat

Reviewed-by: a@x"
expect reject "a merge signed by a, who wrote the change, with b as author"

as b
git merge -q --no-ff feat -m "merge feat

Reviewed-by: b@x"
expect accept "a merge signed and named by b, who did not write the change"

git -c commit.gpgsign=false commit -q --allow-empty -m unsigned
expect reject "an unsigned commit"

# origin/main now holds the accepted merge; moving it back to its first parent rewrites history.
if git push -q --force origin origin/main~1:main 2>/dev/null; then echo "  ✗  a history rewrite"; fail=1
else echo "  ✓  a history rewrite"; fi

exit $fail
