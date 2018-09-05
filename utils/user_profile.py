from django.contrib.auth.models import User
from account.models import UserFriendBlocked, UserFriendRequest, Friendship
from django.db.models import Q

class UserProfile(User):
    class Meta:
        proxy=True

    def get_friend(self, friend):
        #### get all of the current friends
        try:
            return User.objects.filter(
                    Q(friend_friend1__friend1=friend) | 
                    Q(friend_friend2__friend2=friend))
        except:
            raise
            return None

    def get_all_friends(self):
        ### return all of the friends that is not us!
        Friendship.objects.filter(Q(friend2=self) | Q(friend1=self)).values('friend1', 'friend2')

    def block_friend(self, friend):
        #### get all of the current friends
        UserFriendBlocked.objects.create(user=self, friend=friend)

        #### now, let's delete all friend requests...
        UserFriendRequest.objects.filter(Q(user=friend, friend=self) | 
                                         Q(user=self, friend=friend)).delete()

    def get_blocked_friends(self):
        #### get all of the current friends
        return self.blocked_user.order_by('friend__first_name')
    
    def is_blocked(self, friend):
        #### check if the user is blocking for the friend.
        return UserFriendBlocked.objects.filter(Q(user=friend, friend=self) | 
                                                Q(user=self, friend=friend)).count()
