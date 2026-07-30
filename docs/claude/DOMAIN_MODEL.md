# ScubaMob Target Domain Model

This file describes the intended direction. Before creating any model, inspect the current implementation and migration history.

## Accounts

### User

Authentication identity and account-level settings only.

### DiverProfile

Recommended profile concerns:

- display name
- biography
- home location
- experience level
- specialties
- visibility settings
- profile photo reference

Avoid placing unrelated equipment, social, dive-log, or reputation logic directly on the user model.

## Social Graph

### ConnectionRequest

A request from one diver to another.

Suggested states:

- pending
- accepted
- declined
- canceled

### Connection

A single mutual connection record. Avoid creating two mirrored rows unless the existing design requires a carefully managed transition.

### Follow

A directional relationship.

### Block

A directional restriction that must override follow, connection, invitation, messaging, and content visibility behavior.

## Certifications and Reputation

### DiverCertification

A certification claimed by a diver.

### CertificationVerification

Evidence and review state for a certification.

### Endorsement

A skill or specialty endorsement.

### Recommendation

A written professional recommendation.

### BuddyReview

A review tied to a real shared dive or other verifiable interaction where possible.

### ReputationEvent

An immutable or append-oriented event explaining why reputation changed.

### ReputationSnapshot

A calculated summary derived from reputation events.

## Dive Logging

### Dive

Core dive record including owner, times, site, depth, duration, notes, and visibility.

### DiveParticipant

Links users to a shared dive with invitation and participation state.

### DiveCondition

Structured water, weather, visibility, current, and environmental information.

### DiveEquipmentUsage

Records equipment used on a dive.

### DiveMedia

Links media to a dive.

### DiveComputerImport

Tracks imported source data, device metadata, parser state, and errors.

Custom logbook fields may use JSONField, but commonly queried values should use typed relational fields.

## Equipment

### EquipmentCategory

Examples: regulator, BCD, cylinder, exposure protection, computer, camera.

### EquipmentItem

An owned piece of equipment.

### EquipmentMaintenanceSchedule

Defines recurring or due-date maintenance.

### EquipmentServiceRecord

Records completed work and service-provider details.

### EquipmentAttachment

Manuals, receipts, service documents, and photos.

## Media

### MediaAsset

Owned uploaded asset with storage key, metadata, validation state, and visibility.

### Album

A user-owned collection with privacy settings.

### AlbumItem

Orders and links assets within an album.

### MediaVariant

Thumbnail or resized derivatives.

## Dive Sites

### DiveSite

Coordinates, descriptions, access information, and structured metadata.

### DiveSiteFavorite

Unique per user and dive site.

### ConditionReport

User or provider condition observations.

### MarineSighting

Species or noteworthy observation at a site.

### CachedWeather

Provider result with timestamp and expiration information.

## Dive Shops

### DiveShop
### DiveShopReview
### DiveShopTrip
### DiveShopClass
### DiveShopService
### DiveShopClaim

Reviews and claims require moderation and authorization rules.

## Messaging

### Conversation
### ConversationParticipant
### Message
### Notification

Django Channels may add real-time delivery, but persistence and authorization remain in Django models and services.

## Database Invariants

Use database constraints where practical for:

- no self-connections;
- no self-follow or self-block;
- unique active relationship pairs;
- valid latitude and longitude;
- valid rating ranges;
- end time after start time;
- nonnegative depth and duration;
- unique user favorite per dive site;
- unique participant per dive.
