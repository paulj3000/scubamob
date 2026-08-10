# ScubaMob Logbook Roadmap

## Purpose

This roadmap defines how the ScubaMob logbook system should be implemented inside the existing ScubaMob Django repository.

The recommended architecture is a **modular monolith**: the logbook and marketplace should live inside the ScubaMob codebase as separate Django apps with clear internal boundaries. The design should make future extraction into independent services possible without introducing microservice complexity prematurely.

---

# 1. Architectural Decision

## Decision

Implement the logbook system as part of the existing ScubaMob Django repository.

Use separate Django applications for:

- `logbooks`
- `marketplace`

Do **not** create a standalone logbook microservice during the initial implementation.

## Target Repository Structure

```text
scubamob/
├── accounts/
├── divers/
├── social/
├── divesites/
├── equipment/
├── logbooks/
├── marketplace/
├── reputation/
├── notifications/
├── api/
└── scuba/
```

## Architectural Goals

The logbook subsystem should:

- integrate cleanly with diver profiles;
- integrate with dive sites;
- integrate with equipment;
- support dive buddies and social relationships;
- support photos and other media;
- support customizable logbook templates;
- allow users to create their own logbook designs;
- allow users to acquire templates from a marketplace;
- support future paid templates;
- preserve historical template versions;
- allow future mobile/offline synchronization;
- expose a clean API;
- remain extractable into a microservice later.

---

# 2. Domain Model

The system should distinguish between a **template**, a **user-owned logbook**, and the **actual dive entries**.

```text
LogbookTemplate
        |
        | instantiate
        v
UserLogbook
        |
        | contains
        v
DiveLogEntry
```

A marketplace transaction grants a user the right to instantiate or use a template. It does not transfer another diver's dive history.

---

# 3. Core Models

## 3.1 LogbookTemplate

Represents the structure and design of a logbook.

Suggested fields:

```text
id
creator
name
slug
description
cover_image
schema
visibility
status
price
currency
version
created_at
updated_at
published_at
```

### Responsibilities

A template defines:

- available fields;
- field labels;
- field types;
- validation rules;
- required fields;
- ordering;
- sections;
- visual metadata;
- optional dive categories;
- template version.

The schema should use Django `JSONField`.

Example:

```json
{
  "sections": [
    {
      "name": "Wreck Information",
      "fields": [
        {
          "id": "wreck_name",
          "type": "text",
          "label": "Wreck Name",
          "required": true
        },
        {
          "id": "penetration_depth",
          "type": "number",
          "label": "Penetration Depth"
        }
      ]
    }
  ]
}
```

---

## 3.2 UserLogbook

Represents a logbook belonging to a particular diver.

Suggested fields:

```text
id
owner
template
template_version
title
description
visibility
settings
created_at
updated_at
```

A diver may have multiple logbooks.

Examples:

- General Dive Log
- Southern California Wreck Diving
- Underwater Photography
- Technical Diving
- Vacation Dives
- Training Dives

---

## 3.3 DiveLogEntry

Represents an actual logged dive.

Core dive information should remain relational wherever practical.

Suggested fields:

```text
id
logbook
diver
dive_site
dive_date
entry_time
max_depth
average_depth
bottom_time
water_temperature
visibility
buddy
notes
custom_data
created_at
updated_at
```

Template-specific information belongs in `custom_data`.

Example:

```json
{
  "wreck_name": "HMCS Yukon",
  "penetration_depth": 72,
  "gas_mix": "Nitrox"
}
```

Do not dynamically create database columns based on template definitions.

---

# 4. Related Models

The logbook system should eventually support the following related entities.

## DiveLogEquipment

Links equipment used during a dive.

```text
entry
equipment
configuration_notes
```

This should connect to the existing or planned equipment subsystem.

## DiveLogBuddy

Supports one or more buddies on a dive.

```text
entry
diver
name
verification_status
```

