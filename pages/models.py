# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import datetime
import os
import codecs

from django.conf import settings
from django.db import models

from lg.listes import LISTE_SECTIONS

class Page(models.Model):
    """Référence vers un contenu html.
    """
    slug = models.SlugField(unique=True, db_index=True)
    titre = models.CharField(max_length=255)
    section = models.CharField(max_length=64, choices=LISTE_SECTIONS)
    date = models.DateField()

    class Admin:
        list_display = ('section','titre',)
        list_display_links = ('titre',)
        search_fields = ('titre',)
        list_filter = ('section',)
    
    class Meta:
        ordering = ['section'] 

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return ('lg.pages.views.page_detail', (), {
                'section': self.section,
                'slug': self.slug,
                })
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self):
        if not self.id:
            if not self.date:
                self.date = datetime.datetime.now()
        super(Page, self).save()

    def contenu(self):
        self.path = os.path.join(os.path.dirname(settings.PROJECT_PATH), \
                                    'contents/pages',self.section,'%s.html' % self.slug)
        try:
            contenu = codecs.open(self.path,'r','utf-8').read()
            contenu = contenu.replace('img src="','img src="/contents/pages/%s/' % self.section)
            return contenu
        except IOError:
            if settings.DEBUG:
                return "Unable to open file %s" % self.path
            else:
                return ''

