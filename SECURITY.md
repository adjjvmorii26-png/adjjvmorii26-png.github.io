# Security policy

This repository is a static site plus tooling scripts. There is no backend here,
no user accounts, and no data collection: the pages are HTML, CSS, and inline
JavaScript, and the only network calls go to the externally hosted organism API.

## Reporting

Open a private security advisory on this repository
(`Security → Advisories → Report a vulnerability`) rather than a public issue.
Please include the file or URL, what you observed, and how to reproduce it.

## Secrets

Nothing here should hold a credential. Bot tokens, API keys, and passwords belong
in GitHub Secrets (or a local `.env`, which is ignored) — never in HTML, markdown,
a commit message, or a chat transcript.

`scripts/check-secrets.py` fails the build when a credential-shaped string appears
in any file git would publish. `.cline-home/` is ignored because agent session
logs capture whatever was pasted into a conversation.

If a credential is exposed: **rotate it first**, then remove it from history.
Rotation is the only step that actually revokes access; deleting the commit does
not, because the value may already be cached, cloned, or scraped.

## Deployment

Published by GitHub Pages from `master` via `.github/workflows/deploy.yml`. The
workflow runs with `pages: write` and `id-token: write` only.
