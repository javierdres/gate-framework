#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""The catalog's scripts, in both directions.

    python3 tests/test_catalog.py

The validator must reject what the format forbids and accept what it allows. Each test builds a
throwaway catalog from this one's bin/, scopes.md, template and seeds. The same file covers the
generator, adopt_seed.py, applicable.py and the CI gate in ci/.
"""
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

CATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with io.open(os.path.join(CATALOG, "rules", "_TEMPLATE.md"), encoding="utf-8") as _f:
    TEMPLATE = _f.read()

SCOPES_BY_SCOPE = """# Scopes

| Scope | Prefix | Version | What it covers | Custodian (role) |
| --- | --- | --- | --- | --- |
| `cross-cutting` | CROSS | | Every project | Every custodian |
| `security` | SEC | 1.0.0 | Secrets | Custodian of security |
| `backend` | BACK | 0.3.0 | Services | Custodian of backend |
| `frontend` | FRONT | | Web | Custodian of frontend |
| `operations` | OPS | | Operations | Custodian of operations |
| `ai-assisted-work` | AI | | Assisted work | Every custodian |

| Group | Prefix | Remote path prefix | What it covers | Custodian (role) |
| --- | --- | --- | --- | --- |
| `platform` | PLAT | acme/backend/platform | Shared platform | Custodian of platform |
| `platform-jobs` | PJOB | acme/backend/platform/jobs | Jobs on the platform | Custodian of platform |
"""


# The scopes GATE ships, so the tests never depend on the rows an organisation added.
DEFAULT_SCOPES = """# Scopes

