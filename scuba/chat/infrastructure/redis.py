"""
Redis access for the chat domain (docs/chat_dynamo.md §27, Phase 8).

A settings-driven client accessor, mirroring infrastructure/dynamodb.py's
get_client() -- so CHAT_REDIS_URL is the only place the connection target
is configured. Typing-indicator read/write logic lives in
TypingRepository's Redis-backed implementation; this module only hands
out a configured client.
"""
import redis

from scuba.settings import CHAT_REDIS_URL


def get_client() -> redis.Redis:
    return redis.Redis.from_url(CHAT_REDIS_URL)
