# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class LoginForm(forms.Form):
    login = forms.RegexField(max_length=20,
            regex='[a-z0-9_]+',
            label=_('Login'),
            )
    password = forms.CharField(max_length=15, 
            min_length=5, 
            widget= forms.PasswordInput,
            label=_('Password')
            )
    remember = forms.BooleanField(label=_('Remember me on this computer'), required=False)

class LoginForm2(forms.Form):
    groupe = forms.ChoiceField(label=_('Group'))


class LoginOnlyForm(forms.Form):
    login = forms.RegexField(max_length=20,
            regex='[a-z0-9]+',
            label=_('Login'),
            )

