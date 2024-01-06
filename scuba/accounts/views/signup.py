from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View

from scuba.accounts.forms.signup import SignupForm
from scuba.security.models import InvalidEmail
from scuba.settings import IS_PRODUCTION


# -----------------------------------------------------------------------------
# Begin some class-based form stuff
# -----------------------------------------------------------------------------
class SignupView(FormView):
    """ SignupView

    Here is the class for the signup processes
    """
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
    form_class = SignupForm
    extra_context = {
        'hide_nav_account': True,
    }

    def form_valid(self, form):
        """ form_valid

        Once the form has been validated, there is some extra stuff that
        needs to get done for the new user
        """
        request = self.request
        user = form.save()

        user = authenticate(
            self.request,
            email=request.POST['email'],
            password=request.POST['password'])

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()

        request = self.request

        if IS_PRODUCTION:
            form.set_ip_address(request.META.get('HTTP_X_REAL_IP'))

        if form.is_valid():
            return self.form_valid(form)
        else:
            if request.POST.get('email'):
                InvalidEmail.objects.create(
                    email=request.POST['email'],
                    ip_address=request.META.get("HTTP_X_REAL_IP", '0.0.0.0'))
            return self.form_invalid(form)


@method_decorator(csrf_exempt, name='dispatch')
class ValidateEmail(View):
    """ Email validation coming through. This will be used to verify if the
    email address has already been registered
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()

        request = self.request
        form.set_ip_address(request.META.get('HTTP_X_REAL_IP'))

        if form.is_valid():
            return self.form_valid(form)
        else:
            if request.POST.get('email'):
                InvalidEmail.objects.create(
                    email=request.POST['email'],
                    ip_address=request.META.get("HTTP_X_REAL_IP"))

            return self.form_invalid(form)
