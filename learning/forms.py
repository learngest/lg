# -*- encoding: utf-8 -*-

import datetime

from django import forms
from django.utils.translation import ugettext as _

from lg.listes import *

class WorkForm4(forms.Form):
    fichier = forms.FileField(required=False,label=_('File name'))

    def clean_fichier(self):
        if self.cleaned_data['fichier']:
            fichier_ok = False
            # le test devrait se faire sur le content-type
            for suffix in LISTE_ACCEPTED_UPLOAD:
                if self.cleaned_data['fichier'].name.endswith(suffix):
                    fichier_ok = True
                    break
            if not fichier_ok:
                raise forms.ValidationError(_('This filetype is not allowed.'))
                #raise forms.ValidationError('Filetype should be .doc, .xls, .pdf or .zip')
            #filelen = float(len(self.cleaned_data['fichier'].content)) / 1024
            filelen = float(self.cleaned_data['fichier'].size) / 1024
            if filelen > 1024:
                filelen = filelen / 1024
                raise forms.ValidationError(_('Maximum size allowed is 1 Mo, this file is %.2f Mo' % filelen))
                #raise forms.ValidationError(_('Maximum size allowed is 1 Mo'))
        return self.cleaned_data['fichier']

class UtilisateurForm(forms.Form):
    email = forms.EmailField(label=_('Email'))
    newpassword = forms.CharField(max_length=15, min_length=5,
            required=False,
            widget=forms.PasswordInput,
            label=_('New password'),
            )
    newpassword2 = forms.CharField(max_length=15, min_length=5,
            required=False,
            widget=forms.PasswordInput,
            label=_('New password (again)'),
            )
    langue = forms.ChoiceField(choices=LISTE_LANGUES)

    def clean_newpassword2(self):
        if self.cleaned_data['newpassword'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError(_('Please enter the same password twice.'))
        return self.cleaned_data['newpassword2']


