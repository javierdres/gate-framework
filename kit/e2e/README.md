# Automated flows

The shared runner for the flows of every product. Each product keeps its flows in
`products/<product>/e2e/`, one per validated use case.

Rules the runner enforces (GATE stage 8):

- Never against production: an allowlist of hosts is checked before anything opens.
- Real-world effects (charging, buying, signing, writing to third parties) are cut unless the
  environment simulates them and the run authorises it.
- Each person's configuration (URLs, test users, keys) lives outside the repository, with
  restricted permissions, and never passes through the chat.
- Every run leaves local evidence: who ran it, against what, and the result.
