from django.contrib import admin

from scuba.chat.models import Conversation, ConversationParticipant, DirectConversationPair


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation_type', 'title', 'created_by', 'created_at', 'last_message_at')
    list_filter = ('conversation_type',)
    inlines = [ConversationParticipantInline]


class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'user', 'role', 'joined_at', 'left_at', 'muted', 'archived')
    list_filter = ('role', 'muted', 'archived')


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(ConversationParticipant, ConversationParticipantAdmin)
admin.site.register(DirectConversationPair)
