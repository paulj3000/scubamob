#from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView as BaseLoginView
#from django.views.generic.edit import FormView


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    extra_context = {
        'hide_nav_account': True,
    }
