# ScubaMob Development Workflow

## Before Starting a Task

1. Read `CLAUDE.md`.
2. Read the relevant Claude project documents.
3. Inspect the current source, tests, migrations, and settings.
4. Identify the smallest set of files that must change.
5. Note database, authorization, privacy, and external-provider implications.

## Implementation Order

For a typical feature:

1. define or update domain behavior;
2. implement model changes and constraints;
3. create migrations;
4. implement services;
5. implement serializers, forms, views, or APIs;
6. add permissions;
7. update templates or frontend code;
8. add tests;
9. run validation;
10. update documentation and task tracking.

## Migration Discipline

- Run `makemigrations` for only the affected apps when necessary.
- Inspect generated migrations before accepting them.
- Do not edit applied migration history casually.
- Use explicit data migrations for transformations.
- Test both forward migration and important data-preservation behavior.
- Keep schema changes independent when that improves rollback safety.

## Git Discipline

Prefer small commits with one purpose.

Suggested commit structure:

```text
type(scope): concise summary

Why:
- reason for the change

What:
- important implementation details

Validation:
- commands actually run
```

Examples of types:

- feat
- fix
- refactor
- test
- docs
- build
- ci
- security

## Completion Report

Use this format:

```text
Summary
- ...

Files created
- ...

Files modified
- ...

Migrations
- ...

Tests
- ...

Validation
- command: result

Remaining risks
- ...
```

Only list files that were actually created or changed.
