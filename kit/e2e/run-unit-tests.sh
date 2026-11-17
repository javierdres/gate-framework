#!/bin/sh
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
#
# The runner's own tests (the effects guard and the environment checks). No browser, no
# environment, no install: only node.
#
#   sh e2e/run-unit-tests.sh
cd "$(dirname "$0")" || exit 1
if ! command -v node >/dev/null 2>&1; then
  echo "skipped: node not installed"
  exit 0
fi
exec node --test support/*.test.js
