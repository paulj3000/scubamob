from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic.edit import FormView

from scuba.accounts.forms.login import MagicLinkRequestForm
from scuba.accounts.models import User
from scuba.accounts.services import magiclink
from scuba.settings import LOGIN_REDIRECT_URL

# how many magic-link emails a single address may request per window
MAGIC_LINK_REQUEST_LIMIT = 3
MAGIC_LINK_REQUEST_WINDOW_SECONDS = 15 * 60


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    extra_context = {
        'hide_nav_account': True,
    }


class MagicLinkRequestView(FormView):
    """ MagicLinkRequestView

    Let a user request a one-time sign-in link by email instead of a
    password. Always responds the same way whether or not the email is
    registered, so the endpoint cannot be used to enumerate accounts.
    """
    template_name = 'accounts/magic_link_request.html'
    form_class = MagicLinkRequestForm
    success_url = reverse_lazy('magic_link_sent')
    extra_context = {'hide_nav_account': True}

    def form_valid(self, form):
        email = form.cleaned_data['email'].strip().lower()

        if not self._is_rate_limited(email):
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                _, raw_token = magiclink.create_magic_link_token(user)
                magiclink.send_magic_link_email(user, raw_token)

        return super().form_valid(form)

    @staticmethod
    def _is_rate_limited(email):
        cache_key = f'magic-link-request:{email}'
        count = cache.get(cache_key, 0)

        if count >= MAGIC_LINK_REQUEST_LIMIT:
            return True

        cache.set(cache_key, count + 1, timeout=MAGIC_LINK_REQUEST_WINDOW_SECONDS)
        return False


@method_decorator(never_cache, name='dispatch')
class MagicLinkConfirmView(View):
    """ MagicLinkConfirmView

    Verify a magic-link token from an emailed sign-in link and, if it is
    valid, log the user in through the normal session-authentication
    backend.
    """
    invalid_template_name = 'accounts/magic_link_invalid.html'

    def get(self, request, uidb64, token):
        user = magiclink.resolve_user_from_uidb64(uidb64)
        magic_token = magiclink.get_valid_token_for_user(user, token) if user else None

        if not user or not user.is_active or not magic_token:
            return render(request, self.invalid_template_name, {'hide_nav_account': True})

        magic_token.set_redeemed()
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return redirect(LOGIN_REDIRECT_URL)
