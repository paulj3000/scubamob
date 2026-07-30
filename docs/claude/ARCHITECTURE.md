# ScubaMob Architecture

## Current Application Shape

ScubaMob is a Django monolith. Keep the monolith while domain boundaries are clarified. Do not introduce microservices merely because a domain is complex.

Expected Django layers:

- models: persistence and small domain invariants;
- services: business operations and external provider orchestration;
- selectors: reusable read/query logic where useful;
- serializers/forms: validation and representation;
- views/viewsets: HTTP orchestration and permission enforcement;
- tasks: asynchronous work when a task queue is introduced;
- templates/static files: current server-rendered user interface;
- tests: isolated unit, integration, permission, and migration coverage.

## Recommended Domain Boundaries

- accounts and diver profiles
- social graph
- certifications and reputation
- dives and dive planning
- dive sites and conditions
- equipment and maintenance
- media and albums
- dive shops and reviews
- messaging and notifications
- marketplace
- external providers

These may initially remain Django apps inside one deployment.

## External Provider Boundary

WeatherAPI, mapping providers, AWS, and future services must be accessed through service interfaces.

Example structure:

```text
scuba/
  divesites/
    services/
      weather.py
      maps.py
    providers/
      weatherapi.py
      fake_weather.py
```

Application code should depend on the service abstraction, not directly on `requests`.

## Data Storage

- SQLite: local development and lightweight tests.
- MySQL: intended production relational database.
- S3-compatible object storage: media and attachments where configured.
- Redis: future cache and Channels backend.
- JSONField: extensible custom dive-log fields, not a replacement for core relational entities.

## Frontend Evolution

The existing Django templates should remain operational while SvelteKit is introduced feature by feature.

Preferred migration pattern:

1. stable backend APIs;
2. isolated page or component replacement;
3. shared authentication and permission behavior;
4. progressive removal of old templates only after feature parity.

## Architectural Non-Goals

- no premature microservices;
- no document database for core user, relationship, equipment, or dive entities;
- no live external HTTP calls from serializers or model methods;
- no hidden reputation formula without recorded source events;
- no frontend exposure of server-side secrets.
