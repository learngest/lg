# -*- encoding: utf-8 -*-
# vim: set encoding=utf-8 fileencoding=utf-8:

from django import newforms as forms
from django.utils.translation import ugettext_lazy as _

class LoginForm(forms.Form):
    login = forms.RegexField(max_length=20,
            regex='[a-z0-9]+',
            label=_('Login'),
            )
    password = forms.CharField(max_length=15, 
            min_length=5, 
            widget= forms.PasswordInput,
            label=_('Password')
            )
    remember = forms.BooleanField(label=_('Remember me on this computer'), required=False)

class LoginOnlyForm(forms.Form):
    login = forms.RegexField(max_length=20,
            regex='[a-z0-9]+',
            label=_('Login'),
            )

