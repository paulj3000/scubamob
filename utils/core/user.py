from django.contrib.auth.models import User

### let's add some extra functions for the user object.


def get_account(self):
    return self.account.filter().first()

def get_albums(self):
    return self.albums.all()

def get_album_by_guid(self, guid):
    try:
        return self.albums.get(guid=guid)
    except:
        return None

## add a couple of functions to help us
User.get_account        = get_account
User.get_albums         = get_albums
User.get_album_by_guid  = get_album_by_guid
