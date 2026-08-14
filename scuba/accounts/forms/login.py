from django import forms


class MagicLinkRequestForm(forms.Form):
    """ MagicLinkRequestForm

    Request a passwordless sign-in link by email.
    """
    email = forms.EmailField(label="Email")
