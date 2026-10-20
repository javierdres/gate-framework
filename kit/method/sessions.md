# The person's log

Each person has a log of their work with the assistant in `personal/sessions/`: one summary per
topic, with what was decided, what is pending and where each thing is. It is local, the
person's own, and ignored by version control.

The assistant keeps it on its own. The person does not have to ask.

## When the assistant writes

Whenever the work moves forward: a decision or a discarded option, a closed step, something
critical or a pending item, a pause or a close. Not at the end: a session can be cut short, and
what was not written is lost. A one-off question leaves no summary. After writing, it says in
one line what it updated.

## Where and how

One file per topic and start date: `personal/sessions/YYYY-MM-DD-topic.md`, following
`method/templates/session-log.md`. Short sentences. What can be read again in the
code, the tracker or the code platform is linked, not copied. Never credentials or clients'
personal data.

## The index

`personal/sessions/README.md` has two parts: **Open**, with the live critical and pending items,
each linking to its summary; and **By topic**, one line per summary. The headings can be in the
organisation's language; the installer leaves a `<!-- sdlc:open -->` marker under the first one,
and that marker is what the session start guard looks for, so keep it.

## When resuming

The assistant reads the topic's last summary before answering, and checks against the source
whatever may have changed since. If the person greets without a request, it mentions in one line
what is still open.

## What does not go here

A rule goes to the catalog, a product's context to `products/`, and whatever changes a task to
its ticket.
