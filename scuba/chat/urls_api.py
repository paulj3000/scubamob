from django.urls import re_path

import scuba.chat.apis as chat_apis

_UUID = r'[0-9A-Fa-f-]{32,36}'

urlpatterns = [
    re_path(r'^conversations/$', chat_apis.ConversationListApi.as_view()),
    re_path(rf'^conversations/(?P<conversation_id>{_UUID})/$', chat_apis.ConversationDetailApi.as_view()),
    re_path(
        rf'^conversations/(?P<conversation_id>{_UUID})/messages/$',
        chat_apis.ConversationMessagesApi.as_view()),
    re_path(
        rf'^conversations/(?P<conversation_id>{_UUID})/read/$', chat_apis.ConversationReadApi.as_view()),
    re_path(
        rf'^conversations/(?P<conversation_id>{_UUID})/mute/$', chat_apis.ConversationMuteApi.as_view()),
    re_path(
        rf'^conversations/(?P<conversation_id>{_UUID})/archive/$',
        chat_apis.ConversationArchiveApi.as_view()),
    re_path(rf'^direct/(?P<user_id>{_UUID})/$', chat_apis.DirectConversationApi.as_view()),
    re_path(r'^unread-count/$', chat_apis.UnreadCountApi.as_view()),
]
