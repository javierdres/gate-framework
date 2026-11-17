# Project profile

Each project declares, in its instructions file (`AGENTS.md`, or whatever the assistant reads),
the facts the catalog needs to know which rules apply to it. Without them a conditional rule is
undefined, and an agent fills the gap with a guess. The profile is code: when a decision
changes (a database is added, the branch that runs in production changes) the profile changes in
the same change request. A stale profile is worse than none, because the agent obeys it with
confidence.

Copy the block below into the project's instructions file, under a heading that reads exactly
`## Project profile`, and fill in what applies. Keys stay in English; delete what does not
apply rather than leaving placeholders. Other convention files in the repository link to this
one and never repeat it: two sources of conventions end up saying different things, and the
agent obeys whichever it read last.

`bin/applicable.py --profile <path>` reads it and lists the rules that apply, the ones it
cannot decide because the profile is missing a key, and any exception that is invalid or
expired.

## Project profile

```yaml
project:
  id: <the id the tickets use>
  repository: <url>

catalog_version: 0.1.0          # the version of the standard this project follows
adopted: YYYY-MM

kind: [service]                 # service, worker, bot, infrastructure, frontend, library
scopes: [backend, security]     # the catalog scopes besides cross-cutting; groups come from the remote

stack:
  language: <language>
  runtime: <the version the runtime file pins>
  framework: <framework@major>
  package_manager: <tool>

api: rest                       # rest, graphql, none
data:
  store: postgres               # or none
  migrations: <command that creates and runs a migration, or none>
documents: none                 # pdf, html, docx, none: whether it generates documents
timezone: <the business timezone, such as Europe/Madrid>

branches:
  integration: develop          # where working branches start
  production: main              # what runs in production today
  hotfix_from: main

integrations:                   # external systems and the one client each goes through
  - <system>: <path to its client>

forbidden:                      # libraries on their way out, with their replacement
  - <library>: <replacement>

baseline:                       # today's count per frozen rule; it may only go down
  <rule id>: <n>

exceptions:                     # see exceptions.md
  - rule: <rule id>
    reason: <why>
    authorised_by: <role>
    ticket: <id>
    expires: YYYY-MM
```

A rule reads this with `applies_when`, for example `data.store != none`, `kind ~ worker` or
`documents != none`. `=` asks for that exact value, `!=` for a different one, and `~` for that
value or a list containing it.
