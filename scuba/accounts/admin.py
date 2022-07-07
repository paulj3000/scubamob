# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.contrib import admin
from django.contrib.sessions.models import Session

from scuba.accounts.models import User


class UserAdmin(admin.ModelAdmin):
    """ UserAdmin

    Override the user admin, add extra functionality
    """
    def profile_image(self, obj):
        return mark_safe(
            '<img src="%s" alt="%s" style="width:40px;height:auto" />' % \
            (obj.get_profile_image(), obj.get_full_name())
        )

    profile_image.short_description = ''
    profile_image.allow_tags = True


    def reset_password(self, request, userid):
        user = get_object_or_404(self.model, pk=userid)
        form = PasswordResetForm(data={'email': user.email})
        form.is_valid()
        form.save()
        messages.add_message(request, messages.INFO, 'Password reset successfully sent')
        return redirect('/admin/accounts/user/{0}/change/'.format(userid))

    # -----------------------------------------------------------------------------
    # Start some user admin stuff
    # -----------------------------------------------------------------------------
    def all_unexpired_sessions_for_user(self, user):
        user_sessions = []
        all_sessions = Session.objects.filter(expire_date__gte=datetime.now())
        for session in all_sessions:
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') and \
               str(user.pk) == str(session_data.get('_auth_user_id')):
                user_sessions.append(session.pk)
        return Session.objects.filter(pk__in=user_sessions)

    def delete_all_unexpired_sessions_for_user(self, request, queryset):
        for user in queryset:
            for sess in self.all_unexpired_sessions_for_user(user):
                sess.delete()
        messages.add_message(request, messages.INFO, 'Sessions successfully invalidated')

    def block_user(modeladmin, request, queryset):
        ''' block the user's account.

        After the user is blocked, he should not be able to log back into the system
        '''
        for obj in queryset:
            obj.block_user()

        messages.add_message(request, messages.INFO, 'User successfully blocked')

    def send_password_reset(self, request, queryset):
        for user in queryset:
            self.reset_password(request, user.id)

        # set a success message
        messages.add_message(request, messages.INFO, 'Passwords successfully reset')

    delete_all_unexpired_sessions_for_user.short_description = 'Invalidate User Sessions'
    block_user.short_description = "Block User"
    send_password_reset.short_description = "Send Password Reset"

    # add some custom actions for the user
    actions = [
        delete_all_unexpired_sessions_for_user,
        block_user,
        send_password_reset,
    ]

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined',
                    'last_login_date')

    fieldsets = (
        (None, {'fields': ('email', 'full_name', 'is_admin', 'last_login_date', 'ignore_tracking', 'is_protected', 'is_active', 'is_blocked', 'is_staff_member',)}),
        ('Permissions', {'fields': ('groups', )}),
    )

    search_fields = ['full_name', 'email', 'username',]


admin.site.register(User, UserAdmin)