Registered ScubaMob divers should use a relationship to the diver profile.

Non-members may be stored as a display name.

## DiveLogMedia

Stores media associated with the dive.

```text
entry
media_type
file
caption
sort_order
visibility
```

Files should be stored in object storage such as Amazon S3 rather than directly in MySQL.

## DiveLogTag

Allows flexible organization.

Examples:

```text
wreck
night
deep
training
photography
shore
boat
technical
```

---

# 5. Django Application Boundary

The `logbooks` application should encapsulate logbook behavior.

Recommended structure:

```text
logbooks/
├── admin.py
├── apps.py
├── models.py
├── permissions.py
├── urls.py
├── validators.py
│
├── api/
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── services/
│   ├── logbook_service.py
│   ├── entry_service.py
│   ├── template_service.py
│   ├── statistics_service.py
│   └── import_export_service.py
│
├── selectors/
│   ├── logbook_queries.py
│   ├── entry_queries.py
│   └── template_queries.py
│
├── migrations/
└── tests/
```

## Service Layer Rule

Other applications should avoid directly creating or manipulating logbook records when business logic is involved.

Avoid:

```python
DiveLogEntry.objects.create(...)
```

from unrelated applications.

Prefer:

```python
EntryService.create_entry(...)
```

This boundary makes future extraction into a dedicated service easier.

---

# 6. Marketplace Application

Create a separate Django app:

```text
marketplace/
```

The marketplace should initially focus on **logbook templates**.

Recommended structure:

```text
marketplace/
├── models.py
├── services/
├── api/
├── permissions.py
├── migrations/
└── tests/
```

---

# 7. Marketplace Domain

## MarketplaceListing

Represents a published marketplace item.

Suggested fields:

```text
id
seller
template
title
description
price
currency
status
featured
created_at
updated_at
```

## MarketplaceAcquisition

Tracks acquisition or purchase of a template.

Suggested fields:

```text
id
buyer
listing
template
template_version
purchase_price
currency
status
acquired_at
```

Even if all templates are initially free, retain the acquisition model so paid templates can be introduced later.

---

# 8. Template Ownership and Versioning

Template versioning should be implemented early.

Once users create logbooks from a published template, changing that template should not silently alter old dive records.

Recommended model:

```text
Template v1
   |
   +-- User A logbook
   +-- User B logbook

Creator publishes Template v2

Template v2
   |
   +-- User C logbook
```

A `UserLogbook` should record which template version it originated from.

Future upgrades may allow users to voluntarily migrate to a newer template version.

---

# 9. Template Creation

## Phase 1 Template Builder

Initially support common field types:

```text
text
long_text
integer
decimal
date
time
boolean
select
multi_select
rating
```

Later phases may add:

```text
location
equipment_reference
diver_reference
photo
video
signature
calculated_field
```

Templates should support sections and field ordering.

---

# 10. Default ScubaMob Templates

Ship ScubaMob with several official templates.

Recommended initial templates:

## Standard Recreational Dive Log

Fields may include:

- dive number;
- date;
- dive site;
- max depth;
- bottom time;
- water temperature;
- visibility;
- entry type;
- exit type;
- buddy;
- equipment;
- air start;
- air end;
- notes.

## Wreck Diving Log

Additional fields:

- wreck name;
- penetration;
- penetration depth;
- line/reel used;
- current;
- gas mix;
- deco stops.

## Underwater Photography Log

Additional fields:

- camera;
- housing;
- lens;
- strobes;
- ISO;
- aperture;
- shutter speed;
- subject;
- image notes.

## Training Dive Log

Additional fields:

- certification program;
- instructor;
- skills practiced;
- skills completed;
- instructor notes.

---

# 11. Integration with Existing ScubaMob Features

The logbook should integrate with other modules without tightly coupling their internals.

## Diver Profiles

Profiles may display:

```text
total dives
recent dives
favorite dive sites
maximum logged depth
total underwater time
recent logbooks
```

