# Skills

One folder per skill, each with its `SKILL.md` in the open format: a `name`, a `description`
that says what it does and when to use it in the words a person would say, and plain
instructions. Each one implements a contract from GATE's `skills/`.

| Skill | Implements | Phase | Status |
| --- | --- | --- | --- |
| `establish` | `/establish` | Foundation | first version, from GATE |
| `onboard` | `/onboard` | Entry | first version, from GATE; adapt it |
| `guide` | Explains the SDLC to each profile | Entry | pending |
| `save` | Keeps something where it belongs | Entry | pending |
| `define` | `/define` and `/specify` | 1 | pending |
| `self-review` | `/self-review` | 1 | pending |
| `e2e` | The automated part of `/verify`, and the release regression of `/deploy` | 1 | pending |
| `harvest` | `/harvest` | 1 | pending |
| `review` | `/review` | 2 | later |
| `operate` | `/operate` | 2 | later |
| `postmortem` | `/postmortem` | 2 | later |

A skill enters here when a whole role uses it in any product, it does not depend on one
person's data or access, and it carries its own documentation. A skill for one product goes in
that product's folder; a personal one stays in the person's own skills.

A skill guides; it does not enforce. The hard controls stay on the code platform: pipeline,
approvals and protected branches.
