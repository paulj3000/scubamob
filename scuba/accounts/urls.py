from django.conf.urls import include
from django.urls import path, re_path

from scuba.accounts.forms import SettingsForm, PasswordForm
import scuba.accounts.views as account_views
import scuba.accounts.apis as account_api
import scuba.accounts.views.settings as settings_views


urlpatterns = [
    path('socket/', account_api.SocketApi.as_view()),
]
