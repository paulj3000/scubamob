# ScubaMob Modernization Roadmap

## Phase 0: Repository Stability

- [x] Establish pytest, pytest-django, and pytest-cov dependencies.
- [x] Reconcile known migration drift.
- [ ] Ensure `python manage.py check` runs in CI.
- [ ] Ensure `pytest` runs in CI.
- [ ] Keep `makemigrations --check --dry-run` clean.

Exit criteria: tests pass and there is no unexplained migration drift.

## Phase 1: Configuration and Infrastructure

- [ ] Move all secrets and deployment settings to environment variables.
- [ ] Rotate exposed or legacy API credentials.
- [ ] Require HTTPS for external API calls.
- [ ] Support SQLite and configurable MySQL.
- [ ] Validate migrations on MySQL.
- [ ] Retain browser session authentication.
- [ ] Introduce JWT for API clients.
- [ ] Add Channels and Redis when real-time work begins.

### Retire `scuba.sitesettings`

`sitesettings` is a DB-backed config store (API keys, chat/logbook/alerting/AWS/billing endpoint URLs, SNS webhook state) with call sites across `accounts`, `divesites`, `logbooks`, `security`, `aws`, `libs`, and `home`. It also holds one real domain relationship, not just config: `UserFeedFlagged.flag` (`scuba/accounts/models.py:598`) is a live `ForeignKey` to `sitesettings.FlagOption`. No migrations exist for this app, or any app in the project, despite `db.sqlite3` having live tables for these models — there is no `migrate`-reversal path, so table removal is a manual step. `CODE_REVIEW.md` already flags several of its methods/endpoints as broken (broken SNS signature validation in `SNSSubscriptionRequestSerializer`, broken `LogbookApi.get_all_logbooks`, unauthenticated public `/api/sitesettings`). Replace call sites before deleting the app; do not delete first.

