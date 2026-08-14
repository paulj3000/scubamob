# -----------------------------------------------------------------------------
# accounts/services/magiclink.py
#
# Passwordless ("magic link") sign-in: generate a one-time token, email it,
# and verify it when the user clicks the link.
# -----------------------------------------------------------------------------
import hashlib
import secrets

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from scuba.accounts.models import MagicLinkToken, User
from scuba.libs.mail import generate_email, send_mail
from scuba.settings import MAGIC_LINK_TOKEN_TTL_MINUTES, SITE_TITLE, SITE_URL


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()


def create_magic_link_token(user: User) -> tuple[MagicLinkToken, str]:
    """ create_magic_link_token

    Create a new magic-link token for the user, invalidating any
    previously issued, unredeemed tokens so only the newest link works.
    Returns the (MagicLinkToken, raw_token) pair -- only the hash of
    raw_token is persisted.
    """
    MagicLinkToken.objects.filter(user=user, redeemed=False).update(redeemed=True)

    raw_token = secrets.token_urlsafe(32)
    token = MagicLinkToken.objects.create(user=user, token_hash=_hash_token(raw_token))
    return token, raw_token


def get_valid_token_for_user(user: User, raw_token: str) -> MagicLinkToken | None:
    """ get_valid_token_for_user

    Return the matching, unredeemed, unexpired MagicLinkToken for the
    user, or None if the token is missing, already used, or expired.
    """
    token = user.magic_link_tokens.filter(
        token_hash=_hash_token(raw_token), redeemed=False).order_by('-created').first()

    if token is None or token.is_expired():
        return None

    return token


def resolve_user_from_uidb64(uidb64: str) -> User | None:
    """ resolve_user_from_uidb64

    Decode a base64-encoded user id (as used in emailed links), mirroring
    Django's own password-reset uidb64 handling.
    """
    try:
        pk = urlsafe_base64_decode(uidb64).decode()
        return User.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, ValidationError, User.DoesNotExist):
        return None


def build_magic_link_url(user: User, raw_token: str) -> str:
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    path = reverse('magic_link_confirm', kwargs={'uidb64': uidb64, 'token': raw_token})
    return f'{SITE_URL}{path}'


def send_magic_link_email(user: User, raw_token: str) -> None:
    """ send_magic_link_email

    Email the user their one-time sign-in link.
    """
    url = build_magic_link_url(user, raw_token)
    content = (
        f'Click the link below to sign in to your {SITE_TITLE} account. '
        f'This link expires in {MAGIC_LINK_TOKEN_TTL_MINUTES} minutes and can only be used once.'
        f'<br><br>'
        f'<a href="{url}">Sign in to {SITE_TITLE}</a>'
        f'<br><br>'
        "If you didn't request this, you can safely ignore this email."
    )

    html = generate_email(
        user, 'content/emails/magic_link.html',
        {'content': content, 'short_code': f'Sign in to {SITE_TITLE}'})

    send_mail(user, f'Your {SITE_TITLE} sign-in link', html, strip_tags(content))
