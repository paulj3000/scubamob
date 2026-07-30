# ScubaMob Claude Project Instructions

## Mission

ScubaMob is a Django-based social platform for scuba divers. It should provide a LinkedIn-style professional and social network for divers while supporting dive logs, dive planning, equipment maintenance, dive-site intelligence, dive shops, media sharing, messaging, and a trust and reputation system.

The current priority is incremental modernization of the existing application. Do not rewrite the project unless a task explicitly requires it.

## Read First

Before changing code, read these files in order:

1. `docs/claude/PROJECT_CONTEXT.md`
2. `docs/claude/ARCHITECTURE.md`
3. `docs/claude/DOMAIN_MODEL.md`
4. `docs/claude/MODERNIZATION_ROADMAP.md`
5. `docs/claude/SECURITY.md`
6. `docs/claude/TESTING.md`
7. `docs/claude/DEVELOPMENT_WORKFLOW.md`
8. `docs/claude/TASK_TRACKER.md`

Also inspect the actual repository before making assumptions. The source code is authoritative when it conflicts with documentation.

## Core Technical Direction

- Backend: Django 6 and Django REST Framework.
- Development database: SQLite is acceptable.
- Production database target: MySQL.
- Configuration: `django-environ` and environment variables.
- Browser authentication: Django session authentication remains supported.
- API authentication target: JWT.
- Testing: pytest, pytest-django, and pytest-cov.
- Media and object storage: Django storage abstraction, with S3 support where configured.
- Future frontend direction: SvelteKit, introduced incrementally rather than through a full rewrite.
- Future real-time direction: Django Channels and Redis.

## Working Rules

- Make the smallest coherent change that completes the requested task.
- Preserve existing behavior unless the task explicitly changes it.
- Never invent files, models, routes, settings, migrations, or test results.
- Inspect relevant code before proposing or implementing changes.
- Do not make broad refactors during a narrow feature task.
- Keep business logic out of serializers, views, templates, and models when a service layer is appropriate.
- Keep external API calls behind provider or service interfaces.
- Tests must never depend on live WeatherAPI, Google Maps, AWS, or other external services.
- Never commit API keys, passwords, Django secret keys, database credentials, or cloud credentials.
- Use environment variables for all secrets and deployment-specific configuration.
- Prefer Django database constraints over application-only validation for invariants.
- Use `UniqueConstraint` and `CheckConstraint` rather than deprecated patterns when modifying models.
- Add type hints to new service-layer and utility code.
- Keep migrations small, reversible where practical, and aligned with model changes.
- Do not delete historical migrations merely to make local development pass.
- Avoid em dashes in user-facing text.
- Maintain compatibility with the pinned package versions unless dependency changes are part of the task.

## Database Rules

- SQLite and MySQL behavior must both be considered.
- Do not use PostgreSQL-only features.
- Use Django `JSONField` only in ways supported by both SQLite and MySQL.
- Use timezone-aware datetimes.
- Use decimal fields for measurements that require predictable precision.
- Validate latitude and longitude and add database constraints where appropriate.
- Avoid schema changes that silently discard existing data.
- Before changing a model, inspect existing migrations, admin registration, serializers, forms, templates, tests, fixtures, and imports.

## Security and Privacy Rules

- User-owned content must have explicit ownership and authorization checks.
- Private albums and media must not be exposed by guessable URLs or broad queryset access.
- Connection, follow, block, and invitation relationships must prevent self-links and invalid duplicate relationships.
- Trust and reputation values must be auditable and derived from recorded events.
- Never calculate reputation from anonymous or untraceable input.
- Uploaded files must be validated by content type, size, and ownership.
- External URLs and API responses must be treated as untrusted input.
- Admin access must rely on Django permissions or explicit groups, not merely login status.

## Required Validation

Run the relevant subset of these commands after changes:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
pytest --cov
```

When database behavior changes, also validate migrations against the configured database. For MySQL work, state clearly whether MySQL was actually available and tested.

## Required Task Response

For every implementation task, report:

1. Summary of behavior changed.
2. Files created.
3. Files modified.
4. Migrations created or changed.
5. Tests added or updated.
6. Commands run and their actual results.
7. Remaining risks, assumptions, or follow-up work.

Never claim a command passed unless it was run successfully.

## Definition of Done

A change is complete only when:

- the requested behavior is implemented;
- authorization and privacy implications are addressed;
- model changes include valid migrations;
- external dependencies are mocked in tests;
- relevant tests pass;
- `python manage.py check` passes;
- migration drift has been checked;
- documentation is updated when architecture or behavior changes;
- the final response identifies the exact files changed.
