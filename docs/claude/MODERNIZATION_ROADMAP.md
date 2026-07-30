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
