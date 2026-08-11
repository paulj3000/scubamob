# ScubaMob Chat / Messaging Roadmap

## Architecture Decision

ScubaMob messaging will initially be implemented as a **module within the ScubaMob modular monolith**.

It will not initially be deployed as an independent microservice.

The messaging system will have clearly defined internal boundaries so that it can later be extracted into a standalone service without redesigning the application.

## Initial Architecture

```text
ScubaMob Django Application

┌─────────────────────────────────────────────┐
│                  ScubaMob                    │
│                                             │
│  Accounts         Social                    │
│  Profiles         Dive Planning             │
│  Dive Sites       Logbooks                  │
│  Marketplace      Equipment                 │
│                                             │
│              ┌───────────────┐              │
│              │     Chat      │              │
│              │               │              │
│              │ Conversations │              │
│              │ Messages      │              │
│              │ Presence      │              │
│              │ Notifications │              │
│              └───────┬───────┘              │
│                      │                       │
└──────────────────────┼───────────────────────┘
                       │
                 Django Channels
                       │
                    Redis
                       │
                  WebSockets
```

Redis should be treated as infrastructure supporting the application rather than evidence that messaging is a separate service.

---

# Phase 0 — Architecture Foundation

## Goal

Create a messaging architecture that fits the ScubaMob monolith while preserving the ability to extract messaging later.

## Create Django Application

```text
chat/
```

Recommended internal structure:

```text
chat/
├── __init__.py
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
└── tests/
    ├── test_conversations.py
    ├── test_messages.py
    ├── test_permissions.py
    └── test_websockets.py
```

## Architectural Rule

Other ScubaMob applications should not directly create or manipulate messaging records.

Instead, expose operations through:

```python
chat.services
```

Examples:

```python
create_conversation()
send_message()
add_participant()
remove_participant()
mark_conversation_read()
```

This service boundary will make future microservice extraction substantially easier.

---

# Phase 1 — Core Conversation Model

Implement the basic messaging data model.

## Conversation

Represents a private or group conversation.

Suggested fields:

```text
id
conversation_type
title
created_by
created_at
updated_at
last_message_at
```

Conversation types:

```text
DIRECT
GROUP
SYSTEM
```

Future possibilities:

```text
DIVE
TRIP
SHOP
MARKETPLACE
```

## ConversationParticipant

Connect users to conversations.

Suggested fields:

```text
conversation
user
joined_at
left_at
role
last_read_message
muted
archived
```

Roles:

```text
MEMBER
ADMIN
OWNER
```

This model should determine conversation membership and access.

## Message

Suggested fields:

```text
id
conversation
sender
message_type
body
created_at
edited_at
deleted_at
reply_to
```

Message types:

```text
TEXT
IMAGE
FILE
SYSTEM
DIVE
LOGBOOK
LOCATION
```

Design the type system now even if Phase 1 only implements `TEXT`.

---

# Phase 2 — REST Messaging API

Create the normal REST API before implementing real-time updates.

Example endpoints:

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
```

Direct-message helper:

```text
POST /api/chat/direct/{user_id}/
```

This should either:

1. Return an existing direct conversation.
2. Create one.

Do not allow duplicate one-to-one conversations between the same users.

---

# Phase 3 — LinkedIn-Style Messaging UI

Create a persistent messaging panel similar to LinkedIn.

Desktop concept:

```text
┌───────────────────────────────────────────────────┐
│ ScubaMob                                           │
│                                                   │
│                                                   │
│                       ┌─────────────────────────┐ │
│                       │ Messaging               │ │
│                       ├─────────────────────────┤ │
│                       │ Search messages         │ │
│                       ├─────────────────────────┤ │
│                       │ Chris Kelly        2    │ │
│                       │ Dive Buddies            │ │
│                       │ Catalina Trip           │ │
│                       └─────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

Opening a conversation:

```text
┌───────────────────────────────────────────────────┐
│                                       Messaging   │
│                              ┌──────────────────┐ │
│                              │ Chris Kelly      │ │
│                              ├──────────────────┤ │
│                              │ Hey, diving Sat? │ │
│                              │                  │ │
│                              │ Yep. Catalina?   │ │
│                              │                  │ │
│                              ├──────────────────┤ │
│                              │ Write message... │ │
│                              └──────────────────┘ │
└───────────────────────────────────────────────────┘
```

The interface should remain available while users navigate between ScubaMob pages.

---

# Phase 4 — Real-Time Messaging

Add:

```text
Django Channels
Redis
WebSockets
```

Example WebSocket route:

```text
/ws/chat/{conversation_id}/
```

Events may include:

```text
message.created
message.updated
message.deleted

conversation.updated

user.typing
user.stopped_typing

message.read
```

Messages should still be persisted through the application service layer.

WebSockets are a delivery mechanism, not the source of truth.

The database remains authoritative.

---

# Phase 5 — Unread Counts

Implement unread state.

