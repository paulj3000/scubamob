# ScubaMob Task Tracker

Claude should update this file only when explicitly asked or when completing a roadmap task that clearly changes status.

## Active Work

- [ ] Triage and fix remaining CODE_REVIEW.md findings on `main`, starting with the other CRITICAL cross-app items in its §2 (unauthenticated admin/webhook endpoints, image upload pipeline).

## Recently Completed

- 2026-08-05: Replaced the admin-impersonation backdoor with an audited "login as user" support tool. Removed `scuba/libs/authentication/adminoverride.py` and its `AUTHENTICATION_BACKENDS` entry entirely (it let anyone who knew any admin's real email+password log in as any other user via the standard login path, with no audit trail). Replaced it with `scuba.security.services.impersonation` (`start_impersonation`/`stop_impersonation`), a new audited `security.ImpersonationEvent` model (actor, target, reason, started_at/ended_at), and a Django Admin-integrated trigger: a "Impersonate" action/link on the User admin that requires a typed reason and is gated on the real `is_superuser` flag (not `is_admin`/`is_staff`). Superusers cannot impersonate other superusers or themselves. A site-wide banner (via the `Scuba` context processor + `templates/layout.html`) shows "viewing as a support session" with a stop button while impersonating; `POST /impersonate/stop/` restores the original admin's session and closes the audit event. This is the app's first-ever migration for the `security` app (`scuba/security/migrations/0001_initial.py`) since no app in the project had migrations before now — it also captures the pre-existing `BlockedCountry`/`InvalidEmail`/`BouncedEmail`/`InvalidSignup` models as part of that same initial migration, which is expected for a first migration, not scope creep. Verified locally against an empty `db.sqlite3`; if a real deployed database already has these tables, `migrate --fake-initial` will be needed there instead of a plain `migrate`.
- 2026-08-05: Redid the full manual code review on `main` (previously only existed on the `restart` branch, which `main` predates and does not include). Reviewed `scuba/accounts` directly; delegated the "dive domain" cluster (divesites, diveshops, equipment, logbooks, galleries, divegroups, maps, entities, search) and "infra/platform" cluster (sitesettings, content, home, security, aws, libs, robots, environ, system, cache, settings.py) to two independent review passes. Result written to `CODE_REVIEW.md` on `main`. See that file for the full findings; highlights below under Known Technical Debt.
- 2026-08-05: Added `django-ses==4.7.2` to `requirements.txt` on `main` (it was already configured as `EMAIL_BACKEND` but missing from pinned dependencies, so any environment built strictly from `requirements.txt` would hit `ModuleNotFoundError` on the first outgoing email).

## Known Technical Debt

- [ ] Complete CI baseline.
- [ ] Verify all tests avoid live external calls.
- [ ] Finish environment-based secret configuration.
- [ ] Validate current migrations against MySQL.
- [ ] Continue model cleanup using data-preserving migrations.
- [ ] `manage.py makemigrations --check --dry-run` run with no app_label silently reports "No changes detected" even when unmigrated apps genuinely need an initial migration (confirmed 2026-08-05: `security` had zero migrations, `makemigrations --check --dry-run` said clean, but `makemigrations security` correctly generated `0001_initial.py`). Root cause not fully isolated — appears tied to how `MigrationAutodetector.changes()` is invoked across many simultaneously-unmigrated apps. Until every app has at least one migration, validate migration drift per-app (`makemigrations <app> --check --dry-run`), not project-wide.
- [ ] `scuba/accounts/tests/test_api_profile.py` (`test_me_profile`, `test_user_profile_1`) and `scuba/accounts/tests/test_api_user_profiles.py` (`test_get_basic_profile_is_not_private`, `test_get_basic_profile_is_private`, `test_get_basic_profile_is_private_but_buddies`) fail on a truly fresh test database with `no such table: view_profile` — confirmed on unmodified `main` via a throwaway worktree, so this is pre-existing, not a regression from any single session's changes. `accounts.models.ViewProfile` (`db_table='view_profile', managed=False`) expects a DB view that nothing in the codebase creates (no migrations, no `CREATE VIEW` anywhere). A prior session's "129 passed, 1 failed" pytest baseline did not reflect this; treat that number as stale. Needs either a data migration that creates the view or a rework of `apis/profile.py` to stop depending on it.
- [x] ~~Fix `scuba/libs/authentication/adminoverride.py`~~ — done 2026-08-05, see Recently Completed.
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

### 2026-08-05 session handoff (impersonation backdoor fix)

- Branch: `main`.
- Task status: complete. Replaced the `AdminOverride` impersonation backdoor with an audited Django-Admin-integrated "login as user" tool, gated on real `is_superuser`. See Recently Completed above for full behavior description.
- Files created: `scuba/security/services/__init__.py`, `scuba/security/services/impersonation.py`, `scuba/security/migrations/__init__.py`, `scuba/security/migrations/0001_initial.py`, `scuba/accounts/views/impersonation.py`, `scuba/accounts/templates/accounts/admin/impersonate_confirm.html`, `scuba/accounts/tests/test_admin_impersonation.py`, `scuba/security/tests/test_impersonation_service.py`.
- Files modified: `scuba/security/models.py` (new `ImpersonationEvent` model), `scuba/security/admin.py` (read-only admin registration for it), `scuba/accounts/admin.py` (impersonate action/view/URL on `UserAdmin`), `scuba/accounts/templates/accounts/admin/change_user_form.html` (object-tools link), `scuba/libs/context_processors/scuba.py` (`impersonating` flag), `templates/layout.html` (banner + stop button), `scuba/settings.py` (removed `AdminOverride` from `AUTHENTICATION_BACKENDS`), `scuba/urls.py` (`/impersonate/stop/`), `docs/claude/SECURITY.md`, `docs/claude/TASK_TRACKER.md`.
- Files deleted: `scuba/libs/authentication/adminoverride.py`, `scuba/libs/tests/test_authentication_adminoverride.py`.
- Migrations: `scuba/security/migrations/0001_initial.py` — first-ever migration for the `security` app (it had none before). Bundles `ImpersonationEvent` together with the app's pre-existing `BlockedCountry`/`InvalidEmail`/`BouncedEmail`/`InvalidSignup` models, since Django has to snapshot the whole app in its first migration. Verified against a fresh, empty `db.sqlite3` (`migrate` succeeds cleanly). Not tested against any database that might already have these tables from another source (e.g. a deployed environment built before migrations existed) — that would need `migrate --fake-initial` instead of a plain `migrate`, and was out of scope to verify without access to such an environment.
- Tests added: 13 new (`test_admin_impersonation.py` x8, `test_impersonation_service.py` x5), all passing.
- Commands run (venv: `/Coding/scubamob/ENV`): `manage.py check` (clean, only the pre-existing `staticfiles.W004` warning), `manage.py makemigrations security` (generated `0001_initial.py`), `manage.py makemigrations --check --dry-run` (no changes detected, expected now that `security` has migrations), `pytest` full suite (130 passed, 6 failed, 5 skipped).
- Failing tests (all pre-existing, none caused by this change — verified by running the same tests against unmodified `main` in a throwaway `git worktree`): `test_blocked_ip_address` (already known, `CODE_REVIEW.md` §2.5) plus 5 `view_profile`-table-missing failures in `test_api_profile.py`/`test_api_user_profiles.py` that were not previously documented — see the new Known Technical Debt entry above. The prior session's "129 passed, 1 failed" figure did not reflect these 5; treat it as stale.
- Also discovered and documented as technical debt: project-wide `makemigrations --check --dry-run` silently reports "No changes detected" even when an unmigrated app genuinely needs its first migration — only per-app invocation (`makemigrations <app> --check --dry-run`) is reliable until every app has at least one migration.
- Unresolved design questions: none — user chose Django-Admin-integrated trigger over a new API endpoint, and chose to block impersonating other superusers, both up front.
- Next recommended step: pick the next CRITICAL item from `CODE_REVIEW.md` §2 (unauthenticated `/tmp`-writing webhooks or the broken image/S3 upload pipeline are the next-highest blast radius).
