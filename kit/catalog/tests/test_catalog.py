#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The catalog validator and generator, in both directions.

    python3 tests/test_catalog.py

The validator must reject what the format forbids and accept what it allows. Each test builds a
throwaway catalog from this one's bin/, scopes.md and template.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

CATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with io.open(os.path.join(CATALOG, "rules", "_TEMPLATE.md"), encoding="utf-8") as _f:
    TEMPLATE = _f.read()


def rule(**changes):
    """The template turned into HR-0001, with frontmatter lines replaced or removed."""
    text = TEMPLATE.replace("HR-0000", "HR-0001")
    for key, value in changes.items():
        lines = text.split("\n")
        out, skipping = [], False
        for line in lines:
            if skipping:
                if line.startswith("  - "):
                    continue
                skipping = False
            if line.startswith(key + ":"):
                if value is not None:
                    out.append("%s: %s" % (key, value) if not value.startswith("\n") else key + ":" + value)
                skipping = True
                continue
            out.append(line)
        text = "\n".join(out)
    return text


class Catalog(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        shutil.copytree(os.path.join(CATALOG, "bin"), os.path.join(self.dir, "bin"))
        shutil.copy(os.path.join(CATALOG, "scopes.md"), self.dir)
        for sev in ("hard", "soft"):
            os.makedirs(os.path.join(self.dir, "rules", sev))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, sev, name, text):
        with io.open(os.path.join(self.dir, "rules", sev, name), "w", encoding="utf-8") as f:
            f.write(text)

    def validate(self):
        p = subprocess.run([sys.executable, os.path.join(self.dir, "bin", "validate.py")],
                           capture_output=True, text=True)
        return p.returncode, p.stdout

    def assertRejects(self, text, needle, sev="hard", name="HR-0001-a-rule.md"):
        self.write(sev, name, text)
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn(needle, out)

    # accepts what the format allows
    def test_empty_catalog_is_valid(self):
        self.assertEqual(self.validate()[0], 0)

    def test_template_as_a_rule_is_valid(self):
        self.write("hard", "HR-0001-a-rule.md", rule())
        code, out = self.validate()
        self.assertEqual(code, 0, out)

    def test_multiline_approved_by_in_force(self):
        text = rule(status="in force", approved_by="\n  - Custodian of security, 2026-02-01\n  - Every custodian")
        self.write("hard", "HR-0001-a-rule.md", text)
        code, out = self.validate()
        self.assertEqual(code, 0, out)

    def test_soft_rule_without_exceptions(self):
        text = rule(severity="soft").replace("HR-0001", "SR-0001").replace("## Exceptions", "## Notes")
        self.write("soft", "SR-0001-a-rule.md", text)
        self.assertEqual(self.validate()[0], 0)

    def test_quoted_values(self):
        self.write("hard", "HR-0001-a-rule.md", rule(title='"A quoted title"', created="'2026-01-01'"))
        self.assertEqual(self.validate()[0], 0)

    # rejects what the format forbids
    def test_rejects_empty_origin(self):
        self.assertRejects(rule(origin="[]"), "origin is empty")

    def test_rejects_unknown_scope(self):
        self.assertRejects(rule(scope="[php]"), "scope 'php' is not listed")

    def test_rejects_severity_against_folder(self):
        self.assertRejects(rule(severity="soft"), "does not match its directory")

    def test_rejects_unknown_status(self):
        self.assertRejects(rule(status="approved"), "status 'approved'")

    def test_rejects_invalid_dates(self):
        self.assertRejects(rule(created="2026-13-01"), "not a date")
        self.assertRejects(rule(created="2026-03-01", updated="2026-02-01"), "earlier than created")

    def test_rejects_in_force_without_approval(self):
        self.assertRejects(rule(status="in force"), "approved_by is empty")

    def test_rejects_deprecated_without_successor(self):
        self.assertRejects(rule(status="deprecated"), "superseded_by is empty")

    def test_rejects_missing_field(self):
        self.assertRejects(rule(tags=None), "missing field 'tags'")

    def test_rejects_hard_rule_without_exceptions(self):
        self.assertRejects(rule().replace("## Exceptions", "## Notes"), "needs '## Exceptions'")

    def test_rejects_duplicate_id(self):
        self.write("hard", "HR-0001-a-rule.md", rule())
        self.assertRejects(rule(), "duplicate id", name="HR-0001-another-rule.md")

    def test_rejects_wrong_prefix_in_folder(self):
        text = rule().replace("HR-0001", "SR-0001")
        self.assertRejects(text, "prefix does not match", name="SR-0001-a-rule.md")

    # the generator
    def test_generator_strips_quotes_and_counts(self):
        self.write("hard", "HR-0001-a-rule.md", rule(title='"Quoted"'))
        soft = rule(severity="soft", status="in force", approved_by="[Custodian]").replace("HR-0001", "SR-0001")
        self.write("soft", "SR-0001-b-rule.md", soft)
        subprocess.run([sys.executable, os.path.join(self.dir, "bin", "generate_catalog.py")],
                       check=True, capture_output=True)
        with io.open(os.path.join(self.dir, "catalog.json"), encoding="utf-8") as f:
            data = json.load(f)
        titles = [r["title"] for r in data["rules"]]
        self.assertIn("Quoted", titles)
        self.assertEqual(data["totals"]["hard"]["candidate"], 1)
        self.assertEqual(data["totals"]["soft"]["in force"], 1)

    def test_catalog_json_is_ignored(self):
        with io.open(os.path.join(CATALOG, ".gitignore"), encoding="utf-8") as f:
            ignored = f.read().split()
        self.assertIn("catalog.json", ignored)


if __name__ == "__main__":
    unittest.main(verbosity=1)
