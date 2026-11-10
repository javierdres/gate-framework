# API clients

One small client per system (code platform, tracker, production source of truth), with no
dependencies, reading the person's own credential from their home folder with restricted
permissions. Used when the assistant has no connector for that system.

Every client takes the HTTP method as its first argument, `tools/clients/<system>.sh GET <path>`,
even when it only reads. The permissions guard relies on it: GET and HEAD pass, and any other
method, or a call with no method, asks like any other outward write. A GraphQL API takes every
call as a POST, so its client takes the intent instead, `QUERY` or `MUTATION`, and sends both as
POST: queries pass and mutations ask. When a write names a ticket key, such as `ABC-123`, a
tracker authorisation for `ABC` covers it.

Name each credential file after the organisation and the system, for example
`~/.<org>-tracker-key`, never a generic `~/.tracker-key`. The same person may carry another
organisation's SDLC on the same machine, and a generic name makes the two read each other's keys.
