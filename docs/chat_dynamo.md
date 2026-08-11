# ScubaMob Chat / Messaging Roadmap

## 1. Executive Architecture Decision

ScubaMob chat will be implemented as a **first-class domain module inside the existing ScubaMob modular monolith**.

The chat application itself will **not initially be deployed as a standalone microservice**.

However, chat persistence will be intentionally separated from the rest of the platform:

- **Relational database** for conversation metadata, participants, permissions, and user-facing state.
- **Amazon DynamoDB** for chat messages and high-volume message-related data.
- **Redis** for ephemeral real-time state such as typing indicators, presence, and WebSocket channel coordination.
- **Object storage / S3** for large message attachments where appropriate.

This provides data isolation and independent message scaling without prematurely introducing the operational complexity of a fully separate microservice.

---

# 2. Target Architecture

```text
                         ScubaMob
                    Django Modular Monolith
                              |
       +----------------------+----------------------+
       |                      |                      |
       v                      v                      v
 Relational DB             DynamoDB                Redis
       |                      |                      |
 Users                    Messages              Presence
 Profiles                 Reactions             Typing
 Dives                    Message events        WebSocket groups
 Logbooks                 Edit history          Ephemeral state
 Marketplace
 Conversations
 Participants
 Read state
 Permissions
       |
       +----------------------+
                              |
                              v
                            S3
                              |
                       File attachments
                       Images / documents
```

The core rule is:

> The rest of ScubaMob must interact with chat through the chat service layer, never directly through DynamoDB or chat persistence models.

---

# 3. Why This Architecture

Chat traffic has very different characteristics from the rest of ScubaMob.

Most ScubaMob data is relational:

- users
- profiles
- dive sites
- dive plans
- dive logs
- equipment
- marketplace data
- shops
- social relationships

Chat messages are different:

- append-heavy
- potentially very high volume
- usually retrieved by conversation
- usually sorted chronologically
- frequently paginated
- rarely require joins
- can grow much faster than core application data

DynamoDB fits those message access patterns well.

At the same time, conversation membership and permissions remain highly relational and should stay in the main ScubaMob database.

---

# 4. Architectural Principles

## 4.1 Modular Monolith First

Keep chat in the ScubaMob repository.

```text
scubamob/
├── accounts/
├── profiles/
├── social/
├── dives/
├── logbooks/
├── marketplace/
├── equipment/
├── chat/
└── ...
```

Do not introduce a separate chat deployment initially.

## 4.2 Chat Owns Its Persistence

Other modules must not know how chat data is stored.

They should call:

```python
chat.services.send_message(...)
chat.services.create_conversation(...)
chat.services.get_messages(...)
chat.services.share_dive(...)
```

They must not directly call DynamoDB.

## 4.3 Repository Abstraction

Persistence should be hidden behind repositories.

```text
chat/
├── admin.py
├── apps.py
├── consumers.py
├── models.py
├── permissions.py
├── routing.py
├── serializers.py
├── services.py
├── signals.py
├── tasks.py
├── urls.py
├── views.py
├── repositories/
│   ├── __init__.py
│   ├── conversation_repository.py
│   ├── participant_repository.py
│   ├── message_repository.py
│   ├── reaction_repository.py
│   └── attachment_repository.py
├── infrastructure/
│   ├── dynamodb.py
│   ├── redis.py
│   └── storage.py
└── tests/
```

This boundary allows DynamoDB to later be replaced or moved behind a service API without changing the rest of ScubaMob.

---

# 5. Data Ownership

## Relational Database

Keep the following in the main ScubaMob relational database:

```text
Conversation
ConversationParticipant
ConversationSettings
ConversationInvitation
ConversationRole
User blocking relationships
Notification preferences
Conversation archive/mute state
Read state / last-read pointer
```

The relational database is authoritative for:

```text
Who belongs to a conversation?
Who can send messages?
Who owns/administers the conversation?
Who muted or archived it?
Can these two users communicate?
```

## DynamoDB

DynamoDB owns message-oriented data:

```text
Message
MessageReaction
MessageEditHistory
MessageDeliveryEvent
Message metadata
System messages
Rich-message payload references
```

Potential later additions:

```text
Message mention indexes
Conversation message counters
Message retention metadata
Moderation state
```

## Redis

Redis owns ephemeral state:

```text
Typing indicators
Online presence
WebSocket channel groups
Short-lived delivery state
Rate-limit counters
Temporary message deduplication keys
```

