# Profiles

One sheet per profile, answering the same five questions. This is the single source: the
onboarding, the plan and the access checker read from here.

## Profile ids

The only names a profile has anywhere in this SDLC: `GOVERNANCE.md`, `personal/profile.md`,
`tools/access-checks.tsv` and the session-start menu use exactly these. A new profile is added
here first.

| Id | Who | Menu option |
| --- | --- | --- |
| `product` | Product owners and managers | Product |
| `frontend` | Builds the user interface | Builder |
| `backend` | Builds services and data | Builder |
| `fullstack` | Builds both | Builder |
| `qa` | Verifies before production | Builder |
| `operations` | Production, incidents, infrastructure | Operations |
| `security` | Audits and reviews sensitive changes | Security |
| `leadership` | Leads the team and decides | Leadership |
| `support` | Handles users' cases | Support |

The building profiles are `frontend`, `backend`, `fullstack` and `qa`. `/establish` removes the
rows this organisation does not use.

## <Profile>

- **What they get**:
- **What they configure**: each access with the least privilege that works and how to obtain it
- **What data they work with**:
- **Which skills they use**:
- **How they know they are ready**: the access checker shows every access green

Whoever has no account on the code platform gets a read-only access of their own, with an
expiry. Never one token shared by several people.