Visibility rules must be respected.

## Dive Sites

A dive site page may eventually display:

```text
number of dives logged
recent public dives
average visibility
average temperature
popular months
photos
```

Only aggregate information from entries whose privacy settings allow it.

## Equipment

Logging equipment usage creates future opportunities for maintenance automation.

Example:

```text
BCD regulator used on 42 dives
Regulator has accumulated 31 underwater hours
Last service: 10 months ago
```

## Social System

Users may:

- tag registered buddies;
- share dives;
- comment on shared dives;
- verify buddy participation;
- follow public logbook activity.

## Reputation System

Verified dives and buddy confirmations may eventually contribute signals to the ScubaMob trust and reputation system.

They should not be treated as authoritative certification evidence without appropriate validation.

---

# 12. Permissions and Privacy

Privacy must be implemented as a first-class concern.

Suggested visibility levels:

```text
private
friends
connections
invited
public
```

Visibility may exist at both the `UserLogbook` and `DiveLogEntry` levels.

An entry should never become more visible than its parent logbook unless explicitly supported by the permissions model.

Media permissions should inherit from the associated entry by default.

---

# 13. API Design

Expose the feature through Django REST Framework.

Possible endpoints:

```text
GET    /api/logbooks/
POST   /api/logbooks/

GET    /api/logbooks/{id}/
PATCH  /api/logbooks/{id}/
DELETE /api/logbooks/{id}/

GET    /api/logbooks/{id}/entries/
POST   /api/logbooks/{id}/entries/

GET    /api/logbook-entries/{id}/
PATCH  /api/logbook-entries/{id}/
DELETE /api/logbook-entries/{id}/

GET    /api/logbook-templates/
POST   /api/logbook-templates/

GET    /api/logbook-templates/{id}/

GET    /api/marketplace/logbooks/
GET    /api/marketplace/logbooks/{id}/
POST   /api/marketplace/logbooks/{id}/acquire/
```

API business logic should delegate to the service layer.

---

# 14. Search and Discovery

Marketplace search should eventually support:

```text
template name
creator
category
rating
price
popularity
recently added
featured
```

Template categories may include:

```text
recreational
wreck
technical
photography
training
travel
freediving
cave
night
scientific
custom
```

---

# 15. Import and Export

Data portability should be treated as an important product requirement.

Users should eventually be able to export their dive history.

Initial formats:

```text
CSV
JSON
```

Later formats may include common dive-computer or scuba-log formats if useful.

An import layer should be designed separately from the models:

```text
logbooks/services/import_export_service.py
```

Do not make imported files directly responsible for database writes.

---

# 16. Statistics

Create a statistics service rather than embedding calculations throughout views.

Possible metrics:

```text
total dives
dives this year
total bottom time
deepest dive
average depth
most visited site
most common buddy
equipment utilization
dives by month
dives by country
dives by category
```

Recommended location:

```text
logbooks/services/statistics_service.py
```

---

# 17. Implementation Phases

## Phase 0 — Architecture and Contracts

Create the application boundaries before implementing major UI.

Tasks:

- create `logbooks` Django app;
- create `marketplace` Django app;
- document service-layer rules;
- establish model ownership boundaries;
- define privacy model;
- define initial template schema specification;
- define API naming conventions;
- add architecture tests where useful.

Deliverable:

A functioning empty subsystem integrated into the Django project.

---

## Phase 1 — Basic Personal Logbook

Implement basic logbook functionality without marketplace support.

Tasks:

- `UserLogbook`;
- `DiveLogEntry`;
- standard recreational fields;
- entry CRUD;
- logbook CRUD;
- DRF serializers;
- permissions;
- Django admin integration;
- unit tests;
- API tests.

Users should be able to:

1. create a logbook;
2. add a dive;
3. edit a dive;
4. delete a dive;
5. view their dive history.

---

## Phase 2 — ScubaMob Default Templates

