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


class InvalidSenderError(ChatError):
    """ The given sender id does not refer to a real, active user. """


class InvalidMessagePayloadError(ChatError):
    """ The message body/type does not pass basic validation. """


class NotMessageOwnerError(ChatError):
    """ The acting user did not author the message and lacks override rights. """


class InsufficientRoleError(ChatError):
    """ The acting user's participant role does not permit the requested action. """


class NotAuthorizedToViewPresenceError(ChatError):
    """ The requester does not share a conversation with the user whose presence they asked for. """


class NotificationNotFoundError(ChatError):
    """ No notification exists for the given (notification id, recipient) pair. """


class AttachmentNotFoundError(ChatError):
    """ No attachment exists for the given (conversation id, attachment id) pair. """


class InvalidAttachmentError(ChatError):
    """ The uploaded file fails validation (missing, too large, disallowed/undecodable type). """


class RepositoryUnavailableError(ChatError):
    """
    The backing store for a repository (DynamoDB, Redis) could not be
    reached or failed unexpectedly. Distinct from *NotFoundError so callers
    can tell "definitely doesn't exist" apart from "couldn't find out".
    """
