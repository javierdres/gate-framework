# API clients

One small client per system (code platform, tracker, production source of truth), with no
dependencies, reading the person's own credential from their home folder with restricted
permissions. Used when the assistant has no connector for that system.

Name each credential file after the organisation and the system, for example
`~/.<org>-tracker-key`, never a generic `~/.tracker-key`. The same person may carry another
organisation's SDLC on the same machine, and a generic name makes the two read each other's keys.
