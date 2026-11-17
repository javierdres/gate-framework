#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The use-case index: regenerating, checking and refusing bad detail.

    python3 tools/tests/test_use_cases_index.py

Each test builds a throwaway product folder.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "use_cases_index.py")
INDEX = "# Use cases · Shop\n\nIntro stays.\n\n<!-- use-cases:begin -->\nold\n<!-- use-cases:end -->\n\nTail stays.\n"
CASE = ("### %s · %s\n\n- **Role:** buyer · **Client:** web · **Layer:** front · **Criticality:** %s · "
        "**Checks:** %s · **Origin:** ABC-12\n- **Tags:** @cart\n%s\n")


class UseCasesIndex(unittest.TestCase):
    def setUp(self):
        self.product = os.path.join(tempfile.mkdtemp(), "shop")
        os.makedirs(os.path.join(self.product, "use-cases"))
        self.write("use-cases.md", INDEX)
        self.write("use-cases/01-cart.md", "# Cart\n\n" + CASE % ("SHP-UC-0001", "Add an item", "1", "happy path", "")
                   + CASE % ("SHP-UC-0002", "Empty cart", "3", "edge: no items", "- **Status:** automated\n- **Flow:** cart.e2e.js\n"))

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.product))

    def write(self, rel, text):
        with io.open(os.path.join(self.product, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def index(self):
        with io.open(os.path.join(self.product, "use-cases.md"), encoding="utf-8") as f:
            return f.read()

    def run_it(self, *extra):
        p = subprocess.run([sys.executable, SCRIPT, self.product] + list(extra), capture_output=True, text=True)
        return p.returncode, p.stdout

    def test_regenerates_between_markers(self):
        code, out = self.run_it()
        self.assertEqual(code, 0, out)
        text = self.index()
        self.assertIn("Intro stays.", text)
        self.assertIn("Tail stays.", text)
        self.assertNotIn("\nold\n", text)
        self.assertIn("| [Cart](use-cases/01-cart.md) | 2 | 1 | 0 | 1 | 1 |", text)
        self.assertIn("| SHP-UC-0001 | Add an item | buyer |", text)
        self.assertIn("| proposed | — |", text)
        self.assertIn("| automated | cart.e2e.js |", text)

    def test_check_fails_when_stale_and_passes_when_fresh(self):
        self.assertEqual(self.run_it("--check")[0], 1)
        self.assertEqual(self.index(), INDEX)
        self.run_it()
        self.assertEqual(self.run_it("--check")[0], 0)
        before = self.index()
        self.run_it()
        self.assertEqual(self.index(), before)

    def test_repeated_identifiers_and_incomplete_lines_stop_it(self):
        self.write("use-cases/02-pay.md", "# Pay\n\n" + CASE % ("SHP-UC-0001", "Pay", "1", "x", "")
                   + "### SHP-UC-0003 · Broken\n\n- **Role:** buyer\n")
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("repeated identifiers: SHP-UC-0001", out)
        self.assertIn("SHP-UC-0003 has no complete data line", out)
        self.assertEqual(self.index(), INDEX)

    def test_missing_markers(self):
        self.write("use-cases.md", "# Use cases\n")
        code, out = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("markers", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