Conversation participant should maintain something equivalent to:

```text
last_read_message
```

or:

```text
last_read_at
```

Prefer message-based tracking if possible.

Expose:

```text
GET /api/chat/unread-count/
```

The main navbar may display:

```text
Messages (3)
```

The LinkedIn-style messaging drawer can show unread badges beside individual conversations.

---

# Phase 6 — Typing Indicators

Add ephemeral Redis-backed state.

Examples:

```text
Paul is typing...
Chris is typing...
```

Do not store typing state permanently in the database.

WebSocket events:

```text
typing.start
typing.stop
```

Typing indicators should automatically expire after a short period.

---

# Phase 7 — Presence

Optional user states:

```text
ONLINE
AWAY
OFFLINE
```

Presence should primarily live in Redis rather than relational database records.

UI examples:

```text
● Chris Kelly
○ John Smith
```

Avoid exposing precise activity history unless needed.

A simple:

```text
Active now
Recently active
```

model is sufficient.

---

# Phase 8 — Message Notifications

Integrate messaging with ScubaMob notifications.

Example:

```text
Chris Kelly sent you a message.
```

Notification delivery may eventually include:

```text
In-app
Email
Push
```

Users should be able to configure notification preferences.

Example:

```text
Messages

☑ In-app
☑ Push
☐ Email
```

---

# Phase 9 — Attachments

Add message attachments.

Supported types could initially include:

```text
Images
Documents
Dive logs
Dive plans
Dive sites
```

Storage should use the existing ScubaMob media/storage architecture.

An attachment should be represented separately from the Message record.

Example:

```text
MessageAttachment

message
attachment_type
file
content_type
size
metadata
created_at
```

---

# Phase 10 — ScubaMob-Specific Rich Messages

This is where ScubaMob messaging should become more than generic chat.

Users should be able to send application objects directly into conversations.

## Share a Dive Site

```text
Casino Point
Avalon, Catalina Island

Depth: 20–90 ft
Visibility: 40 ft

[View Dive Site]
```

## Share a Planned Dive

```text
Catalina Dive

Saturday
8:00 AM

Participants: 4

[View Dive]
[Join Dive]
```

## Share a Logbook Entry

```text
Blue Cavern

Max Depth: 62 ft
Bottom Time: 47 min

[View Dive Log]
```

## Share Equipment

```text
Scubapro MK25
Last serviced: March 2026

[View Equipment]
```

These messages should reference ScubaMob objects rather than duplicating the underlying data.

---

# Phase 11 — Dive Group Conversations

Automatically create conversations around activities.

Examples:

```text
Dive Trip Chat
Dive Group Chat
Buddy Group Chat
Training Group Chat
```

When someone joins a planned dive:

```text
Paul joined the dive.
```

The system can create system-generated messages.

Example:

```text
SYSTEM:
Paul added Chris to the Catalina Dive.
```

---

# Phase 12 — Dive Shop Messaging

Allow users to communicate with dive shops.

Example:

```text
User
   │
   ▼
ScubaMob Messaging
   │
   ▼
Dive Shop
```

Potential use cases:

```text
Ask about rentals
Ask about dive schedules
Ask about equipment
Request training
Ask about charters
```

Conversation type:

```text
SHOP
```

This could eventually become a meaningful ScubaMob business feature.

---

# Phase 13 — Marketplace Messaging

Marketplace purchases should use ScubaMob messaging.

Example:

```text
Paul
 ↓
Custom Logbook Designer
```

Conversation type:

```text
MARKETPLACE
```

Users could discuss:

```text
customization
support
orders
logbook templates
refund questions
```

Avoid revealing private email addresses between marketplace participants.

---

# Phase 14 — Blocking and Safety

Messaging must respect ScubaMob social safety rules.

Implement:

```text
User blocking
Message reporting
Conversation reporting
Spam throttling
Rate limits
```

If user A blocks user B:

```text
user B cannot:

start a new conversation
send messages
add user A to group conversations
```

The chat permission layer should query the ScubaMob social/blocking subsystem.

---

# Phase 15 — Search

Add message search.

Example:

```text
Search messages...

"catalina"
```

Search results:

```text
Chris Kelly
"Want to dive Catalina Saturday?"

Catalina Dive Group
"The boat leaves at 7:30."
```

Initially database search is sufficient.

A specialized search service is unnecessary until scale requires one.

---

# Phase 16 — Message Reactions

Support lightweight reactions.

Examples:

```text
👍
❤️
😂
🤿
```

Suggested model:

```text
MessageReaction

message
user
reaction
created_at
```

Unique constraint:

```text
message + user + reaction
```

---

# Phase 17 — Reply / Quote

Allow users to reply to specific messages.

```text
Chris:
Visibility looks great Saturday.

Paul:
> Visibility looks great Saturday.

Let's hit Casino Point.
```

Implement with:

```text
Message.reply_to
```

---

# Phase 18 — Editing and Deletion

Support:

```text
Edit message
Delete message
```

Prefer soft deletion.

Example:

```text
deleted_at
```

UI:

```text
Message deleted
```

Do not physically remove messages immediately unless required by retention policies.

---

# Phase 19 — Group Conversation Administration

Group conversations should support:

```text
Add participant
Remove participant
Promote admin
Leave conversation
Rename conversation
Change conversation image
Mute notifications
```

Conversation administrators should be separate from broader ScubaMob administrative roles.

---

# Phase 20 — Mobile Messaging

On mobile, messaging should transition from the desktop popup/drawer model to a dedicated screen.

Example:

```text
/messages
/messages/{conversation_id}
```

Desktop:

```text
LinkedIn-style floating interface
```

Mobile:

```text
Full-screen messaging interface
```

Both should use the same APIs.

---

# Phase 21 — Background Jobs

Introduce background processing for:

```text
email notifications
push notifications
attachment processing
image thumbnails
spam detection
inactive conversation cleanup
```

Use the project's selected task system.

Candidates include:

```text
Celery
Django-Q
AWS SQS workers
```

Do not execute expensive notification or attachment work inside WebSocket handlers.

---

# Phase 22 — Observability

Track messaging metrics.

Examples:

```text
messages sent
active conversations
message delivery latency
WebSocket connections
failed WebSocket events
notification failures
attachment failures
```

Logging should include:

```text
conversation_id
message_id
user_id
request_id
```

Do not log message bodies in normal production logs.

---

# Phase 23 — Scale Preparation

The architecture should allow multiple ScubaMob application instances.

Example:

```text
                    Load Balancer
                         │
             ┌───────────┴───────────┐
             │                       │
        Django Node 1           Django Node 2
             │                       │
             └───────────┬───────────┘
                         │
                       Redis
                         │
                      Database
```

Django Channels + Redis allows WebSocket traffic to be distributed between application servers.

This will support a substantial user base before messaging needs to become a separate service.

---

# Phase 24 — Microservice Extraction Threshold

Do **not** extract messaging merely because it uses WebSockets.

Consider extracting chat when several of the following become true:

```text
Messaging traffic dominates ScubaMob traffic.

Messaging requires independent scaling.

WebSocket servers need different infrastructure.

Messaging deployments occur independently.

Large engineering teams own messaging separately.

Chat reliability requirements differ significantly from the main site.

Hundreds of thousands or millions of concurrent messaging connections exist.

Dedicated message storage becomes necessary.
```

At that point:

```text
ScubaMob
    │
    ▼
Messaging API
    │
    ▼
Chat Service
    │
    ├── Message Database
    ├── Redis
    ├── WebSocket Gateway
    └── Workers
```

Because ScubaMob initially accesses messaging through `chat.services`, that layer can later become an API client without significantly affecting the rest of the application.

---

# Recommended Initial Technology

For the current ScubaMob architecture:

```text
Django 6
Django REST Framework
Django Channels
Redis
WebSockets
Existing ScubaMob relational database
Existing media/S3 architecture
Existing authentication system
```

Avoid introducing Kafka, RabbitMQ, a second database, or an independent chat deployment during the initial implementation.

---

# Suggested Implementation Order

The practical implementation sequence should be:

```text
Phase 0
Architecture boundaries

Phase 1
Conversation models

Phase 2
REST API

Phase 3
LinkedIn-style UI

Phase 4
WebSocket messaging

Phase 5
Unread messages

Phase 6
Typing indicators

Phase 7
Presence

Phase 8
Notifications

Phase 9
Attachments

Phase 10
ScubaMob rich messages

Phase 11
Dive group conversations

Phase 12
Dive shop messaging

Phase 13
Marketplace messaging

Phase 14
Blocking/reporting

Phase 15+
Advanced messaging features
```

---

# Architectural Principle

ScubaMob should remain:

```text
ONE REPOSITORY
ONE APPLICATION
MULTIPLE DOMAIN MODULES
```

not:

```text
profiles-service
dive-service
logbook-service
chat-service
marketplace-service
notification-service
```

at this stage.

The internal architecture should resemble microservices through clear domain boundaries without taking on the operational complexity of actually deploying microservices.

The preferred model is:

```text
                ScubaMob
                   │
       ┌───────────┼────────────┐
       │           │            │
     Social      Diving       Commerce
       │           │            │
       └───────────┼────────────┘
                   │
                 Chat
                   │
             Notifications
```

Chat is therefore a **first-class ScubaMob domain**, but not yet a separate infrastructure service.

## Core Product Principle

Chat should not become merely a generic texting feature.

ScubaMob messaging should eventually allow users to send and interact with:

- Dive sites
- Planned dives
- Dive trips
- Logbook entries
- Equipment
- Dive shop information
- Marketplace items
- Training opportunities

This makes messaging connective infrastructure across the ScubaMob platform while keeping the implementation inside the modular monolith until independent scaling becomes necessary.