Implement template-driven logbooks.

Tasks:

- `LogbookTemplate`;
- JSON schema validation;
- default templates;
- template instantiation;
- `custom_data`;
- version field;
- template preview;
- validation service.

Ship initial official templates.

Recommended:

- Recreational;
- Wreck;
- Photography;
- Training.

---

## Phase 3 — Template Builder

Allow users to create custom templates.

Tasks:

- template creation UI;
- sections;
- field builder;
- field ordering;
- required fields;
- preview;
- draft templates;
- publish workflow;
- template cloning.

Users should be able to build their own logbook without modifying database schema.

---

## Phase 4 — Marketplace MVP

Allow templates to be shared and acquired.

Tasks:

- `MarketplaceListing`;
- `MarketplaceAcquisition`;
- free template acquisition;
- template ownership;
- marketplace browsing;
- categories;
- creator profiles;
- search;
- template previews;
- acquisition history.

Initially, all templates may be free.

The domain model should still support prices.

---

## Phase 5 — Equipment Integration

Connect log entries with equipment.

Tasks:

- equipment used per dive;
- usage counters;
- underwater usage hours;
- equipment history;
- maintenance integration.

Potential dashboard signals:

```text
Regulator: 47 dives since service
BCD: 29 underwater hours
Computer battery: maintenance reminder
```

---

## Phase 6 — Social Logbooks

Integrate the logbook with ScubaMob social features.

Tasks:

- buddy tagging;
- buddy verification;
- share dive;
- privacy levels;
- invite-only entries;
- reactions;
- comments;
- activity feed integration.

---

## Phase 7 — Dive Site Intelligence

Use anonymized or appropriately shared logbook information to improve dive-site content.

Potential aggregates:

```text
visibility trends
water temperature
popular months
recent conditions
average dive duration
frequently used entry points
```

Privacy rules must be enforced before aggregation.

---

## Phase 8 — Media

Add dive media support.

Tasks:

- photos;
- video;
- captions;
- albums;
- ordering;
- S3 storage;
- thumbnails;
- access control.

Media metadata belongs in MySQL.

Media files belong in object storage.

---

## Phase 9 — Statistics and Dashboard

Create diver analytics.

Tasks:

- dive statistics;
- charts;
- personal records;
- annual summaries;
- favorite sites;
- favorite buddies;
- equipment usage;
- dashboard widgets.

---

## Phase 10 — Marketplace Commerce

Introduce paid templates only after marketplace usage is proven.

Potential capabilities:

- payment provider integration;
- seller payouts;
- refunds;
- marketplace fees;
- transaction history;
- tax handling;
- seller agreements.

Payment data should not be stored directly in ScubaMob beyond provider identifiers and appropriate transaction metadata.

---

## Phase 11 — Reviews and Marketplace Reputation

Add marketplace trust features.

Possible capabilities:

- template ratings;
- reviews;
- verified acquisition badges;
- creator ratings;
- abuse reporting;
- moderation;
- featured creators.

Integrate with ScubaMob's broader trust/reputation architecture where appropriate.

---

## Phase 12 — Import and Export

Provide data portability.

Tasks:

- CSV export;
- JSON export;
- import wizard;
- import validation;
- duplicate detection;
- migration reports.

Future work may support dive computers or external scuba logging applications.

---

## Phase 13 — Offline and Mobile Support

Design APIs for eventual mobile applications.

Possible capabilities:

- offline draft dives;
- synchronization;
- conflict resolution;
- queued photo uploads;
- mobile GPS;
- dive-site lookup.

This phase may be one of the first points where service extraction deserves serious evaluation.

---

# 18. Database Strategy

Continue using MySQL as the primary database.

Use relational fields for stable concepts:

```text
users
logbooks
entries
dive sites
equipment
buddies
media metadata
marketplace transactions
```

Use `JSONField` for customizable template structures and custom entry values.

