# -*- encoding: utf-8 -*-

import datetime

from django import forms
from django.utils.translation import ugettext as _

import listes
#from coaching.models import Groupe

class LoginsForm(forms.Form):
    source = forms.FileField(label=_('Source file'))
    groupe = forms.ChoiceField(label=_('Group'))
    langue = forms.ChoiceField(choices=listes.LISTE_LANGUES,label=_('Preferred language'))
    fermeture = forms.DateTimeField(required=False, label=_('Valid till'))
    envoi_mail = forms.ChoiceField(choices=((0,_('No')),(1,_('Yes'))), label=_('Send credentials by mail'))

class UtilisateurForm(forms.Form):
    nom = forms.CharField(max_length=30, label=_('Last name'))
    prenom = forms.CharField(max_length=30, label=_('First name'))
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
    
    fermeture = forms.DateTimeField(required=False, label=_('Valid till'))
    
    langue = forms.ChoiceField(choices=listes.LISTE_LANGUES,label=_('Preferred language'))
    
    groupe_id = forms.ChoiceField(label=_('Group'))

    def clean_newpassword2(self):
        if self.cleaned_data['newpassword'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError(_('Please enter the same password twice.'))
        return self.cleaned_data['newpassword2']

class EcheanceForm1(forms.Form):
    groupe = forms.ChoiceField(label=_('Group'))

class EcheanceForm2(forms.Form):
    utilisateur = forms.ChoiceField(label=_('Student'))
    cours = forms.ChoiceField(label=_('Course'))

class EcheanceForm3(forms.Form):
    module = forms.ChoiceField(label=_('Module'))
    deadline = forms.DateTimeField(label=_('Deadline'),initial=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

class EcheanceForm4(forms.Form):
    deadline = forms.DateTimeField(label=_('Deadline'),initial=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

class WorkForm1(forms.Form):
    groupe = forms.ChoiceField(label=_('Group'))

class WorkForm2(forms.Form):
    cours = forms.ChoiceField(label=_('Course'))

class WorkForm3(forms.Form):
    titre = forms.CharField(max_length=100, label=_('Title'))
    libel = forms.CharField(widget=forms.Textarea,label=_('Description'),required=False)
    fichier = forms.FileField(required=False,label=_('Additional document'))

    def clean_fichier(self):
        if self.cleaned_data['fichier']:
            fichier_ok = False
            # le test devrait se faire sur le content-type
            for suffix in ('.doc','.pdf','.xls','.zip'):
                if self.cleaned_data['fichier'].name.endswith(suffix):
                    fichier_ok = True
                    break
            if not fichier_ok:
                raise forms.ValidationError(_('Filetype should be .doc, .xls, .pdf or .zip'))
            filelen = float(self.cleaned_data['fichier'].size) / 1024
            if filelen > 1024:
                filelen = filelen / 1024
                raise forms.ValidationError(_('Maximum size allowed is 1 Mo, this file is %.2f Mo' % filelen))
        return self.cleaned_data['fichier']

class MailForm(forms.Form):
    subject = forms.CharField(max_length=100, label=_('Subject'))
    content = forms.CharField(widget=forms.Textarea,label=_('Text'),required=False)
