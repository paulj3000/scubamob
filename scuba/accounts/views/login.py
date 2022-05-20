from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.views.generic.edit import FormView


class LoginView(BaseLoginView):
    #form_class = AuthenticationForm
    template_name = 'accounts/login.htmxxl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'hide_nav_account': True,
        })
        return context

