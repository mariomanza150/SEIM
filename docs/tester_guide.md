# Tester toolkit guide

The tester toolkit helps a small group of human testers exercise SEIM on the **test**
environment (`seim.incognitoslw.com`, win-a8) and report problems with screenshots,
recordings and diagnostics. It is invisible everywhere else.

## When the toolkit is on

All three must be true:

1. `TESTER_TOOLS_ENABLED=true` in the server env file,
2. `DEPLOY_TIER` is `test` (or `development` locally),
3. the signed-in user has **Is tester** checked in Django admin (*Users → Testing*).

Otherwise every `/api/qa/*` endpoint returns 404 and the SPA shows nothing. System check
`qa.E001` refuses to start with the tools on and any other tier.

## For testers

- Sign in with **your own account**. The yellow **TEST** badge in the top bar opens the
  tester menu: Tester hub, Test accounts, My reports, Email outbox, Tester guide.
- **Test accounts** — act as a demo account (student, coordinator, partner, admin). A
  banner shows who you are acting as; **Return to my account** restores your session.
  Demo accounts are shared and reset from time to time.
- **Report issue** (button or `Ctrl+Shift+B`) — title, description, steps, severity,
  screenshot / screen capture / short recording, optional diagnostics (recent console
  errors, failed request URLs and status codes, navigation). Passwords, tokens and request
  bodies are never collected. Limits: `QA_MAX_ATTACHMENTS` files, `QA_MAX_IMAGE_MB` for
  images/logs, `QA_MAX_VIDEO_MB` for recordings.
- **My reports** — follow status and reply to questions from admins.
- **Email outbox** — the test server does not deliver email; messages sent to demo accounts
  and to you appear here (HTML is rendered in a sandboxed frame).
- Never enter real student data. Never share the demo password outside the test group.

## For admins

- **Designate testers**: Django admin → Users → select → action *Mark as tester* (or the
  *Testing* fieldset). Demo accounts can never be testers.
- **Triage**: every non-demo admin who is a tester receives new-report notifications and
  can triage in Django admin (*QA → Issues*) or the SPA report pages.
- **View as a user**: on *Test accounts*, admins can act as any non-superuser account for
  30 minutes. Every start/stop is recorded in *QA → Audit events*.
- **Reset demo data**: Tester hub → *Reset demo data* (queues `reset_demo_data` on Celery:
  `cleanup_demo_data` → `seed_demo_readiness` → `seed_test_accounts`). QA reports and real
  users are kept.

## Demo accounts and the demo password

- `manage.py seed_test_accounts` creates/updates one demo account per role, marks them
  `is_demo_account`, strips superuser, and sets every demo password to
  `TESTER_DEMO_PASSWORD`. `--tester EMAIL` marks a real user as tester.
- The password lives **only** in the server env file (win-a8:
  `C:\Users\mario\Documents\MARIO\SEIM\.env.local-prod`). It is never shown in the UI,
  logged, or committed. Rotate it by changing the env value, restarting the stack and
  re-running `seed_test_accounts`.
- Demo accounts cannot change their password or delete themselves, and neither can a
  tester who is acting as another account.
- On `DEPLOY_TIER=test` the seed commands fail if `TESTER_DEMO_PASSWORD` is missing; on
  `DEPLOY_TIER=production` they refuse to run at all. Local/CI development keeps the
  legacy passwords from `exchange/demo_seed.py`.

## Server configuration (win-a8)

```
TESTER_TOOLS_ENABLED=true
DEPLOY_TIER=test
TESTER_DEMO_PASSWORD=<generated, server only>
EMAIL_BACKEND=qa.mail.CaptureEmailBackend
```

`GIT_COMMIT` is set by `scripts/deploy-local-prod.ps1` so the version badge shows the
deployed commit.
