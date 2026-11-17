# Products

| Product | Product owner (role) | Use cases | Folder |
| --- | --- | --- | --- |

`/establish` creates the folders of the pilot products named in the interview. Any other
product's folder is created from `_template/` when someone first works on it, not before.

Each product's `README.md` says whom to ask, by role: who decides what is built, where its
tickets live, who knows the code best and who sees production. `define` reads it to suggest who
takes a requirement, and the names it finds there point to whom to ask; they never judge anyone.

A use case gets its id when it enters the product's `use-cases.md`, never in the ticket that
proposed it, so two tickets in flight never take the same number.
