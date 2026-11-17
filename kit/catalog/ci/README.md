# The catalog's gate in a project's pipeline

A rule in prose is an intention. The same rule in the pipeline is a fact. This folder holds a
gate any project can run on its change requests, on any CI platform, with nothing but git and
Python's standard library.

## The rule it follows

**The gate freezes debt by counting it against the target branch.** For every automated rule a
project breaks today, the gate counts the occurrences at the merge base with the target branch
and at the change's head, and fails only if the count went up. What is already broken blocks
nobody, and nothing new gets in. Today's count goes in `baseline:` of the project profile, so
the trend can be measured; it may only go down.

The alternative, softening the gate, looks the same on day one and is worthless by day thirty:

| | Soften | Freeze |
| --- | --- | --- |
| What is done | lower the threshold, let the job fail, leave the rule as a warning | count today's debt and block against that count |
| Today's debt | passes | passes |
| New debt | **also passes** | **fails** |
| How much debt there is | nobody knows | a number, in the repository |

A gate set at the ideal and switched off is decoration. The same gate set at today's baseline
and switched on is real. The same ratchet works beyond pattern counts: a coverage threshold set
at today's coverage that may only rise, linter rules turned to errors with the current
violations counted, known dependency advisories listed so any new one fails, files the
formatter would change listed in its ignore file instead of the job switched off. A test job
that passes with zero tests is worse than no job, because it reports the opposite of the truth.

**The project pins the version it follows; behind it warns, far behind it fails.** A project one
minor or patch behind the current standard gets a warning and plans the upgrade. One major
behind fails, because a major version means a new blocking rule it does not apply.

**While the standard is 0.x, nothing blocks.** Every finding is printed as a warning and the job
passes. A project that wants to block earlier runs the gate with `--enforce` once the standard
reaches 1.0.0.

**A repository with no pipeline starts here.** It does not adopt the standard rule by rule: its
first step is this gate, and from there the counts freeze whatever it has.

## How to wire it

The gate is included from the system at a fixed version, never copied and never taken from the
default branch. A change to the default branch would otherwise reach every project with no
version and without anyone deciding it.

1. Write the project's counts in a `counts.tsv`, one automated rule per line: the rule id, an
   extended regular expression and, optionally, the paths it applies to. Tabs between fields.

   ```
   # rule	pattern	paths
   HR-0004	verify\s*=\s*False|rejectUnauthorized:\s*false	*.py *.ts *.js
   HR-0009	--reload|start:dev|DEBUG\s*=\s*True	Dockerfile* *.sh
   SR-0012	forEach\(async	*.ts *.js
   ```

2. Add a job that runs only on change requests, fetches the target branch with its history, and
   calls the gate. Shown in neutral pseudo-configuration; translate it to your platform:

   ```
   job catalog-gate:
     when: change request
     fetch: full history of the target branch
     run:
       - curl -fsSL <system raw URL>/<tag>/catalog/ci/gate.py -o /tmp/gate.py
       - python3 /tmp/gate.py --base origin/$TARGET_BRANCH
                               --counts counts.tsv
                               --profile AGENTS.md
                               --current <latest released version>
                               [--enforce]
   ```

3. Make the platform require the job to pass before merging, and require an approval from
   someone other than the author. Without that, the gate is advice.

## What it does not do

It does not replace the project's linters, tests or security scanners: it is the ratchet around
them. It does not decide which rules are automated: the catalog does, through `verification`.
And it never reads the catalog's candidates, which block nothing.

```
python3 gate.py --help
```
