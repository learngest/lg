# -*- encoding: utf-8 -*-

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
        ('zh-cn', _('Simplified Chinese')),
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
        ('qrm', 'QRM'),
        ('rnd', 'Question à valeurs aléatoires'),
        ('exa', 'Réponse exacte'),
        ('num', 'Réponse numérique, 5 chiffres significatifs'),
)

LISTE_PAGES = ('home', 'news', 'demo', 'overview', 'contributors', 'legal',)

LISTE_ACCEPTED_UPLOAD = ('.doc','.docx','.odt','.sxw',
                         '.pdf',
                         '.xls','.xlsx','.ods','.sxc',
                         '.zip')
