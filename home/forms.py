# -----------------------------------------------------------------------------
# scuba/logbook/forms.py
#
# This is the main class for the migrator.  This will take in a username, and 
# an optional new username.  The result will dictate whether the account can 
# successfully be migrated
#
# (C) Copyright 2013, Divespot.  All rights reserved.
#
# Author: Pauljames "The Juggernaut" Dimitriu
# -----------------------------------------------------------------------------
from pprint import pprint

from django import forms

class HomeLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'login-input', 'style':'width:140px'}), max_length=200)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'login-input', 'style':'width:140px' }))
