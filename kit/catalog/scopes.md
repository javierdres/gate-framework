# Scopes

Every rule declares one or more scopes in its `scope` field, and the validator accepts only the
scopes in this table. A rule is born in the scope where it was learned and becomes cross-cutting
once it is shown to apply in a second place. Add a row per technical layer the organisation
actually has, with its custodian's role.

The keys stay in English, whatever language the documents are written in, because the
validator and the review skills read them.

| Scope | What it covers | Custodian (role) |
| --- | --- | --- |
| `cross-cutting` | Every project and layer | Every custodian |
| `product` | Definition, acceptance criteria, data | Custodian of product |
| `security` | Secrets, personal data, dependencies, access, exposure | Custodian of security |
| `operations` | Deployment, observability, alerts, continuity | Custodian of operations |