Do not use the relational database for rapidly changing presence or typing state.

## Object Storage

Use S3 or the existing ScubaMob object-storage system for:

```text
Photos
Videos
Documents
Dive-plan exports
Logbook attachments
Marketplace images
Other large binary objects
```

DynamoDB should contain only attachment metadata and object references.

---

# 6. DynamoDB Message Design

## Primary Access Pattern

The most important query is:

```text
Give me messages from conversation X,
ordered chronologically,
with pagination.
```

Recommended initial key structure:

```text
PK = CONVERSATION#<conversation_id>
SK = MESSAGE#<timestamp>#<message_id>
```

Example:

```text
PK: CONVERSATION#9f83...
SK: MESSAGE#2026-08-11T14:31:12.182Z#2e18...
```

This allows DynamoDB Query operations to efficiently retrieve messages from a conversation.

---

# 7. Example Message Item

```json
{
  "PK": "CONVERSATION#12345",
  "SK": "MESSAGE#2026-08-11T14:31:12.182Z#abc123",
  "message_id": "abc123",
  "conversation_id": "12345",
  "sender_id": "42",
  "message_type": "TEXT",
  "body": "Want to dive Catalina Saturday?",
  "created_at": "2026-08-11T14:31:12.182Z",
  "edited_at": null,
  "deleted_at": null
}
```

Use application-generated unique IDs rather than relying entirely on timestamps for uniqueness.

---

# 8. DynamoDB Index Strategy

Do not create indexes simply because they might someday be useful.

Indexes should correspond to concrete access patterns.

Possible future index:

```text
GSI1PK = USER#<sender_id>
GSI1SK = <created_at>
```

This may support moderation or administrative queries such as:

```text
Messages sent by user X
```

Do not use GSIs for arbitrary relational-style querying.

---

# 9. Message Ordering

Use a combination of:

```text
timestamp
+
unique message ID
```

for the sort key.

Do not assume two messages cannot be generated in the same millisecond.

The system should preserve deterministic ordering when timestamps collide.

---

# 10. Message Pagination

Messages should always be paginated.

Use DynamoDB's native cursor mechanism.

API example:

```text
GET /api/chat/conversations/{id}/messages/?limit=50
```

Response:

```json
{
  "results": [],
  "next_cursor": "..."
}
```

Avoid traditional SQL-style offset pagination for DynamoDB messages.

---

# 11. Phase 0 — Chat Domain Foundation

## Goal

Create the domain boundaries before implementing UI features.

Tasks:

- Create `chat` Django application.
- Create repository interfaces.
- Create service layer.
- Define relational vs DynamoDB ownership.
- Define message IDs.
- Define conversation IDs.
- Define message event schema.
- Define error handling.
- Define idempotency strategy.
- Add environment configuration.
- Add DynamoDB local/test strategy.

Recommended configuration:

```text
CHAT_DYNAMODB_TABLE
CHAT_DYNAMODB_REGION
CHAT_REDIS_URL
CHAT_ATTACHMENT_BUCKET
```

Do not scatter table names throughout the code.

---

# 12. Phase 1 — Relational Conversation Models

Create the relational conversation model.

## Conversation

Suggested fields:

```text
id
conversation_type
title
created_by
created_at
updated_at
last_message_at
last_message_id
```

Conversation types:

```text
DIRECT
GROUP
DIVE
TRIP
SHOP
MARKETPLACE
SYSTEM
```

Some types may be introduced later, but reserve the design for them now.

---

# 13. ConversationParticipant

Suggested fields:

```text
id
conversation
user
role
joined_at
left_at
last_read_message_id
last_read_at
muted
archived
notifications_enabled
```

Roles:

```text
MEMBER
ADMIN
OWNER
```

This table controls membership and authorization.

---

# 14. Direct Conversation Uniqueness

Do not allow duplicate direct conversations between two users.

The application should provide:

```python
get_or_create_direct_conversation(user_a, user_b)
```

Repeated requests between the same pair should return the same active direct conversation.

---

# 15. Phase 2 — DynamoDB Message Repository

Implement the message repository independently from HTTP endpoints.

Recommended interface:

```python
class MessageRepository:
    def create_message(...)
    def get_message(...)
    def list_messages(...)
    def update_message(...)
    def soft_delete_message(...)
```

The repository should contain all DynamoDB-specific implementation details.

The rest of the chat application should operate on domain objects or DTOs.

---

# 16. Phase 3 — Chat Service Layer

