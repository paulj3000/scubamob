import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse

from scuba.accounts.decorators import can_view_profile
from scuba.accounts.serializers.profile import ProfileSerializer
from scuba.sitesettings.models import SystemSetting


@method_decorator([login_required, can_view_profile], name='dispatch')
class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        """ get_context_data

        override the get_context_data. add some extra data
        """
        context = super().get_context_data(**kwargs)
        profile_data = \
            ProfileSerializer(
                self.request.profile, context={'request': self.request}).data

        context.update({
            'chat_server_active': SystemSetting.get_chat_server_active(),
            'profile': self.request.profile,
            'profile_json': json.dumps(profile_data),
        })

        return context


@method_decorator(login_required, name='dispatch')
class AddUIMessageView(View):
    def post(self, request):
        if request.get('message'):
            print(request['message'])

            messages.add_message(request, messages.INFO, 'Hello world.')
        return JsonResponse()
