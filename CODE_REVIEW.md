# ScubaMob Code Review

Date: 2026-07-30
Scope: full application code under `scuba/` (models, views, apis, serializers, forms, admin, signals, libs), excluding `tests/`, `migrations/` (none exist for custom apps), `__pycache__`, and `node_modules`. `scuba/settings.py` and project-level config reviewed separately.

Method: manual read-through of `scuba/accounts` (the largest and most security-sensitive app) plus targeted verification of `scuba/settings.py`; two independent research passes over the remaining apps, split into a "dive domain" cluster (divesites, diveshops, equipment, logbooks, galleries, divegroups, maps, entities, search) and an "infra/platform" cluster (sitesettings, content, home, security, aws, libs, robots, environ, system, cache). Every finding below cites a file and line. A sample of the most severe cross-app claims (galleries `Album.guid`, the diveshops model stub, the `aws/apis.py` duplicated `except` block, `security/apis.py`'s unauthenticated file write) was independently re-verified by directly reading the cited code before inclusion here.

Note on migrations: this project has **no** `migrations/` directory for any custom app. Django auto-creates their tables on `migrate` ("unmigrated apps" mode). This is expected/known (see `CODE_REVIEW` companion work on `view_profile.sql`) and is not repeated as a finding per app.

---

## 1. Executive summary

The codebase is in a substantially rougher state than `python manage.py check` or the existing test suite would suggest — both pass cleanly, but neither exercises most of the code paths below. Across the ~20 Django apps reviewed:

- **Several entire features are non-functional end-to-end**, not just buggy at the edges: dive logging (`logbooks`), photo/album management (`galleries`), dive shops (`diveshops`), and dive-group management (`divegroups`) all call methods or reference model fields that do not exist, so their primary user-facing flows raise 500s or `AttributeError`/`TypeError` on first use.
- **There are unauthenticated paths to genuinely sensitive actions**: an admin-only "reset this user's password" / "resend welcome email" URL pair that isn't wrapped in Django's `admin_view()` and is therefore reachable without login (`accounts/admin.py`); an equipment-maintenance CRUD surface with no `@login_required` or ownership check at all (`equipment/views.py`); a hidden authentication backend that lets any admin log in as any other user with no audit trail (`libs/authentication/adminoverride.py`).
- **The account-creation password policy is effectively unenforced.** Django's configured `AUTH_PASSWORD_VALIDATORS` (min length 8, common-password check, etc.) are never invoked by either signup path; the custom validator that *is* used allows 4-character passwords, and the DRF `/register` API enforces no password rules whatsoever.
- **External provider calls are uniformly missing timeouts** (WeatherAPI, Google Maps, the chat/logbook/settings/alerting servers), several use plain HTTP instead of HTTPS, and several webhook-style endpoints (AWS SNS, CodeBuild, CodePipeline, bounced-email) accept and trust unauthenticated, unverified payloads, including writing them unbounded to hardcoded files under `/tmp`.
- Two of the areas explicitly called out as done in `MODERNIZATION_ROADMAP.md` Phase 0 ("stabilize tests, migrations, configuration") are true only in a narrow sense: `manage.py check` and the test suite pass, but that's because the test suite doesn't touch most of the code paths documented here.

The `view_profile.sql` correctness bugs found and fixed earlier this session (missing `GROUP BY`, wrong join key, column mismatch with the `ViewProfile` model) are **not** repeated in detail here — see the `restart` branch — but are mentioned in the `accounts` section for completeness since that area was reviewed in full.

Findings are ranked CRITICAL / HIGH / MEDIUM / LOW within each section. Given the volume, this is a curated list of what would matter to a senior engineer reviewing this as a PR, not an exhaustive style-nit dump.

---

## 2. Cross-app critical findings (read this section first)

These are the highest-impact issues found anywhere in the review, gathered in one place regardless of which app they live in.

1. **CRITICAL — Admin impersonation backdoor with no audit trail.** `scuba/libs/authentication/adminoverride.py:9-46`, wired into `AUTHENTICATION_BACKENDS` in `scuba/settings.py:120-124`. Any user who knows an admin's real email+password can log in **as any other user** by submitting that target user's email as the login `email` and `"<admin_email>%<admin_password>"` as the password. It's reachable through the standard login path (`LoginSerializer.validate` → `django.contrib.auth.authenticate()`, `scuba/accounts/serializers/account.py:96-98`, live at `POST /login` via `LoginUserApi`). The only trace left behind is `request.session['adminoverride'] = True` — no record of which admin did it, when, or to whom. This violates the project's own rule that "Admin access must rely on Django permissions or explicit groups, not merely login status" and has no moderation/audit trail as `SECURITY.md` requires.

2. **CRITICAL — Unauthenticated admin actions on arbitrary users.** `scuba/accounts/admin.py:53-61`: the custom admin URLs `.../reset-password/` and `.../emails/welcome/` are registered via `re_path` directly against `self.reset_password` / `self.send_welcome_email_to_user`, **without** wrapping them in `self.admin_site.admin_view(...)` (the standard Django pattern — Django's own docs call this out explicitly as required for custom admin views to inherit the admin's login/permission enforcement). Every other admin URL (list/add/change/delete) gets this protection automatically; these two do not. Result: anyone, unauthenticated, can `POST`/`GET` `/admin/accounts/user/<uuid>/reset-password/` to trigger a password-reset email for any user by ID, or `/admin/accounts/user/<uuid>/emails/welcome/` to force a welcome-email resend. Combined with the `AllowAny` `ValidateUserId` endpoint (`apis/settings.py:140-151`), which confirms whether a given UUID belongs to a real user, this gives an anonymous caller a full probe-and-spam path.
   - Both handlers are additionally broken even if reached correctly: `reset_password` (line 65-71) doesn't check `form.is_valid()` before calling `form.save()`; `send_welcome_email_to_user` (line 109) calls `user.send_welcome_email()` with no arguments, but the model method requires an `email_template` parameter (`models.py:477`) — so it 500s with a `TypeError` regardless of the auth gap.
   - The same missing-`admin_view()` pattern recurs independently in `scuba/divesites/admin.py:36` (`path('all', self.get_all_divesites)`), exposing every divesite via `DivesiteSerializer` with no auth.

3. **CRITICAL — Weak/unenforced password policy across every signup path.**
   - `scuba/accounts/validators/signup.py:1-13` (`validate_password`, used by `SignupForm`) allows any 4-20 character password and never calls Django's configured `AUTH_PASSWORD_VALIDATORS` (`MinimumLengthValidator`, `CommonPasswordValidator`, etc. from `settings.py:159-172`), so those validators are effectively dead configuration.
   - `scuba/accounts/serializers/account.py:9-62` (`RegisterSerializer`, live at `POST /register` via `RegisterUserApi`, `AllowAny`) applies **no password validation at all** — `password = serializers.CharField(write_only=True)` with no length/complexity constraint, `create()` just hashes whatever was submitted.
   - The `validate_password` function itself also has a latent bug: `if password and len(password) < 4 or len(password) > 20:` — operator precedence means a falsy/`None` password would call `len(None)` and raise `TypeError` rather than returning `False`. Currently masked because Django's required-field check on the model-backed `password` field runs first, but fragile.

4. **HIGH — IP/country-based signup blocking is completely disconnected, and this is independently provable.** `scuba/accounts/forms/signup.py` imports `BlockedCountry` and `InvalidIPAddress` (line 6, 8) and accepts an `ip_address` constructor argument (line 25-27), but never references either the model or the exception anywhere in `clean()` or any `clean_<field>` method — the enforcement logic was removed or never finished. This is the direct root cause of the pre-existing, currently-failing test `test_blocked_ip_address` (`scuba/accounts/tests/test_account_forms_signup.py`) observed when running the suite earlier this session: the form now falls through to a username-uniqueness error instead of the expected country-block error. Separately, even a correct implementation would need to trust `request.META.get("HTTP_X_REAL_IP")` (`views/signup.py:29`, `signals.py:39`) — a client/proxy-settable header — without any indication in this codebase that a trusted reverse proxy strips/overwrites it before requests reach Django. Worth fixing both: restore the actual block check, and confirm the IP header is set by infrastructure the app controls, not passed through from the client.

5. **HIGH — No authorization at all on equipment maintenance endpoints.** `scuba/equipment/views.py:75-108` (`practice_requirements`, `practice_require_edit`, `delete_requirement`, all live routes per `scuba/equipment/urls.py:19-28`): no `@login_required`, no ownership check against `EquipmentMaintenance.equipment.user`. Any caller, authenticated or not, can create, edit, or delete any other user's equipment-maintenance records by guessing/incrementing IDs. `scuba/equipment/views.py:12-16` and `:61-72` (`index`, `archive2`, `archive3`) similarly return `Equipment.objects.all()`/`EquipmentMaintenance.objects.all()` unscoped and unauthenticated — every user's equipment list is publicly viewable. This directly violates the project rule that "every user-owned queryset must be scoped explicitly."

6. **HIGH — Unauthenticated, unverified AWS/SNS-style webhooks that write attacker-controlled data unbounded to disk.**
   - `scuba/security/apis.py:11-30` (`BouncedEmailsAPI`, `AllowAny`): any non-subscription-confirmation POST body is appended verbatim, unbounded, to `/tmp/bounced.txt` with no size cap or error handling — a disk-exhaustion vector, and a way to inject arbitrary content into a server-side file.
   - `scuba/aws/apis.py:28-31,76-79` (`CodeBuildAPI`, `CodePipelineAPI`, both `AllowAny`): identical pattern against `/tmp/build.txt` / `/tmp/pipeline.txt`, executed unconditionally before any validation.
   - None of these three endpoints verify the AWS SNS message signature against `SigningCertURL` before trusting the payload — anyone can POST a forged "SNS" message. The one place that *should* validate related signature/replay fields, `SNSSubscriptionRequestSerializer` (`scuba/sitesettings/serializers.py:40-56`), has validator methods named to match the wrong casing (`validate_signature` vs. the declared field `Signature`) so DRF never invokes them — silently dead validation.
   - `scuba/aws/apis.py:39-64` additionally has a confirmed, verified bug independent of the auth issue: the `try` block has two identical `except KeyError:` clauses with unreachable duplicated code between them, and the one that *is* reachable returns `Response(status=status.HTTP_400_HTTP_400_BAD_REQUEST)` — an attribute that does not exist on `rest_framework.status` — so a malformed webhook payload crashes with `AttributeError` instead of cleanly returning 400.

7. **HIGH — Broken image-upload pipeline via Pillow API incompatibility.** `scuba/libs/imageuploader.py:37`: `Image.ANTIALIAS`, removed in Pillow ≥10.0, is called against the pinned `pillow==12.2.0` (`requirements.txt`). Every call to `ImageUploader.compress_upload_image` — the shared image-compression path — raises `AttributeError`. Combined with `scuba/libs/models/awsmodel.py:22-38` (`AWSModel.delete()`/`upload_file()` reference `S3` and `settings` without importing either, and call `s3.upload_from_filename(...)`, a method that doesn't exist on the actual `S3` class in `scuba/libs/aws/s3.py`), the shared image/file-upload infrastructure used by `content.Image` and the `galleries` app is broken in at least three independent ways.

8. **HIGH — Core "album" and "dive log" features are non-functional.** See the `galleries` and `logbooks` sections below for detail; summarized here because they represent two of the product's headline features (per `PROJECT_CONTEXT.md`: "publish and selectively share media," "create, import, and share dive logs") being entirely unusable as shipped, not just buggy at the margins.

---

## 3. `scuba/accounts` (reviewed directly, in full)

This is the largest app (~4,800 lines) and backs authentication, profiles, the social graph (buddies/followers/blocks), settings, and chat proxying. Beyond the cross-app critical items above (items 1, 2, 3, 4 all live here), the following were found:

**HIGH**
- `scuba/accounts/permissions.py:23`: `CanViewProfile.has_permission` — `if user.blocked.filter(buddy=obj) or obj.blocked.filter(user=obj):`. The second clause should be `obj.blocked.filter(buddy=user)` ("has the profile owner blocked *me*"); instead, filtering `obj.blocked` (already scoped to `user=obj` by the related-name manager) by `user=obj` again is a no-op filter that matches *any* block `obj` has ever made, against anyone. Net effect: a user who has blocked literally anyone becomes unviewable to *everyone*, not just the person they blocked — a fail-safe-direction bug (denies too broadly) but a real one, and it means the intended check ("did they block me specifically") never actually runs as written.
- `scuba/accounts/models.py:433` (`User.get_setting`): `return self.settings.create(setting=SETTINGS_KEYS[settings_key], value=default)` references `settings_key`, an undefined name — the parameter is `setting_key` (no "s"). Raises `NameError` every time a default setting must be created for a user who hasn't set a given preference yet.
- `scuba/accounts/models.py:386-417` (`upload_profile_image_as_string`): the `ext` used for both the S3 object key and the `Content-Type` header is extracted via `re.search("data:image/(?P<ext>.*?);base64,...")` directly from client-supplied input with **no check against `settings.IMAGE_TYPES`/`VALID_CONTENT_TYPES`** before use — violates the project's own upload-safety rule against trusting client-provided content type. Separately, the stored filename is hardcoded to end in `.png` (line 395) regardless of the actual extracted `ext`, so a JPEG/GIF upload is stored under a `.png` name.
- `scuba/accounts/apis/buddies.py:127-132` (`BuddyRequestApi(generics.RetrieveDestroyAPIView)`) defines no `queryset`/`get_queryset`, yet is live-routed at `requests/(?P<id>...)/ ` in `urls_buddies_api.py:17` — any request raises DRF's `AssertionError` for a missing queryset.
- `scuba/accounts/admin.py:92-100` (`block_user` admin action, registered and reachable in `actions`) calls `obj.block_user()` — no such method exists on `User` (only `block_buddy` does). Using this bulk action from the admin UI always raises `AttributeError`.

**MEDIUM**
- Debug artifacts left in live security-relevant paths: `serializers/account.py:111-118` (five `print()` statements logging the username and full `user` object on every username/password login attempt); `apis/settings.py:95-96` (`pprint(request.data)` on every settings POST); `serializers/chat.py:22` (`print(...)` in a serializer method called on every chat-user list request).
- `apis/settings.py`, `apis/chat.py`: multiple `requests.get`/`requests.post` calls to the internal settings/chat services with no `timeout=`, and `res.json()` called without checking `res.status_code` first, passing upstream errors straight through to the client (`apis/settings.py:90-91,100-101,131-136`; `apis/chat.py:61-64,90-102,167-168`).
- `scuba/accounts/views/signup.py:50-73` (`ValidateEmail`): `@method_decorator(csrf_exempt, name='dispatch')` on an endpoint that writes to `InvalidEmail` on every failed validation, with no rate limiting anywhere in the codebase — a plausible spam/DB-fill vector.
- `scuba/accounts/signals.py:35-48` (`post_login`): hardcodes every logged-in user's session `zipcode` to `92107` and timezone to `America/Los_Angeles` regardless of the actual user, wrapped in a `try/except UnknownTimeZoneError` that can never trigger since the timezone string is a hardcoded literal — looks like unfinished/stubbed personalization logic left in permanently. Also sits awkwardly next to `settings.py`'s `USE_TZ = False` (see §9), which makes the `timezone.activate()` call here largely inert.
- `scuba/accounts/apis/settings.py:60-72` (`SetPrimaryEmailObjectApi.put`): unreachable dead code after the `try/except` (a bare `return UserEmail.objects.filter(...)` that can never execute and wouldn't be a valid `Response` if it did).
- `scuba/accounts/serializers/buddies.py:87` (`AddBuddySerializer.validate_buddy_id`): raises `Http404` instead of `serializers.ValidationError`, inconsistent with every sibling validator in the same file; also blocks buddy requests to *any* private profile outright, which may or may not be the intended product behavior (worth confirming — it seems to work against the point of buddy requests as the mechanism for a private user to let someone in).
- `scuba/accounts/apis/chat.py:74-99`: a large commented-out alternate implementation of `post()` left inline; `apis/chat.py:56`: `params={'users': to_query + [user.id], ...}` uses the raw UUID object (dashed string form) rather than the `pk_as_str` convention used everywhere else when talking to the external chat server — a plausible ID-format mismatch on the receiving end.
- `scuba/accounts/admin.py:109-119` (`send_welcome_email_to_user`) also has the wrong-arity bug noted in §2 item 2; the sibling bulk action `send_welcome_email` (line 121-130) is defined but never added to `actions`, so it's unreachable dead code.

**LOW**
- `UserListApi` (`apis/chat.py:18-36`) is `AllowAny` and returns name/profile-image data for arbitrary user-ID lists — combined with `ValidateUserId` (also `AllowAny`), allows anonymous ID enumeration/probing, though the data returned (name, profile image) is mild.
- Duplicate `AUTH_USER_MODEL = 'accounts.User'` line in `settings.py` (lines 128 and 140) — harmless, just sloppy.

---

## 4. Dive-domain apps (divesites, diveshops, equipment, logbooks, galleries, divegroups, maps, entities, search)

*(Researched by a dedicated review pass; the most surprising claims — the galleries `Album.guid` bug and the diveshops model stub — were independently re-verified by directly reading the source.)*

### divesites
Model layer is reasonable; the API layer is badly broken, and weather integration is called directly from a serializer.

- **CRITICAL**: `scuba/divesites/apis.py:36,71` — `DivesiteListApi`/`DivesiteReviewListApi.get_queryset()` call `Divesite.get_local_divesites(...)` / `Divesite.get_local_diveshops(...)`, neither of which exists anywhere on the model. Both are public (`AllowAny`) live routes (`urls_api.py:6-9`) — the two main site-discovery endpoints 500 on every request.
- **CRITICAL**: `scuba/divesites/models.py:100-114` (`upload_banner`) is broken three independent ways: calls a nonexistent `get_active_image()`; calls `.create()` on `self.banner`, which is a string property, not a related manager; and the `hasattr(self, 'divesitebanner')` check in `get_banner()` can never be true because the actual reverse accessor is `related_name='banners'`. Reached via the `upload_banner` admin action (`admin.py:54-62`).
- **CRITICAL**: `scuba/divesites/admin.py:36` — `path('all', self.get_all_divesites)` isn't wrapped in `admin_view()` (same class of bug as `accounts/admin.py` above) — unauthenticated dump of every divesite.
- **HIGH**: `forms/admin.py:50` — `self.cleaned_data.get('is_anonyous', None)` (typo for `is_anonymous`) always evaluates falsy, so `DivesiteCheckinAdmin` always pushes check-ins to the public feed regardless of the actual anonymity flag — a real privacy regression reachable from Django admin.
- **HIGH**: `serializers.py:76-111` (`DivesiteSerializer.get_stats`) calls the live WeatherAPI directly from a serializer (once per divesite on `many=True` list responses), the underlying calls have no timeout and use plain HTTP (see `libs/weather.py` below), only `InvalidWeatherDataException` is caught (any connection error/timeout is an unhandled 500), and the method calls `.save()` as a side effect of serializing a GET request.
- **MEDIUM**: no `CheckConstraint` on `Divesite.lat`/`long` anywhere, despite this being explicitly required by `DOMAIN_MODEL.md`; `long` field is declared twice (`models.py:22-23`); `temp_c`/`visibility` are inconsistently typed `Float`/`PositiveSmallInteger` across three different models rather than `Decimal`; `DivesiteReviewSerializer.validate_rating` accepts `0`, outside the declared 1-5 `RATING_CHOICES`.
- **LOW**: `scuba/divesites/forms.py` is entirely unreachable — `forms/` (a package) shadows it, so this module can never be imported.

### diveshops
Essentially vestigial — the model is a one-field stub, and the surrounding code (confirmed) references fields/methods that only exist inside a commented-out block.

- **CRITICAL**: `scuba/diveshops/models.py:6-25` — `Diveshop` has only a `name` field; `description`, `url`, `lat`, `long`, `is_active`, and `get_local_diveshops` are all inside a docstring/comment (verified directly).
- **CRITICAL**: `scuba/diveshops/views/__init__.py:25` calls `Diveshop.get_local_diveshops(...)` (the commented-out method) — live at `@login_required` route `json/getlocaldiveshops/` — 500s for any authenticated user.
- **CRITICAL**: `scuba/diveshops/forms.py:55,29` — `class Meta: model = 'diveshops'` (a string, not a model class) — raises on import; `:25` — `kwargs.keys().count('site_id')`, and `dict_keys` has no `.count()` in Python 3. `views/shopadmin.py:2,6` import `django.core.context_processors` (removed pre-Django-2.0) and a wrong `diveshops.forms` path (missing the `scuba.` prefix) — both fail immediately if imported. Currently these two modules aren't imported at startup (the routes that would pull them in are commented out in `urls.py:20-23`), so they're latent rather than presently fatal — but 100% broken the moment anyone re-enables them, and `forms.py` can't even be imported standalone today.

### galleries
The most broken app reviewed. No privacy field on `Album` at all, and the live album/media routes reference a model field that doesn't exist.

- **CRITICAL (privacy)**: `Album` (`models.py:80-148`) has no visibility/privacy field whatsoever, despite `DOMAIN_MODEL.md` explicitly specifying "Album: a user-owned collection with privacy settings." There is no way to mark an album private anywhere in this app.
- **CRITICAL (confirmed directly)**: `Album` has no `guid` field (only the inherited UUID `id`), yet the live, routed views and API filter/reference `Album.guid` throughout: `views/__init__.py:19,31` (`get_object_or_404(Album, guid=album_id)`), `models.py:148` (`Album.to_json()`), `api.py:70,81,107`. Every album view, edit, create, and image-list request raises `FieldError`/`AttributeError`. This is effectively the entire album feature.
- **CRITICAL**: `signals.py:13-24` — the `pre_delete` receiver registered on `Media` accesses `instance.album_image.all()`, but that reverse accessor exists only on `Album` (from `AlbumImage.album`, `related_name='album_image'`) — **deleting any `Media` row raises `AttributeError` inside the signal and aborts the delete.**
- **CRITICAL**: `models.py:190-192` — `AlbumMedia.media = models.ForeignKey(Album, ...)` — a field named `media` that points to `Album` instead of `Media`; the album↔media join table cannot actually link an album to a photo. Likely a copy-paste error.
- **CRITICAL**: `models.py:53-77` (`Media.upload_new_media`) calls `Media.objects.create(filename=..., content_type=..., aws_filename=...)`, but `Media` has neither a `content_type` nor `aws_filename` field, and the call never sets `user=` even if it worked — every media upload (`MediaUploadApi`, `serializers.py:23-25,43-45`) fails, and ownership wouldn't be attached even if it didn't.
- **HIGH**: `models.py:100-140` (`add_image_thumbnail`) wraps binary bytes in `io.StringIO` instead of `io.BytesIO`, calls the removed `Image.ANTIALIAS` (same Pillow incompatibility as §2 item 7), and computes paste coordinates via float division where PIL requires integers — any one of the three would fail first.
- **HIGH (upload safety)**: no file size limit anywhere in the upload path; content type is trusted from the client with no server-side verification of actual file bytes.
- **MEDIUM**: `views/albums.py` and `api.py:62`/`views/images.py:19` use `HttpRequest.REQUEST` (removed Django 1.9) and `django.core.urlresolvers` (removed Django 2.0) — `views/albums.py` is currently unreached dead code, but `api.py`/`views/images.py` *are* live-routed and would fail on those lines alone even before the `guid` bug.

### logbooks
The entire "dive log" feature — the product's second headline feature per `PROJECT_CONTEXT.md` — doesn't work, and there is no `Dive` model at all.

- **CRITICAL**: `views/dives.py:19,25,28` — `DiveForm(us_request.POST, user_id=..., log_id=...)`, but `DiveForm` (`forms.py:21`) is a plain `forms.Form` with no `__init__` accepting those kwargs — `TypeError` on every call to the live `dives/edit/` routes.
- **CRITICAL**: `forms.py:56` (`DiveForm.save()` calls `super().save(data)`, but `forms.Form` has no `save()`); `forms.py:44` (`findlog()` references `self.collection`, an undefined MongoDB handle — leftover from an abandoned Mongo integration).
- **CRITICAL**: `models.py:25-27` (`LogbookFolder.get_logs`) references `DiveLog()`, never imported or defined anywhere; `models.py:15-17` (`Logbook.get_logs`) is a no-op `pass` stub.
- **HIGH**: `views/logs_json.py:6,11` — both `logbookfolderlogs`/`logbookfolders` are `raise NotImplementedError`, yet live-routed behind `@login_required` (`urls.py:21-22`) — always 500 for any authenticated user.

### equipment
See §2 item 5 (unauthenticated CRUD/ownership bypass) — the most severe finding in this app. Additionally: field names (`addone`/`addtwo`/`addthree`/`addfour`) suggest tutorial-scaffold code never replaced with the actual documented domain model (categories/items/maintenance schedules/service records/attachments); `forms.py:23-27` (`EquipmentForm.save`) never returns the saved instance, breaking the normal `ModelForm.save()` contract.

### divegroups
No working create/join/manage-group flow exists anywhere — the only view wired into this app (`views/__init__.py`, routed as `/groups/`) implements an unrelated "friends" feature against `accounts` models, never referencing `Group`/`GroupUser`/`GroupUserJoinRequest` at all. Separately, `models.py:17-18` (`Group.is_user_admin`) returns `True` for *any* member regardless of the `isadmin` flag — currently unused anywhere, but a real privilege-check bug if this ever gets wired up. A stray `print(user.get_account())` sits in the live `divegroups` view.

### maps, entities, search
Low-risk. `maps/models.py:30-35` (`Region.get_weather_by_lat_long`) calls the WeatherAPI provider directly from a model staticmethod — same anti-pattern flagged in `divesites`. `entities` has no bugs found (also has no admin registration for its reference-data models, a minor operational gap). `search/views.py:18,21,26` has stray debug `print()`s in a live view.

### Cross-cutting (dive-domain cluster)
- Zero uses of `CheckConstraint`/`UniqueConstraint` across all nine apps in this cluster — every uniqueness invariant relies on the deprecated `unique_together`, and no lat/long range constraints exist anywhere despite being explicitly required.
- `diveshops` and `galleries` both contain Django ≤1.8-era API usage (`django.core.urlresolvers`, `django.core.context_processors`, `HttpRequest.REQUEST`) that cannot import under the Django 6 target this project has adopted — a repo-wide sweep for these three patterns beyond this cluster is likely worthwhile.

---

## 5. Infra/platform apps (sitesettings, content, home, security, aws, libs, robots, environ, system, cache)

*(Researched by a dedicated review pass; the aws/apis.py duplicated-`except` bug and security/apis.py's unauthenticated file write were independently re-verified by directly reading the source.)*

### sitesettings
The integration/config hub (API keys, external server URLs) — in worse shape than most, with two admin/API actions calling undefined methods.

- **HIGH**: `apis.py:40` (`GetSystemSettingsApi.get`) does `{item.key: item.url for item in data}`, but `SystemApi` has no `url` field (only `key`, `value`, `is_active`) — `AttributeError` on every call to this `AllowAny` endpoint.
- **HIGH**: `apis.py:14` (`GetSystemEndpointsApi.get`) calls `Endpoint.get_active_endpoints()`, never defined anywhere — same failure mode, also unauthenticated.
- **HIGH**: `admin.py:20-23` — the "Sync system apis" admin action calls `setting.sync_settings()`, a method `SystemApi` doesn't have.
- **HIGH**: no `timeout=` on any of the `ChatApi`/`LogbookApi` HTTP client calls (`models.py:312,329,339,349,358,392,400`).
- **MEDIUM (has real downstream effect)**: `serializers.py:40-56` (`SNSSubscriptionRequestSerializer`) — `validate_signature`/`validate_message_id`/`validate_timestamp` are defined without `@staticmethod` and with snake_case names that don't match the declared camelCase field names (`Signature`, `MessageId`, `Timestamp`) — DRF only auto-invokes `validate_<exact_field_name>`, so none of these three ever run. This is the serializer used by both `security/apis.py` and `aws/apis.py`'s webhook endpoints (§2 item 6), so the missing replay/duplicate checks are not theoretical.
- **LOW**: `GetSystemEndpointsApi`/`GetSystemSettingsApi` are `AllowAny` and (when working) expose internal server URLs/endpoints to anyone; duplicate/dead config entries in `settings.py` (`'SETTINGS_SERVER'` listed twice, `SETTINGS_APIS` defined twice verbatim).

### content
- **HIGH**: `forms/admin.py` — the `ImageForm.filename` extension allowlist (`FileExtensionValidator(['jpg','png'])`) checks the *filename's* extension, but the actual stored S3 key/extension and `Content-Type` come from `guess_extension(image.content_type)` — the client-supplied multipart content type, which the validator never touches. An attacker can name a file `x.png` (passes validation) while sending an arbitrary `Content-Type`, landing it on S3/CloudFront with a mismatched extension and content type — a real content-type-spoofing / stored-content risk.
- **MEDIUM**: `urls_news.py:13` imports `from skm.content import views as news_views` — `skm` isn't this project's package (a leftover from an earlier codebase name, also visible in stale docstrings under `scuba/libs`); this module isn't included in the root URLconf, so the whole "News" feature is currently dead rather than actively broken in production, but can't be revived without fixing this import.
- **MEDIUM**: `signals.py:19-30` — `NewsArticle.url` is unconditionally recomputed from `title` on every save (unlike the sibling `Article` handler, which only sets `url` if unset) — editing a published article's title silently changes its permanent URL, with no collision handling.

### home
- **MEDIUM**: `apis.py:23,29-31` (`SearchApi.get`, `AllowAny`) doesn't validate the `q` query param before using it in an ORM `Q()` lookup — a request without `q` risks an unhandled exception.
- **LOW**: hardcoded fallback postal code `92107` used both as the default and as the weather-failure fallback (`apis.py:42,63`) — should be configurable, and matches the same hardcoded zipcode found independently in `accounts/signals.py`.

### security
- **HIGH**: `apis.py` (`BouncedEmailsAPI`) — see §2 item 6.

### aws
- **CRITICAL/HIGH**: `apis.py` (`CodeBuildAPI`, `CodePipelineAPI`) — see §2 items 6 and 6b (the duplicated `except KeyError` block with the `HTTP_400_HTTP_400_BAD_REQUEST` typo, confirmed directly).
- **MEDIUM**: `CodePipelineAPI.post` (`apis.py:87-103`) has no exception handling at all — malformed input (missing `Message`/`detail`/`resources` keys) raises unhandled `TypeError`/`KeyError`.
- **LOW**: `scuba/aws/apps.py` names its `AppConfig` class `SystemConfig`, duplicating the name of an unrelated class in `scuba/system/apps.py` — suggests the CI/CD webhook functionality moved from `scuba.system` to `scuba.aws` without cleanup (see `system` below).

### libs
- **CRITICAL**: `models/awsmodel.py:22-38` — `AWSModel.delete()`/`upload_file()` reference `S3` and `settings` without importing either, and call a nonexistent `s3.upload_from_filename(...)` — confirmed against the actual `S3` class in `libs/aws/s3.py`, which only exposes `upload_file`, `upload_data`, `upload_raw_data`, `upload_public_file`, `delete_file`, `get_object`, `rename_file`. `AWSModel` is a base class for `content.Image` — deleting a content image via admin always crashes.
- **HIGH**: `imageuploader.py:37` — see §2 item 7 (Pillow `ANTIALIAS` incompatibility).
- **HIGH**: `weather.py:8-9` — WeatherAPI is called over plain `http://`, with the API key sent as a query-string parameter over that unencrypted connection.
- **HIGH**: no `timeout=` anywhere across `weather.py` (3 calls), `alerting.py:16`, `fileutils.py:38`.
- **MEDIUM**: `weather.py`'s `get_current_by_postal_code` doesn't check `res.status_code` before `.json()`, unlike its two siblings in the same file; `alerting.py:send_buddy_request` has no error handling or return value at all — callers can't detect delivery failure; `google_address.py:get_geocode_from_postal_code` has zero timeout or error handling around the Google Maps client call.
- **LOW**: `models/locationmodel.py:59-61` filters on `current_lat`/`current_lngg` (typo), but the model's actual fields are `lat`/`lng` — dead code today (no subclasses exist yet) but broken as written; non-cryptographic `random` module used for password/temp-name generation (`stringutils.py`) where `secrets` would be appropriate; `libs/constants.py` contains an entire unrelated billing-domain constant block with a stale `skm/skmbilling/` docstring path — dead/misplaced.

### robots
- **HIGH**: `settings.py:18-21` — the custom settings-proxy's `__getattr__` returns `None` for unknown attributes instead of raising `AttributeError`, which makes every `hasattr(settings, X)` check in `views.py` unconditionally `True` for all of this app's own known setting names (`SITE_BY_REQUEST`, `USE_HOST`, etc.) — none of these feature flags can actually be turned off via env vars as designed. Concretely, `get_current_site` (`views.py:30-38`) always takes the host-header-based `Site` lookup branch regardless of the `ROBOTS_SITE_BY_REQUEST` default (`False`), which will raise `Site.DoesNotExist` for any request whose `Host` header doesn't exactly match a registered `Site` — a real availability risk for the public `robots.txt` route behind proxies/load balancers.

### environ, system, cache
- **LOW**: `environ/apps.py:8-9` duplicates a signal import that `accounts/apps.py` already performs — harmless but confusing.
- **MEDIUM (latent)**: `system/urls.py:3,7-8` imports `scuba.system.apis`, a module that doesn't exist in this app (only `admin.py`/`apps.py`/`models.py`/`urls.py` exist) — not currently wired into the root URLconf, so presently dead, but will break immediately if anyone re-enables it. Strongly suggests the CI/CD webhook functionality was migrated to `scuba.aws` (see above) without cleaning up the old module.
- `cache/` has no models, views, admin, or logic of any kind — nothing to review.

---

## 6. Project configuration (`scuba/settings.py`)

Reviewed directly.

- **HIGH**: `USE_TZ = False` (line 185) directly contradicts this project's own written rule ("Use timezone-aware datetimes") and is visibly inconsistent with code that already assumes timezone awareness (`accounts/signals.py`'s `timezone.activate()` call, which is largely inert under `USE_TZ=False`).
- **HIGH**: `EMAIL_BACKEND = 'django_ses.SESBackend'` (line 217), but `django-ses` is **not** in `requirements.txt` and is not installed in this environment (confirmed via `pip show django-ses`) — any code path that sends email (confirmation codes, password resets, welcome emails) will raise `ModuleNotFoundError` in an environment built strictly from `requirements.txt`.
- **MEDIUM**: `CORS_ORIGIN_ALLOW_ALL = True` / `CORS_ALLOW_ALL_ORIGINS = True` (lines 274-275) are set, but `django-cors-headers` isn't installed or in `INSTALLED_APPS`/`MIDDLEWARE` — currently dead/no-op settings, but a landmine: whoever eventually adds the CORS package will silently inherit "allow every origin" as the pre-configured default.
- **MEDIUM**: `REST_FRAMEWORK['PAGINATE_BY'] = 2` (line 144) is a DRF 2.x-era setting name with no effect under modern DRF (there's no `DEFAULT_PAGINATION_CLASS` configured) — every `ListAPIView` in the codebase (buddy lists, feeds, galleries, albums) returns a fully unpaginated queryset, not the "2 items per page" the config appears to intend.
- **LOW**: `openai==2.15.0` is pinned in `requirements.txt` but never imported anywhere in the codebase (confirmed via repo-wide grep) — dead dependency, unnecessary attack surface/supply-chain footprint.
- **LOW**: `IS_PRODUCTION = False` (line 279) is a hardcoded literal, not environment-driven, so it can never be `True`; only consumed by one template context processor.
- **LOW**: `AWS_PROFILE = 'default'` (line 234) is hardcoded rather than sourced from env like every other AWS setting in the same file, and is inconsistent with `S3.get_session()`'s preference for `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env vars elsewhere in `libs/aws/s3.py` — likely to fail in containerized deployments without a local named AWS CLI profile.
- **LOW**: duplicate `AUTH_USER_MODEL` assignment (lines 128, 140).

---

## 7. Cross-cutting patterns worth fixing systemically, not file-by-file

1. **No outbound HTTP timeout anywhere in the codebase.** Every `requests.get`/`requests.post` call found across `accounts`, `divesites`, `sitesettings`, and `libs` omits `timeout=`. A single shared `requests.Session` with a default timeout (or a lightweight wrapper) would close this everywhere at once instead of patching each call site individually.
2. **Provider calls embedded directly in serializers/models instead of behind a service interface**, exactly the pattern `ARCHITECTURE.md` calls out as a non-goal (weather in `divesites/serializers.py` and `maps/models.py`; chat/settings proxying directly in `accounts/apis/*.py`).
3. **Custom Django-admin URL registration bypassing `admin_view()`** appears independently in two apps (`accounts`, `divesites`) — worth a repo-wide grep for `def get_urls` in every `admin.py` to check for more instances.
4. **Leftover debug `print()`/`pprint()` statements in live request-handling code** — found in `accounts` (3 separate files), `content`, `divegroups`, `search`, and `libs/aws/s3.py`. A pre-commit lint rule (ruff already flags `print` via `T20` if enabled) would catch these going forward.
5. **Unauthenticated write access to hardcoded files under `/tmp`** as a "logging" mechanism for webhook payloads (`security`, `aws` — three separate endpoints, same pattern) — should go through the actual `LOGGING` config instead.
6. **Stale Django API usage from the pre-1.9/2.0 era** (`HttpRequest.REQUEST`, `django.core.urlresolvers`, `django.core.context_processors`) surfacing in `diveshops` and `galleries` — a repo-wide grep for these three symbols would likely turn up more, and none of them can work under the Django 6 target this project has already adopted.
7. **No `CheckConstraint`/`UniqueConstraint` usage anywhere in the reviewed apps** — every invariant (lat/long ranges, uniqueness) relies on either nothing or the deprecated `unique_together`, despite both being explicitly required by `CLAUDE.md`/`DOMAIN_MODEL.md`.

8. **Business logic concentrated in `models.py` instead of a service layer**, contrary to `ARCHITECTURE.md`'s own prescribed layering (`services/` for "business operations and external provider orchestration"; models for "persistence and small domain invariants") and `CLAUDE.md`'s instruction to keep business logic out of models when a service layer is appropriate. A per-file method count makes the concentration concrete:

   | File | Methods | Lines |
   |---|---|---|
   | `accounts/models.py` | 73 | 974 |
   | `sitesettings/models.py` | 50 | 501 |
   | `galleries/models.py` | 13 | 205 |
   | `divesites/models.py` | 16 | 241 |
   | `content/models.py` | 12 | 171 |
   | `robots/models.py` | 5 | 110 |
   | (all other apps) | ≤3 each | — |

   `accounts/models.py` is the clear outlier and the one reviewed in depth: methods like `block_buddy` (multi-step — unfriend, delete pending requests, create the block record), `send_confirmation_code_email`, and `upload_profile_image_as_string` (base64 decode, S3 upload, thumbnail swap — also the site of the upload-validation gap in §3) mix persistence with multi-step business logic and external side effects, which is exactly what makes them hard to unit-test in isolation and hard to mock provider calls out of (a recurring theme throughout this review — see items 1-2 above). `sitesettings/models.py` is similar but more extreme: nearly the entire file *is* external-provider orchestration (chat/logbook/settings HTTP clients), making it almost entirely a service-layer candidate rather than model logic.

   Not everything needs to move: thin one-line queryset wrappers (`get_all_buddies`, `get_feed`, `is_blocked`) read fine as model methods, and moving them would add indirection for no benefit. The useful test is whether a method has more than one side effect or calls something outside the DB (email, S3, HTTP) — those are the ones worth extracting into `accounts/services/` (and similarly for `sitesettings`).

---

## 8. How this squares with the modernization roadmap

`MODERNIZATION_ROADMAP.md` Phase 0 marks "stabilize tests, migrations, and configuration" as largely done, and it's true that `manage.py check`, `makemigrations --check --dry-run`, and `pytest` all currently pass. This review is the concrete evidence for why that's necessary but not sufficient: the existing test suite (32 test files, concentrated in `accounts`, `content`, `divesites`, `home`, `libs`, `security`) doesn't exercise `galleries`, `logbooks`, `diveshops`, `divegroups`, or `equipment` at all, which is exactly where the non-functional features live. Phase 2 ("Add API integration tests," "Add permission and privacy tests") is the item most directly responsible for these bugs shipping unnoticed, and would have caught nearly every CRITICAL/HIGH item in this document (a single authenticated request to each listed endpoint would have surfaced most of them).

---

## 9. Suggested priority order

Given the number of genuinely broken features, a full top-to-bottom fix pass isn't realistic in one sitting. Suggested sequencing if asked to act on this:

1. Close the two unauthenticated-access holes (accounts admin URLs, equipment endpoints) and the `AdminOverride` backdoor — these are exploitable today with no dependency on anything else being fixed first.
2. Fix or remove the three unauthenticated `/tmp`-writing webhook endpoints (`security`, `aws` ×2) — either add SNS signature verification or gate them behind a shared secret/IP allowlist until that's built.
3. Decide product intent on `galleries`/`logbooks`/`diveshops`/`divegroups`: given how little of each currently works, it may be faster to rebuild the core model+view layer against `DOMAIN_MODEL.md` than to patch the individual `AttributeError`s in place.
4. Restore the signup password policy (route both signup paths through Django's real `AUTH_PASSWORD_VALIDATORS`) and the IP/country block check.
5. Everything else in this document, roughly in the severity order given per section.