Implement business logic inside `chat.services`.

Examples:

```python
create_conversation()
create_direct_conversation()
send_message()
edit_message()
delete_message()
mark_conversation_read()
add_participant()
remove_participant()
leave_conversation()
archive_conversation()
mute_conversation()
```

`send_message()` should perform:

```text
1. Validate user authentication.
2. Validate conversation membership.
3. Validate block/safety rules.
4. Validate payload.
5. Create message ID.
6. Persist message to DynamoDB.
7. Update conversation metadata.
8. Publish real-time event.
9. Schedule notifications.
10. Return normalized message object.
```

---

# 17. Distributed Write Handling

The architecture now contains two databases.

For example:

```text
DynamoDB
    message written

SQL
    conversation.last_message_at updated
```

These operations cannot be assumed to be one atomic database transaction.

Design for this deliberately.

Use:

```text
Idempotent operations
Retry-safe message IDs
Background reconciliation
Eventually consistent conversation metadata
```

Do not attempt to simulate a global distributed SQL transaction.

The message itself should be authoritative.

If `last_message_at` temporarily fails to update, it can be repaired.

---

# 18. Idempotency

Every message send operation should have an idempotency mechanism.

Example:

```text
client_message_id
```

The browser can generate a UUID before sending.

A retry should not create a duplicate message.

This becomes especially important with:

```text
mobile networks
WebSockets
HTTP retries
background resend
connection interruption
```

---

# 19. Phase 4 — REST Messaging API

Implement REST before relying on WebSockets.

Suggested endpoints:

```text
GET    /api/chat/conversations/
POST   /api/chat/conversations/

GET    /api/chat/conversations/{id}/
PATCH  /api/chat/conversations/{id}/

GET    /api/chat/conversations/{id}/messages/
POST   /api/chat/conversations/{id}/messages/

POST   /api/chat/conversations/{id}/read/
POST   /api/chat/conversations/{id}/mute/
POST   /api/chat/conversations/{id}/archive/

POST   /api/chat/direct/{user_id}/
```

The REST API should work even if the WebSocket infrastructure is unavailable.

---

# 20. Phase 5 — LinkedIn-Style Desktop UI

Implement a persistent floating messaging interface.

```text
┌────────────────────────────────────────────────────┐
│ ScubaMob                                            │
│                                                    │
│                         ┌────────────────────────┐ │
│                         │ Messaging              │ │
│                         ├────────────────────────┤ │
│                         │ Search conversations   │ │
│                         ├────────────────────────┤ │
│                         │ Chris Kelly        2   │ │
│                         │ Dive Buddies           │ │
│                         │ Catalina Trip          │ │
│                         └────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

Selecting a conversation opens a chat panel without requiring navigation away from the current page.

---

# 21. UI State

The messaging UI should support:

```text
collapsed
conversation list
active conversation
multiple open conversations later
unread badges
minimized conversations
```

Initial implementation can support one open active conversation.

Avoid cloning every LinkedIn behavior in version 1.

---

# 22. Phase 6 — Real-Time Messaging

Add:

```text
Django Channels
Redis
WebSockets
```

Suggested route:

```text
/ws/chat/
```

A single authenticated WebSocket per client is preferable to opening one WebSocket for every conversation.

Events can identify the conversation:

```json
{
  "event": "message.created",
  "conversation_id": "12345",
  "message": {}
}
```

---

# 23. WebSocket Events

Initial event types:

```text
message.created
message.updated
message.deleted
conversation.updated
typing.started
typing.stopped
message.read
participant.joined
participant.left
```

Future events:

```text
reaction.added
reaction.removed
presence.changed
```

---

# 24. WebSockets Are Not Storage

WebSockets exist to deliver events.

They are not the message database.

Correct flow:

```text
User sends message
      |
      v
Chat service
      |
      v
DynamoDB
      |
      v
WebSocket event
      |
      v
