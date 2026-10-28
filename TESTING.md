# Site checks

Added 2026-10-28 after the free audit form returned HTTP 500 on every submission from
8 to 28 Oct (commit 39dfcb8 used `re` without importing it) and nobody noticed.

Four layers, each catches what the one before can miss:

1. **Tests** (`tests/`): ruff's crash rules (undefined names, syntax errors) on every
   `.py` file, plus pytest through Flask's test client: every sitemap page and built
   page is 200, root files, linked assets, apex and legacy redirects, the 410s, and
   `/api/audit`, `/api/contact`, `/api/booking` with valid and invalid input. SMTP and
   outbound HTTP are stubbed and the network is cut off, so tests never send mail.
   Run: `tools/ci/check.sh` (creates `.venv` on first run).
2. **Gates**: `.githooks/pre-push` runs the checks on the exact commit being pushed and
   refuses the push on failure (turn on per clone: `git config core.hooksPath .githooks`).
   `.github/workflows/checks.yml` runs the same on every push and PR to main, and Render
   (service redaccel-site) deploys only when those checks pass (`autoDeployTrigger: checksPass`).
3. **Live probe** on the mini: `~/Businesses/redaccel/agents/ops/health/site_probe.py`,
   every 15 minutes. It uses the `X-Redaccel-Probe` header (secret = `PROBE_SECRET` env var
   on Render, never in this public repo) to run `/api/audit` end to end without SMTP, and
   once a day sends one real `[TEST]` audit mail to contact@redaccel.com.
4. `/api/audit` prints every submission to the logs (`AUDIT_SUBMISSION ...`) before
   doing anything else, so a crash can no longer lose the lead's details.

## No-JavaScript form posts and the health check (2026-10-28)

- `/api/audit` also takes the browser's own form post (urlencoded or multipart). It answers
  with a full site page (the 404 page's shell, wording from `main.js`): 200 received, 400
  check the form, 503 with the mailto fallback. The JSON path is unchanged.
- `/healthz` returns `ok` when the built site's key files exist. Render's `healthCheckPath`
  on `redaccel-site` points at it, so a deploy that cannot start never replaces the live site.
