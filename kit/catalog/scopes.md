# Scopes

Every rule declares one or more scopes in its `scope` field, and the validator accepts only the
scopes and groups in the tables below. A rule is born in the scope where it was learned and
becomes cross-cutting once it is shown to apply in a second place. Add a row per technical
layer the organisation actually has, with its custodian's role.

The keys and the column headers stay in English, whatever language the documents are written
in, because the validator and the review skills read them.

| Scope | Prefix | Version | What it covers | Custodian (role) |
| --- | --- | --- | --- | --- |
| `cross-cutting` | CROSS | | Every project and layer | Every custodian |
| `product` | PROD | | Definition, acceptance criteria, data | Custodian of product |
| `security` | SEC | | Secrets, personal data, dependencies, access, exposure | Custodian of security |
| `operations` | OPS | | Deployment, observability, alerts, continuity | Custodian of operations |

- **Prefix** names the rules of the scope when the catalog is laid out by scope, as in
  `SEC-0001`. The layout by severity ignores it and uses `HR`, `SR` and `RC`.
- **Version** is the version of the scope's standard, when the scope is kept as a versioned
  standard (see README.md). While it is `0.x` nothing in the scope blocks, and its hard rules in
  force are reported as required. Empty means the scope is not versioned.

## Two layouts

A catalog keeps its rules one way or the other. The validator accepts either, and rejects a
catalog with rules in force in both.

**By severity**, the default and the simplest while the catalog is small:

```
rules/hard/HR-0001-....md
rules/soft/SR-0001-....md
rules/recommended/RC-0001-....md
calibration/false-positives.md
```

**By scope**, once each scope has its own custodian and its own pace. Each scope's folder
holds its rules, named with the scope's prefix, and its own record of false positives beside
them, so whoever reviews a layer reads its rules and its discards together:

```
rules/security/SEC-0001-....md
rules/security/false-positives.md
rules/backend/BACK-0001-....md
rules/backend/false-positives.md
rules/groups/<group>/<PREFIX>-0001-....md
```

Moving from one layout to the other gives every rule a new id. The old file stays, deprecated
with `superseded_by` pointing at the new id, because old reviews cite the old one.

## Groups

Some rules belong to neither a layer nor a product but to a platform that a group of
repositories shares: a deployment platform, an infrastructure template, a common pipeline.
Those repositories may belong to several products and mix stacks, and are still built and
reviewed against the same platform. A group's rules add to those of the layer, the product,
security and cross-cutting, and replace none. In the layout by scope they live in
`rules/groups/<group>/`; in the layout by severity they carry the group's key in `scope`.

| Group | Prefix | Remote path prefix | What it covers | Custodian (role) |
| --- | --- | --- | --- | --- |

The group comes from the repository's remote (`git remote get-url origin`). Its path on the
code platform is matched against each group's remote path prefix, and the longest match is the
repository's group. A parent group's rules keep applying, so a subgroup that needs rules of its
own gets its own row and folder and loses nothing. `bin/applicable.py` resolves it.
