from django import forms
from scuba.divesites.models import DivesiteReview


class DivesiteReviewForm(forms.ModelForm):

    add_to_feed = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if self.instance is not None:
            instance = self.instance

            if hasattr(instance, 'user'):
                user_feed = instance.user.get_feed_review(instance.id)
                if user_feed:
                    self.fields['add_to_feed'].initial = True

    def save(self, commit=True):
        add_to_feed = self.cleaned_data.get('add_to_feed', None)

        # ...do something with add_to_feed here...
        instance = super().save(commit=commit)
        user = instance.user

        if add_to_feed:
            # make sure there is no instance of this in the database
            # already
            if not user.get_feed_review(instance.id):
                user.add_review_to_feed(instance.id)

        else:
            feed = user.get_feed_review(instance.id)
            if feed:
                feed.delete()

        # now return the instance
        return instance

    class Meta:
        model = DivesiteReview
        fields = '__all__'


class DivesiteCheckinForm(forms.ModelForm):

    def save(self, commit=True):
        is_anonymous = self.cleaned_data.get('is_anonyous', None)

        # ...do something with add_to_feed here...
        instance = super().save(commit=commit)
        user = instance.user

        if not is_anonymous:
            # make sure there is no instance of this in the database
            # already
            if not user.get_feed_checkin(instance.id):
                user.add_checkin_to_feed(instance.id)
        else:
            feed = user.get_feed_checkin(instance.id)
            if feed:
                feed.delete()

        # now return the instance
        return instance

    class Meta:
        model = DivesiteReview
        fields = '__all__'
