# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import os
#import os.path
import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaulttags import include_is_allowed

import listes
from learning.models import Cours, Module, Contenu, ModuleTitre
from learning.forms import WorkForm4, UtilisateurForm
from coaching.models import Utilisateur, Echeance, Work, WorkDone, Log
from session.views import visitor_may_see_module, visitor_may_see_work, has_visitor, new_visitor_may_see_module

def profile(request):
    # récup visiteur
    v = request.session['v']
    if request.method == 'POST':
        f = UtilisateurForm(request.POST)
        if f.is_valid():
            v.email = f.cleaned_data['email']
            v.langue = f.cleaned_data['langue']
            request.session['django_language'] = v.langue
            if f.cleaned_data['newpassword2']:
                v.password = f.cleaned_data['newpassword2']
                v.save(change_password=True)
            else:
                v.save(change_password=False)
            request.session['v'] = v
            msg = _('%s changed successfully.') % v.login
            return render_to_response('learning/profile.html',
                {'visiteur': v.prenom_nom(), 
                 'admin': v.statut(),
                'v': v, 
                'form': f, 'msg': msg})
        else:
            return render_to_response('learning/profile.html',
                {'visiteur': v.prenom_nom(), 
                 'admin': v.statut(),
                 'client': v.groupe.client,
                'v': v, 'form': f})
    else:
        f = UtilisateurForm(v.__dict__)
        return render_to_response('learning/profile.html',
                {'visiteur': v.prenom_nom(), 
                 'admin': v.statut(),
                 'client': v.groupe.client,
                'v': v,
                'form': f,
                })
profile = has_visitor(profile)

def devoir(request):
    """View: assignment and form to upload when work is done."""
    # récup visiteur
    u = request.session['v']
    # récup devoir
    try:
        w = Work.objects.get(id=request.GET['id'])
    except Work.DoesNotExist:
        HttpResponseRedirect('/home/')
    w.url = w.get_fichier_url()
    if w.fichier:
        w.fichier = os.path.basename(w.fichier)
    if request.method == 'POST':
        # devoir rendu, sauvegarder
        f = WorkForm4(request.POST, request.FILES)
        if f.is_valid():
            if f.cleaned_data['fichier']:
                import sha
                import zipfile
                fichier = ''.join(('g%d-' % u.groupe.id,
                                    u.login,'-',
                                    datetime.datetime.now().strftime('%Y%m%d-%H%M%S'),
                                    os.path.splitext(f.cleaned_data['fichier'].filename)[1]))
                fichier = fichier.encode('iso-8859-1')
                content = f.cleaned_data['fichier'].content
                signature = sha.new(content).hexdigest()
                date = datetime.datetime.now()
                # try: si le devoir existe, pas de sauvegarde.
                try:
                    wd = WorkDone.objects.get(utilisateur=u, work=w)
                except WorkDone.DoesNotExist:
                    wd = WorkDone(utilisateur=u, work=w, date=date, fichier=fichier, signature=signature)
                    wd.save()
                    wd.save_fichier_file(fichier, content)
                    # groupe-cours zipfile
                    zfichier = ''.join(('g%d' % u.groupe.id,'-', 
                                        w.cours.slug,
                                        '.zip'))
                    try:
                        zf = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT,'workdone',zfichier),
                                        'a',zipfile.ZIP_DEFLATED)
                    except IOError:
                        zf = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT,'workdone',zfichier),
                                        'w',zipfile.ZIP_DEFLATED)
                    zf.write(os.path.join(settings.MEDIA_ROOT,'workdone',fichier))
                    zf.close()
                    # login zipfile
                    zfichier = ''.join(('g%d' % u.groupe.id,'-', 
                                        u.login,
                                        '.zip'))
                    try:
                        zf = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT,'workdone',zfichier),
                                        'a',zipfile.ZIP_DEFLATED)
                    except IOError:
                        zf = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT,'workdone',zfichier),
                                        'w',zipfile.ZIP_DEFLATED)
                    zf.write(os.path.join(settings.MEDIA_ROOT,'workdone',fichier))
                    zf.close()
                    return render_to_response('learning/devoir.html',
                            {'visiteur': u.prenom_nom(),
                             'client': u.groupe.client,
                             'vgroupe': u.groupe,
                             'admin': u.statut(),
                             'devoir': w,
                             'fichier': fichier,
                             'signature': signature,
                             })
            return render_to_response('learning/devoir.html',
                        {'visiteur': u.prenom_nom(),
                         'client': u.groupe.client,
                        'admin': u.statut(),
                        'form': f,
                        'devoir': w }) 
    else:
        # afficher toutes les caractéristiques du devoir
        # et le formulaire pour le rendre
        f = WorkForm4() 
    return render_to_response('learning/devoir.html',
            {'visiteur': u.prenom_nom(),
             'client': u.groupe.client,
            'admin': u.statut(),
            'form': f,
            'devoir': w }) 
