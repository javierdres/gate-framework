#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Per-message guard. One short reminder, so the log survives long sessions."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "personal", "sessions")

print("Log: if this message leaves a decision, a closed step, a discard, something critical, a "
      "pending item or a pause, update the topic's summary in %s and its README.md index, "
      "following method/sessions.md, and say so in one line. A one-off question leaves no "
      "summary." % LOG)
sys.exit(0)
