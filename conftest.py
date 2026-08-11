"""
Session-wide pytest configuration.
"""


def pytest_configure(config):
    """
    Real-time chat delivery (docs/chat_dynamo.md Phase 6) uses
    channels_redis in production, which needs a live Redis. CLAUDE.md
    forbids tests depending on a live external service, so every test run
    gets the in-process channels.layers.InMemoryChannelLayer instead --
    set once here rather than requiring every test that (directly or
    indirectly, via chat.services.send_message) touches the channel layer
    to remember its own override.
    """
    from django.conf import settings

    settings.CHANNEL_LAYERS = {
        'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'},
    }
