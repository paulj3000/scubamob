"""
Error hierarchy for the chat domain (docs/chat_dynamo.md Phase 0).

Service-layer and repository code should raise these instead of letting
DynamoDB/boto3 or ORM-level exceptions leak past the chat.services boundary,
so the rest of ScubaMob never has to know how chat data is stored.
"""


class ChatError(Exception):
    """ Base class for every chat-domain error. """


class ConversationNotFoundError(ChatError):
    """ No conversation exists for the given conversation id. """


class MessageNotFoundError(ChatError):
    """ No message exists for the given (conversation id, message id). """


class NotAConversationParticipantError(ChatError):
    """ The acting user is not a current participant of the conversation. """


class BlockedUserError(ChatError):
    """ The message or conversation would cross a user-blocking relationship. """


class RepositoryUnavailableError(ChatError):
    """
    The backing store for a repository (DynamoDB, Redis) could not be
    reached or failed unexpectedly. Distinct from *NotFoundError so callers
    can tell "definitely doesn't exist" apart from "couldn't find out".
    """