Recipients
```

Persist first, broadcast second.

---

# 25. Phase 7 — Unread Messages

Use participant state from the relational database.

Recommended:

```text
last_read_message_id
last_read_at
```

Expose:

```text
GET /api/chat/unread-count/
```

Show unread totals in the navigation bar or messaging launcher.

---

# 26. Unread Count Strategy

Do not query every DynamoDB message every time an unread badge is rendered.

Options include:

```text
conversation unread counters
last-read pointers
cached unread totals
background updates
```

Start simple.

Optimize only when usage demonstrates the need.

---

# 27. Phase 8 — Typing Indicators

Typing state belongs in Redis.

Example events:

```text
typing.started
typing.stopped
```

Keys should automatically expire.

Example concept:

```text
chat:typing:<conversation_id>:<user_id>
```

Never permanently store typing indicators.

---

# 28. Phase 9 — Presence

Presence should also be ephemeral.

Possible states:

```text
ONLINE
RECENTLY_ACTIVE
OFFLINE
```

Avoid exposing exact last-seen timestamps unless ScubaMob explicitly decides to make that part of the product.

---

# 29. Phase 10 — Notifications

Integrate chat with the broader ScubaMob notification system.

Potential channels:

```text
In-app
Push
Email
```

Notifications should be asynchronous.

Do not send emails inside the synchronous message-write path.

---

# 30. Phase 11 — Attachments

Add support for:

```text
Images
Documents
Dive logs
Dive plans
Dive sites
Equipment
```

Binary content belongs in S3.

DynamoDB stores attachment references.

Use signed URLs when private content is retrieved.

---

# 31. Phase 12 — Rich ScubaMob Messages

ScubaMob chat should become more than generic direct messaging.

Support sharing platform objects.

Examples:

```text
Dive sites
Planned dives
Logbook entries
Equipment
Marketplace items
Dive shop information
```

Do not duplicate the full source object in the message.

Store references such as:

```json
{
  "message_type": "DIVE",
  "entity_type": "dive",
  "entity_id": "12345"
}
```

---

# 32. Phase 13 — Dive Conversations

Allow conversations to be associated with dives.

Examples:

```text
Catalina Saturday Dive
Blue Cavern Dive
Certification Weekend
```

When a diver joins:

```text
Paul joined the dive.
```

Use system messages for events generated by ScubaMob.

---

# 33. Phase 14 — Group Messaging

Support:

```text
Create group
Add members
Remove members
Leave conversation
Rename conversation
Set image
Promote admin
Mute conversation
```

Group roles remain in the relational database.

Messages remain in DynamoDB.

---

# 34. Phase 15 — Dive Shop Messaging

Allow divers to communicate with dive businesses.

Possible requests:

```text
Rental questions
Training availability
Charter information
Equipment questions
Dive schedules
Reservations
```

Conversation type:

```text
SHOP
```

The design should later allow shop staff accounts to participate in the same business conversation.

---

# 35. Phase 16 — Marketplace Messaging

Marketplace interactions should use the same chat domain.

Conversation type:

```text
MARKETPLACE
```

Possible topics:

```text
Product questions
Custom logbook requests
Order support
Pricing
Customization
Refund questions
```

Do not expose private email addresses by default.

---

# 36. Phase 17 — Blocking and Safety

Messaging must honor the ScubaMob social graph.

Implement:

```text
message reporting
conversation reporting
user blocking
spam throttling
rate limits
abuse detection hooks
```

---

# 37. Phase 18 — Rate Limiting

Add protection against:

```text
message floods
spam
automated abuse
attachment abuse
conversation creation abuse
```

Redis is appropriate for short-lived counters.

---

# 38. Phase 19 — Message Reactions

Support lightweight reactions.

Examples:

```text
👍
❤️
😂
🤿
```

Reactions can be stored in DynamoDB.

Choose the exact key design based on the access patterns required.

---

# 39. Phase 20 — Replies

Messages should support:

```text
reply_to_message_id
```

This enables quoted/reply UI without duplicating the original message body.

---

# 40. Phase 21 — Editing and Deletion

Support:

```text
Edit message
Delete message
```

Prefer soft deletion.

Suggested fields:

```text
edited_at
deleted_at
```

The UI should show:

```text
Message deleted
```

rather than simply making the record disappear.

---

# 41. Message Edit History

Optionally store edit history separately.

This can be useful for:

```text
moderation
abuse review
audit requirements
support investigations
```

---

# 42. Phase 22 — Search

DynamoDB is not a full-text search engine.

Do not use DynamoDB table scans for broad chat search.

When full-text search becomes necessary, introduce a dedicated search index such as OpenSearch.

Potential future pipeline:

```text
DynamoDB
   |
DynamoDB Streams
   |
Indexer
   |
