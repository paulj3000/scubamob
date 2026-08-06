''' service layer for audited superuser "login as user" support tooling '''
from django.contrib.auth import login as django_login
from django.http import HttpRequest

from scuba.accounts.models import User
from scuba.security.models import ImpersonationEvent

SESSION_IMPERSONATOR_ID_KEY = 'impersonator_id'
SESSION_IMPERSONATION_EVENT_ID_KEY = 'impersonation_event_id'


class ImpersonationError(Exception):
    ''' raised when an impersonation start/stop request cannot be honored '''


def start_impersonation(request: HttpRequest, actor: User, target: User, reason: str) -> ImpersonationEvent:
    ''' log `actor` in as `target`, recording an audit event

    Raises ImpersonationError if the request is not allowed.
    '''
    if not actor.is_superuser:
        raise ImpersonationError('Only superusers may impersonate another user.')

    if request.session.get(SESSION_IMPERSONATOR_ID_KEY):
        raise ImpersonationError('You are already impersonating a user. Stop that session first.')

    if not reason or not reason.strip():
        raise ImpersonationError('A reason is required to impersonate a user.')

    if target.pk == actor.pk:
        raise ImpersonationError('You cannot impersonate yourself.')

    if target.is_superuser:
        raise ImpersonationError('Superuser accounts cannot be impersonated.')

    if not target.is_active:
        raise ImpersonationError('Inactive accounts cannot be impersonated.')

    event = ImpersonationEvent.objects.create(
        actor=actor,
        target=target,
        reason=reason.strip(),
        ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
    )

    # django_login() flushes the session when the authenticated user changes,
    # so the impersonation markers must be set *after* this call, not before.
    django_login(request, target, backend='django.contrib.auth.backends.ModelBackend')
    request.session[SESSION_IMPERSONATOR_ID_KEY] = str(actor.pk)
    request.session[SESSION_IMPERSONATION_EVENT_ID_KEY] = str(event.pk)

    return event


def stop_impersonation(request: HttpRequest) -> ImpersonationEvent:
    ''' restore the original admin session, closing out the audit event

    Raises ImpersonationError if the current session is not impersonating anyone.
    '''
    actor_id = request.session.get(SESSION_IMPERSONATOR_ID_KEY)
    event_id = request.session.get(SESSION_IMPERSONATION_EVENT_ID_KEY)

    if not actor_id or not event_id:
        raise ImpersonationError('This session is not impersonating anyone.')

    try:
        actor = User.objects.get(pk=actor_id)
    except User.DoesNotExist as exc:
        raise ImpersonationError('The original admin account no longer exists.') from exc

    try:
        event = ImpersonationEvent.objects.get(pk=event_id, ended_at__isnull=True)
    except ImpersonationEvent.DoesNotExist as exc:
        raise ImpersonationError('No active impersonation event found for this session.') from exc

    # same ordering constraint as start_impersonation: login() flushes the session
    django_login(request, actor, backend='django.contrib.auth.backends.ModelBackend')

    event.mark_ended()

    return event
