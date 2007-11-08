# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

from django.utils.translation import ugettext_lazy as _

(ETUDIANT, COACH, ADMINISTRATEUR, STAFF) = range(4)

LISTE_STATUT = (
        'Etudiant',
        'Coach',
        'Administrateur',
        'Staff',
)

LISTE_LANGUES = (
        ('fr', _('French')),
        ('en', _('English')),
#        ('zh-cn', _('Simplified Chinese')),
)

LISTE_TYPES = (
        ('htm', 'HTML'),
        ('swf', 'Flash movie'),
        ('pdf', 'Portable Document Format'),
        ('doc', 'MS Word document'),
        ('xls', 'MS Excel document'),
)

LISTE_TYPQ = (
        ('qcm', 'QCM'),
        ('exa', 'Réponse exacte'),
        ('num', 'Réponse numérique, 5 chiffres significatifs'),
)

LISTE_SECTIONS = (
        ('home', 'Home'),
        ('products', 'Products'),
        ('about', 'About'),
)