| Scope | Prefix | Version | What it covers | Custodian (role) |
| --- | --- | --- | --- | --- |
| `cross-cutting` | CROSS | | Every project and layer | Every custodian |
| `product` | PROD | | Definition | Custodian of product |
| `security` | SEC | | Secrets | Custodian of security |
| `operations` | OPS | | Operations | Custodian of operations |
"""


def rule(**changes):
    """The template turned into HR-0001, with frontmatter lines replaced, removed or added."""
    text = TEMPLATE.replace("HR-0000", "HR-0001")
    for key, value in changes.items():
        lines = text.split("\n")
        out, skipping, found = [], False, False
        for line in lines:
            if skipping:
                if line.startswith("  - "):
                    continue
                skipping = False
            if line.startswith(key + ":"):
                found = True
                if value is not None:
                    out.append("%s: %s" % (key, value) if not value.startswith("\n") else key + ":" + value)
                skipping = True
                continue
            out.append(line)
        if not found and value is not None:
            out.insert(out.index("approved_by: []") if "approved_by: []" in out else 2, "%s: %s" % (key, value))
        text = "\n".join(out)
    return text


def as_id(text, rid):
    """Rename the rule itself (its id and heading), leaving the ids it cites alone."""
    return text.replace("id: HR-0001", "id: " + rid, 1).replace("# HR-0001 ·", "# %s ·" % rid, 1)


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        shutil.copytree(os.path.join(CATALOG, "bin"), os.path.join(self.dir, "bin"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(os.path.join(CATALOG, "seeds"), os.path.join(self.dir, "seeds"))
        self.put("scopes.md", DEFAULT_SCOPES)
        for sev in ("hard", "soft"):
            os.makedirs(os.path.join(self.dir, "rules", sev))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def put(self, rel, text):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write(self, sev, name, text):
        self.put(os.path.join("rules", sev, name), text)

    def run_bin(self, script, *args):
        p = subprocess.run([sys.executable, os.path.join(self.dir, "bin", script)] + list(args),
                           capture_output=True, text=True, cwd=self.dir)
        return p.returncode, p.stdout + p.stderr

    def validate(self):
        return self.run_bin("validate.py")

    def assertValid(self):
        code, out = self.validate()
        self.assertEqual(code, 0, out)

    def assertRejects(self, text, needle, sev="hard", name="HR-0001-a-rule.md"):
        if text is not None:
            self.write(sev, name, text)
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn(needle, out)

    def catalog_json(self):
        code, out = self.run_bin("generate_catalog.py")
        self.assertEqual(code, 0, out)
        with io.open(os.path.join(self.dir, "catalog.json"), encoding="utf-8") as f:
            return json.load(f)


class Catalog(Base):
    # accepts what the format allows
    def test_empty_catalog_is_valid(self):
        self.assertEqual(self.validate()[0], 0)

    def test_template_as_a_rule_is_valid(self):
        self.write("hard", "HR-0001-a-rule.md", rule())
        self.assertValid()

    def test_multiline_approved_by_in_force(self):
        text = rule(status="in force", approved_by="\n  - Custodian of security, 2026-02-01\n  - Every custodian")
        self.write("hard", "HR-0001-a-rule.md", text)
        self.assertValid()

    def test_soft_rule_without_exceptions(self):
        text = rule(severity="soft").replace("HR-0001", "SR-0001").replace("## Exceptions", "## Notes")
        self.write("soft", "SR-0001-a-rule.md", text)
        self.assertEqual(self.validate()[0], 0)

    def test_recommended_rule(self):
        text = as_id(rule(severity="recommended", verification="manual", detected_by="review"), "RC-0001")
        self.write("recommended", "RC-0001-a-rule.md", text)
        self.assertValid()

    def test_quoted_values(self):
        self.write("hard", "HR-0001-a-rule.md", rule(title='"A quoted title"', created="'2026-01-01'"))
        self.assertEqual(self.validate()[0], 0)

    def test_without_the_optional_fields(self):
        self.write("hard", "HR-0001-a-rule.md", rule(verification=None, detected_by=None))
        self.assertValid()

    def test_hard_manual_with_business_defect(self):
        self.write("hard", "HR-0001-a-rule.md",
                   rule(verification="manual", detected_by="review", tags="[business-defect]"))
        self.assertValid()

    def test_applies_when_and_waivable(self):
        self.write("hard", "HR-0001-a-rule.md",
                   rule(applies_when="[data.store != none, kind ~ worker]", waivable="false"))
        self.assertValid()

    def test_citation_of_an_existing_rule(self):
        self.write("hard", "HR-0001-a-rule.md", rule() + "\nSee also SR-0001.\n")
        self.write("soft", "SR-0001-b-rule.md", as_id(rule(severity="soft"), "SR-0001"))
        self.assertValid()

    def test_superseded_both_ways(self):
        old = rule(status="deprecated", superseded_by="HR-0002")
        new = as_id(rule(supersedes="[HR-0001]"), "HR-0002")
        self.write("hard", "HR-0001-old.md", old)
        self.write("hard", "HR-0002-new.md", new)
        self.assertValid()

    def test_repealed_with_a_derogated_row(self):
        self.write("hard", "HR-0001-a-rule.md", rule(status="deprecated", superseded_by="repealed"))
        self.put("calibration/not-adopted.md", "# Not adopted\n\n## Derogated\n\n| Rule | Version | Reason | Instead |\n"
                 "| --- | --- | --- | --- |\n| HR-0001 | 1.2.0 | under 50% for two quarters | nothing |\n")
        self.assertValid()

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

    def test_rejects_bad_verification_values(self):
        self.assertRejects(rule(verification="sometimes"), "verification 'sometimes'")
        self.assertRejects(rule(verification="auto", detected_by="luck"), "detected_by 'luck'")
        self.assertRejects(rule(verification="manual", detected_by="pipeline", tags="[business-defect]"),
                           "detected_by is 'pipeline'")

    def test_rejects_hard_manual_without_business_defect(self):
        self.assertRejects(rule(verification="manual", detected_by="review"), "business-defect")

    def test_rejects_bad_applies_when_and_waivable(self):
        self.assertRejects(rule(applies_when="[the database exists]"), "applies_when 'the database exists'")
        self.assertRejects(rule(waivable="sometimes"), "waivable 'sometimes'")

    def test_rejects_citation_of_a_missing_rule(self):
        self.assertRejects(rule() + "\nSee HR-0099 for the rest.\n", "cites 'HR-0099'")

    def test_rejects_successor_that_does_not_point_back(self):
        self.write("hard", "HR-0002-new.md", as_id(rule(), "HR-0002"))
        self.assertRejects(rule(status="deprecated", superseded_by="HR-0002"), "does not list 'HR-0001'",
                           name="HR-0001-old.md")

    def test_rejects_successor_that_does_not_exist(self):
        self.assertRejects(rule(status="deprecated", superseded_by="HR-0007"), "superseded_by 'HR-0007'")

    def test_rejects_supersedes_pointing_at_an_active_rule(self):
        self.write("hard", "HR-0002-old.md", as_id(rule(), "HR-0002"))
        self.assertRejects(rule(supersedes="[HR-0002]"), "that rule's superseded_by")

    def test_rejects_superseded_by_on_an_active_rule(self):
        self.assertRejects(rule(superseded_by="repealed"), "not 'deprecated'")

    def test_rejects_repealed_without_a_derogated_row(self):
        self.assertRejects(rule(status="deprecated", superseded_by="repealed"), "derogated")

    # the generator
    def test_generator_strips_quotes_and_counts(self):
        self.write("hard", "HR-0001-a-rule.md", rule(title='"Quoted"'))
        soft = rule(severity="soft", status="in force", approved_by="[Custodian]").replace("HR-0001", "SR-0001")
        self.write("soft", "SR-0001-b-rule.md", soft)
        data = self.catalog_json()
        titles = [r["title"] for r in data["rules"]]
        self.assertIn("Quoted", titles)
        self.assertEqual(data["totals"]["hard"]["candidate"], 1)
        self.assertEqual(data["totals"]["soft"]["in force"], 1)

    def test_generator_exposes_fields_and_reporting(self):
        self.write("hard", "HR-0001-a-rule.md", rule(status="in force", approved_by="[Every custodian]",
                                                     waivable="false", applies_when="[data.store != none]"))
        self.write("hard", "HR-0002-b-rule.md", as_id(rule(), "HR-0002"))
        by_id = {r["id"]: r for r in self.catalog_json()["rules"]}
        self.assertEqual(by_id["HR-0001"]["reported_as"], "blocking")
        self.assertEqual(by_id["HR-0002"]["reported_as"], "suggestion")
        self.assertEqual(by_id["HR-0001"]["verification"], "auto")
        self.assertEqual(by_id["HR-0001"]["detected_by"], "pipeline")
        self.assertEqual(by_id["HR-0001"]["applies_when"], ["data.store != none"])
        self.assertFalse(by_id["HR-0001"]["waivable"])
        self.assertTrue(by_id["HR-0002"]["waivable"])

    def test_seeds_never_reach_the_catalog(self):
        data = self.catalog_json()
        self.assertEqual(data["rules"], [])
        self.assertEqual(self.validate()[0], 0)

    def test_catalog_json_is_ignored(self):
        with io.open(os.path.join(CATALOG, ".gitignore"), encoding="utf-8") as f:
            ignored = f.read().split()
        self.assertIn("catalog.json", ignored)

    def test_template_and_public_template_agree(self):
        public = os.path.join(os.path.dirname(os.path.dirname(CATALOG)), "templates", "rule.md")
        if os.path.exists(public):
            with io.open(public, encoding="utf-8") as f:
                self.assertEqual(f.read(), TEMPLATE)


class ByScope(Base):
    """The layout by scope: rules/<scope>/<PREFIX>-NNNN with false-positives.md beside them."""

    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.dir, "rules"))
        self.put("scopes.md", SCOPES_BY_SCOPE)

    def sec(self, rid="SEC-0001", **changes):
        changes.setdefault("scope", "[security]")
        return as_id(rule(**changes), rid)

    def test_scope_folder_is_valid(self):
        self.put("rules/security/SEC-0001-a-rule.md", self.sec())
        self.put("rules/security/false-positives.md", "# Known false positives\n")
        self.assertValid()

    def test_group_folder_is_valid(self):
        self.put("rules/groups/platform/PLAT-0001-a-rule.md", as_id(rule(scope="[platform]"), "PLAT-0001"))
        self.assertValid()

    def test_rejects_wrong_prefix(self):
        self.put("rules/security/BACK-0001-a-rule.md", as_id(rule(scope="[security]"), "BACK-0001"))
        self.assertRejects(None, "expected SEC-NNNN-slug.md")

    def test_rejects_folder_not_in_scopes(self):
        self.put("rules/payments/PAY-0001-a-rule.md", as_id(rule(), "PAY-0001"))
        self.assertRejects(None, "neither a severity folder nor a scope")

    def test_rejects_folder_missing_from_scope_field(self):
        self.put("rules/security/SEC-0001-a-rule.md", self.sec(scope="[cross-cutting]"))
        self.assertRejects(None, "lists 'security' in its scope")

    def test_rejects_group_outside_groups(self):
        self.put("rules/platform/PLAT-0001-a-rule.md", as_id(rule(scope="[platform]"), "PLAT-0001"))
        self.assertRejects(None, "rules/groups/platform/")

    def test_rejects_mixed_layouts(self):
        self.put("rules/security/SEC-0001-a-rule.md", self.sec())
        self.put("rules/hard/HR-0001-a-rule.md", rule())
        self.assertRejects(None, "Use one layout")

    def test_mixed_layouts_while_moving(self):
        self.put("rules/hard/HR-0001-old.md", rule(status="deprecated", superseded_by="SEC-0001"))
        self.put("rules/security/SEC-0001-new.md", self.sec(supersedes="[HR-0001]"))
        self.assertValid()

    def test_cites_by_scope_prefix(self):
        self.put("rules/security/SEC-0001-a-rule.md", self.sec() + "\nRelated: BACK-0042.\n")
        self.assertRejects(None, "cites 'BACK-0042'")

    def test_rejects_duplicate_scope_and_prefix(self):
        self.put("scopes.md", SCOPES_BY_SCOPE + "\n| Scope | Prefix |\n| --- | --- |\n| `security` | SEC |\n| `payments` | BACK |\n")
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("'security' is listed more than once", out)
        self.assertIn("same prefix BACK", out)

    def test_draft_scope_never_blocks(self):
        self.put("rules/backend/BACK-0001-a-rule.md",
                 as_id(rule(scope="[backend]", status="in force", approved_by="[All]"), "BACK-0001"))
        self.put("rules/security/SEC-0001-a-rule.md", self.sec(status="in force", approved_by="[All]"))
        by_id = {r["id"]: r for r in self.catalog_json()["rules"]}
        self.assertEqual(by_id["BACK-0001"]["reported_as"], "required")
        self.assertEqual(by_id["SEC-0001"]["reported_as"], "blocking")


def all_scopes_md():
    return SCOPES_BY_SCOPE


class AdoptSeed(Base):
    def adopt(self, *args):
        return self.run_bin("adopt_seed.py", *args)

    def seed_ids(self):
        ids = []
        for base, _, files in os.walk(os.path.join(self.dir, "seeds")):
            for name in files:
                m = re.match(r"^(SEED-[A-Z]+-\d{2})-", name)
                if m:
                    ids.append(m.group(1))
        return sorted(ids)

    def test_every_seed_is_well_formed(self):
        code, out = self.adopt("--check")
        self.assertEqual(code, 0, out)

    def test_every_seed_adopts_into_a_valid_catalog_by_severity(self):
        self.put("scopes.md", all_scopes_md())
        code, out = self.adopt(*self.seed_ids())
        self.assertEqual(code, 0, out)
        self.assertValid()
        data = self.catalog_json()
        self.assertEqual(len(data["rules"]), len(self.seed_ids()))
        self.assertTrue(all(r["status"] == "candidate" and r["reported_as"] == "suggestion" for r in data["rules"]))
        self.assertTrue(all(any("Seeded from GATE " + r["seeded_from"] in o for o in r["origin"])
                            for r in data["rules"]))

    def test_every_seed_adopts_into_a_valid_catalog_by_scope(self):
        self.put("scopes.md", all_scopes_md())
        shutil.rmtree(os.path.join(self.dir, "rules"))
        code, out = self.adopt("--layout", "scope", *self.seed_ids())
        self.assertEqual(code, 0, out)
        self.assertValid()
        self.assertTrue(os.path.exists(os.path.join(self.dir, "rules", "security")))

    def test_ids_are_sequential_and_never_reused(self):
        self.write("hard", "HR-0003-existing.md", as_id(rule(), "HR-0003"))
        code, out = self.adopt("SEED-SEC-01", "SEED-SEC-02")
        self.assertEqual(code, 0, out)
        names = sorted(os.listdir(os.path.join(self.dir, "rules", "hard")))
        self.assertTrue(any(n.startswith("HR-0004-no-credential") for n in names), names)
        self.assertTrue(any(n.startswith("HR-0005-logs-without") for n in names), names)
        self.assertValid()

    def test_running_twice_changes_nothing(self):
        self.adopt("SEED-SEC-01")
        before = sorted(os.listdir(os.path.join(self.dir, "rules", "hard")))
        code, out = self.adopt("SEED-SEC-01")
        self.assertEqual(code, 0, out)
        self.assertIn("already adopted", out)
        self.assertEqual(before, sorted(os.listdir(os.path.join(self.dir, "rules", "hard"))))

    def test_scope_missing_from_scopes_md(self):
        code, out = self.adopt("SEED-BACK-01")
        self.assertEqual(code, 1, out)
        self.assertIn("not in scopes.md", out)
        code, out = self.adopt("SEED-BACK-01", "--scope", "cross-cutting")
        self.assertEqual(code, 0, out)
        self.assertValid()

    def test_unknown_seed(self):
        code, out = self.adopt("SEED-SEC-99")
        self.assertEqual(code, 1, out)

    def test_dry_run_writes_nothing(self):
        code, out = self.adopt("--dry-run", "SEED-SEC-01")
        self.assertEqual(code, 0, out)
        self.assertIn("would adopt", out)
        self.assertEqual(os.listdir(os.path.join(self.dir, "rules", "hard")), [])

    def test_adopted_rule_keeps_its_lesson_and_history(self):
        self.adopt("SEED-SEC-01")
        name = os.listdir(os.path.join(self.dir, "rules", "hard"))[0]
        with io.open(os.path.join(self.dir, "rules", "hard", name), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("# HR-0001 · ", text)
        self.assertIn("security audit", text)
        self.assertIn("seeded_from: SEED-SEC-01", text)
        self.assertIn("Adopted as a candidate from GATE seed SEED-SEC-01", text)
        self.assertNotIn("seed_id:", text)


PROFILE = """# A project

