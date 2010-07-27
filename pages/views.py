# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import os
import codecs
import datetime

from django.conf import settings
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.utils import translation

def page(request, page='home'):
    lang = request.GET.get('lang',None)
    if lang:
        request.session['django_language'] = lang
        translation.activate(lang)
    else:
        lang = translation.get_language()

#    lang = request.GET.get('lang',translation.get_language())
    if not page in settings.PAGES:
        page = 'home'
    path = os.path.join(os.path.dirname(settings.PROJECT_PATH),
                        'contents/pages',lang,'%s.html' % page)
    try:
        contenu = codecs.open(path,'r','utf-8').read()
    except IOError:
        lang = 'en'
        path = os.path.join(os.path.dirname(settings.PROJECT_PATH),
                            'contents/pages',lang,'%s.html' % page)
        try:
            contenu = codecs.open(path,'r','utf-8').read()
        except IOError:
            raise Http404
    
    return render_to_response('pages/page.html',
            {'here': page,
             'contenu': contenu,
             'lang': lang,
             'fr_selected': lang=='fr',
            }) 
