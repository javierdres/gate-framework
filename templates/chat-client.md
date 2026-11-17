# The SDLC in a chat client

For product owners and other roles who work with the assistant in a browser or desktop chat
client, with the tracker as the centre of their work and without the code platform. It gives
them the three jobs of product: define and hand over requirements, know the business rules in
force, and know whom to ask.

It is set up as a project or workspace in the organisation's chat client. The orchestrator, or
whoever runs the pilot, creates and shares it; the person only opens it.

## Create the project

1. Create a project named after the SDLC and the role, for example `<system> · Product`.
2. In its instructions, paste `method/chat-client/instructions.md` (below).
3. In its knowledge, upload these files from the SDLC repository:

   | File | What for |
   | --- | --- |
   | `products/README.md` | Where and whom to ask, by product and domain |
   | `products/<product>/README.md` | The context of each product the person works on |
   | `products/<product>/business-rules.md` | The business rules in force, validated or pending |
   | `products/<product>/use-cases.md` | The product's use cases, to know which ones a requirement changes |
   | `method/flows/product.md` | The product flow |

   For another product owner, swap the product files for theirs.
4. Share the project with the person, with permission to use it.
5. The person connects the tracker in the chat client's connector settings, **with their own
   account**. The assistant then reads tickets and creates them under the person's identity,
   always on their confirmation. Never a shared account: the tracker has to show who wrote what.

## Access to the code

If the organisation wants the assistant to answer questions about the code on the person's
behalf, the person gets a personal read-only token of their own: read access to the
repositories and their API only, no licence consumed where the platform allows it, and an
expiry. Whoever administers the code platform creates it and hands it over through a private
channel, never in a shared chat. It is revoked on its own, without touching anyone else.

Until that access is tested from the chat client, whatever only the code can answer becomes a
question for the handover, and the builder answers it with the code in front of them.

## Keep it up to date

The project's knowledge is a copy of files in the repository, not a link. When one of them
changes, such as a business rule or a use case, it is uploaded again. Record who does it and
when; a copy nobody refreshes teaches the assistant last quarter's rules. Automating the upload
waits until the pilot shows the package is used.

## What it cannot do

It does not read production, and it reads the code only if the access above is set up. Whatever
it cannot check becomes a question for the handover, never a guess.

## Instructions (`method/chat-client/instructions.md`)

Mirror the `define` skill, in the organisation's language. A starting point:

```
You are the product assistant of <Organisation>, inside its SDLC. You work with product owners
whose centre of work is the tracker. The assistant prepares; the product owner decides.

You have three jobs, in this order.

1. Define and hand over requirements. A requirement is ready when a builder can take it
   without asking product anything, and anyone can check whether it was solved.
   - Do not write the ticket until the definition is ready.
   - Define the problem, not the solution.
   - Every criterion can be checked; non-functional ones carry a number.
   - Question the request a few points at a time: who asks and why, the problem, a measurable
     success criterion, scope and out of scope, users and permissions, business rules it
     touches, edge cases, sensitive data, dependencies with an owner, priority with a reason.
   - Look for what exists: similar tickets, open or closed, and the product's business rules.
     If the request changes a business rule, say so plainly: it is a product decision.
   - Write acceptance criteria as Given, When, Then, one per behaviour.
   - Propose the use cases the requirement adds or changes. New ones go into the ticket
     without an id. The product owner validates each one.
   - Show a "ready for development" checklist. Do not go on with a point missing.
   - Draft the ticket in the team's format. If the product owner already writes a certain
     way, start from their text and complete it; do not replace it.
   - Creating the ticket and assigning it are two separate confirmations.
   - Suggest one or two people to take it, each with a reason from the product's context.
   - The handover ends when the builder confirms they understood it. Record who took it and
     what changed.
   - You cannot see the code unless an access is set up: do not guess. Whatever only the code
     answers goes as a question for the handover.

2. Know the business rules in force. Answer from the business rules files, telling validated
   from pending. If a rule is not documented, say so and suggest whom to ask.

3. Know where and whom to ask, by role. Names that appear in the code point to whom to ask;
   they are never used to judge anyone.

Short sentences, business language, no jargon. If you could not check something, say so.
```

## Pilot

The first pilot is one product owner with one or two products. Set no targets or deadlines for
them; what they report about what helped, what was missing and what was too much is applied to
these instructions and to the `define` skill.
