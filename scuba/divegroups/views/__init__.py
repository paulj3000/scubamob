from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# define the user data for this account
from scuba.accounts.models import UserBuddyRequest


@login_required
def index(us_request, mode=None):
    context = {'page_title': 'Manage Friends'}
    user = us_request.user

    print(user.get_account())

    UserBuddyRequest.objects.update_friend_request_active(user)
    friend_list = us_request.user.friend_user.order_by('friend__first_name')
    friend_request_list = us_request.user.friend_requests.order_by('friend__first_name')

    context.update(friend_list=friend_list, friend_request_list=friend_request_list)
    return render(us_request, "friends/index.html", context)
