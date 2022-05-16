from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login

from scuba.accounts.forms import AccountForm


# -----------------------------------------------------------------------------
# Begin some class-based form stuff
# -----------------------------------------------------------------------------
class SignupView(FormView):
    """ SignupView

    Here is the class for the signup processes
    """
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
    form_class = AccountForm

    def form_valid(self, form):
        """ form_valid

        Once the form has been validated, there is some extra stuff that
        needs to get done for the new user
        """
        request = self.request
        user = form.save()

        # add mailchimp free user
        #user.add_free_mailchimp()

        # send the welcome email
        #user.send_welcome_free_email()
        #user.add_login(request.META.get('HTTP_X_REAL_IP'),
        #               request.META.get('HTTP_USER_AGENT'))

        user = authenticate(
            self.request,
            username=request.POST['username'],
            password=request.POST['password1'])

        print(" THE USER ... ")
        print(user)

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        return super().form_valid(form)
