# When the code platform has no merge requests or protected branches

Small teams sometimes run git on a plain server, or on a platform without protected branches or
mandatory approvals. GATE still needs the two controls those features give: nobody rewrites the
main branch, and nothing reaches it without someone else having reviewed it. This hook gives
them on any git server that runs hooks.

## What it enforces

On the default branch only:

- No deletion and no history rewrite: fast-forward only.
- Every new commit signed with an SSH key listed in `allowed_signers`, which also gives the SDLC
  a verifiable identity per person without platform accounts (`identity.method: ssh-signing` in
  `sdlc.yml`).
- Changes arrive as a merge commit with a `Reviewed-by: <identity>` trailer from a signer who is
  not the merge's author. A review is then a branch, a conversation in its ticket, and a merge
  that names who reviewed it.
- During formulation, the orchestrator sets `git config sdlc.formulation true` in the bare
  repository and the review requirement is lifted. Removing it is part of ending formulation.

## Setting it up

1. Each person creates an SSH signing key and configures git to sign every commit:
   `git config --global gpg.format ssh`, `git config --global user.signingkey ~/.ssh/id_ed25519.pub`
   and `git config --global commit.gpgsign true`.
2. `allowed_signers` at the root of the SDLC lists one line per person: their identity, the
   namespaces and their public key, for example
   `person@company.example namespaces="git" ssh-ed25519 AAAA...`. Adding someone is a reviewed
   change like any other.
3. On the server: `cp tools/server-hooks/update <repo>.git/hooks/update && chmod +x` it.

## What it cannot do

It does not run the pipeline, and it does not show a review interface. Those stay where the team
has them. What it guarantees is that the rules hold even when the platform does not enforce them.