OpenSearch
```

Search should be treated as a derived index, not the authoritative message store.

---

# 43. Phase 23 — DynamoDB Streams

DynamoDB Streams can later drive asynchronous processing.

Potential consumers:

```text
Search indexing
Analytics
Moderation
Notification fan-out
Archival
Audit pipelines
AI features
```

Do not introduce Streams until there is a concrete consumer.

---

# 44. Phase 24 — Background Jobs

Use asynchronous workers for:

```text
Email notifications
Push notifications
Attachment processing
Thumbnail generation
Virus scanning
Spam analysis
Moderation
Search indexing
Metadata reconciliation
```

Potential technologies:

```text
AWS SQS
Celery
Django-Q
Lambda
```

If ScubaMob remains AWS-centric, SQS is a natural option.

---

# 45. Phase 25 — Mobile Messaging

Desktop:

```text
LinkedIn-style floating messaging interface
```

Mobile:

```text
/messages
/messages/{conversation_id}
```

Use the same APIs and service layer.

---

# 46. Phase 26 — Delivery State

Possible future message states:

```text
SENT
DELIVERED
READ
```

Start with `sent` and `read` unless product requirements demand more.

---

# 47. Phase 27 — Read Receipts

Direct messages may support:

```text
Seen
```

Group conversations may instead show aggregated state.

---

# 48. Phase 28 — Conversation List Optimization

The conversation list should not require loading messages from every DynamoDB partition.

Store summary metadata in SQL:

```text
last_message_id
last_message_at
last_message_sender_id
last_message_preview
```

Treat this metadata as a repairable projection of the authoritative DynamoDB message.

---

# 49. Phase 29 — DynamoDB Capacity Strategy

Initially use:

```text
On-demand capacity
```

unless actual traffic patterns justify provisioned capacity.

Review capacity mode later using real traffic and cost metrics.

---

# 50. Phase 30 — Hot Partition Protection

Conversation ID is the natural partition key.

For ordinary direct and group chats this should work well.

Extremely large public chat rooms could create hot partitions.

Do not prematurely shard conversation partitions.

---

# 51. Phase 31 — Retention and TTL

DynamoDB TTL can be useful for truly temporary records.

Examples:

```text
temporary delivery events
short-lived moderation staging
ephemeral system artifacts
```

Normal user messages should not automatically expire unless ScubaMob intentionally introduces disappearing messages or retention policies.

---

# 52. Phase 32 — Backups and Recovery

Configure:

```text
DynamoDB point-in-time recovery
AWS backups where appropriate
S3 lifecycle policies
Relational database backups
```

Document and test restoration procedures.

---

# 53. Phase 33 — Security

DynamoDB access should occur only from trusted backend infrastructure.

Do not give the browser direct DynamoDB permissions.

Flow:

```text
Browser
   |
ScubaMob API / WebSocket
   |
Chat service
   |
DynamoDB
```

Use least-privilege IAM policies.

---

# 54. Message Privacy

Avoid logging:

```text
message bodies
attachment contents
private conversation text
```

Production logs should primarily contain identifiers:

```text
conversation_id
message_id
sender_id
request_id
event type
```

---

# 55. Phase 34 — Moderation Architecture

Create moderation hooks without forcing moderation logic directly into message persistence.

Possible flow:

```text
Message persisted
      |
      v
Async moderation job
      |
      v
Flag / review / action
```

---

# 56. Phase 35 — Observability

Monitor:

```text
Messages sent per minute
Message write latency
DynamoDB throttling
DynamoDB errors
WebSocket connections
WebSocket disconnects
Notification failures
Attachment failures
Redis latency
Unread reconciliation failures
```

---

# 57. Phase 36 — Testing Strategy

## Unit Tests

Test:

```text
service logic
permission checks
repository serialization
message validation
block rules
idempotency
```

## Integration Tests

Test:

```text
DynamoDB repository
SQL + DynamoDB interaction
Redis behavior
WebSocket delivery
attachment storage
```

## End-to-End Tests

Test:

```text
start conversation
send message
receive message
reload history
mark read
block user
send attachment
share dive
```

---

# 58. Local Development

Production may use DynamoDB, but development must remain easy.

Options include:

```text
DynamoDB Local
LocalStack
Dedicated development DynamoDB table
```

Choose one and document it.

---

# 59. Phase 37 — Infrastructure as Code

DynamoDB resources should be managed through the project's infrastructure process.

Define:

```text
table name
partition key
sort key
GSIs
point-in-time recovery
encryption
tags
stream configuration
```

Do not configure production tables manually as the authoritative deployment method.

---

# 60. Phase 38 — Cost Monitoring

Track:

```text
DynamoDB read/write cost
storage growth
S3 attachment storage
Redis cost
notification cost
search indexing cost
```

---

# 61. Phase 39 — Future Chat Service Extraction

Current:

```text
ScubaMob
   |
