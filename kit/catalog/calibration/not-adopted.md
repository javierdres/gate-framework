# Not adopted

What the organisation decided, as a standard, not to adopt, and the rules it repealed. A
standard with no stated limits turns into permission to over-engineer, and the same proposals
come back every quarter unless the answer is written down.

This is not a record of false positives. A false positive is one finding rejected in one
change, and anyone may record it. An entry here is a decision about the whole standard, so it
belongs to the custodian of its scope and goes in by change request like a rule.

## Not adopted

Practices, rules or seeds that were proposed and turned down, with the reason. When the reason
stops holding, the custodian removes the row and the proposal can come back.

| What | Scope | Why not | Decided |
| --- | --- | --- | --- |

Examples of the kind of row that belongs here, never real entries: "a minimum test coverage
figure: coverage as an end in itself, the baseline that only goes up already covers it";
"one framework for every service: the profile declares what each project uses and migrating
is not a goal"; "style rules with a single reviewer behind them and no fixes: the linter
configuration of each project settles them".

## Derogated

Rules repealed with no replacement, by id. The rule's file stays, with `status: deprecated` and
`superseded_by: repealed`, and the validator checks that its id is in this table. A rule
replaced by another does not need a row: its `superseded_by` already says where to go.

| Rule | Version or date | Reason | What to do instead |
| --- | --- | --- | --- |