Do not introduce MongoDB or DynamoDB solely for customizable logbook fields unless a future requirement proves that MySQL JSON support is insufficient.

---

# 19. Storage Strategy

Recommended storage:

```text
MySQL
    structured application data
    template schemas
    custom entry data
    relationships
    permissions
    marketplace records

Amazon S3
    logbook covers
    dive photos
    video
    attachments
```

---

# 20. Testing Strategy

Each phase should include tests before being considered complete.

Minimum coverage should include:

## Model tests

- ownership;
- relationships;
- cascading behavior;
- version behavior.

## Permission tests

- private logbooks;
- public logbooks;
- friends/connections;
- invited users;
- unauthorized access.

## Template tests

- valid schema;
- invalid schema;
- required fields;
- unsupported field types;
- template versioning.

## API tests

- create;
- read;
- update;
- delete;
- authorization;
- filtering.

## Marketplace tests

- acquisition;
- ownership;
- duplicate acquisition;
- unpublished template access;
- seller permissions.

---

# 21. Future Microservice Extraction Criteria

The logbook should remain part of the modular monolith unless there is a concrete reason to extract it.

Evaluate extraction when one or more of these become true:

- logbook traffic requires independent scaling;
- mobile synchronization requires dedicated infrastructure;
- logbook processing creates substantial asynchronous workloads;
- third-party applications depend heavily on the logbook API;
- the logbook becomes a standalone commercial product;
- a separate engineering team owns the subsystem;
- deployments need to occur independently;
- service-level availability requirements differ materially from ScubaMob core;
- the subsystem has clearly separable data ownership.

Do not extract it merely to adopt a microservice architecture.

---

# 22. Extraction Preparation

To make future extraction easier:

- use service-layer APIs;
- minimize cross-app direct model writes;
- use explicit identifiers;
- keep logbook business logic inside `logbooks`;
- keep marketplace business logic inside `marketplace`;
- avoid circular imports;
- centralize permission logic;
- document internal APIs;
- emit domain events for major actions when useful.

Potential future events:

```text
logbook.created
logbook.deleted
dive.created
dive.updated
dive.deleted
template.published
template.acquired
```

These do not initially require Kafka, SNS, or another external event infrastructure.

They may initially use internal Django signals or application-level event dispatching where appropriate.

---

# 23. Near-Term Repository Milestones

The recommended immediate implementation sequence is:

```text
1. Create logbooks Django app
2. Define UserLogbook
3. Define DiveLogEntry
4. Implement service layer
5. Add DRF endpoints
6. Add permissions
7. Add tests
8. Add LogbookTemplate
9. Implement JSON schema
10. Add default templates
11. Create template builder
12. Create marketplace Django app
13. Add listing/acquisition models
14. Implement free marketplace
15. Integrate equipment
16. Integrate social features
17. Add marketplace commerce later
```

---

# 24. Definition of Done for Logbook MVP

The initial ScubaMob Logbook MVP is complete when a user can:

- create a logbook;
- choose a ScubaMob default template;
- add and edit dives;
- use template-specific custom fields;
- associate a dive with a dive site;
- associate buddies;
- associate equipment;
- control logbook privacy;
- view their dive history;
- view basic statistics;
- export their data;
- acquire at least one free marketplace template.

Paid marketplace support is **not** required for the MVP.

---

# 25. Final Architectural Position

ScubaMob should remain a **modular Django monolith** during the current development stages.

The logbook is too closely related to:

- divers;
- dive sites;
- equipment;
- social relationships;
- media;
- reputation;
- dashboards;
- marketplace features;

to justify a separate network service today.

The architecture should optimize for:

```text
strong module boundaries
        +
single repository
        +
single deployment
        +
shared relational database
        +
clean service interfaces
```

If ScubaMob grows to the point where the logbook has independent scaling, ownership, deployment, or integration requirements, the module can then be extracted into a dedicated service with considerably less disruption.