1. [x] Inventory current values — done 2026-08-11: `site_settings.json` (the fixture `entrypoint.sh` actually `loaddata`s) holds live `SystemApi` rows (`AWS_CLOUDFRONT_URL`, `SETTINGS_SERVER`, `BILLING_SERVER`, `ALERTING_SERVER`, `API_SERVER`, `AWS_SERVER`, `CHAT_SERVER`), one `SystemSetting` (`CHAT_SERVER_ACTIVE=0`), `AlertingApi` (`ALERTS`, `BUDDY_REQUEST`), `AWSApi` (`S3_FILE_UPLOAD`/`S3_FILE_RENAME`/`S3_GEN_POST_URL`/`S3_DELETE`/`S3_HEADERS`), `BillingApi` (`AUTHORIZE_CC`, `PROCESSORS`), `ChatApi` (`GET_ALL_USER_CHATS`), `SettingsApi` (all four), and `APIKey` (`WEATHER_API`, `GOOGLE_MAPS`). No live `SystemSetting.DEFAULT_PROFILE_IMAGE`/`DEFAULT_BANNER_IMAGE`/`ALERT_SERVER_ACTIVE` rows exist in the fixture — those getters (item 11) fall through to their code defaults today. Found a second, orphaned fixture, `scuba/sitesettings/fixtures/google_settings.json` — a single `APIKey` row with a *different* Google Maps key, never referenced by `entrypoint.sh` or any management command (confirmed via grep); dead data, not a second live source of truth. `BillingApi`, `Endpoint`, `EndpointParam` confirmed to have no call sites outside `scuba/sitesettings` itself and can simply be dropped. (`LogbookApi` is already gone, see item 7.)
2. [x] Move `FlagOption` (and update `UserFeedFlagged.flag`'s FK) into `scuba/accounts` — done 2026-08-11. Both `sitesettings` and `accounts` have zero migrations, so this was a pure code move (model class + admin registration relocated, `db_table = 'flag_option'` kept identical) — no migration, no data movement, verified via `makemigrations --check --dry-run` staying clean.
3. [ ] Add matching `django-environ` settings in `scuba/settings.py` for each inventoried config value (API keys, server URLs, feature flags). Partially done 2026-08-11: added `WEATHER_API_KEY` and wired up the existing-but-previously-unused `GOOGLE_API_KEY` (see item 4) — both env vars follow the project's existing `env.Env(...)` default-value pattern in `scuba/settings.py`. The remaining server-URL/feature-flag settings (AWS, chat, alerting, settings-server, billing) are intentionally deferred to land alongside their own call-site replacement in items 5-11, rather than adding settings with no consumer yet.
4. [x] Replace `APIKey.get_weather_api_key()` / `get_google_maps_key()` call sites (`scuba/libs/weather.py`, `scuba/libs/external/google_address.py`) with the new settings — done 2026-08-11. `Weather.get_api_key()` now returns `settings.WEATHER_API_KEY` directly; `GoogleAddress.get_geocode_from_postal_code()` now passes `settings.GOOGLE_API_KEY` to the `googlemaps.Client`. Surfaced and fixed a blocking pre-existing gap while adding the first-ever test for `google_address.py`: the `googlemaps` package was imported by that module but never pinned in `requirements.txt` (previously flagged as known debt, 2026-08-06 entry) — not installed in the dev venv, so the new test failed at collection, aborting the whole `pytest` run. Added `googlemaps==4.10.0` to `requirements.txt` and installed it, since the missing pin was now actively blocking, not just theoretical debt. `APIKey`'s two rows (`WEATHER_API`, `GOOGLE_MAPS`) and its fixtures are left in place for now — the model itself is dropped with the rest of the app in items 14-15, not here.
5. [x] Replace `AWSApi`/`SystemApi.get_aws_*` call sites — done 2026-08-11. **`scuba/accounts/serializers/chat.py`**: `UserListSerializer.get_profile_image()`'s `SystemApi.get_aws_cloudfront_url()` replaced with the existing `settings.AWS_CLOUDFRONT` env var — scoped via `AskUserQuestion` (consolidate onto the setting already used by `galleries`/`divesites`/`content` for image URLs from the same `AWS_S3_BUCKET`, over adding a second dedicated CloudFront setting mirroring the DB value). **`scuba/libs/fileutils.py`**: `FileUtils.delete_file_from_s3()` called `SystemApi.get_s3_delete()` — a method that doesn't exist on `SystemApi` at all (`get_s3_delete` is actually defined on the sibling `AWSApi` class), so this was already raising `AttributeError` before this fix, and had **zero call sites anywhere** in the codebase (confirmed via grep) — a broken, unreachable proxy to an external `AWS_SERVER` HTTP endpoint that (like the already-removed `LogbookApi`) was likely never actually running. Rewrote it to call the project's existing, tested, direct-boto3 `S3.delete_file()` (`scuba/libs/aws/s3.py`, already used by the upload pipeline fixed in §2.7) instead of porting the broken proxy pattern forward — no new setting needed, since `S3.delete_file()` already relies on the established `AWS_S3_BUCKET` setting. (`scuba/aws/apis.py` does not call any `get_aws_*` getter — its only `sitesettings` import is the SNS serializer covered by item 10 — and `scuba/libs/context_processors/scuba.py` has no AWS calls either, see item 9.) `AWSApi` and `SystemApi.get_aws_cloudfront_url()`/`get_aws_url_by_key()` in `scuba/sitesettings/models.py` are now fully orphaned (zero call sites) but deliberately left in place — dropped with the rest of the app in items 14-15, matching the precedent set by item 4's `APIKey`.
6. [x] Replace `ChatApi`/`SystemApi.get_chat_server`/`SystemSetting.get_chat_server_active` call sites — done 2026-08-11, scoped via `AskUserQuestion`. Added `settings.CHAT_SERVER`/`CHAT_SERVER_ACTIVE`. Found the same "phantom microservice" pattern as `LogbookApi` (item 7): 4 of `ChatApi`'s 5 endpoint keys (`CHAT_LOOKUP`, `CREATE_CHAT`, `GET_ALL_CHAT_MESSAGES`, `ADMIN_GET_ALL_CHATS`) had no fixture row anywhere, so calling those methods always raised `ChatApi.DoesNotExist` before any HTTP request — only `GET_ALL_USER_CHATS` (`/api/chats/user/all`) was ever actually configured. User chose to drop the four broken methods and their call sites entirely rather than invent endpoint paths that were never real, matching item 7's precedent. **Dropped**: `scuba/accounts/apis/admin_chat.py` and its `urls_admin_chats_api.py` (whole module was just the broken `admin_get_all_chats` call, mounted at `/admin/api/chats/all`; route removed from `scuba/urls.py`); `GetChatMessagesApi` (`apis/chat.py`, mounted at `/api/chats/messages` — its `.get()` called the broken `get_all_chat_messages`, and its `.post()` was independently broken too, referencing `self.serializer_class` when the class attribute was actually named `serializer`); `scuba/accounts/management/commands/loadchats.py` entirely — its whole `handle()` depends on `chat_lookup`/`create_chat` succeeding to get a `chat_id` before it can do anything else, so once those are gone the command can never do anything meaningful (confirmed via grep it had zero other references). Removed the four broken classmethods from `sitesettings.ChatApi`, keeping `get_all_user_chats` (still correct, just now orphaned — left in place per item 4/5 precedent, dropped with the rest of the app in items 14-15). **Replaced (working call sites)**: `ChatWUserApi.get()`/`GetChatsApi.get()` (`apis/chat.py`) and `ChatSerializer.save()` (`serializers/chat.py`) now use `settings.CHAT_SERVER` directly instead of `SystemApi.get_chat_server()` — these already hardcoded their own relative paths, so no endpoint-path invention needed. `GetAllChatsApi.get()` (`apis/chat.py`) now builds its request inline (`f"{CHAT_SERVER}/api/chats/user/all"`) instead of going through `ChatApi.get_all_user_chats()` — as a side effect this actually fixes a latent bug: the old code wrapped `ConnectionError`/`JSONDecodeError` as `ChatServerDownException`, which the caller's `except requests.exceptions.ConnectionError` never actually caught, so a down chat server produced an unhandled 500 instead of the intended `{'error': 'cannot reach chat server'}` response; inlining the request means the real `ConnectionError` is now caught directly. `views/profiles.py`'s `ProfileView` and `libs/context_processors/scuba.py`'s `Scuba()` context processor both now read `settings.CHAT_SERVER_ACTIVE` instead of `SystemSetting.get_chat_server_active()`. Updated `test_outbound_request_timeouts.py` to patch the imported `CHAT_SERVER` name instead of the removed `SystemApi.get_chat_server`, and added `test_get_all_chats_api_has_a_timeout` covering the newly-inlined `/api/chats/all` route (previously only unit-tested via the model classmethod directly, never through the live route). `apis/socket.py` does not call anything chat-related — see item 9.
7. [x] Replace `LogbookApi`/`SystemApi.get_logbook_server` call sites — done: intentionally dropped rather than ported. `LogbookApi` (and its `LOGBOOK_APIS`/`LOGBOOK_SERVER` choices and `LogbookServerDownException`) is deleted from `scuba/sitesettings`; the broken `/api/logbooks/` proxy (`scuba/logbooks/apis/logbook.py`, `urls_logbooks_api.py`) is deleted along with its `scuba/urls.py` route. `LogbookFolder.get_logs()` (`scuba/logbooks/models.py`) no longer calls a phantom `DiveLog()` Mongo client. The real local `logbooks` app (`Logbook`/`LogbookFolder`/`LogbookTag` models, still unmigrated) is left in place as the foundation for `docs/logbook.md`'s Phase 1 — that phase (real `UserLogbook`/`DiveLogEntry`, service layer, DRF endpoints, tests) is separate, not-yet-scheduled work.
8. [ ] Replace `SettingsApi`/`SystemApi.get_settings_server` call sites (`scuba/accounts/apis/settings.py`).
9. [ ] Replace `AlertingApi`/`SystemApi.get_alerting_*` call sites — `scuba/libs/alerting.py` (`get_alerting_buddy_request`), `scuba/accounts/apis/socket.py` (`get_alerting_url`, `get_socket_server_settings`), and `scuba/libs/context_processors/scuba.py` (`SystemSetting.get_alert_server_active`, which sits alongside that file's chat-active flag from item 6). Note `AlertingApi` the model class itself has zero call sites anywhere (confirmed via grep) — `SystemApi`/`SystemSetting` hold the real getters — so `AlertingApi` just gets dropped per item 1, nothing to "replace" for the class itself.
10. [ ] Decide the fate of `SNSSubscriptionRequest`/webhook handling in `scuba/security/apis.py` and `scuba/aws/apis.py` — already flagged as unauthenticated/broken in `CODE_REVIEW.md`; fix or remove rather than porting as-is. If kept, move the model itself out of `sitesettings` (it is webhook state, not config).
11. [ ] Replace `SystemSetting.get_default_profile_image()` (`scuba/accounts/models.py`, two call sites) / `get_default_banner_image()` (`scuba/divesites/models.py`) call sites with settings-based defaults. (`scuba/accounts/views/profiles.py` imports `SystemSetting` but only for `get_chat_server_active`, covered by item 6 — it has no default-image call.)
12. [ ] Update every test that references `sitesettings` fixtures/models directly — `test_api_alerts.py`, `test_api_user_accounts.py`, `test_api_user_divesite_favorite.py`, `test_divesite_methods.py`, `test_api_user_divesites.py`, `test_api_search.py`, plus `test_outbound_request_timeouts.py`, `test_api_home.py`, `test_weather.py` (`scuba/libs/tests/`), `test_api_user_list.py`, `test_context_processor_scuba.py` (`scuba/libs/tests/`) — to use the new settings-based mocks. (`scuba/sitesettings/tests/test_apis.py` is deleted along with the app in item 14, not updated.)
13. [ ] Remove `'scuba.sitesettings'` from `INSTALLED_APPS` in `scuba/settings.py`.
14. [ ] Delete `scuba/sitesettings/` (models, admin, apis, serializers, exceptions, fixtures, templates) once nothing imports it.
15. [ ] Drop the now-orphaned tables (`system_api`, `endpoint`, `endpoint_param`, `system_setting`, `alerting_api`, `aws_api`, `billing_api`, `chat_api`, `settings_api`, `api_key`, `flag_option` if not moved, `sns_subscription_requests` if not moved) via manual SQL or the project's first real migration baseline — not a normal `migrate` reversal. (`logbook_api` never had a live table — no migrations exist for this app and `db.sqlite3` never had that table — so there is nothing to drop for it.)
16. [ ] Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`, and `pytest` to confirm nothing still imports `scuba.sitesettings`.

Exit criteria: `grep -rn "sitesettings" scuba/` returns nothing, all tests pass, and no live config value or the `FlagOption`/`SNSSubscriptionRequest` data was lost.

## Phase 2: Testing and External Services

- [ ] Mock WeatherAPI in all tests.
- [ ] Remove network calls from serializers.
- [ ] Add provider interfaces for weather and maps.
- [ ] Add API integration tests.
- [ ] Add permission and privacy tests.
- [ ] Increase meaningful model and service coverage.

## Phase 3: Core Model Cleanup

- [ ] Separate DiverProfile from account identity.
- [ ] remove duplicate or placeholder user fields.
- [ ] replace fake date defaults with nullable fields.
- [ ] replace mirrored buddy records with a clear relationship model.
- [ ] add connection requests, follows, and blocks.
- [ ] replace `unique_together` when touched.
- [ ] add relationship, rating, coordinate, and date constraints.

## Phase 4: Equipment

- [ ] implement normalized equipment categories and items.
- [ ] implement maintenance schedules.
- [ ] implement service records and attachments.
- [ ] add upcoming and overdue maintenance dashboard data.

## Phase 5: Dive Logging

- [ ] implement dives, participants, conditions, equipment use, media, and imports.
- [ ] support shared dives and invitations.
- [ ] support GPS and custom fields.
- [ ] preserve private and participant-only visibility.

## Phase 6: Media

- [ ] implement media assets, albums, album items, and variants.
- [ ] move upload processing to services.
- [ ] validate uploads.
- [ ] add asynchronous thumbnail generation.
- [ ] normalize UUID and foreign-key behavior.
- [ ] support invite-only albums.

## Phase 7: Dive Sites

- [ ] normalize latitude and longitude naming.
- [ ] add coordinate constraints.
- [ ] fix banner and favorite relationships.
- [ ] cache weather.
- [ ] add condition reports, marine sightings, and trending sites.

## Phase 8: Dive Shops

- [ ] implement shops, reviews, trips, classes, services, and claims.
- [ ] add moderation and ownership rules.

## Phase 9: Networking

- [ ] implement LinkedIn-style connections.
- [ ] implement followers.
- [ ] implement privacy controls.
- [ ] implement shared-dive invitations.
- [ ] enforce block behavior consistently.

## Phase 10: Trust and Reputation

- [ ] implement certifications and verification.
- [ ] implement endorsements and recommendations.
- [ ] implement buddy reviews.
- [ ] implement reputation events and snapshots.
- [ ] make every reputation change explainable.

## Phase 11: Dashboard

- [ ] friend and followed-diver activity.
- [ ] favorite dive-site conditions.
- [ ] equipment reminders.
- [ ] upcoming dives.
- [ ] notifications.
- [ ] reputation summary.

## Phase 12: Messaging

- [ ] direct messaging.
- [ ] group chat.
- [ ] dive-planning conversations.
- [ ] Channels-based delivery.
- [ ] persisted notification and read states.

## Phase 13: Marketplace

- [ ] customizable logbook templates.
- [ ] digital products.
- [ ] ratings.
- [ ] purchases and entitlements.

## Phase 14: Performance

- [ ] add measured indexes.
- [ ] optimize feed and dashboard queries.
- [ ] cache dashboards, site conditions, and weather.
- [ ] move long-running work to asynchronous jobs.

## Phase 15: Code Quality and Frontend

- [ ] introduce consistent service layers.
- [ ] remove inappropriate business logic from models.
- [ ] standardize timestamps and naming.
- [ ] add type hints.
- [ ] introduce Ruff and Black.
- [ ] begin incremental SvelteKit migration after APIs stabilize.

## Final Success Criteria

- all tests pass;
- no migration drift;
- SQLite development remains usable;
- MySQL is supported and validated;
- API authentication uses JWT where appropriate;
- browser sessions remain supported;
- external calls are mocked in tests;
- domain models match product requirements;
- privacy and authorization are tested;
- the application is ready for incremental SvelteKit adoption.
