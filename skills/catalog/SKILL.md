---
skill: catalog
stage: cross-cutting
name: Cross-cutting
triggered_by: []
consulted_by: [refine, design, self-review, review]
triggers: []
gate: none
gate_owner: —
writes_outside: []
consults: [catalog]
---

# /catalog — Cross-cutting

## Purpose

Fetch the rules in force that apply by scope and by project, so the other skills do not each solve it their own way.

## Preconditions

A catalog readable by machine. For conditional rules, the project profile in the project's instructions file.

## What it does

- Filters by status, scope and projects, and by `applies_when` against the project profile.
- Resolves the project's group from its remote, by the longest matching path prefix, and adds that group's rules and its parent groups' to those of the layer, the product, security and cross-cutting.
- Returns each rule with how review reports it: blocking only for a hard rule in force whose scope is not a draft standard (version 0.x), required for soft rules in force, suggestion for recommended rules and for every candidate.
- Lists apart, rather than dropping, the rules it cannot decide because the profile does not declare what they read, and names the missing key.
- Returns, with the rules, the project's exceptions in force, and flags any that expired or that names a rule which admits none.
- Returns the false positives of the scopes involved and what the organisation decided not to adopt, so review does not raise either.
- If the catalog cannot be read, says so explicitly rather than passing over it in silence.

## What it does NOT do

- Does not assess code.
- Does not promote or edit rules.
- Never returns seeds. A seed nobody adopted is not a rule.

## Gate

None. This skill does not stop the chain.

## Dossier

**Reads:** Scope and project of the work, the project profile and the repository's remote.

**Writes:** Applicable rules with how review reports each, the undetermined ones with the key they need, and the exceptions in force.