devoir = visitor_may_see_work(devoir)

def module(request, slug=None):
    """View: return user's dashboard for given module"""
    # récup visiteur
    u = request.session['v']
    # module demandé
    #try:
    #    m = Module.objects.get(slug=slug)
    #except Module.DoesNotExist:
    #    HttpResponseRedirect('/tdb/')
    m = get_object_or_404(Module, slug=slug)
    # recup cours auquel le module appartient
    id_cours = request.GET['cid']
    try:
        c = Cours.objects.get(id=id_cours)
    except Cours.DoesNotExist:
        HttpResponseRedirect('/tdb/')
    m.title = m.titre(langue=u.langue)
    m.valide = u.module_is_valide(m)
    if u.echeance(c,m):
        m.echeance = u.echeance(c,m).echeance
        if m.valide:
            m.datev = u.valide_set.get(module=m).date
            m.retard = m.echeance < m.datev
        else:
            m.retard = m.echeance < datetime.datetime.now()
    else:
        m.echeance = ''
        m.retard = False
        if m.valide:
            m.datev = u.valide_set.get(module=m).date
    m.docs = []
    for typ in [l[0] for l in listes.LISTE_TYPES]:
        try:
            d = m.contenu_set.get(type=typ,langue=u.langue)
        except Contenu.DoesNotExist:
            try:
                d = m.contenu_set.get(type=typ,langue='fr')
            except Contenu.DoesNotExist:
                continue
        d.img = "/media/img/%s.gif" % d.type
        if d.type in ('htm','swf'):
            d.nbconsult, d.lastconsult = u.stats_contenu(d)
        m.docs.append(d)
    m.tests = []
    if not u.groupe.is_demo:
        for t in m.granule_set.all():
            t.title = t.titre(langue=u.langue)
            t.nbtries = u.nb_essais(t)
            t.lastdate, t.lastscore = u.last_score(t)
            t.bestdate, t.bestscore = u.best_score(t)
            t.validdate, t.validscore = u.valid_score(t)
            m.tests.append(t)
    return render_to_response('learning/module.html',
            {'visiteur': u.prenom_nom(),
             'client': u.groupe.client,
             'vgroupe': u.groupe,
             'admin': u.statut(),
             'module': m }) 
module = new_visitor_may_see_module(module)

