# ScubaMob Code Review

Date: 2026-08-05
Branch: `main` (redone from scratch against `main` — this branch does **not** include the timezone/SES/settings fixes that were separately applied on the `restart` branch; every finding below was independently re-verified by reading the code on `main`, not carried over from any earlier review)
Scope: full application code under `scuba/` (models, views, apis, serializers, forms, admin, signals, libs), excluding `tests/`, `migrations/` (none exist for custom apps on this branch either), `__pycache__`, and `node_modules`. `scuba/settings.py` and project-level config reviewed separately.

Method: manual read-through of `scuba/accounts` (the largest and most security-sensitive app, reviewed directly, in full) plus two independent review passes over the remaining apps, split into a "dive domain" cluster (divesites, diveshops, equipment, logbooks, galleries, divegroups, maps, entities, search) and an "infra/platform" cluster (sitesettings, content, home, security, aws, libs, robots, environ, system, cache, `scuba/settings.py`). Every finding below cites a file and line and was independently verified by reading the cited code on `main` before inclusion.

Note on migrations: this project has **no** `migrations/` directory for any custom app on `main` (confirmed: `find scuba -iname migrations` returns nothing, and `manage.py makemigrations --check --dry-run` reports "No changes detected" only because there is no migration state to diff against). Django auto-creates their tables on `migrate` ("unmigrated apps" mode). This is not repeated as a per-app finding below.

---

## 1. Executive summary

`python manage.py check` passes and `pytest` is nearly green (129 passed / 1 known failure / 5 skipped), but neither exercises most of the code paths documented below. Across the ~20 Django apps reviewed:

- **An admin-impersonation backdoor with no audit trail is wired into the standard login path.** `scuba/libs/authentication/adminoverride.py`, registered in `AUTHENTICATION_BACKENDS`, lets anyone who knows any admin's real email+password log in **as any other user** by submitting the target's email with a specially-formatted password. The only trace is a session flag; there is no logging of which admin did it, when, or to whom.
- **Two unauthenticated admin URLs let anyone reset any user's password or resend their welcome email**, and both are additionally broken even when reached (`scuba/accounts/admin.py`).
- **Several unauthenticated webhook endpoints write attacker-controlled, unbounded data to fixed `/tmp` paths** (`scuba/aws/apis.py`, `scuba/security/apis.py`), and one of them chains into a **stored XSS in the Django admin** with zero authentication required to plant the payload (`scuba/aws/admin.py`).
- **Several entire features are non-functional end-to-end**, not just buggy at the edges: dive logging (`logbooks`), photo/album management (`galleries`), dive shops (`diveshops`), dive-group management (`divegroups`), and the equipment maintenance flow all call methods or reference model fields that do not exist, so their primary user-facing flows raise 500s or `AttributeError`/`TypeError` on first use.
- **The account-creation password policy is effectively unenforced**, and two "change password" / "change username" API endpoints validate input but never actually persist it — they return `200 OK` while doing nothing.
- **The image/file upload pipeline is broken independently in at least five places** (`scuba/libs/imageuploader.py`, `scuba/libs/aws/s3.py`, `scuba/libs/models/awsmodel.py`), and every app that depends on it (`content`, `divesites`, `galleries`) inherits the breakage.
- **`equipment/views.py` has no authorization at all**: any visitor, logged in or not, can view, edit, or delete any other user's equipment and maintenance records by guessing sequential integer IDs.
- **External provider calls are uniformly missing timeouts** (WeatherAPI, the chat/logbook/settings/alerting servers), the WeatherAPI base URL is plain HTTP, and the AWS SNS webhooks never verify the SNS message signature before trusting the payload.
- **`DEBUG` and `SECRET_KEY` both have insecure fail-open defaults** (`DEBUG=(bool, True)`, a hardcoded fallback secret key) in `scuba/settings.py`, so a misconfigured environment silently runs in debug mode with a source-committed secret.
- Two of the areas explicitly called out as done in `MODERNIZATION_ROADMAP.md` Phase 0 ("stabilize tests, migrations, configuration") are true only in a narrow sense: `manage.py check` and most of the test suite pass, but that's because the test suite doesn't touch most of the code paths documented here.

Findings are ranked CRITICAL / HIGH / MEDIUM / LOW within each section. Given the volume, this is a curated list of what would matter to a senior engineer reviewing this as a PR, not an exhaustive style-nit dump.

---

## 2. Cross-app critical findings (read this section first)

These are the highest-impact issues found anywhere in the review, gathered in one place regardless of which app they live in.

1. **CRITICAL — Admin impersonation backdoor with no audit trail.** `scuba/libs/authentication/adminoverride.py:9-46`, wired into `AUTHENTICATION_BACKENDS` in `scuba/settings.py:120-124`. Any user who knows an admin's real email+password can log in **as any other user** by submitting that target user's email as the login `email` and `"<admin_email>%<admin_password>"` as the password. It's reachable through the standard login path (`LoginSerializer.validate` → `django.contrib.auth.authenticate()`, `scuba/accounts/serializers/account.py:96-98`, live at `POST /login` via `LoginUserApi`) and through any other code path that calls `django.contrib.auth.authenticate()`, since Django tries every backend in `AUTHENTICATION_BACKENDS` in order. The only trace left behind is `request.session['adminoverride'] = True` — no record of which admin did it, when, or to whom. Impersonation authority is gated only by the `is_admin` boolean on the `User` model, not Django's staff/superuser permission system.