chat.services
   |
   +-- SQL
   +-- DynamoDB
   +-- Redis
```

Future:

```text
ScubaMob
   |
Messaging API client
   |
   v
Chat Service
   |
   +-- metadata store
   +-- DynamoDB
   +-- Redis
   +-- WebSocket infrastructure
```

The rest of ScubaMob should not need significant changes.

---

# 62. Microservice Extraction Criteria

Do not extract chat just because:

```text
it uses DynamoDB
it uses Redis
it uses WebSockets
it has a separate message database
```

Consider extraction when several of the following become true:

```text
Chat requires independent scaling.
Chat deployments need to happen independently.
Messaging traffic dominates normal API traffic.
WebSocket workloads require different infrastructure.
Chat reliability requirements diverge from the main site.
A separate engineering team owns messaging.
Independent release cycles become valuable.
The monolith becomes an operational bottleneck.
Chat requires geographic or multi-region scaling.
```

---

# 63. Recommended Initial Technology Stack

```text
Django 6
Django REST Framework
Django Channels
Relational ScubaMob database
Amazon DynamoDB
Redis
WebSockets
Amazon S3
AWS IAM
CloudWatch
```

Potential later services:

```text
SQS
Lambda
OpenSearch
SNS / push infrastructure
```

---

# 64. Recommended Implementation Sequence

## Milestone 1 — Foundation

```text
Chat Django module
Repository boundaries
DynamoDB table
Conversation SQL models
Basic permissions
```

## Milestone 2 — Basic Messaging

```text
Create conversation
Send text message
Retrieve history
Pagination
Direct conversations
```

## Milestone 3 — User Interface

```text
LinkedIn-style floating panel
Conversation list
Message window
Unread badges
```

## Milestone 4 — Real-Time

```text
Django Channels
Redis
WebSockets
Live delivery
Reconnect handling
```

## Milestone 5 — Messaging Quality

```text
Read state
Typing indicators
Presence
Message editing
Deletion
Replies
Reactions
```

## Milestone 6 — Attachments

```text
Image uploads
Documents
S3 storage
Signed URLs
Attachment metadata
```

## Milestone 7 — ScubaMob Integration

```text
Share dive sites
Share dive plans
Share logbooks
Share equipment
Dive chat
```

## Milestone 8 — Commerce

```text
Dive shop conversations
Marketplace messaging
Business participants
```

## Milestone 9 — Safety

```text
Blocking
Reporting
Spam limits
Rate limits
Moderation hooks
```

## Milestone 10 — Scale

```text
Streams
Search indexing
Analytics
Operational dashboards
Capacity optimization
```

---

# 65. Final Architecture Principle

ScubaMob should remain:

```text
ONE REPOSITORY
ONE DEPLOYABLE APPLICATION
MULTIPLE DOMAIN MODULES
SEPARATE STORAGE WHERE IT MAKES SENSE
```

The architecture is therefore:

```text
                         ScubaMob
                            |
            +---------------+---------------+
            |               |               |
          Social          Diving         Commerce
            |               |               |
            +---------------+---------------+
                            |
                           Chat
                            |
              +-------------+-------------+
              |             |             |
             SQL         DynamoDB        Redis
              |             |             |
        conversation      messages      realtime
         metadata                       ephemeral
```

This provides the benefits of storage isolation without paying the full cost of microservices.

---

# 66. Product Principle

Chat should not become a generic bolt-on messenger.

It should become the communication layer connecting ScubaMob's core experiences.

Users should eventually be able to communicate around:

```text
Divers
Dive buddies
Dive groups
Dive trips
Dive sites
Dive plans
Logbooks
Equipment
Dive shops
Training
Marketplace items
```

A message should be capable of carrying both human conversation and references to ScubaMob objects.

---

# 67. Current Recommended Decision

For the current stage of ScubaMob:

**Use the modular monolith for the chat application.**

**Use the relational database for conversation metadata and permissions.**

**Use DynamoDB as the dedicated chat-message store.**

**Use Redis for ephemeral real-time state and Django Channels.**

**Use S3 for message attachments.**

**Do not create a standalone chat microservice yet.**

This architecture gives ScubaMob a clean path from initial implementation to large-scale messaging without forcing a premature distributed-services architecture.

