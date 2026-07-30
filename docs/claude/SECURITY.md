# ScubaMob Security and Privacy

## Secrets

The following must come from environment variables or deployment secret stores:

- Django `SECRET_KEY`
- database URL and credentials
- WeatherAPI key
- Google Maps key
- AWS access configuration
- email credentials
- JWT signing configuration when customized

Never place server secrets in JavaScript, templates, committed `.env` files, fixtures, or test output.

## Authentication

- Retain Django session authentication for the server-rendered browser UI.
- Use JWT for non-browser API clients when introduced.
- Do not remove CSRF protection from session-authenticated endpoints.
- Rate-limit authentication and invitation endpoints when infrastructure supports it.

## Authorization

Every user-owned queryset must be scoped explicitly.

Sensitive resources include:

- profiles with nonpublic fields;
- albums and media;
- dive logs;
- shared dives;
- equipment records;
- certification evidence;
- messages;
- reputation detail;
- invitations and connection requests.

Never rely only on hidden buttons in the UI. Server-side permissions are required.

## Blocking Rules

A block must prevent, at minimum:

- new connection requests;
- new follows;
- direct messages;
- album invitations;
- shared-dive invitations;
- visibility that should not cross a block boundary.

The exact treatment of already shared records must be defined and tested.

## Upload Safety

Validate:

- authenticated ownership;
- maximum size;
- allowed file types;
- generated storage names;
- image decoding where applicable;
- access-control behavior;
- derivative generation errors.

Do not trust the filename or browser-provided content type alone.

## External API Safety

- use HTTPS;
- set connection and read timeouts;
- validate response status and shape;
- do not expose raw provider errors to users;
- cache responses where reasonable;
- avoid provider calls inside model methods and serializers;
- mock provider behavior in tests.

## Reputation Integrity

- store source events;
- prevent users from reviewing themselves;
- tie reviews to verifiable interactions where practical;
- protect moderation actions with explicit permissions;
- retain audit history for verification and moderation changes;
- avoid a single opaque mutable score as the only record.

## Logging

Do not log:

- passwords;
- tokens;
- API keys;
- complete authentication headers;
- private message bodies by default;
- sensitive certification documents;
- unnecessary personal information.
