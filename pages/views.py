# -*- encoding: utf-8 -*-

import os
import codecs
import datetime

from django.conf import settings
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.utils import translation

from listes import *

def page(request, page='home'):
    if 'v' in request.session:
        v = request.session['v']
        visiteur = v.prenom_nom()
    else:
        visiteur = None
    langues = [list(i)+[0] for i in LISTE_LANGUES]

    lang = request.GET.get('lang',None)
    if lang:
        request.session['django_language'] = lang
        translation.activate(lang)
    else:
        lang = translation.get_language()
    
    for l in langues:
        if lang==l[0]:
            l[2]=1

    if not page in LISTE_PAGES:
        page = 'home'
    path = os.path.join(settings.LG_CONTENTS_ROOT,
                        'pages',lang,'%s.html' % page)
    try:
        contenu = codecs.open(path,'r','utf-8').read()
    except IOError:
        lang = 'en'
        path = os.path.join(settings.LG_CONTENTS_ROOT,
                            'pages',lang,'%s.html' % page)
        try:
            contenu = codecs.open(path,'r','utf-8').read()
        except IOError:
            raise Http404
    
    return render_to_response('pages/page.html',
            {'here': page,
             'visiteur': visiteur,
             'contenu': contenu,
             'langues': langues,
            }) 
