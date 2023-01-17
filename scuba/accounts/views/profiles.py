from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages

from scuba.accounts.models import UserBuddyRequest, UserBuddy, User
from scuba.accounts.decorators import can_view_profile
from scuba.sitesettings.models import SystemSetting


@login_required
def profile(us_request, username):
    user = us_request.user

    # let's get the user based on the uidb36 coming in
    profile = None

    # let's try and get the user
    profile = get_object_or_404(User, username=username)

    # nope, is it a possible friend?
    if len(UserBuddy.objects.filter(user=user, friend=profile)) or \
        len(UserBuddyRequest.objects.filter(user=profile, friend=user)):
            authorized = True

    context = {
        'chat_server_active': SystemSetting.get_chat_server_active(),
        'profile': self.request.profile,
    }

    UserBuddyRequest.update_friend_request_active(user)
    friend_request_list = us_request.user.friend_requested.order_by('friend__first_name')

    context.update(friend_request_list=friend_request_list)
    #return render(us_request, "accounts/profile.html", context)


@method_decorator([login_required, can_view_profile], name='dispatch')
class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        """ get_context_data

        override the get_context_data. add some extra data
        """
        context = super().get_context_data(**kwargs)
        context['chat_server_active'] = SystemSetting.get_chat_server_active()
        context['profile'] = self.request.profile
        return context


@method_decorator(login_required, name='dispatch')
class AddUIMessageView(View):
    def post(self, request):
        if request.get('message'):
            print(request['message'])

            messages.add_message(request, messages.INFO, 'Hello world.')
        return JsonResponse()
