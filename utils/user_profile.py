from django.contrib.auth.models import User
from django.templatetags.static import static
from django.db.models import Q

from scuba.accounts.models import UserFriendBlocked, UserFriendRequest, Friendship
from scuba.settings import AWS_PROFILE_BLANK_URL


class UserProfile(User):
    class Meta:
        proxy=True

    def get_friend(self, friend):
        # get all of the current friends
        try:
            return User.objects.filter(
                    Q(friend_friend1__friend1=friend) |
                    Q(friend_friend2__friend2=friend))
        except:
            raise
            return None

    def get_all_friends(self):
        # return all of the friends that is not us!
        Friendship.objects.filter(Q(friend2=self) | Q(friend1=self)).values('friend1', 'friend2')

    def block_friend(self, friend):
        # get all of the current friends
        UserFriendBlocked.objects.create(user=self, friend=friend)

        # now, let's delete all friend requests...
        UserFriendRequest.objects.filter(Q(user=friend, friend=self) |
                                         Q(user=self, friend=friend)).delete()

    def get_blocked_friends(self):
        # get all of the current friends
        return self.blocked_user.order_by('friend__first_name')

    def is_blocked(self, friend):
        # check if the user is blocking for the friend.
        return UserFriendBlocked.objects.filter(Q(user=friend, friend=self) |
                                                Q(user=self, friend=friend)).count()

    def get_account(self):
        return self.account

    def get_albums(self):
        return self.albums.all()

    def get_album_by_guid(self, guid):
        try:
            return self.albums.get(guid=guid)
        except:
            return None

    # ----------------------------------------------------------------------------
    # Start profile image stuff
    # ----------------------------------------------------------------------------
    @property
    def profile_image(self):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''

        if hasattr(self, 'userprofileimage'):
            return self.userprofileimage.get_profile_image()

        # No profile image. just return a default
        return static(AWS_PROFILE_BLANK_URL)

    def upload_profile_image_as_string(self, uploaded_image_string):
        ''' upload a profile image to S3 when the uploaded image is sent
        over as a string
        Params:
            uploaded_image_string: a string representation of a profile image
        '''
        # generate the file name the
        img_length = 5 # the sub key length
        sub_name = StringUtils.generate_random_number(img_length)
        base_name = "profiles/%s/%s_%d.png" % (self.get_aws_id(), sub_name, int(time.time()))

        #if re.search(r'^data:image\/(jpg|png);base64', uploaded_image_string, re.DOTALL):
        result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", uploaded_image_string)

        profile_image = None
        if result:
            ext = result.groupdict().get("ext")
            data = result.groupdict().get("data")

            img = base64.urlsafe_b64decode(data)
            User.upload_image(base_name, 'image/%s' % ext, img)

            # does the user have a prfofile image? if so, replace it
            if hasattr(self, 'userprofileimage'):
                profile_image = getattr(self, 'userprofileimage')
                profile_image.image = base_name
                profile_image.save()
            else:
                profile_image = UserProfileImage.objects.create(user=self, image=base_name)

        # return the new profile image
        return profile_image

    @staticmethod
    def upload_image(filename, content_type, uploaded_image):
        """ upload_image

        Upload a new object to s3 for the user.
        """
        # set the header and file information
        header = {'ContentType': content_type}

        # generate the key name
        S3.upload_raw_data(AWS_S3_BUCKET, filename, uploaded_image, **header)
