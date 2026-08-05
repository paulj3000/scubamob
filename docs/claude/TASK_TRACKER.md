# ScubaMob Task Tracker

Claude should update this file only when explicitly asked or when completing a roadmap task that clearly changes status.

## Active Work

- [ ] Triage and fix CODE_REVIEW.md findings on `main`, starting with the CRITICAL cross-app items in its §2 (admin impersonation backdoor, unauthenticated admin/webhook endpoints, image upload pipeline).

## Recently Completed

- 2026-08-05: Redid the full manual code review on `main` (previously only existed on the `restart` branch, which `main` predates and does not include). Reviewed `scuba/accounts` directly; delegated the "dive domain" cluster (divesites, diveshops, equipment, logbooks, galleries, divegroups, maps, entities, search) and "infra/platform" cluster (sitesettings, content, home, security, aws, libs, robots, environ, system, cache, settings.py) to two independent review passes. Result written to `CODE_REVIEW.md` on `main`. See that file for the full findings; highlights below under Known Technical Debt.
- 2026-08-05: Added `django-ses==4.7.2` to `requirements.txt` on `main` (it was already configured as `EMAIL_BACKEND` but missing from pinned dependencies, so any environment built strictly from `requirements.txt` would hit `ModuleNotFoundError` on the first outgoing email).

## Known Technical Debt

- [ ] Complete CI baseline.
- [ ] Verify all tests avoid live external calls.
- [ ] Finish environment-based secret configuration.
- [ ] Validate current migrations against MySQL.
- [ ] Continue model cleanup using data-preserving migrations.
- [ ] Fix `scuba/libs/authentication/adminoverride.py` — full account-impersonation backdoor reachable via the standard login path, no audit trail (`CODE_REVIEW.md` §2.1).
- [ ] Wrap `scuba/accounts/admin.py`'s custom `reset-password`/`emails/welcome` URLs in `admin_site.admin_view(...)` — currently unauthenticated, and broken even when reached (`CODE_REVIEW.md` §2.2).
- [ ] Remove/rework the unauthenticated `/tmp`-writing webhooks in `scuba/aws/apis.py` and `scuba/security/apis.py`, and fix the stored-XSS chain in `scuba/aws/admin.py`'s `reports()` (`CODE_REVIEW.md` §2.3).
- [ ] Actually enforce a password policy: `RegisterSerializer` (accounts) has none, and `validate_password` has a 4-20 char range plus an operator-precedence bug (`CODE_REVIEW.md` §2.4).
- [ ] `SetPasswordApi`/`SetUsernameApi` validate but never call `.save()`/`.update()` — both endpoints are silent no-ops (`CODE_REVIEW.md` §2.4).
- [ ] Reconnect or remove the dead IP/country signup-blocking code in `scuba/accounts/forms/signup.py` — root cause of the currently-failing test `test_blocked_ip_address` (`CODE_REVIEW.md` §2.5).
- [ ] Add authorization to every view in `scuba/equipment/views.py` — currently no login/ownership checks at all (`CODE_REVIEW.md` §2.6).
- [ ] Fix the image/S3 upload pipeline — broken in 5+ independent places across `scuba/libs/imageuploader.py`, `scuba/libs/aws/s3.py`, `scuba/libs/models/awsmodel.py` (`CODE_REVIEW.md` §2.7).
- [ ] `galleries`, `logbooks`, `diveshops`, `divegroups` are non-functional end-to-end (undefined methods/fields, dead code, broken imports) — see `CODE_REVIEW.md` §4 for the full per-app list before scoping any new feature work in these apps.
- [ ] `scuba/accounts/forms/__init__.py`'s `SettingsForm`/`PasswordForm` bind to `django.contrib.auth.models.User` instead of the project's swapped `AUTH_USER_MODEL`, and are wired live into `/settings/account`/`/settings/password/` — will fail the moment a user tries to use them (`CODE_REVIEW.md` §3.1).
- [ ] Add DRF throttling and cookie/TLS hardening settings (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, etc.) — currently absent project-wide (`CODE_REVIEW.md` §5).
- [ ] Add `timeout=` to every outbound `requests.get`/`requests.post` call (weather, chat, logbook, settings, alerting servers) — currently unbounded everywhere they were checked (`CODE_REVIEW.md` §2, §4, §5, multiple entries).

## Decision Log

Record durable decisions with a date.

### Template

```text
YYYY-MM-DD: Decision title

Decision:
...

Reason:
...

Consequences:
...
```

### 2026-08-05: Redo the full code review against `main` instead of relying on the `restart`-branch review

Decision:
Ran a fresh, independent full-codebase review on `main` rather than assuming the earlier review (done on `restart`, which branched later and applied fixes `main` doesn't have) still applied.

Reason:
`main` and `restart` had diverged — `restart` already fixed `USE_TZ`, the SES backend, and some settings.py issues that are still present, unfixed, on `main`. Reusing the old review's findings without re-verifying against `main`'s actual code would have risked stale/incorrect claims.

Consequences:
`CODE_REVIEW.md` on `main` is now a from-scratch, independently-verified document (not a copy of the `restart`-branch one) and found a substantially larger set of issues than the original pass, including several not previously documented (e.g. the `galleries`/`logbooks`/`diveshops` apps being non-functional end-to-end, the stored-XSS chain in `scuba/aws/admin.py`, and the non-functional `SetPasswordApi`/`SetUsernameApi` endpoints). Before merging or comparing the two branches, treat `main`'s `CODE_REVIEW.md` as authoritative for `main`'s actual state.

## Handoff Notes

At the end of a substantial session, record:

- current branch;
- task status;
- exact files changed;
- commands run;
- failing tests;
- unresolved design questions;
- next recommended step.

### 2026-08-05 session handoff

- Branch: `main`.
- Task status: full code review redone and written to `CODE_REVIEW.md`; `django-ses` dependency gap fixed; no other code changes made (findings-only pass, matching the original review's scope).
- Files changed: `CODE_REVIEW.md` (new content), `requirements.txt` (added `django-ses==4.7.2`), `docs/claude/TASK_TRACKER.md` (this update).
- Commands run: `python manage.py check` (clean), `python manage.py makemigrations --check --dry-run` (no changes detected — no migrations exist for any custom app), `pytest -q` (129 passed, 1 failed — `test_blocked_ip_address`, 5 skipped), `python -c "from django_ses import SESBackend"` (succeeds after the requirements.txt fix).
- Failing tests: `scuba/accounts/tests/test_account_forms_signup.py::TestAccountFormSignup::test_blocked_ip_address` — pre-existing, root-caused in `CODE_REVIEW.md` §2.5 (dead IP/country block-check code in `SignupForm`).
- Unresolved design questions: none raised this session; next step is prioritizing which CRITICAL findings in `CODE_REVIEW.md` to fix first (the admin-impersonation backdoor and the unauthenticated `/tmp`-writing webhooks are the highest-blast-radius items).
- Next recommended step: pick one CRITICAL item from `CODE_REVIEW.md` §2 to fix (with tests) rather than attempting the whole list at once, per the project's "smallest coherent change" rule.
