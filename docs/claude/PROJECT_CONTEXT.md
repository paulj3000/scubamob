# ScubaMob Project Context

## Product Vision

ScubaMob is a professional and social network for scuba divers. Its core concept is similar to LinkedIn, adapted to diving.

A diver should be able to:

- create a professional diving profile;
- record certifications, experience, specialties, and interests;
- connect with other divers;
- follow divers without requiring a mutual connection;
- publish and selectively share media;
- create, import, and share dive logs;
- plan dives with other people;
- track owned equipment and maintenance;
- follow favorite dive sites and view current conditions;
- discover dive shops, trips, classes, and services;
- receive dashboard alerts and activity updates;
- build an auditable reputation based on verified activity.

## Privacy Model

Not all content is public.

The system must support:

- public profile information;
- connection-only information;
- invite-only albums;
- private dive logs;
- shared dives visible only to participants;
- blocked-user restrictions;
- explicit ownership checks for uploaded media and records.

## Current Modernization Strategy

The repository is being modernized incrementally.

The order of work is:

1. stabilize tests, migrations, and configuration;
2. isolate external APIs;
3. clean up core models;
4. implement equipment and dive logging;
5. modernize media and dive sites;
6. add networking, trust, dashboard, and messaging;
7. improve performance and introduce a modern frontend gradually.

## Product Principles

- Privacy is a feature, not an afterthought.
- Reputation must be explainable and auditable.
- Dive data should remain useful even without social features.
- External services must enhance the product without becoming hard runtime dependencies.
- Data migrations must preserve existing user content.
- The platform must remain usable on mobile devices.
