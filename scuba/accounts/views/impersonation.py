from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from scuba.security.services import impersonation


class StopImpersonationView(View):
    """ StopImpersonationView

    Restore the original admin's session. Deliberately not gated on
    is_staff/is_superuser: while impersonating, the logged-in user is the
    (usually non-staff) target, so this view instead relies on the
    'impersonator_id'/'impersonation_event_id' session markers that only
    start_impersonation() can set.
    """
    def post(self, request):
        try:
            impersonation.stop_impersonation(request)
        except impersonation.ImpersonationError as exc:
            messages.add_message(request, messages.ERROR, str(exc))
            return redirect('index')

        messages.add_message(request, messages.INFO, 'Impersonation session ended.')
        return redirect('/admin/accounts/user/')