## Project profile

```yaml
project:
  id: billing
catalog_version: 1.2.0
kind: [service, worker]   # two kinds
scopes: [backend]
data:
  store: postgres
exceptions:
  - rule: SR-0001
    reason: the registry takes minutes
    authorised_by: Custodian of backend
    ticket: BILL-1
    expires: 2099-01
  - rule: HR-0001
    reason: in a hurry
    authorised_by: nobody
    expires: 2020-01
```

## Something else
"""


class Applicable(Base):
    def setUp(self):
        super().setUp()
        self.put("scopes.md", SCOPES_BY_SCOPE)
        sys.path.insert(0, os.path.join(CATALOG, "bin"))

    def test_profile_parsing_and_conditions(self):
        import _rules
        path = os.path.join(self.dir, "AGENTS.md")
        self.put("AGENTS.md", PROFILE)
        p = _rules.read_profile(path)
        self.assertEqual(p["project"]["id"], "billing")
        self.assertEqual(p["kind"], ["service", "worker"])
        self.assertEqual(p["exceptions"][0]["rule"], "SR-0001")
        self.assertEqual(p["exceptions"][1]["expires"], "2020-01")
        self.assertTrue(_rules.evaluate("data.store != none", p))
        self.assertTrue(_rules.evaluate("kind ~ worker", p))
        self.assertFalse(_rules.evaluate("kind = worker", p))
        self.assertIsNone(_rules.evaluate("documents != none", p))

    def test_groups_by_longest_prefix(self):
        import _rules
        scopes = _rules.read_scopes(os.path.join(self.dir, "scopes.md"))
        self.assertEqual(_rules.groups_for("git@code.example:acme/backend/platform/jobs/nightly.git", scopes),
                         ["platform-jobs", "platform"])
        self.assertEqual(_rules.groups_for("https://code.example/acme/backend/platform/api", scopes), ["platform"])
        self.assertEqual(_rules.groups_for("https://code.example/acme/backend/platformer/api", scopes), [])

    def test_expiry(self):
        import _rules
        today = datetime.date(2026, 11, 17)
        self.assertFalse(_rules.expired("2026-11", today))
        self.assertTrue(_rules.expired("2026-10", today))
        self.assertTrue(_rules.expired("2026-11-16", today))
        self.assertIsNone(_rules.expired("soon", today))

    def test_applicable_rules_and_exceptions(self):
        os.makedirs(os.path.join(self.dir, "rules", "recommended"))
        self.write("hard", "HR-0001-a-rule.md", rule(waivable="false", scope="[backend]"))
        self.write("soft", "SR-0001-b-rule.md", as_id(rule(severity="soft", scope="[backend]",
                                                           applies_when="[data.store != none]"), "SR-0001"))
        self.write("soft", "SR-0002-c-rule.md", as_id(rule(severity="soft", scope="[backend]",
                                                           applies_when="[documents != none]"), "SR-0002"))
        self.write("soft", "SR-0003-d-rule.md", as_id(rule(severity="soft", scope="[frontend]"), "SR-0003"))
        self.write("soft", "SR-0004-e-rule.md", as_id(rule(severity="soft", scope="[platform]"), "SR-0004"))
        self.assertValid()
        self.put("AGENTS.md", PROFILE)
        code, out = self.run_bin("applicable.py", "--profile", os.path.join(self.dir, "AGENTS.md"),
                                 "--remote", "git@code.example:acme/backend/platform/billing.git", "--json")
        data = json.loads(out[:out.rindex("}") + 1])
        applies = {r["id"] for r in data["applies"]}
        self.assertEqual(applies, {"HR-0001", "SR-0001", "SR-0004"})
        self.assertEqual([r["id"] for r in data["undetermined"]], ["SR-0002"])
        self.assertEqual(data["groups"], ["platform"])
        self.assertTrue(any("HR-0001: that rule never admits one" in p for p in data["problems"]))
        self.assertTrue(any("expired" in p for p in data["problems"]))
        self.assertFalse(any("SR-0001" in p for p in data["problems"]))
        self.assertEqual(code, 1)

    def test_profile_template_reads(self):
        import _rules
        p = _rules.read_profile(os.path.join(CATALOG, "project-profile.md"))
        self.assertIsNotNone(p)
        self.assertIn("catalog_version", p)
        self.assertEqual(p["data"]["store"], "postgres")


class Gate(unittest.TestCase):
    """ci/gate.py on a throwaway repository."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.gate = os.path.join(CATALOG, "ci", "gate.py")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.file("app.py", "requests.get(url, verify=False)\n")
        self.file("counts.tsv", "# rule\tpattern\tpaths\nHR-0004\tverify=False\t*.py\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.git("checkout", "-qb", "change")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def git(self, *args):
        subprocess.run(["git"] + list(args), cwd=self.dir, check=True, capture_output=True)

    def file(self, name, text):
        with io.open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            f.write(text)

    def gate_run(self, *args):
        p = subprocess.run([sys.executable, self.gate, "--base", "main", "--counts", "counts.tsv"] + list(args),
                           cwd=self.dir, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def commit(self, text):
        self.file("app.py", text)
        self.git("commit", "-qam", "change")

    def test_existing_debt_passes(self):
        self.commit("requests.get(url, verify=False)\nprint('ok')\n")
        code, out = self.gate_run("--enforce", "--current", "1.0.0")
        self.assertEqual(code, 0, out)

    def test_new_debt_fails_when_enforced(self):
        self.commit("requests.get(url, verify=False)\nrequests.post(url, verify=False)\n")
        code, out = self.gate_run("--enforce", "--current", "1.0.0")
        self.assertEqual(code, 1, out)
        self.assertIn("HR-0004", out)

    def test_new_debt_only_warns_without_enforce_or_in_draft(self):
        self.commit("requests.get(url, verify=False)\nrequests.post(url, verify=False)\n")
        self.assertEqual(self.gate_run()[0], 0)
        code, out = self.gate_run("--enforce", "--current", "0.4.0")
        self.assertEqual(code, 0, out)
        self.assertIn("0.x", out)

    def test_version_lag(self):
        sys.path.insert(0, os.path.join(CATALOG, "ci"))
        import gate
        self.assertEqual(gate.version_lag("1.2.0", "1.2.0"), "ok")
        self.assertEqual(gate.version_lag("1.1.0", "1.2.0"), "warn")
        self.assertEqual(gate.version_lag("1.2.0", "2.0.0"), "fail")
        self.assertEqual(gate.version_lag("nonsense", "2.0.0"), "fail")
        self.commit("print('clean')\n")
        code, out = self.gate_run("--enforce", "--pinned", "1.4.0", "--current", "2.1.0")
        self.assertEqual(code, 1, out)
        code, out = self.gate_run("--enforce", "--pinned", "2.0.0", "--current", "2.1.0")
        self.assertEqual(code, 0, out)
        self.assertIn("behind", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
