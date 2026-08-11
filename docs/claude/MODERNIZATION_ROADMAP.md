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

1. [ ] Inventory current values: dump `SystemApi`, `SystemSetting`, `APIKey`, `AlertingApi`, `AWSApi`, `ChatApi`, `SettingsApi` rows from `db.sqlite3` (or the fixtures in `scuba/sitesettings/fixtures/`) so no live config value is lost. `BillingApi`, `Endpoint`, `EndpointParam` have no call sites outside `scuba/sitesettings` itself and can simply be dropped. (`LogbookApi` is already gone, see item 7.)
2. [ ] Move `FlagOption` (and update `UserFeedFlagged.flag`'s FK) into `scuba/accounts` — it is domain data (moderation flag options), not deployment config, and has a real dependent row via `UserFeedFlagged`.
3. [ ] Add matching `django-environ` settings in `scuba/settings.py` for each inventoried config value (API keys, server URLs, feature flags).
4. [ ] Replace `APIKey.get_weather_api_key()` / `get_google_maps_key()` call sites (`scuba/libs/weather.py`, `scuba/libs/external/google_address.py`) with the new settings.
5. [ ] Replace `AWSApi`/`SystemApi.get_aws_*` call sites (`SystemApi.get_aws_cloudfront_url()` in `scuba/accounts/serializers/chat.py`, `SystemApi.get_s3_delete()` in `scuba/libs/fileutils.py`) with settings-based S3/CloudFront config. (`scuba/aws/apis.py` does not call any `get_aws_*` getter — its only `sitesettings` import is the SNS serializer covered by item 10 — and `scuba/libs/context_processors/scuba.py` has no AWS calls either, see item 9.)
6. [ ] Replace `ChatApi`/`SystemApi.get_chat_server`/`SystemSetting.get_chat_server_active` call sites (`scuba/accounts/apis/chat.py`, `apis/admin_chat.py`, `serializers/chat.py`, `management/commands/loadchats.py`, `views/profiles.py`, `libs/context_processors/scuba.py`). `apis/socket.py` does not call anything chat-related — see item 9.
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