def tdb(request):
    """View: returns user's dashboard."""
    # récup visiteur
    u = request.session['v']
    # récup des cours du visiteur
    les_cours = u.cours_list()
    tout_ouvert = (u.groupe.is_open or u.statut() > 0)
    module_prec_valide = True
    for c in les_cours:
        c.title = c.titre(langue=u.langue)
        c.modules = []
        for m in [mc.module for mc in c.modulecours_set.all()]:
            m.ouvert = tout_ouvert or module_prec_valide
            m.title = m.titre(langue=u.langue)
            m.url = "/learning/module/%s/?cid=%s" % (m.slug, c.id)
            if u.echeance(c,m):
                m.echeance = u.echeance(c,m).echeance
                m.retard = m.echeance < datetime.datetime.now() and not u.module_is_valide(m)
            else:
                m.echeance = ''
            if m.ouvert:
                if m.granule_set.count() > 0:
                    m.progress = "%d / %d" % (u.nb_granules_valides(m),m.granule_set.count())
                m.docs = []
                for typ in [l[0] for l in listes.LISTE_TYPES]:
                    try:
                        d = m.contenu_set.get(type=typ,langue=u.langue)
                    except Contenu.DoesNotExist:
                        try:
                            d = m.contenu_set.get(type=typ,langue='fr')
                        except Contenu.DoesNotExist:
                            continue
                    d.img = "/media/img/%s.gif" % d.type
                    m.docs.append(d)

                if not u.groupe.is_demo:
                    ct = u.current_test(m)
                    if ct:
                        m.curtest = ct.titre(u.langue)
                        m.curtestid = ct.slug
            c.modules.append(m)
            # module est validé si :
            # - le précédent est validé et celui-ci n'a pas de test
            # - OU il a été validé
            # ET
            # - le cours précédent est validé s'il existe (voir ci-dessous, devoirs)
            module_prec_valide = (module_prec_valide and m.granule_set.count()==0) \
                                or u.module_is_valide(m)
        c.devoirs = []
        for w in Work.objects.filter(groupe=u.groupe, cours= c):
            try:
                w.echeance = Echeance.objects.filter(utilisateur=u, cours=c)\
                            .latest('echeance').echeance
            except Echeance.DoesNotExist:
                try:
                    w.echeance = Echeance.objects.filter(groupe=u.groupe, utilisateur__isnull=True, cours=c)\
                                .latest('echeance').echeance
                except Echeance.DoesNotExist:
                    w.echeance = None
            # devoir rendu par cet utilisateur ?
            try:
                wd = WorkDone.objects.get(utilisateur=u, work=w)
                w.rendu_le = wd.date
                w.signature = wd.signature
                if w.echeance:
                    w.retard = w.echeance < w.rendu_le
            except WorkDone.DoesNotExist:
                module_prec_valide = False
                w.rendu_le = False
                w.url = '/learning/devoir/?id=%s' % w.id 
                if w.echeance:
                    w.retard = w.echeance < datetime.datetime.now()
            w.open = u.cours_is_open(c)
            c.devoirs.append(w)

    return render_to_response('learning/tdb.html',
            {'visiteur': u.prenom_nom(),
             'client': u.groupe.client,
             'prenom': u.prenom,
             'vgroupe': u.groupe,
             'admin': u.statut(),
             'test': not u.groupe.is_demo,
             'les_cours': les_cours }) 
tdb = has_visitor(tdb)

def help_support(request, slug=None):
    """View: html help content.

    Returns the html content embedded in user's template.
    """
    # on a besoin de la langue dans laquelle afficher le contenu
    # elle peut être passée en GET (param l) sinon langue défaut du visiteur
    # calcul du nom absolu du fichier à rendre
    # si aucun contenu type 'htm' trouvé pour ce module, redirection /home/
    # sinon, recherche d'un contenu dans la langue demandée
    # s'il n'existe pas, recherche d'un contenu en français
    if not slug:
        HttpResponseRedirect('/tdb/')
    v = request.session['v']
    langue = request.GET.get('l',request.session['django_language'])
    #try:
    #    m = Module.objects.get(slug=slug)
    #except Module.DoesNotExist:
    #    HttpResponseRedirect('/tdb/')
    m = get_object_or_404(Module, slug=slug)
    lc = Contenu.objects.filter(module=m,type='htm')
    if not lc:
        HttpResponseRedirect('/tdb/')
    try:
        c = lc.get(langue=langue)
        msg = None
    except Contenu.DoesNotExist:
        try:
            c = lc.get(langue='fr')
            msg = _('We are sorry, this content is not available in your preferred language.') 
        except Contenu.DoesNotExist:
            HttpResponseRedirect('/tdb/')
    except AssertionError:
        c = lc[0]
    base = ''
    if 'HTTP_X_FORWARDED_HOST' in request.META:
        base =''.join(('http://',request.META['HTTP_X_FORWARDED_HOST']))
    else:
        if 'HTTP_REFERER' in request.META:
            base = '/'.join(request.META['HTTP_REFERER'].split('/')[:3])
        else:
            HttpResponseRedirect('/home/')
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    support_path = os.path.join(os.path.dirname(settings.PROJECT_PATH), \
                                'contents',c.module.slug,c.langue,c.ressource)
    base = os.path.join(base,'contents',c.module.slug,c.langue,c.ressource)
    if not include_is_allowed(support_path):
        HttpResponseRedirect('/tdb/')
    try:
        support = open(support_path).read()
    except IOError:
        if settings.DEBUG:
            support = "Unable to open file %s" % support_path
        else:
            support = ''
    return render_to_response('learning/support.html',
                                {'visiteur': v.prenom_nom(),
                                 'client': v.groupe.client,
                                 'vgroupe': v.groupe,
                                 'admin': v.statut(),
                                 'baselink': base,
                                 'msg': msg,
                                 'support': support})