2. **CRITICAL — Unauthenticated admin actions on arbitrary users.** `scuba/accounts/admin.py:53-63`: the custom admin URLs `.../reset-password/` and `.../emails/welcome/` are registered via `re_path` directly against `self.reset_password` / `self.send_welcome_email_to_user`, **without** wrapping them in `self.admin_site.admin_view(...)` (the standard Django pattern required for custom admin views to inherit the admin's login/permission enforcement). Every other admin URL (list/add/change/delete) gets this protection automatically; these two do not. Result: anyone, unauthenticated, can `POST`/`GET` `/admin/accounts/user/<uuid>/reset-password/` to trigger a password-reset email for any user by ID, or `/admin/accounts/user/<uuid>/emails/welcome/` to force a welcome-email resend.
   - Both handlers are additionally broken even if reached: `reset_password` (line 65-71) calls `form.is_valid()` but never checks its return value before calling `form.save()`. `send_welcome_email_to_user` (line 109-119) calls `user.send_welcome_email()` with **no arguments**, but the model method requires an `email_template` parameter (`accounts/models.py:477`) — guaranteed `TypeError`.
   - Combined with `ValidateUserId` (duplicated, `AllowAny`, at both `scuba/accounts/apis/settings.py:140-151` and `scuba/accounts/iapis/settings.py:11-24`), which confirms whether a given UUID belongs to a real user, an anonymous caller has a full probe-and-spam path against any user account.

3. **CRITICAL — Unauthenticated webhooks write attacker-controlled, unbounded data to fixed `/tmp` paths, and one chains into stored XSS.**
   - `scuba/aws/apis.py` (`CodeBuildAPI`, `CodePipelineAPI`, both `AllowAny`, mounted at `/aws/cicd/build` and `/aws/cicd/pipeline`) and `scuba/security/apis.py:11-30` (`BouncedEmailsAPI`, `AllowAny`, at `/security/emails/bounced`) all append raw, unvalidated request bodies verbatim to hardcoded files under `/tmp` (`/tmp/build.txt`, `/tmp/pipeline.txt`, `/tmp/bounced.txt`) in append mode, forever, with no size cap — a disk-exhaustion DoS vector and a predictable-path symlink-race target.
   - None of these verify the AWS SNS message signature against `SigningCertURL` before trusting the payload, and the one serializer that should validate signature/replay fields (`SNSSubscriptionRequestSerializer`, `scuba/sitesettings/serializers.py:40-56`) has validator methods missing `@staticmethod` — DRF calls them as bound methods with an extra `self` argument, so every real AWS `SubscriptionConfirmation` request raises `TypeError` and the one legitimate use of this serializer is completely broken, while the unauthenticated `Notification`-type ingestion path (which never touches this serializer) still works.
   - Chained from the build webhook: `scuba/aws/apis.py` copies the attacker-controlled `build-id` field into `CodeBuildJobSerializer`, which creates a `CodeBuildJob` row with that value as its plain `CharField` primary key. `scuba/aws/admin.py:18-26`'s `reports()` admin display method then interpolates `obj.id` directly into an HTML string wrapped in `mark_safe()` with **no escaping**. An unauthenticated attacker can plant a `build-id` like `"><img src=x onerror=...>` that executes as stored XSS the next time any staff/admin user opens that project's admin page — zero authentication required to plant the payload.
   - `scuba/aws/apis.py:57,64` also has `return Response(status=status.HTTP_400_HTTP_400_BAD_REQUEST)` — not a real DRF status constant — so the "handle malformed payload" branch itself raises `AttributeError`, turning an intended 400 into an unhandled 500; `CodePipelineAPI.post` has no `try/except` around message parsing at all.

4. **CRITICAL — Weak/unenforced password policy across every signup and change-password path.**
   - `scuba/accounts/validators/signup.py:1-13` (`validate_password`, used by `SignupForm`) allows any 4-20 character password and never calls Django's configured `AUTH_PASSWORD_VALIDATORS`, so those validators are effectively dead configuration. The same function (with the same operator-precedence bug — `if password and len(password) < 4 or len(password) > 20:`, so a `None` password reaches `len(None)` and raises `TypeError` instead of returning `False`) is duplicated a second time in `scuba/accounts/forms/__init__.py:107-120`.
   - `scuba/accounts/serializers/account.py:9-62` (`RegisterSerializer`, live at `POST /register` via `RegisterUserApi`, `AllowAny`) applies **no password validation at all**.
   - `SetPasswordApi`/`SetPasswordSerializer` (`scuba/accounts/apis/signup.py:45-59`, `serializers/signup.py:29-47`) and `SetUsernameApi`/`SetUsernameSerializer` (`apis/signup.py:62-75`, `serializers/signup.py:9-26`) both **validate but never actually persist the change** — the views call `serializer.is_valid()` and return `200 OK` without ever calling `.save()`/`.update()`, so the serializers' own `update()` methods (which do contain the real `user.set_password(...)` / `user.username = ...` logic) are dead code. A user who "changes" their password or username via these endpoints sees success and nothing happens.

5. **HIGH — IP/country-based signup blocking is completely disconnected.** `scuba/accounts/forms/signup.py` imports `BlockedCountry`, `InvalidSignup`, and `InvalidIPAddress` (lines 6, 8) and accepts an `ip_address` constructor argument, but never references any of them in `clean()` or any `clean_<field>` method — the enforcement logic was removed or never finished. This is the direct root cause of the currently-failing test `test_blocked_ip_address` (`scuba/accounts/tests/test_account_forms_signup.py`), observed when running the suite. Separately, even a correct implementation would trust `request.META.get("HTTP_X_REAL_IP")` (`views/signup.py:29`, `signals.py:39`) — a client/proxy-settable header — with no indication in this codebase that a trusted reverse proxy strips/overwrites it before requests reach Django.

6. **HIGH — No authorization at all on equipment endpoints.** `scuba/equipment/views.py` (`index`, `archive2`, `archive3`, `practice_requirements`, `practice_require_edit`, `delete_requirement`): no `@login_required`, no ownership check against the record's `user`, and sequential-integer (not UUID) primary keys make every record trivially enumerable. Any caller, authenticated or not, can view, edit, or delete any other user's equipment or maintenance records. Directly violates the project rule that every user-owned queryset must be scoped explicitly.

7. **CRITICAL — Image/file upload pipeline is broken in at least five independent places**, and every app that depends on it inherits the breakage:
   - `scuba/libs/imageuploader.py:37`: `Image.ANTIALIAS`, removed in Pillow ≥10, called against the pinned `pillow==12.2.0` — `AttributeError` on every call to `compress_upload_image` (divesite banners, galleries, content).
   - `scuba/libs/imageuploader.py:70`: `S3.upload_raw_data(AWS_S3_BUCKET, filename, image_file, **header)` — arguments are positionally swapped against the real signature `upload_raw_data(name, fileobj, bucket=..., **headers)`, so the bucket name, filename, and file object all land in the wrong parameters on every call.
   - `scuba/libs/models/awsmodel.py:22-28` (`AWSModel.delete()`): references `S3` without importing it — `NameError` on every delete of any `AWSModel` subclass, concretely including `content.Image` (breaks the Django admin delete action).
   - `scuba/libs/models/awsmodel.py:30-38` (`AWSModel.upload_file()`): references `settings` without importing it, and calls `s3.upload_from_filename(...)`, a method that doesn't exist on the `S3` class at all.
   - `scuba/libs/fileutils.py:27`: calls `S3.upload_file_content(...)`, another method that doesn't exist on `S3` — `AttributeError` unconditionally.
   - Galleries' own upload path (`scuba/galleries/models.py`) stacks four more independent bugs on top of this (wrong buffer type for Pillow, reused text buffer as a binary save target, the same removed `Image.ANTIALIAS`, and float coordinates passed where Pillow requires integers) — see §4.5.

8. **HIGH — Core "album", "dive log", "dive shop", and "dive group" features are entirely non-functional**, not just buggy at the margins. See §4 (Dive Domain Cluster) for the full per-app breakdown; summarized here because these represent headline product features (per `PROJECT_CONTEXT.md`: "publish and selectively share media," "create, import, and share dive logs," "discover dive shops," connect via dive groups) being unusable as shipped.

9. **HIGH — insecure fail-open defaults for `DEBUG` and `SECRET_KEY`.** `scuba/settings.py:13-14`: `DEBUG=(bool, True)` and `DJANGO_SECRET_KEY=(str, "dev-only-insecure-secret-key")`. If the environment is ever incomplete in a real deployment, Django silently runs with `DEBUG=True` (full tracebacks and settings values leaked to any visitor on any of the many unhandled-exception paths documented in this review) and a hardcoded, source-committed secret key shared across every clone of this repo.

---

## 3. `scuba/accounts` (reviewed directly, in full)

### CRITICAL

1. **Two different `SignupForm`/settings forms disagree on which `User` model to use, and the wrong one is wired live.** `scuba/accounts/forms/__init__.py:1-138` defines `SettingsForm`, `PasswordForm`, `EmailInviteForm`, and a second, different `SignupForm` — all importing `from django.contrib.auth.models import User` (line 5), Django's **built-in default** user model. But `scuba/settings.py` sets `AUTH_USER_MODEL = 'accounts.User'`, which means `django.contrib.auth.models.User` has no migrated table in this project at all. `scuba/accounts/urls_settings.py:5-16` wires exactly these broken `SettingsForm`/`PasswordForm` classes into the live `/settings/account` and `/settings/password/` routes (`settings_views.settings`, `views/settings.py`). Any user attempting to update their profile or change their password through these routes will fail as soon as the form tries to resolve or save against a nonexistent model. (The *other*, correct `SignupForm`, in `scuba/accounts/forms/signup.py`, does import `scuba.accounts.models.User` and is what `views/signup.py` actually uses for registration — so the two modules silently disagree with each other.)
2. **`EmailInviteForm.save()` (`forms/__init__.py:70-104`) is entirely broken.** It references `self.user`, which is never set anywhere in `__init__`, and filters/creates `UserBuddyRequest` using `friend=` and `email=` keyword arguments — neither field exists on the `UserBuddyRequest` model (`accounts/models.py:692-711`, whose actual fields are `user`, `buddy`, `is_active`, `is_accepted`, `is_deleted`). Every call raises `AttributeError`/`FieldError`/`TypeError`.
3. **`User.get_setting()` (`models.py:419-435`) raises `NameError` on its own fallback path.** The "generate a default" branch references `settings_key` (lowercase, undefined) instead of the actual local variable `setting_key` — any first-time lookup of a setting with no existing row crashes.
4. **Welcome-email generation is broken by two independent missing imports.** `User.send_welcome_email()` (models.py:477-487) checks `if EMAIL_BACKEND:` but `EMAIL_BACKEND` is never imported anywhere in `models.py` — `NameError`. `generate_welcome_email()` (models.py:489-504) uses `BeautifulSoup` (only referenced in a commented-out line elsewhere in the file) and `self.full_name` (the model only defines a `get_full_name()` *method*, not a `full_name` property) — both raise on every call.
5. **Profile-image-upload-as-base64-string is broken by two independent missing methods.** `User.upload_profile_image_as_string()` (models.py:386-417) calls `self.get_aws_id()` — this method exists only on the unrelated `Divesite` model (`divesites/models.py:52`), not on `User` — and `User.upload_image(...)`, a classmethod that doesn't exist anywhere in the codebase. Both raise `AttributeError`.
6. **`User.get_active_buddy_requests()` (models.py:125-137) is completely broken.** It does `user = self.user` (there is no `.user` attribute on `User` — `self` already *is* the user), then `user.friend_requested.filter(...)` (no such related name exists; the actual relation is `buddy_requested`), then `.sort('first_name')` on a queryset (`.sort()` is a Python list method, not a QuerySet method). Guaranteed to raise on the first line alone.
7. **Duplicate `GetBuddiesListApi` class definition silently shadows the safe one and discloses arbitrary buddy lists.** `scuba/accounts/apis/profile.py` defines `GetBuddiesListApi` twice: once at line 14 (correctly scoped to `self.request.user`), and again at line 142-159 with `lookup_field = 'id'` and **no `permission_classes`** — the second definition wins (later class statement in the same module overwrites the name), meaning any authenticated caller can fetch **any other user's** buddy list by supplying their id in the URL, with no ownership, block, or privacy check at all.
8. **Duplicated, drifted `FeedSerializer` implementations leak anonymous check-in identity through one of two equivalent endpoints.** `scuba/accounts/serializers/feed.py:33-73` and `scuba/accounts/serializers/profile.py:231-270` both define a `FeedSerializer.get_item()` that renders a `DivesiteCheckin` — but only the `feed.py` copy checks `obj.is_anonymous` before returning full checkin data; the `profile.py` copy does not. `apis/profile.py`'s `GetFeedApi` (via `serializers/profile.py`) therefore leaks the identity of "anonymous" check-ins, while `apis/feed.py`'s otherwise-identical `GetFeedApi` (via `serializers/feed.py`) does not — the same underlying data is protected or not depending purely on which of two duplicate endpoints is hit.
9. **`GetFeedApi` (both `apis/profile.py:162-179` and `apis/feed.py:27-44`) lets any authenticated user view any other user's feed by ID**, with no ownership, privacy, or block check in the queryset itself (contrast with `ProfileSerializer.to_representation()`, `serializers/profile.py:68-90`, which *does* correctly strip private-profile fields for non-buddies — that protection is not applied here).

### HIGH

10. **`CanViewProfile.has_permission()` (`permissions.py:6-26`) has a broken "did they block me" check.** `obj.blocked.filter(user=obj)` is tautological — `obj.blocked` is already the related manager filtered to `user=obj`, so adding `.filter(user=obj)` again changes nothing; it does not check whether `obj` has blocked the *viewer* (`user`). The correct filter would be `obj.blocked.filter(buddy=user)`. As written, one direction of the mutual-block check never actually verifies anything about the requesting user.
11. **`can_view_profile` decorator (`decorators.py:7-42`) never checks `profile.is_private` at all.** It gates on blocks, `is_active`, and `is_hidden`, but the `is_private` boolean that exists specifically to mark a profile non-public (`models.py:73`, `ViewProfile.is_private`) is never read here — a private profile is only as protected as the (separately buggy, see #10) block check and the `is_active`/`is_hidden` checks make it.
12. **Unauthenticated PII disclosure via `UserListApi`.** `scuba/accounts/apis/chat.py:18-36`, `permission_classes = [AllowAny]`: given a list of user ids, returns each user's full name and profile-image URL (`serializers/chat.py:14-35`) with no privacy, block, or `is_private` check whatsoever. Combined with the enumerable `ValidateUserId` endpoint (see §2 finding 2), an anonymous caller can enumerate valid user ids and then pull full name + photo for each.
13. **Debug statements left in production code paths log sensitive data.** `LoginSerializer.validate()` (`serializers/account.py:111-118`) has four leftover `print(f"USERNAME {username}")` and three `print(user)` calls that fire on every username/password login attempt, writing to server stdout/logs. `UserSettingApi.post()` (`apis/settings.py:95-96`) does `pprint(request.data)`. `UserListSerializer.get_profile_image()` (`serializers/chat.py:22`) prints the CloudFront URL on every call.
14. **Missing timeouts on outbound calls to internal services**, consistent with the pattern found project-wide: `apis/chat.py`'s `ChatWUserApi`/`GetChatsApi`/`GetChatMessagesApi`/`GetAllChatsApi`, and `apis/settings.py`'s `UserSettingApi`/`UserSettingListApi`, all call `requests.get`/`requests.post` against the chat/settings servers with no `timeout=`.
15. **`GetGalleryApi`/`GetAlbumsApi` (`apis/profile.py:59-79, 105-118`) use `self.request.id`, which does not exist on `HttpRequest`** (the id should come from `self.kwargs['id']`, as the sibling `GetFeedApi` in the same file correctly does) — `AttributeError` on every call.
16. **`GetPhotosApi.get_queryset()` (`apis/profile.py:120-125`) is missing a `return` statement** — it calls `self.request.user.get_photos()` but discards the result, so the view always operates on `None` as a queryset.
17. **`AddUIMessageView.post()` (`views/profiles.py:39-45`) is broken by two independent bugs**: `request.get('message')` — `HttpRequest` has no `.get()` method — and `JsonResponse()` called with no `data` argument, which `JsonResponse.__init__` requires. Every request to this view raises.

### MEDIUM

18. **`ValidateUserId` is duplicated verbatim** (`apis/settings.py:140-151` and `iapis/settings.py:11-24`), both `AllowAny`, both usable as a user-existence oracle; the `iapis` copy has marginally better exception handling (also catches `ValidationError`, returns 400) but the underlying exposure is the same in both.
19. **`LoginSerializer.create()` (`serializers/account.py:189-201`) calls `user.generate_default_playlists()`**, a method that does not exist anywhere in the codebase. Currently dormant/dead — the login view never calls `.save()`/`.create()` on this serializer — but confirms leftover copy-paste from an unrelated project template.
20. **`PrimaryEmailSerializer.update()` and `UserSettingSerializer.update()` (`serializers/settings.py:59-64, 86-91`) are identical copy-paste**, both calling `set_primary_email(...)` — the setting-update serializer's `update()` doesn't actually update a setting. Currently unused/dead since `UserSettingApi`'s view methods proxy to an external HTTP settings service instead of calling `.save()`.
21. **`admin.py`'s `all_unexpired_sessions_for_user` (line 78) filters `Session.objects.filter(expire_date__gte=datetime.now())` using a naive `datetime`** — currently harmless since `USE_TZ = False` on this branch, but will need to change to `django.utils.timezone.now()` the moment timezone support is enabled (as it was on the `restart` branch).
22. Debug print in `signals.py`-adjacent management command output and elsewhere is low-impact; see LOW below for the remaining instances.

### LOW

23. `signals.py`'s `post_login` handler (lines 35-48) hardcodes every logged-in user's session timezone to `America/Los_Angeles` and zipcode to `92107` regardless of where they actually are, with a dead `try/except UnknownTimeZoneError` around a hardcoded, always-valid timezone string.
24. `forms/admin.py`'s `ChangeAccountForm`/`SettingsForm` (lines 18-93) call `instance.get_ignore_tracking()`, `get_is_protected()`, `get_is_staff()`, `set_ignore_tracking()`, `set_is_protected()`, `set_is_staff()` — none of these methods exist on `User` (confirmed via repo-wide search). Currently dead/unused (not wired into `UserAdmin`), but a landmine if ever connected.
25. `views/collections.py`'s `IndexView` defines `get_context_datas` (typo for `get_context_data`) — the override is silently never called by Django.
26. `serializers/divesites.py`'s `UserDivesiteFavoriteSerializer.create()` (lines 35-42) and `xto_representation()` (lines 48-61) both contain unreachable debug code (`from pprint import pprint`, etc.) after a `return`/behind an `x`-prefixed disabled method name.
27. Duplicate `validate_password` function (identical operator-precedence bug) exists in both `validators/signup.py` and `forms/__init__.py`.

---

## 4. Dive Domain Cluster (divesites, diveshops, equipment, logbooks, galleries, divegroups, maps, entities, search)

### divesites

**CRITICAL**

1. **Nonexistent model methods called from live public API endpoints.** `scuba/divesites/apis.py:36` (`DivesiteListApi.get_queryset`, `AllowAny`, at `/api/divesites/` and `/api/divesites/getlocaldivesites`) calls `Divesite.get_local_divesites(lat, lng, distance)`. `apis.py:71` (`DivesiteReviewListApi.get_queryset`) calls `Divesite.get_local_diveshops(lat, lng, distance)`. Neither method exists anywhere in the codebase (`Divesite` only defines `get_all_active_divesites`). Every hit to these two endpoints raises `AttributeError` → 500.
2. **Banner upload is broken across three independent bugs** (`scuba/divesites/models.py`): `upload_banner()` (line 114) calls `.create()` on `self.banner`, which is a `@property` returning a string, not a related manager; `get_banner()` (lines 88-98) checks `hasattr(self, 'divesitebanner')`, but the actual related name is `banners` (line 157), so this is always `False`; `DivesiteBanner.image_cleaned` (line 164-165) references `self.image`, but the model's field is named `banner` (line 158). The admin action driving this (`DivesiteAdmin.upload_banner`, `admin.py:54-62`) is also `@csrf_exempt` on an authenticated, staff-only POST file-upload endpoint — CSRF protection deliberately disabled on an admin action.
3. **Wrong S3 call signature breaks every upload.** `scuba/libs/imageuploader.py:70`: arguments passed to `S3.upload_raw_data` are positionally swapped against its real signature (see §2 finding 7) — affects `Divesite.upload_banner` directly.
4. **Pillow API removed** (`imageuploader.py:37`, `Image.ANTIALIAS`) — breaks every divesite banner upload, same root cause as §2 finding 7.

**HIGH**

5. **Anonymous checkin identity leak.** `DivesiteCheckin.is_anonymous` (models.py:192) is recorded but never enforced by the API — `DivesiteCheckinSerializer` (serializers.py:361-374) unconditionally includes the `user` field, and `CheckinApi.list()` (apis.py:127-133) returns it regardless of the flag. A user who checks in "anonymously" is still fully identified via `GET /api/divesites/<id>/checkins`.
6. **No lat/long validation.** `Divesite.lat`/`Divesite.long` (models.py:20-23) have no `MinValueValidator`/`MaxValueValidator`/`CheckConstraint`. Out-of-range coordinates are accepted and fed unchecked into the external weather lookup and map rendering — direct violation of the project's stated coordinate-validation rule.

**MEDIUM**

7. Non-unique `url` slug (models.py:19, regenerated from `name` on every save with no `unique=True`) can raise `MultipleObjectsReturned` in `SiteView.dispatch()` (`views.py:49`) when two divesites share a name.
8. `get_divesite_stats(self, date)` (models.py:125-135) never actually filters by the `date` argument — silently aggregates all-time stats instead of the requested day, on every divesite detail view.
9. `DivesiteSerializer.get_stats()` (serializers.py:76-111) performs a `.save()` write and an inline, uncached-path external weather call from what is otherwise a GET request on an `AllowAny` endpoint.
10. `DivesiteFavorite` (models.py:176-182) has no DB-level uniqueness constraint on (`divesite`, `user`) — only enforced by `update_or_create` in the serializer — so any other write path can create duplicates, which then fan out from `FavoriteListApi` (no `.distinct()`).
11. Measurement fields are inconsistently typed across models (`FloatField` on `DivesiteReview`, `PositiveSmallIntegerField` on `DivesiteCheckin`/`DivesiteDailyStats` for the same real-world quantity) — none use `DecimalField` as the project rules require.

**LOW**

12. `Divesite.long` is declared twice, identically (models.py:22-23).
13. `DivesiteReviewSerializer.validate()` ends with a redundant no-op `.filter()` call (serializers.py:238).

### diveshops

Effectively a non-functional stub.

**CRITICAL**

1. `Diveshop` model (`scuba/diveshops/models.py`) has every field except `name` commented out, including `get_local_diveshops`, which sits entirely inside a `'''...'''` block and does not exist as a callable.
2. `scuba/diveshops/views/__init__.py:25` calls `Diveshop.get_local_diveshops(...)` — guaranteed `AttributeError`, live at `/diveshops/json/getlocaldiveshops/`.
3. `scuba/diveshops/forms.py`: `DiveShopAddressForm.Meta.model = 'diveshops'` (line 55) is a string, not a model class — crashes at import time. The file also imports a top-level `utils` package (`from utils.external.google_address import GoogleAddress`) that doesn't exist anywhere in the repo.
4. `scuba/diveshops/views/shopadmin.py:2` imports `django.core.context_processors.csrf`, removed from Django long ago, and imports `diveshops.forms` (missing the `scuba.` prefix) — two independent `ModuleNotFoundError`s. Not currently reachable (routes are commented out in `urls.py`), but confirms this module is broken if re-enabled.

### equipment

**CRITICAL**

1. **No authorization on the equipment list.** `scuba/equipment/views.py`'s `index()` (`Equipment.objects.all()`) has no `@login_required` and no per-user scoping — every visitor sees every user's full equipment list at `/equipment/`.
2. **IDOR on maintenance records.** `practice_require_edit`, `delete_requirement` (views.py:87-108) perform zero ownership checks — any user can edit or delete any other user's `EquipmentMaintenance` row by id (a sequential integer, not a UUID).
3. **Broken template paths guarantee 500s.** `archive2`, `archive3`, `practice_requirements`, `practice_require_edit`, `delete_requirement` load templates without the `equipment/` app-namespace prefix that the actual files live under — `TemplateDoesNotExist` on every call.

**MEDIUM**

4. `edit()` lacks `@login_required`; on POST with no `equipment_id`, an anonymous request proceeds to `form.user = request.user` (an `AnonymousUser`) and crashes with an uncaught `ValueError` rather than a controlled redirect — protected by accident, not by design.
5. `EquipmentForm.save()` (forms.py:23-27) never returns the saved instance and requires an externally-injected `self.user` before saving.
6. `Equipment`/`EquipmentMaintenance` use default auto-increment integer PKs (unlike every other model in this domain, which uses `UUIDModel`), making finding #2's IDOR trivially enumerable.

### logbooks

The user-facing feature is entirely non-functional.

**CRITICAL**

1. `DiveForm` (`scuba/logbooks/forms.py`) is a plain `forms.Form`, but `views/dives.py`'s `edit()` constructs it with `user_id=`/`log_id=` kwargs that `forms.Form.__init__` doesn't accept — `TypeError` on every GET/POST to `/logbooks/dives/edit/`.
2. `DiveForm.save()` calls `super().save(data)` — `forms.Form` has no `save()` method.
3. `LogbookFolder.get_logs()` (models.py:25-27) references an undefined name `DiveLog` and a nonexistent `self.guid`.
4. `Logbook.get_logs(user)` (models.py:15-17) is a stub that always returns `None`.
5. `logbookfolderlogs`/`logbookfolders` (`views/logs_json.py`) both unconditionally `raise NotImplementedError`, wired live.
6. `GetAllLogbooks` (`apis/logbook.py`, at `/api/logbooks/`) calls into `LogbookApi.get_all_logbooks` (`sitesettings/models.py:370-375`), which itself calls `query_logbook_server()` on a value that is already parsed JSON, not a URL — raises `requests.exceptions.MissingSchema`, uncaught by the surrounding `except requests.ConnectionError`. 500s on every call.

Note: the actual `Logbook`/`LogbookFolder`/`LogbookTag` Django models are never referenced by any view, API, or admin anywhere — the real logbook data path is entirely external and independently broken (above), making these ORM models dead weight.

**HIGH**

7. `LogbookApi.query_logbook_server`/`post_to_logbook_server` (`sitesettings/models.py:390-403`) call `requests.get`/`requests.post` with no `timeout=` — a hung upstream logbook server blocks the worker indefinitely.

### galleries

The most severely broken app in this review.

**CRITICAL**

1. `views/albums.py:5` imports `django.core.urlresolvers.reverse`, removed since Django 2.0 — `ModuleNotFoundError` on import (currently dead/unreachable since `urls.py` never imports this module, but broken code sitting live in the tree).
2. `showalbum`/`editalbum` (`views/__init__.py:19,31`, live at `/gallery/albums/<uuid>` and its edit route) call `get_object_or_404(Album, guid=album_id)` — `Album` has no `guid` field — `FieldError` on every request. (The ownership check written after it, `album.user != us_request.user`, is correct but never executes.)
3. `Album.to_json()`/`add_image()` (models.py:145-148, 87-98) reference `self.guid`, which doesn't exist on `Album` — breaks every caller across `galleries/api.py` and `views/albums.py`.
4. `AlbumMedia.media` (models.py:192) is a `ForeignKey` to `Album` again instead of `Media` — this join table cannot actually associate media with albums.
5. `Media.upload_new_media()` (models.py:76-77) creates a `Media` with `content_type`/`aws_filename` kwargs that don't exist as fields on the model, and omits the required `user` FK — breaks the shared `create()` used by both `AlbumSerializer` and `MediaSerializer`, so `MediaUploadApi.post()` is completely broken.
6. `Media.get_image()`/`get_thumbnail()` (models.py:44-48) reference `self.image`, a field that doesn't exist on `Media`.
7. `Album.add_image_thumbnail()` (models.py:100-140) stacks four independent guaranteed-crash bugs: wraps binary image bytes in a text `StringIO`; reuses that same `StringIO()` as a Pillow save target (Pillow needs binary); calls the removed `Image.ANTIALIAS`; passes float coordinates to `bg.paste()`, which requires integers.
8. `Album.add_image()`/`add_image_thumbnail()` call `S3.upload_raw_data(name, data, settings.GALLERY_BUCKET, headers)` with `headers` as an extra 4th positional argument the real 3-parameter signature doesn't accept.
9. `User.get_account()`/`User.get_album_by_guid()` are called (models.py:93,108; `views/images.py:28`) but exist nowhere in the codebase.
10. `us_request.REQUEST` is used in three places (`views/albums.py`, `galleries/api.py:62`, `views/images.py:19`, including the live upload endpoint) — `HttpRequest.REQUEST` was removed in Django 1.9.
11. `galleries/signals.py`'s `pre_delete` handler on `Media` does `instance.album_image.all()` — no such reverse relation exists — deleting a `Media` row **always fails**.
12. `galleries/api.py:json_getalbumimages` (lines 100-112) ends with `return JsonResponse()` with no `data` argument, discarding the correctly-computed (and correctly ownership-scoped) result — `TypeError` on every request.

**HIGH**

13. Upload content type/extension is derived solely from the client-supplied `content_type` header with no verification against actual file bytes and no size limit anywhere in the path.
14. `GetDailyPicApi.get()` (`api.py:15-20`) and `getalbums()` (`api.py:77-89`) both call attribute access on a `.first()` result that can be `None` — `AttributeError` whenever no matching row exists.

**MEDIUM**

15. `json_deletealbum` (`api.py:92-97`) does no lookup, no ownership check, and no delete — it just returns an empty array while looking like a success response.
16. `views/albums.py:json_createalbum` uses `account=us_request.user`, but the model's FK is named `user`.
17. `galleries/admin.py` registers only `Album` — `AlbumImage`, `Media`, `AlbumMedia`, `DailyImage` have no admin/moderation visibility at all.

### divegroups

**CRITICAL**

1. The only view in this app, `index()` (`views/__init__.py:13`, live at `/groups/`), calls `user.get_account()`, which doesn't exist anywhere — `AttributeError` on every visit.
2. This view has nothing to do with dive groups: it operates on `UserBuddyRequest`/buddy relations (a feature belonging to `accounts`) and renders `friends/index.html`. The actual `Group`/`GroupUser`/`GroupUserJoinRequest` models in `scuba/divegroups/models.py` are never referenced by any view, API, serializer, or admin — the stated "dive groups" feature is entirely unimplemented.

**HIGH**

3. `Group.privacy` (models.py:10) is defined but never read or enforced anywhere — provides zero actual access control if intended to mark a group private.

**MEDIUM**

4. `Group.is_user_admin()` (models.py:17-18) checks only group membership, ignoring `GroupUser.isadmin` entirely — any member would pass an "is admin" check. Currently unused, but a live privilege-escalation bug the moment something gates on it.
5. `GroupUser.isadmin` (models.py:24) defaults to `True` — any code path creating a `GroupUser` without explicitly passing `isadmin=False` silently grants admin rights.
6. `Group.title` (models.py:8) is globally `unique=True` across the whole platform — two different users can't each create a group with a common name.

### maps

**HIGH**

1. `Weather.get_current_by_q_param`/`get_current_by_postal_code`/`get_current_by_lat_lng` (`scuba/libs/weather.py`) all call `requests.get(...)` with no `timeout=`. This backs `Region.get_weather_by_lat_long` (`maps/models.py:30-35`), invoked synchronously from `DivesiteSerializer.get_stats()` on an `AllowAny` endpoint on essentially every divesite request without a warm cache — a hung upstream weatherapi.com response blocks the worker indefinitely, reachable by anonymous traffic. The base URLs are also plain `http://`, not `https://`.
2. `get_current_by_postal_code` never checks `res.status_code` (unlike its siblings) before calling `res.json()`.

**MEDIUM**

3. `Region.get_weather_by_lat_long` performs no validation on the `lat`/`long` values before forwarding them externally — consistent with the missing coordinate validation on `Divesite` itself.

### entities

No functional or security findings — inert scaffolding (two reference-data models, an empty `views.py` stub, nothing wired up).

### search

**MEDIUM**

1. `SearchLocation` has no DB-level uniqueness on (`user`, `location`); `SearchView.dispatch()` relies on `get_or_create` alone, which is not race-safe under concurrent requests.
2. The `location` value is written via `get_or_create` without `full_clean()` — a value longer than `max_length=128` silently succeeds on SQLite but raises `DataError` on MySQL, a concrete parity gap against the project's stated production target.

**LOW**

3. Leftover debug `print()` statements in `SearchView.dispatch()`, including printing the fetched/created object (containing user search-location text) to server logs.

---

## 5. Infrastructure / Platform Cluster (sitesettings, content, home, security, aws, libs, robots, environ, system, cache, settings.py)

### Project-level settings (`scuba/settings.py`, `requirements.txt`, `scuba/urls.py`)

**HIGH**

1. Insecure fail-open defaults for `DEBUG`/`SECRET_KEY` — see §2 finding 9.
2. `USE_TZ = False` (settings.py:185) with timezone-sensitive code paths elsewhere in the codebase — every `auto_now_add`/`auto_now` field across this cluster stores naive datetimes; mixing with any aware-datetime logic risks `RuntimeWarning`s and incorrect comparisons the moment timezone support is enabled (as it was on the separate `restart` branch).
3. `EMAIL_BACKEND = 'django_ses.SESBackend'` (settings.py:217) with no `django-ses` in `requirements.txt` as of the start of this review (now added — see Follow-ups below) — every `django.core.mail` call raised `ModuleNotFoundError` until fixed.
4. `CORS_ORIGIN_ALLOW_ALL = True` / `CORS_ALLOW_ALL_ORIGINS = True` (settings.py:274-275) are currently dead (no `django-cors-headers` installed/configured), but a landmine: whoever adds that package later silently inherits "allow every origin" as the pre-configured default on a site using session-cookie auth.
5. `REST_FRAMEWORK['PAGINATE_BY'] = 2` (settings.py:144) is a DRF 2.x-era setting name with no effect under DRF 3.16 — every `ListAPIView` in the project returns a fully unpaginated queryset.
6. `googlemaps` is imported at module scope by `scuba/libs/external/google_address.py` (used live by `scuba/diveshops/forms.py`) but is not pinned in `requirements.txt`.

**MEDIUM**

7. No DRF throttling configured anywhere (`DEFAULT_THROTTLE_CLASSES`/`RATES` absent), combined with numerous `AllowAny` endpoints found throughout this review.
8. No `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE`/`SECURE_SSL_REDIRECT`/`SECURE_HSTS_SECONDS` anywhere, combined with `BasicAuthentication` in `DEFAULT_AUTHENTICATION_CLASSES`.
9. `IS_PRODUCTION = False` (settings.py:279) is a hardcoded literal, not environment-driven — any template logic gated on it never activates in a real deployment.
10. Dead/contradictory settings clutter: commented `COMPRESS_CSS_HASHING_METHOD`, `x`-prefixed disabled `xCOMPRESS_FILTERS`/`xCOMPRESS_YUGLIFY_BINARY` left in place, unused `TEST_PEP8_DIRS`.

### `scuba/libs/authentication`

**CRITICAL** — `AdminOverride` account-impersonation backdoor — see §2 finding 1.

**MEDIUM**

- `rest_framework.authentication.TokenAuthentication` is misplaced in `AUTHENTICATION_BACKENDS` (settings.py:121) — it's a DRF authentication class, not a Django auth backend; harmless today only because `authenticate()` silently swallows the resulting `TypeError`, but signals confusion between the two concepts.

**HIGH**

- `UsernameAuthentication` (`usernameauthentication.py`) has no lockout/throttling, combined with the project-wide absence of DRF throttling (#7 above) — an unthrottled login oracle for username enumeration.

### `scuba/libs/aws`, `scuba/libs/models/awsmodel.py`, `scuba/libs/imageuploader.py`

**CRITICAL** — the S3/image upload pipeline is broken in five independent places — see §2 finding 7 for the full breakdown.

**MEDIUM**

- Inconsistent AWS credential resolution: `S3.__init__` unconditionally requires a local named AWS CLI profile (`AWS_PROFILE`), while `S3.get_session()` correctly prefers env-var credentials first. Any code that instantiates `S3(bucket)` directly (e.g. `scuba/libs/mail.py:51`) fails with `ProfileNotFound` in any container/CI environment without a literal `~/.aws/credentials` file.

**LOW** — debug `print(bucket_name)` on every `S3(...)` instantiation (`s3.py:27`).

### `scuba/libs` — remaining utilities

**HIGH**

- WeatherAPI base URLs are plain `http://`, not `https://` (`libs/weather.py:8-9`), and every call in the file has no `timeout=` — directly exercised on every home-page load (`scuba/home/apis.py:60-63`) via a cache-set that is never read back, so caching provides no actual protection.
- `StringUtils.get_random_password_string()` (`libs/stringutils.py:56-63`) uses Python's `random` module (not cryptographically secure) for a function explicitly named for password generation.

**MEDIUM**

- Inconsistent error handling: `Weather.get_current_by_postal_code` doesn't check `res.status_code` unlike its siblings.
- `FileUtils.write_to_file` performs an unsanitized filesystem write with a caller-supplied filename — no path-traversal check (not directly attacker-reachable today).
- Numerous other outbound calls without timeouts across `fileutils.py`, `alerting.py`, and `sitesettings/models.py`'s `ChatApi`/`LogbookApi`/`SettingsApi` HTTP helpers.
- `LocationModel.get_local_objects()` (`libs/models/locationmodel.py:36-61`) filters on `current_lat`/`current_lngg`, fields that don't exist (the model defines `lat`/`lng`) — `FieldError` if ever called; currently dead/unused.

**LOW**

- `StringUtils.generate_short_id` is decorated `@staticmethod` but declared with `cls` as its first parameter — works only because callers pass the class explicitly; fragile.
- `Scuba` context processor (`context_processors/scuba.py:33`) uses `request.session.get('profile_image', user.get_profile_image())` — the default argument is evaluated eagerly on every render, defeating the intended session cache.

### `scuba/aws` — CI/CD webhooks

**CRITICAL** — unauthenticated unbounded `/tmp` writes and the chained stored-XSS — see §2 finding 3.

**MEDIUM**

- `CodePipelineState.payload` is `CharField(max_length=1024)` while `scuba/aws/apis.py:95` stores the full re-serialized SNS envelope into it — exceeds 1024 chars for realistic payloads; fails under MySQL strict mode, silently truncates/accepts under SQLite — a concrete cross-backend parity gap.
- `CodeBuildJob.BUILD_STATUS_VALUES` is a Python `set` literal used as Django `choices=` — sets are unordered, risking inconsistent choice ordering across environments/Python versions.

### `scuba/security` — bounced-email webhook

**CRITICAL** — same unauthenticated unbounded-disk-write pattern as the AWS webhooks — see §2 finding 3. The dedicated `BouncedEmail`/`InvalidEmail` models exist but are never populated by this handler — the "track bounces" feature is entirely unimplemented; the endpoint just appends raw JSON and always returns 200 regardless of payload validity.

### `scuba/sitesettings`

**CRITICAL**

- `SNSSubscriptionRequestSerializer`'s field validators are missing `@staticmethod` (see §2 finding 3) — every real AWS subscription-confirmation request 500s.
- `/api/sitesettings` (non-`/all` variant, `apis.py:36-40`) references `item.url` on `SystemApi`, a model with no `url` field — `AttributeError` on every call to this public, unauthenticated endpoint.
- `/api/endpoints` (`apis.py:14`) calls `Endpoint.get_active_endpoints()`, a method that doesn't exist anywhere in the codebase — `AttributeError` on every call to this public, unauthenticated route.

**MEDIUM**

- `BaseAPI.__init__` (`models.py:217-223`) reassigns shared class-level model metadata (`self._meta.get_field('key').choices`) on every single instantiation, including every row fetched in a queryset — wasteful and a thread-safety hazard under concurrent workers.
- `GetSystemSettingsApi`'s "all" variant (`apis.py:30-34`, `AllowAny`) exposes the entire `SystemApi` table (internal integration URLs/keys/active flags for AWS/billing/chat/logbook/alerting) to any unauthenticated caller.

**LOW**

- `SNSSubscriptionRequestAdmin.confirm_sns_request` (`admin.py:64-67`) doesn't actually confirm anything — it just `print()`s the subscribe URL. Harmless today, but if ever "completed" by fetching that attacker-supplied `subscribe_url` without validating it's a genuine `sns.*.amazonaws.com` host, it becomes SSRF.

### `scuba/content`

**HIGH**

- `content/urls_news.py:13` imports `from skm.content import views as news_views` — the `skm` package doesn't exist anywhere in this repo (a stale pre-rename import). Currently dead (not wired into `scuba/urls.py`), but breaks immediately if ever included.
- `content.Image` inherits the broken `AWSModel.delete()` (see §2 finding 7) — deleting an `Image` via Django admin is broken.

**MEDIUM**

- Upload validation (`content/forms/admin.py:20-52`) trusts client-supplied filename extension and `Content-Type` header with no magic-byte verification and no file-size limit — contradicts the project's own upload-validation rule (admin-gated today, so lower likelihood).

**LOW**

- Leftover debug `print()` in `content/views/__init__.py:77`.
- `FAQSection.save()`/`FAQEntry.save()` compute the next `position` via an unlocked `aggregate(Max(...))` with no unique constraint — a race condition under concurrent saves (admin-only, low likelihood).

### `scuba/home`

**HIGH** — see the WeatherAPI finding above; this is the concrete endpoint (`home/apis.py:60-68`) that exercises it on every request.

**MEDIUM**

- `home/forms/admin.py:15` imports `from scuba.home.models import Jumbotron` — `scuba/home/models.py` doesn't exist at all. Currently dead (no `admin.py` registers this form), but a leftover template (`templates/home/admin/change_jumbotron_form.html`) suggests a removed feature whose form was never cleaned up.

### `scuba/robots`

**MEDIUM/HIGH**

- The custom `Settings.__getattr__` proxy (`robots/settings.py:18-21`) never raises `AttributeError` for unknown names — it returns `None` instead — which means every `hasattr(settings, ...)` check in `robots/views.py` is unconditionally `True`. Concretely, `get_current_site()` always attempts a host-based `Site.objects.get(domain=...)` lookup regardless of the actual `ROBOTS_SITE_BY_REQUEST` setting, which can raise `Site.DoesNotExist` and 500 the public, frequently-crawled `/robots.txt` endpoint the moment the request's `Host` header doesn't exactly match a registered `Site` domain (very plausible behind a load balancer).

### `scuba/environ`

**LOW** — `environ/apps.py`'s `AppConfig.ready()` wires up `accounts` signal registration from an unrelated static-content app; a surprising, easy-to-miss cross-app coupling that would silently break `accounts` signals if `environ` is ever removed from `INSTALLED_APPS`.

### `scuba/system`

**MEDIUM/HIGH** — `system/urls.py` imports `scuba.system.apis`, a module that doesn't exist. Currently dormant because `scuba.system.urls` is never included in `scuba/urls.py`, but the app is still listed in `INSTALLED_APPS`. This is unmistakably an abandoned duplicate of `scuba.aws` (identical `cicd/build`/`cicd/pipeline` paths and class names; `scuba/aws/apps.py`'s `AppConfig` is even still named `SystemConfig`) — recommend deleting `scuba/system` or finishing its consolidation into `scuba.aws`.

### `scuba/cache`

No findings — placeholder `AppConfig` only, no models/views yet.

---

## 6. Follow-ups already applied during this review session

- `requirements.txt`: added `django-ses==4.7.2` (was configured as `EMAIL_BACKEND` but absent from the pinned dependency list — §5 finding 3 / original §1 "HIGH — FIXED" style note). No other code in this document has been modified; everything above reflects `main` as found.

## 7. Summary of severities

| Severity | Rough count | Highlights |
|---|---|---|
| CRITICAL | ~28 | Admin impersonation backdoor; unauthenticated+broken admin reset-password/welcome-email URLs; unauthenticated `/tmp`-writing webhooks (×3) with a chained stored XSS; S3/image upload pipeline broken in 5+ places; galleries app broken in 12+ independent ways; logbooks, diveshops, divegroups, equipment features non-functional; broken public `/api/sitesettings`, `/api/endpoints`; non-functional set-password/set-username endpoints |
| HIGH | ~25 | Unenforced password policy; disconnected IP/country signup blocking; no equipment authorization; missing timeouts across every external integration (weather, chat, logbook, settings, alerting); insecure `DEBUG`/`SECRET_KEY` defaults; weak RNG for password generation; anonymous-checkin identity leak; duplicated/drifted feed serializers; PII disclosure via `AllowAny` user-list endpoint |
| MEDIUM | ~30 | Missing DB constraints where the project's own rules call for them; dead/contradictory settings; cross-backend (SQLite/MySQL) parity gaps; thread-safety hazard in shared model metadata mutation; various dead/orphaned modules and stale imports |
| LOW | ~20 | Debug `print()`/`pprint()` left in code; typos silently disabling method overrides; duplicate fields/functions; minor race conditions |

No other fixes were applied beyond the `requirements.txt` change noted in §6 — this document is findings-only, matching the original review's scope.
