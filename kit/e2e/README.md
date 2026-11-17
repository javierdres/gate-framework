# Automated flows

The shared runner for the flows of every product, on Playwright (GATE stage 8). Each product
keeps its flows in `products/<product>/e2e/`, one `*.e2e.js` per validated use case, and becomes
a project of its own: nothing to register. Flows walk the product from outside, against a
deployed test environment, from the person's machine. Nothing is created or run in the product
repositories.

```
cd <system>/e2e
npm ci && npx playwright install chromium     # the first time
npx playwright test --project <product>       # one product
npx playwright test --grep "@checkout"        # what a change walks through
sh run-unit-tests.sh                          # the runner's own tests, node only
```

A flow imports `test` and `expect` from `e2e/support/test.js`, not from `@playwright/test`, so
its page and its `api` helper go through the effects guard.

## The environment file

Each product reads `~/.<org>-e2e/<product>.env` (or `$E2E_HOME/<product>.env`), where `<org>` is
`organisation.short_name` in `system.yml`. It lives outside the repository, belongs to the person,
never passes through the chat and must be `0600`: the run refuses it otherwise.

| Key | What it holds |
| --- | --- |
| `BASE_URL` | The test environment. Without it, the product's flows are skipped and say which file to fill |
| `ALLOWED_HOSTS` | Comma-separated hosts the run may reach. A `BASE_URL` outside it stops the run. Production is never declared |
| `ALLOWED_ORIGINS` | Extra origins the page may load from; any other origin is aborted |
| `SIMULATED` | The integrations this environment simulates, for effects that need them |
| `USER_<ROLE>`, `PASSWORD_<ROLE>` | One test user per role |

## The effects guard

A flow never charges, buys, signs, registers or writes to a third party for real.
`products/<product>/e2e/effects.json` declares which calls have such effects, and
`support/effects.js` documents its format. Without that file the product runs strict: reads
only, and any write or GraphQL mutation is cut.

An effect goes out only when all of these hold: the case is tagged `@effect-<id>`, the run
authorises it, every integration it needs is in `SIMULATED`, the run is attended and the cap is
not reached.

```
E2E_EFFECTS=payment npx playwright test --project <product> --grep @effect-payment
```

With effects authorised the run goes one case at a time and without retries, because a retry
could repeat a charge. In CI or with `E2E_UNATTENDED` set, nothing with an effect goes out. The
cap is `E2E_MAX_EFFECTS`, 20 by default.

## Evidence

Every run leaves its evidence in `~/.<org>-e2e/evidence/<date-time>/`, a folder only its owner can
read: `summary.md` with who ran it, from which commit of the system, against which hosts, with which
authorisations, the result of each case, the effects that went out and the calls cut; `run.json`
with the same data; `report/` with the browsable report; and `manifest.json` with the SHA-256 of
every file, written last.