help_support = has_visitor(help_support)

def support(request, slug=None, **kwargs):
    """View: html course content.
    The new_visitor_may_see_module decorator checks that:
    - the module is part of at least one course the visitor's
      group is subscribed to

    Returns the html content embedded in user's template.
    """
    # on a besoin de la langue dans laquelle afficher le contenu
    # elle peut être passée en GET (param l) sinon langue défaut du visiteur
    # calcul du nom absolu du fichier à rendre
    # si aucun contenu type 'htm' trouvé pour ce module, redirection /home/
    # sinon, recherche d'un contenu dans la langue demandée
    # s'il n'existe pas, recherche d'un contenu en français
    if not slug:
        HttpResponseRedirect('/tdb/')
    v = request.session['v']
    ltyp = kwargs['ltyp']
    langue = request.GET.get('l',request.session['django_language'])
    #try:
    #    m = Module.objects.get(slug=slug)
    #except Module.DoesNotExist:
    #    HttpResponseRedirect('/tdb/')
    m = get_object_or_404(Module, slug=slug)
    lc = Contenu.objects.filter(module=m,type=ltyp)
    if not lc:
        HttpResponseRedirect('/tdb/')
    try:
        c = lc.get(langue=langue)
        msg = None
    except Contenu.DoesNotExist:
        try:
            c = lc.get(langue='fr')
            msg = _('We are sorry, this content is not available in your preferred language.') 
        except Contenu.DoesNotExist:
            HttpResponseRedirect('/tdb/')
    except AssertionError:
        c = lc[0]
    #base = ''.join(('http://',request.META['HTTP_HOST']))
    base = ''
    if 'HTTP_X_FORWARDED_HOST' in request.META:
        base =''.join(('http://',request.META['HTTP_X_FORWARDED_HOST']))
    else:
        if 'HTTP_REFERER' in request.META:
            base = '/'.join(request.META['HTTP_REFERER'].split('/')[:3])
        else:
            HttpResponseRedirect('/home/')
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    if ltyp == 'htm':
        support_path = os.path.join(os.path.dirname(settings.PROJECT_PATH), \
                                    'contents',c.module.slug,c.langue,c.ressource)
        base = os.path.join(base,'contents',c.module.slug,c.langue,c.ressource)
        if not include_is_allowed(support_path):
            HttpResponseRedirect('/tdb/')
        try:
            support = open(support_path).read()
        except IOError:
            if settings.DEBUG:
                support = "Unable to open file %s" % support_path
            else:
                support = ''
        return render_to_response('learning/support.html',
                                    {'visiteur': v.prenom_nom(),
                                     'client': v.groupe.client,
                                     'vgroupe': v.groupe,
                                     'admin': v.statut(),
                                     'baselink': base,
                                     'msg': msg,
                                     'support': support})
    else:
        support = os.path.join('/contents',c.module.slug,c.langue,'flash',c.ressource)
        base = os.path.join(base,'contents',c.module.slug,c.langue,'flash',c.ressource)
        return render_to_response('learning/anim.html',
                                    {'visiteur': v.prenom_nom(),
                                     'client': v.groupe.client,
                                     'vgroupe': v.groupe,
                                     'admin': v.statut(),
                                     'baselink': base,
                                     'msg': msg,
                                     'support': support})
support = new_visitor_may_see_module(support)

