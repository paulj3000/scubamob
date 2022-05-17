from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from scuba.accounts.forms import AccountForm
from scuba.settings import FACEBOOK_APP


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
            username=request.POST['email'],
            password=request.POST['password1'])

        print(" THE USER ... ")
        print(user)

        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'hidelogin': True,
            'facebook_id': FACEBOOK_APP,
            'hide_steps': self.hide_steps,
        })
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ValidateEmail(View):
    """ Email validation coming through. This will be used to verify if the
    email address has already been registered
    """
    def post(self, request):
        """ Do the actual post """
        if request.session.get('duplicate_email_ok'):
            return JsonResponse(True, safe=False)

        email = request.POST.get('email')

        retval = 'true'

        if email:
            user = request.user
            if user.is_authenticated:
                ex_user = User.objects.filter(email=email).first()
                if ex_user:
                    if str(ex_user.id) != str(user.id):
                        retval = 'false'
                    else:
                        retval = 'true'
                else:
                    retval = 'true'
            else:
                if User.objects.filter(email=email).count():
                    retval = 'false'
        else:
            retval = 'false'

        return JsonResponse(retval, safe=False)
