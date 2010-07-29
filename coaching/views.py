# -*- encoding: utf-8 -*-

import datetime
import csv

from urllib import quote

from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import smart_str
from django.core.mail import EmailMessage
from django.views.generic import list_detail
from django.core.urlresolvers import reverse

from session.views import visitor_is, visitor_is_at_least, visitor_may_see_list
from coaching.forms import *
from coaching.models import Client, Utilisateur, Groupe, Echeance, Work, WorkDone, Log, Tempsparmodule
from learning.models import Cours, Module, Contenu, ModuleCours
from testing.models import Granule
from listes import *

def makefilters(params, filtres):
    """Makes dictionnary of filters for list views.
    Takes current request and a dictionnary of filters with
    nom, title, valeurs (dictionnary of id and valeur) as keys.

    Returns one dictionnary per filter, adding to valeurs'keys selected and url."""
    for filtre in filtres:
        newparams = params.copy()
        if filtre['nom'] in params:
            for valeur in filtre['valeurs']:
                if str(valeur['id']) == params[filtre['nom']]:
                    valeur['selected'] = True
                else:
                    valeur['selected'] = False
                newparams[filtre['nom']] = valeur['id']
                valeur['url']  = newparams.urlencode()
            del newparams[filtre['nom']]
            filtre['valeurs'].insert(0, {'id': '_tout', 'libel': _('All'), 'selected': False, 'url': newparams.urlencode()})
        else:
            for valeur in filtre['valeurs']:
                valeur['selected'] = False
                valeur['url'] = params.urlencode() + '&%s=%s' % (filtre['nom'], str(valeur['id']))
            filtre['valeurs'].insert(0, {'id': '_tout', 'libel': _('All'), 'selected': True, 'url': params.urlencode()})
    return filtres

def liste_works(request, **kwargs):
    """View: list of assignments of this administrator's groups or users.

    Filters on group and cours."""

    # préparation des paramètres
    # les clés de ce dictionnaire *doivent* être des chaînes
    params = dict(request.GET.items())
    for key, value in params.items():
        if not isinstance(key, str):
            del params[key]
            params[smart_str(key)] = value
    # u = utilisateur courant
    u = request.session['v']
    # recup de la liste des echéances gérées par cet admin
    le = Work.objects.filter(groupe__in=u.groupes_list())
    # recup de la liste des objets correspondant aux paramètres passés
    le = le.filter(**params)
    for e in le:
        try:
            e.echeance = Echeance.objects.filter(groupe=e.groupe, cours=e.cours).latest('echeance').echeance
        except Echeance.DoesNotExist:
            e.echeance = None
        e.cours.title = e.cours.titre(langue=u.langue)
    # construction des filtres
    lg = {'nom': 'groupe', 'title': _('group'), 'valeurs': [{'id': g.id, 'libel':g.nom} for g in u.groupes_list()]}
    lc = {'nom': 'cours', 'title': _('course'), 'valeurs': [{'id': c.id, 'libel':c.titre(u.langue)} for c in u.cours_list()]}
    lf = [filtre for filtre in [lg,lc] if len(filtre['valeurs'])>1]
    lf = makefilters(request.GET, lf)
    return render_to_response('coaching/liste_work.html',
                            {'visiteur': u.prenom_nom(),
                             'staff': u.status==STAFF,
                             'client': u.groupe.client,
                             'liste_works': le, 
                             'liste_filtres': lf,})
liste_works = visitor_is(ADMINISTRATEUR)(liste_works)

def add_work(request):
    """View: adds an assignment for a groupe/cours.
    """
    # récup visiteur
    v = request.session['v']
    if request.method == 'POST':
        if 'c' in request.POST:
            # dernière étape, recup des valeurs et sauvegarde du devoir à rendre
            g = Groupe.objects.get(id=request.POST['g'])
            c = Cours.objects.get(id=request.POST['c'])
            try:
                e = Echeance.objects.filter(groupe=g, cours=c).latest('echeance').echeance
            except Echeance.DoesNotExist:
                e = None
            f3 = WorkForm3(request.POST, request.FILES)
            if f3.is_valid():
                v.lastw = datetime.datetime.now()
                request.session['v'] = v
                v.save()
                if f3.cleaned_data['fichier']:
                    w = Work(groupe=g, cours=c, 
                            titre = f3.cleaned_data['titre'],
                            libel = f3.cleaned_data['libel'],
                            fichier = f3.cleaned_data['fichier'].name)
                    #w.save()
                    w.fichier.save(f3.cleaned_data['fichier'].name,
                                    request.FILES['fichier'], 
                                    save=True)
                else:
                    w = Work(groupe=g, cours=c, 
                            titre = f3.cleaned_data['titre'],
                            libel = f3.cleaned_data['libel'])
                    w.save()
                if 'save' in request.POST:
                    msg = _('Assignment successfully created. \
                            <a href="/coaching/work/add/" style="font-weight: bold;">Add a new one</a>')
                    return render_to_response('coaching/add_work.html',
                        {'visiteur': v.prenom_nom(),
                         'client': v.groupe.client,
                         'staff': v.status==STAFF,
                         'msg' : msg,
                         'groupe': g, 'cours': c, 'deadline': e,
                         'titre': f3.cleaned_data['titre'],
                         'libel': f3.cleaned_data['libel'],
                         'fichier': f3.cleaned_data['fichier']  })
                else:
                    # save and add a new one
                    return HttpResponseRedirect('/coaching/work/add/')
            else:
                return render_to_response('coaching/add_work.html',
                    {'visiteur': v.prenom_nom(), 
                     'client': v.groupe.client,
                     'staff': v.status==STAFF,
                     'form': f3, 'groupe': g, 'cours': c, 'deadline': e  })
        else:
            if 'g' in request.POST:
                # troisième étape, titre, libellé et fichier éventuel
                g = Groupe.objects.get(id=request.POST['g'])
                f2 = WorkForm2(request.POST)
                f2.fields['cours'].choices = [(c.id, c.titre(v.langue)) for c in g.cours.all()]
                if f2.is_valid():
                    c = Cours.objects.get(id=f2.cleaned_data['cours'])
                    c.title = c.titre(v.langue)
                    try:
                        e = Echeance.objects.filter(groupe=g, cours=c).latest('echeance').echeance
                    except Echeance.DoesNotExist:
                        e = None
                    f3 = WorkForm3()
                    return render_to_response('coaching/add_work.html',
                        {'visiteur': v.prenom_nom(), 
                         'client': v.groupe.client,
                         'staff': v.status==STAFF,
                         'form': f3, 'groupe': g, 'cours': c, 'deadline': e  })
            else:
                # deuxième étape, cours
                f = WorkForm1(request.POST)
                f.fields['groupe'].choices = [(g.id, g.nom) for g in v.groupes_list()]
                if f.is_valid():
                    g = Groupe.objects.get(id=f.cleaned_data['groupe'])
                    f2 = WorkForm2()
                    f2.fields['cours'].choices = [(c.id, c.titre(v.langue)) for c in g.cours.all()]
                    return render_to_response('coaching/add_work.html',
                        {'visiteur': v.prenom_nom(), 
                         'client': v.groupe.client,
                         'staff': v.status==STAFF,
                            'form': f2, 'groupe': g })
    # première étape, groupe
    f = WorkForm1()
    f.fields['groupe'].choices = [(g.id, g.nom) for g in v.groupes_list()]
    return render_to_response('coaching/add_work.html',
        {'visiteur': v.prenom_nom(), 
         'client': v.groupe.client,
         'staff': v.status==STAFF,
        'form': f })
add_work = visitor_is(ADMINISTRATEUR)(add_work) 

def maj_work(request):
    """View: change or delete assignment.
    """
    # récup visiteur
    v = request.session['v']
    if request.method == 'POST':
        if 'trash' in request.POST:
            # effacer l'échéance
            w = Work.objects.get(id=request.GET['id'])
            try:
                w.echeance = Echeance.objects.filter(groupe=w.groupe, cours=w.cours).latest('echeance').echeance
            except Echeance.DoesNotExist:
                w.echeance = None
            w.delete()
            msg = _('This assignment has been deleted. \
            <a href="/coaching/work/manage/?id=%s&undo" style="color: red;">Undo</a>') % w.id
            return render_to_response('coaching/maj_work.html',
                                    {'visiteur': v.prenom_nom(),
                                    'client': v.groupe.client,
                                    'staff': v.status==STAFF,
                                    'msg' : msg,
                                    'deleted': True,
                                    'groupe': w.groupe,
                                    'cours': w.cours,
                                    'echeance': w.echeance,
                                    'titre': w.titre,
                                    'libel': w.libel,
                                    'fichier': w.fichier  })
        else:
            # modifier le travail à faire
            # recup l'original, modifier et sauver
            w = Work.objects.get(id=request.GET['id'])
            f = WorkForm3(request.POST, request.FILES)
            try:
                w.echeance = Echeance.objects.filter(groupe=w.groupe, cours=w.cours).latest('echeance').echeance
            except Echeance.DoesNotExist:
                w.echeance = None
            if f.is_valid():
                if f.cleaned_data['fichier']:
                    w.titre = f.cleaned_data['titre']
                    w.libel = f.cleaned_data['libel']
                    w.fichier = f.cleaned_data['fichier'].name
                    #w.save()
                    w.fichier.save(f.cleaned_data['fichier'].name,
                                    request.FILES['fichier'], 
                                    save=True)
                else:
                    w.titre = f.cleaned_data['titre']
                    w.libel = f.cleaned_data['libel']
                    w.save()
                msg = _('Assignment successfully saved.')
            else:
                msg = None
            return render_to_response('coaching/maj_work.html',
                                    {'visiteur': v.prenom_nom(),
                                    'client': v.groupe.client,
                                    'staff': v.status==STAFF,
                                    'msg' : msg,
                                    'form': f,
                                    'groupe': w.groupe,
                                    'cours': w.cours,
                                    'echeance': w.echeance,
                                    'titre': w.titre,
                                    'libel': w.libel,
                                    'fichier': w.fichier  })
            
    # première étape, afficher le travail à faire ou annuler le delete
    if 'undo' in request.GET:
        try:
            e = Work.trash.get(id=request.GET['id'])
        except Work.DoesNotExist:
            return HttpResponseRedirect('/coaching/work/')
        e.restore()
        msg = _('Assignment successfully restored.')
    else:
        msg = None
    try:
        e = Work.objects.get(id=request.GET['id']) 
    except Work.DoesNotExist:
        return HttpResponseRedirect('/coaching/work/')
    try:
        e.echeance = Echeance.objects.filter(groupe=e.groupe, cours=e.cours).latest('echeance').echeance
    except Echeance.DoesNotExist:
        e.echeance = None
    f = WorkForm3(e.__dict__)
    return render_to_response('coaching/maj_work.html',
                            {'visiteur': v.prenom_nom(),
                            'client': v.groupe.client,
                            'staff': v.status==STAFF,
                            'msg' : msg,
                            'form': f,
                            'groupe': e.groupe,
                            'cours': e.cours,
                            'echeance': e.echeance,
                            'fichier': e.fichier,
                             })
maj_work = visitor_is(ADMINISTRATEUR)(maj_work) 

def liste_echeances(request, **kwargs):
    """View: list of echeances of this administrator's groups or users.

    Filters on group and cours."""

    # préparation des paramètres
    # les clés de ce dictionnaire *doivent* être des chaînes
    params = dict(request.GET.items())
    for key, value in params.items():
        if not isinstance(key, str):
            del params[key]
            params[smart_str(key)] = value
    # u = utilisateur courant
    u = request.session['v']
    # recup de la liste des echéances gérées par cet admin
    le = Echeance.objects.filter(groupe__in=u.groupes_list())
    # recup de la liste des objets correspondant aux paramètres passés
    le = le.filter(**params)
    # construction des filtres
    lg = {'nom': 'groupe', 'title': _('group'), 'valeurs': [{'id': g.id, 'libel':g.nom} for g in u.groupes_list()]}
    lc = {'nom': 'cours', 'title': _('course'), 'valeurs': [{'id': c.id, 'libel':c.titre(u.langue)} for c in u.cours_list()]}
    lf = [filtre for filtre in [lg,lc] if len(filtre['valeurs'])>1]
    lf = makefilters(request.GET, lf)
    return render_to_response('coaching/liste_echeance.html',
            {'visiteur': u.prenom_nom(),
             'staff': u.status==STAFF,
             'client': u.groupe.client,
             'liste_echeances': le, 'liste_filtres': lf,})
liste_echeances = visitor_is(ADMINISTRATEUR)(liste_echeances)

def add_echeance(request):
    """View: adds a deadline for user/group and course/module.
    """
    # récup visiteur
    v = request.session['v']
    if request.method == 'POST':
        if 'c' in request.POST:
            # dernière étape, recup des valeurs et sauvegarde de l'échéance
            g = Groupe.objects.get(id=request.POST['g'])
            uf = {}
            if request.POST['u'] == "0":
                u = None
                uf['id'], uf['nom_prenom'] = (0, _('== All Students =='))
            else:
                u = Utilisateur.objects.get(id=request.POST['u'])
                uf['id'], uf['nom_prenom'] = (u.id, u.nom_prenom())
            c = Cours.objects.get(id=request.POST['c'])
            c.title = c.titre(v.langue)
            f3 = EcheanceForm3(request.POST)
            lm = [(0, _('== All Modules =='))]
            lm.extend([(mc.module.id, mc.module.slug) for mc in c.modulecours_set.all()])
            f3.fields['module'].choices = lm
            if f3.is_valid():
                v.lastw = datetime.datetime.now()
                request.session['v'] = v
                v.save()
                if f3.cleaned_data['module'] == "0":
                    m = None
                    mf = {}
                    mf['id'], mf['slug'] = (0, _('== All Modules =='))
                else:
                    m = Module.objects.get(id=f3.cleaned_data['module'])
                    mf = m
                e = Echeance(groupe=g,utilisateur=u,cours=c,module=m,
                        echeance=f3.cleaned_data['deadline'])
                e.save()
#                Echeance.objects.create(groupe=g,utilisateur=u,cours=c,module=m,
#                                        echeance=f3.cleaned_data['deadline'])
                if 'save' in request.POST:
                    msg = _('Deadline successfully created. \
                            <a href="/coaching/echeance/add/" style="font-weight: bold;">Add a new one</a>')
                    return render_to_response('coaching/add_echeance.html',
                            {'visiteur': v.prenom_nom(),
                            'client': v.groupe.client,
                            'staff': v.status==STAFF,
                            'msg' : msg,
                            'groupe': g, 'utilisateur': uf, 'cours': c, 'module': mf, 
                            'deadline': f3.cleaned_data['deadline']  })
                else:
                    # save and add a new one
                    return HttpResponseRedirect('/coaching/echeance/add/')
            else:
                return render_to_response('coaching/add_echeance.html',
                        {'visiteur': v.prenom_nom(),
                         'staff': v.status==STAFF,
                         'client': v.groupe.client,
                         'form': f3, 'groupe': g, 'utilisateur': uf, 'cours': c })
        else:
            if 'g' in request.POST:
                # troisième étape, module et echéance
                g = Groupe.objects.get(id=request.POST['g'])
                f2 = EcheanceForm2(request.POST)
                lu = [(0, _('== All Students =='))]
                lu.extend([(u.id, u.nom_prenom()) for u in g.utilisateur_set.all()])
                f2.fields['utilisateur'].choices = lu
                f2.fields['cours'].choices = [(c.id, c.titre(v.langue)) for c in g.cours.all()]
                u = {}
                if f2.is_valid():
                    if f2.cleaned_data['utilisateur'] == "0":
                        u['id'], u['nom_prenom'] = (0, _('== All Students =='))
                    else:
                        ut = Utilisateur.objects.get(id=f2.cleaned_data['utilisateur'])
                        u['id'], u['nom_prenom'] = (ut.id, ut.nom_prenom())
                    c = Cours.objects.get(id=f2.cleaned_data['cours'])
                    c.title = c.titre(v.langue)
                    f3 = EcheanceForm3()
                    lm = [(0, _('== All Modules =='))]
                    lm.extend([(mc.module.id, mc.module.slug) for mc in c.modulecours_set.all()])
                    f3.fields['module'].choices = lm
                    return render_to_response('coaching/add_echeance.html',
                            {'visiteur': v.prenom_nom(), 
                             'client': v.groupe.client,
                            'staff': v.status==STAFF,
                            'form': f3, 'groupe': g, 'utilisateur': u, 'cours': c  })
            else:
                # deuxième étape, utilisateur et cours
                f = EcheanceForm1(request.POST)
                f.fields['groupe'].choices = [(g.id, g.nom) for g in v.groupes_list()]
                if f.is_valid():
                    g = Groupe.objects.get(id=f.cleaned_data['groupe'])
                    f2 = EcheanceForm2()
                    lu = [(0, _('== All Students =='))]
                    lu.extend([(u.id, u.nom_prenom()) for u in g.utilisateur_set.all()])
                    f2.fields['utilisateur'].choices = lu
                    f2.fields['cours'].choices = [(c.id, c.titre(v.langue)) for c in g.cours.all()]
                    return render_to_response('coaching/add_echeance.html',
                            {'visiteur': v.prenom_nom(), 
                             'client': v.groupe.client,
                            'staff': v.status==STAFF,
                            'form': f2, 'groupe': g })
    # première étape, groupe
    f = EcheanceForm1()
    f.fields['groupe'].choices = [(g.id, g.nom) for g in v.groupes_list()]
    return render_to_response('coaching/add_echeance.html',
            {'visiteur': v.prenom_nom(), 
             'client': v.groupe.client,
             'staff': v.status==STAFF,
             'form': f })
add_echeance = visitor_is(ADMINISTRATEUR)(add_echeance) 

def maj_echeance(request):
    """View: updates or deletes a deadline for user/group and course/module.
    """
    # récup visiteur
    v = request.session['v']
    if request.method == 'POST':
        if 'trash' in request.POST:
            # effacer l'échéance
            e = Echeance.objects.get(id=request.GET['id'])
            e.delete()
            msg = _('This deadline has been deleted. \
            <a href="/coaching/echeance/manage/?id=%s&undo" style="color: red;">Undo</a>') % e.id
            if e.utilisateur:
                u = e.utilisateur
            else:
                u = {}
                u['nom_prenom'] = _('== All Students ==')
            if e.module:
                m = e.module
            else:
                m = {}
                m['slug'] = _('== All Modules ==')
            return render_to_response('coaching/maj_echeance.html',
                                    {'visiteur': v.prenom_nom(),
                                    'client': v.groupe.client,
                                    'staff': v.status==STAFF,
                                    'msg' : msg,
                                    'groupe': e.groupe, 'utilisateur': u,
                                    'cours': e.cours, 'module': m,
                                    'echeance': e.echeance,
                                     })
        else:
            # modifier l'échéance
            # recup l'echeance originale, modifier la date et re-sauver
            e = Echeance.objects.get(id=request.GET['id'])
            f = EcheanceForm4(request.POST)
            if e.utilisateur:
                u = e.utilisateur
            else:
                u = {}
                u['nom_prenom'] = _('== All Students ==')
            if e.module:
                m = e.module
            else:
                m = {}
                m['slug'] = _('== All Modules ==')
            if f.is_valid():
                e.echeance = f.cleaned_data['deadline']
                e.save()
                msg = _('Deadline successfully saved.')
            else:
                msg = None
            return render_to_response('coaching/maj_echeance.html',
                                    {'visiteur': v.prenom_nom(),
                                    'client': v.groupe.client,
                                    'staff': v.status==STAFF,
                                    'msg' : msg,
                                    'form': f,
                                    'groupe': e.groupe, 'utilisateur': u,
                                    'cours': e.cours, 'module': m,
                                     })
            
    # première étape, afficher l'échéance ou annuler le delete
    if 'undo' in request.GET:
        try:
            e = Echeance.trash.get(id=request.GET['id'])
        except Echeance.DoesNotExist:
            return HttpResponseRedirect('/coaching/echeance/')
        e.restore()     
        msg = _('Deadline successfully restored.')
    else:
        msg = None
    try:
        e = Echeance.objects.get(id=request.GET['id']) 
    except Echeance.DoesNotExist:
        return HttpResponseRedirect('/coaching/echeance/')
    f = EcheanceForm4({ 'deadline' : e.echeance})
    if e.utilisateur:
        u = e.utilisateur
    else:
        u = {}
        u['nom_prenom'] = _('== All Students ==')
    if e.module:
        m = e.module
    else:
        m = {}
        m['slug'] = _('== All Modules ==')
    return render_to_response('coaching/maj_echeance.html',
                            {'visiteur': v.prenom_nom(),
                            'client': v.groupe.client,
                            'staff': v.status==STAFF,
                            'msg' : msg,
                            'form': f,
                            'groupe': e.groupe, 'utilisateur': u,
                            'cours': e.cours, 'module': m,
                             })
maj_echeance = visitor_is(ADMINISTRATEUR)(maj_echeance) 

def log_utilisateur(request):
    """View: log des visites d'un utilisateur
    """
    # récup visiteur
    v = request.session['v']
    try:
        u = Utilisateur.objects.get(id=request.GET['id'])
    except Utilisateur.DoesNotExist:
        return HttpResponseRedirect(reverse('v_home'))
    if not u.groupe in v.groupes_list():
        return HttpResponseRedirect(reverse('v_home'))
    logs = Log.objects.filter(utilisateur=u)[:50]
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    return render_to_response('coaching/log.html',
            {'visiteur': v.prenom_nom(),
             'client': v.groupe.client,
             'staff': v.status==STAFF,
             'u' : u,
             'logs': logs }) 
log_utilisateur = visitor_is_at_least(COACH)(log_utilisateur)

def logs(request):
    """View: log des visites
    """
    # récup visiteur
    v = request.session['v']
    us = Utilisateur.objects.filter(groupe__in=v.groupes_list())
    logs = Log.objects.filter(utilisateur__in=us)
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    return list_detail.object_list(
            request,
            queryset=logs,
            paginate_by= 23,
            allow_empty= True,
            extra_context = {
                'visiteur': v.prenom_nom(),
                'staff': v.status==STAFF,
                },
            )
logs = visitor_is(ADMINISTRATEUR)(logs)

def detail_module(request):
    # récup visiteur
    v = request.session['v']
    # utilisateur
    uid = request.GET['id']
    try:
        u = Utilisateur.objects.get(id=uid)
    except Utilisateur.DoesNotExist:
        HttpResponseRedirect(reverse('v_home'))
    # module demandé
    id_mod = request.GET['mid']
    try:
        m = Module.objects.get(id=id_mod)
    except Module.DoesNotExist:
        HttpResponseRedirect(reverse('v_home'))
    # recup cours auquel le module appartient
    id_cours = request.GET['cid']
    try:
        c = Cours.objects.get(id=id_cours)
    except Cours.DoesNotExist:
        HttpResponseRedirect(reverse('v_home'))
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
    for typ in [l[0] for l in LISTE_TYPES]:
        try:
            d = m.contenu_set.get(type=typ,langue=u.langue)
        except Contenu.DoesNotExist:
            try:
                d = m.contenu_set.get(type=typ,langue='fr')
            except Contenu.DoesNotExist:
                continue
        d.img = "/media/img/%s.png" % d.type
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
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    return render_to_response('coaching/detail_module.html',
            {'visiteur': v.prenom_nom(),
             'client': v.groupe.client,
             'staff': v.status==STAFF,
             'vgroupe': v.groupe,
             'u': u,
             'module': m }) 
detail_module = visitor_is_at_least(COACH)(detail_module)

def detail_utilisateur(request):
    """View: détails du travail d'un utilisateur
    """
    # récup visiteur
    v = request.session['v']
    try:
        u = Utilisateur.objects.get(id=request.GET['id'])
    except Utilisateur.DoesNotExist:
        return HttpResponseRedirect(reverse('v_home'))
    if not u.groupe in v.groupes_list():
        return HttpResponseRedirect(reverse('v_home'))
    # récup des dossiers rendus
    import os.path
    u.zfichier = ''.join(('g%d' % u.groupe.id,'-', 
                        u.login,
                        '.zip'))
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT,'workdone',u.zfichier)):
            u.zfichier = None
    # récup des cours
    # FIXME changer pour n'avoir que les cours du coach si v est un coach
    les_cours = u.cours_list()
    for c in les_cours:
        c.title = c.titre(langue=v.langue)
        c.modules = []
        for m in [mc.module for mc in c.modulecours_set.all()]:
            m.title = m.titre(langue=v.langue)
            m.url = "/coaching/detail/module/?id=%s&mid=%s&cid=%s" % (u.id, m.id, c.id)
            m.essais = 0
            for t in m.granule_set.all():
                m.essais += u.nb_essais(t)
            if u.echeance(c,m):
                m.echeance = u.echeance(c,m).echeance
                m.retard = m.echeance < datetime.datetime.now() and not u.module_is_valide(m)
                if m.retard:
                    m.problem = _('Late')
            else:
                m.echeance = ''
            if u.module_is_valide(m):
                m.progress = u.date_validation_module(m)
                if m.echeance and m.echeance < m.progress:
                    m.problem = _('Completed late')
            else:
                if m.granule_set.count() > 0:
                    m.progress = "%d / %d" % (u.nb_granules_valides(m),m.granule_set.count())
            c.modules.append(m)
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
                #w.url = ''.join(('/upload/',wd.get_fichier_url()))
                #w.url = wd.get_fichier_url()
                w.url = wd.fichier.url
                if w.echeance:
                    w.retard = w.echeance < w.rendu_le
            except WorkDone.DoesNotExist:
                #module_prec_valide = False
                w.rendu_le = False
                w.url = '/learning/devoir/?id=%s' % w.id 
                if w.echeance:
                    w.retard = w.echeance < datetime.datetime.now()
            c.devoirs.append(w)
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    return render_to_response('coaching/detail.html',
            {'visiteur': v.prenom_nom(),
             'client': v.groupe.client,
             'staff': v.status==STAFF,
             'admin': v.status>COACH,
             'u' : u,
             'les_cours': les_cours }) 
detail_utilisateur = visitor_is_at_least(COACH)(detail_utilisateur)

def profile_utilisateur_admin(request, utilisateur=None):
    """View: user's record for administrator.

    Administrator may update some fields :
    - group
    - first name
    - last name
    - email
    - valid till date
    - language
    """
    # récup visiteur
    v = request.session['v']
    # test visiteur est admin du groupe de cet utilisateur
    try:
        u = Utilisateur.objects.get(login=utilisateur)
    except Utilisateur.DoesNotExist:
        return HttpResponseRedirect(reverse('v_home'))
    if not u.groupe in v.groupes_list():
        return HttpResponseRedirect(reverse('v_home'))
    if request.method == 'POST':
        f = UtilisateurForm(request.POST)
        f.fields['groupe_id'].choices = [(g.id,g.nom) for g in v.groupes_list()]
        if f.is_valid():
            v.lastw = datetime.datetime.now()
            request.session['v'] = v
            v.save()
            u.groupe_id = f.cleaned_data['groupe_id']
            u.nom = f.cleaned_data['nom']
            u.prenom = f.cleaned_data['prenom']
            u.email = f.cleaned_data['email']
            u.fermeture = f.cleaned_data['fermeture']
            u.langue = f.cleaned_data['langue']
            request.session['django_language'] = u.langue
            if f.cleaned_data['newpassword2']:
                u.password = f.cleaned_data['newpassword2']
                u.save(change_password=True)
            else:
                u.save(change_password=False)
            msg = _('%s changed successfully.') % u.login
            return render_to_response('coaching/fiche.html',
                {'visiteur': v.prenom_nom(), 
                'client': v.groupe.client,
                'u': u, 
                'form': f, 'msg': msg})
        else:
            return render_to_response('coaching/fiche.html',
                {'visiteur': v.prenom_nom(), 
                 'client': v.groupe.client,
                 'u': u, 'form': f})
    else:
        f = UtilisateurForm(u.__dict__)
        f.fields['groupe_id'].choices = [(g.id,g.nom) for g in v.groupes_list()]
        return render_to_response('coaching/fiche.html',
                {'visiteur': v.prenom_nom(), 
                 'client': v.groupe.client,
                 'u': u, 'form': f})
profile_utilisateur_admin = visitor_is(ADMINISTRATEUR)(profile_utilisateur_admin)

def liste_utilisateurs(request, **kwargs):
    """ View: list of users coached or administered by visitor.

    Returns a table of :
    - group
    - login
    - last name
    - first name
    - language
    and other fields related to status of visitor (admin or coach).
    Sortable on any field(s), filters on group and language."""

    # v = utilisateur courant, on récupère les groupes coachés
    v = request.session['v']
    # préparation des paramètres
    # les clés de ce dictionnaire *doivent* être des chaînes
    params = dict(request.GET.items())
    for key, value in params.items():
        if not isinstance(key, str):
            del params[key]
            params[smart_str(key)] = value
    # recup de la liste des utilisateurs gérés par cet admin
    lu = Utilisateur.objects.filter(groupe__in=v.groupes_list())
    # recup de la liste des objets correspondant aux paramètres passés
    lu = lu.filter(**params)
    # construction des filtres
    lg = {'nom': 'groupe', 'title': _('group'), 'valeurs': [{'id': g.id, 'libel':g.nom} for g in v.groupes_list()]}
    ll = {'nom': 'langue', 'title': _('language'), 'valeurs': [{'id': l[0], 'libel':l[1]} for l in LISTE_LANGUES]}
    lf = [filtre for filtre in [lg,ll] if len(filtre['valeurs'])>1]
    lf = makefilters(request.GET, lf)
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    if 'groupe' in params and not 'langue' in params:
        gid = Groupe.objects.get(id=params['groupe'])
    else:
        gid = None
    return render_to_response('coaching/liste_admin.html',
            {'visiteur': v.prenom_nom(),
             'client': v.groupe.client,
             'staff': v.status==STAFF,
             'gid': gid,
             'liste_utilisateurs': lu, 'liste_filtres': lf,})
liste_utilisateurs = visitor_may_see_list(liste_utilisateurs)

def liste_clients(request):
    """View: stats by client for staff

    Returns a table of:
    - client
    - group
    - # of courses for this group
    - # of modules in this group courses
    - # of logins for this client-group
    - # of users who worked yesterday
    """
    v = request.session['v']
    # préparation des paramètres
    # les clés de ce dictionnaire *doivent* être des chaînes
    params = dict(request.GET.items())
    for key, value in params.items():
        if not isinstance(key, str):
            del params[key]
            params[smart_str(key)] = value
    # recup de la liste des utilisateurs gérés par cet admin
    clients = Client.objects.all()
    # recup de la liste des objets correspondant aux paramètres passés
    lc = clients.filter(**params)
    # construction des filtres
    lg = {'nom': 'id', 'title': _('client'), 'valeurs': [{'id': c.id, 'libel':c.nom} for c in clients]}
    lf = [filtre for filtre in [lg] if len(filtre['valeurs'])>1]
    lf = makefilters(request.GET, lf)
    # construction de la liste
    liste = []
    for client in lc:
        for groupe in client.groupe_set.all():
            groupe.nb_cours = groupe.cours.count()
            groupe.nb_modules = 0
            for c in groupe.cours.all():
                groupe.nb_modules += ModuleCours.objects.filter(cours=c).count()
            groupe.nb_logins = groupe.utilisateur_set.count()
            auj = datetime.date.today()
            hier = auj - datetime.timedelta(1)
            groupe.hier = groupe.utilisateur_set.filter(lastw__gte=hier,lastw__lt=auj).count()
            liste.append(groupe)
    v.lastw = datetime.datetime.now()
    request.session['v'] = v
    v.save()
    return render_to_response('coaching/liste_clients.html',
            {'visiteur': v.prenom_nom(),
             'client': v.groupe.client,
             'liste_filtres': lf,
             'staff': v.status==STAFF,
             'liste_groupes': liste,
            })
liste_clients = visitor_is(STAFF)(liste_clients)

def create_logins(request):
    """Creation de logins à partir d'un fichier csv.
    """
    import os
    import time
    import StringIO
    import unicodedata
    import random
    import sha
    #from mailer.sender import send_mail
    from utils import send_mail
    v = request.session['v']
    if request.method == 'POST':
        if 'fsource' in request.POST:
            g = Groupe.objects.get(id=request.POST['groupe'])
            logins = []
            fich_logins = '/logins/logins-g%s-%s.csv'% (g.id, time.strftime('%Y%m%d%H%M%S',time.localtime()))
            fich_erreurs = '/logins/erreurs-g%s-%s.csv'% (g.id, time.strftime('%Y%m%d%H%M%S',time.localtime()))
            nom_logins = settings.MEDIA_ROOT + fich_logins
            nom_erreurs = settings.MEDIA_ROOT + fich_erreurs
            flogin = open(nom_logins,'w')
            ferreur = open(nom_erreurs,'w')
            for line in open(request.POST['fsource']):
                line = line.strip()
                line = line.decode('iso-8859-1')
                nom, prenom, email = line.split('\t')
                nom = nom.title()
                prenom = prenom.title()
#                login = prenom[:2] + nom
#                login = unicodedata.normalize('NFKD',login).encode('ASCII','ignore').lower()
#                i = login.rfind(' ')
#                if i > 5:
#                    login = login[0:i]
#                login = login.replace(' ','')
#                i = login.rfind('-')
#                if i > 5:
#                    login = login[0:i]
#                login = login.replace('-','')
                login = email.split('@')[0][:20]
                login = unicodedata.normalize('NFKD',login).encode('ASCII','ignore').lower()
                login = login.replace(' ','')
                password = sha.new(str(random.random())).hexdigest()[:8]
                try:
                    Utilisateur.objects.get(login=login)
                    saved = False
                    status = ugettext('Exists already.')
                except Utilisateur.DoesNotExist:
                    u = Utilisateur(login=login, nom=nom, prenom=prenom, 
                                    password = password,
                                    email=email, fermeture=request.POST['fermeture'], 
                                    langue=request.POST['langue'], groupe=g)
                    u.save(change_password=True)
                    saved= True
                    status = ugettext('Saved.')
                if request.POST['envoi_mail']=='1' and saved:
                    try:
#                        fmail = open(settings.MEDIA_ROOT + 'logins/mail_login.txt')
#                        mailmsg = fmail.read()
#                        mailmsg = mailmsg.decode('iso-8859-1')
#                        mailmsg = mailmsg % {'login': u.login, 
#                                             'password': password,
#                                             'groupe': g.nom,
#                                             'coach': g.administrateur.prenom_nom(),
#                                             'coach_mail': g.administrateur.email,
#                                             }
                        mailmsg = render_to_string('mail_login.txt', 
                                {'login': u.login, 
                                  'password': password,
                                  'here': 'admin',
                                  'groupe': g.nom,
                                  'coach': g.administrateur.prenom_nom(),
                                  'coach_mail': g.administrateur.email,})
                        send_mail(sender='info@learngest.com',
                                  recipients=[u.email],
                                  subject='E-learning - %s' % g.client.nom,
                                  msg = mailmsg,
                                  )
                        status = ' '.join((status,ugettext('Mail sent.')))
                    except IOError:
                        status = ' '.join((status,ugettext('Mail error.')))
                    #fmail.close()
                if saved:
                    #newline = '\t'.join((nom,prenom,email,login,password,'\n'))
                    newline = ';'.join((nom,prenom,email,login,password,'\n'))
                    newline = newline.encode('iso-8859-1')
                    flogin.write(newline)
                else:
                    newline = ';'.join((nom,prenom,email,login,'\n'))
                    newline = newline.encode('iso-8859-1')
                    ferreur.write(newline)
                logins.append({'login':login, 'password': password, 
                                'nom':nom,'prenom':prenom,'email':email,
                                'status': status,
                                })
            flogin.close()
            ferreur.close()
            v.lastw = datetime.datetime.now()
            request.session['v'] = v
            v.save()
            return render_to_response('coaching/logins3.html',
                                {'visiteur': v.prenom_nom(),
                                 'client': v.groupe.client,
                                 'logins': logins,
                                 'staff': v.status==STAFF,
                                 'groupe': g,
                                 'langue': request.POST['langue'],
                                 'fermeture': request.POST['fermeture'],
                                 'envoi_mail': int(request.POST['envoi_mail']),
                                 'fsource': nom_logins,
                                 'usource': fich_logins,
                                })

        else:
            f = LoginsForm(request.POST, request.FILES)
            f.fields['groupe'].choices = [(g.id, g.nom) for g in Groupe.objects.all()]
            if f.is_valid():
                g = Groupe.objects.get(id=f.cleaned_data['groupe'])
                start_now = False
                logins = []
                nom_source = settings.MEDIA_ROOT + '/logins/source-g%s-%s.txt'\
                        % (g.id, time.strftime('%Y%m%d%H%M%S',time.localtime()))
                fsource = open(nom_source, 'w')
                for line in StringIO.StringIO(request.FILES['source'].read()):
                    if line.startswith('Nom\t'):
                        start_now = True
                        continue
                    if start_now:
                        line = line.decode('iso-8859-1').strip()
                        if not line:
                            continue
                        try:
                            nom, prenom, email = line.split('\t')
                        except ValueError:
                            errmsg = 'Invalid file content : %s' % line
                            fsource.close()
                            os.unlink(nom_source)
                            return render_to_response('coaching/logins.html',
                                                    {'visiteur': v.prenom_nom(),
                                                     'client': v.groupe.client,
                                                     'staff': v.status==STAFF,
                                                     'errmsg': errmsg,
                                                     'form': f,
                                                    })
                        nom = nom.title()
                        prenom = prenom.title()
                        email = email.lower()
                        logins.append({'nom':nom,'prenom':prenom,'email':email})
                        line = line.encode('iso-8859-1')
                        fsource.write(line)
                        fsource.write('\n')
                fsource.close()
                return render_to_response('coaching/logins2.html',
                                    {'visiteur': v.prenom_nom(),
                                     'client': v.groupe.client,
                                     'logins': logins,
                                     'staff': v.status==STAFF,
                                     'groupe': g,
                                     'langue': f.cleaned_data['langue'],
                                     'fermeture': f.cleaned_data['fermeture'],
                                     'envoi_mail': int(f.cleaned_data['envoi_mail']),
                                     'fsource': nom_source,
                                    })
            else:
                return render_to_response('coaching/logins.html',
                                        {'visiteur': v.prenom_nom(),
                                         'staff': v.status==STAFF,
                                         'client': v.groupe.client,
                                         'form': f,
                                        })
    else:
        f = LoginsForm()
        f.fields['groupe'].choices = [(g.id, g.nom) for g in Groupe.objects.all()]
        return render_to_response('coaching/logins.html',
                                {'visiteur': v.prenom_nom(),
                                 'staff': v.status==STAFF,
                                 'client': v.groupe.client,
                                 'form': f,
                                })
create_logins = visitor_is(STAFF)(create_logins)

def menu(request):
    """View: displays administrator's menu.
    """
    # v = utilisateur courant
    v = request.session['v']
    return render_to_response('coaching/menu.html',
            {'visiteur': v.prenom_nom(), 
             'client': v.groupe.client,
             'here': 'admin',
             'admin': v.status,
             'staff': v.status==STAFF })
menu = visitor_is(ADMINISTRATEUR)(menu)

def send_email(request):
    """View: sends an email to user or group.
    """
    #from mailer.sender import send_mail
    #from utils import send_mail
    v = request.session['v']
    if 'id' in request.GET:
        # verif v est coach du groupe des id
        for id in request.GET.getlist('id'):
            try:
                u = Utilisateur.objects.get(pk=id)
            except Utilisateur.DoesNotExist:
                return HttpResponseRedirect('/coaching/')
            if not u.groupe in v.groupes_list():
                return HttpResponseRedirect('/coaching/')
    else:
        if 'gid' in request.GET:
            try:
                g = Groupe.objects.get(pk=request.GET['gid'])
            except Groupe.DoesNotExist:
                return HttpResponseRedirect('/coaching/')
            if not g in v.groupes_list():
                return HttpResponseRedirect('/coaching/')
    if 'gid' in request.GET:
        dest_list = [u.prenom_nom() for u in g.utilisateur_set.all()]
        email_list = [u.email for u in g.utilisateur_set.all()]
        u = None
    else:
        dest_list = []
        email_list = []
        g = None
        for id in request.GET.getlist('id'):
            u = Utilisateur.objects.get(pk=id)
            dest_list.append(u.prenom_nom())
            email_list.append(u.email)
    if request.method == 'POST':
        f = MailForm(request.POST)
        if f.is_valid():
            mail = EmailMessage(subject=f.cleaned_data['subject'],
                    body=f.cleaned_data['content'],
                    from_email='%s <profs@learngest.com>' % v.prenom_nom(),
                    to=email_list,
                    headers={'Reply-To': v.email})
            mail.send()
#            send_mail(sender=v.email,
#                      recipients=email_list,
#                      subject=f.cleaned_data['subject'],
#                      msg = f.cleaned_data['content'],
#                      )
            msg = _('The message has been sent.')
            return render_to_response('coaching/sendmail.html',
                                        {'visiteur': v.prenom_nom(),
                                         'msg': msg,
                                         'staff': v.status==STAFF,
                                         'from': v.email,
                                         'gid': g,
                                         'uid': u,
                                         'dest_list': dest_list,
                                         'subject': f.cleaned_data['subject'],
                                         'content': f.cleaned_data['content'],
                                        })
        else:
            return render_to_response('coaching/sendmail.html',
                                        {'visiteur': v.prenom_nom(),
                                         'from': v.email,
                                         'staff': v.status==STAFF,
                                         'dest_list': dest_list,
                                         'form': f,
                                         'gid': g,
                                         'uid': u,
                                        })
    else:
        f = MailForm()
        return render_to_response('coaching/sendmail.html',
                                    {'visiteur': v.prenom_nom(),
                                     'from': v.email,
                                     'staff': v.status==STAFF,
                                     'dest_list': dest_list,
                                     'form': f,
                                     'gid': g,
                                     'uid': u,
                                    })
send_email = visitor_is_at_least(COACH)(send_email)

def liste_csv(request):
    v = request.session['v']
    if not 'gid' in request.GET:
        return HttpResponseRedirect('/coaching/')
    else:
        try:
            g = Groupe.objects.get(pk=request.GET['gid'])
        except Groupe.DoesNotExist:
            return HttpResponseRedirect('/coaching/')
        if not g in v.groupes_list():
            return HttpResponseRedirect('/coaching/')
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=groupe%s.csv' % request.GET['gid']
        writer = csv.writer(response,delimiter=';')
        writer.writerow([s.encode("iso-8859-1") for s in [ugettext('Last Name'),
                        ugettext('First Name'),
                        ugettext('Login'),
                        ugettext('Email'),
                        ugettext('Last Work'),
                        ugettext('Time Spent'),
                        ugettext('Modules'),
                        ugettext('Validated'),
                        ugettext('Validated Late'),
                        ugettext('Currently Late'),]])
        for u in g.utilisateur_set.all():
            ligne = [s.encode("iso-8859-1") for s in [u.nom, 
                        u.prenom, 
                        u.login, 
                        u.email]]
            ligne.extend(( u.lastw, 
                        u.time_elapsed(), 
                        u.nb_modules, 
                        u.nb_valides, 
                        u.nb_retards, 
                        u.nb_actuel))
            writer.writerow(ligne)
        return response
liste_csv = visitor_is_at_least(COACH)(liste_csv)

def sanitize_temps(start, end):
    temps = end - start
    secondes = temps.days * 86400 + temps.seconds
    if secondes > 14400:
        secondes = 600
    return secondes

def old_time_csv(request):
    def prettyprint(secs):
        return "%02i:%02i:%02i" % (
                int(secs / 3600), 
                int((secs % 3600) / 60), 
                secs%60) 

    v = request.session['v']
    if not 'gid' in request.GET:
        return HttpResponseRedirect('/coaching/')
    else:
        try:
            g = Groupe.objects.get(pk=request.GET['gid'])
        except Groupe.DoesNotExist:
            return HttpResponseRedirect('/coaching/')
        if not g in v.groupes_list():
            return HttpResponseRedirect('/coaching/')
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=temps-g%s.csv' % request.GET['gid']
        writer = csv.writer(response,delimiter=';')
        modules = g.modules_list()

        ligne = [s.encode("iso-8859-1") for s in [ugettext('Last Name'),
                        ugettext('First Name'),
                        ugettext('Login'),
                        ugettext('Email'),]]
        for module in modules:
            ligne.append(module.titre(langue=v.langue).encode("iso-8859-1"))
        writer.writerow(ligne)

        for u in g.utilisateur_set.all():
            logs = Log.objects.filter(utilisateur=u).order_by('date')
            u.timespent = {}
            curmod = None
            testing = False
            for log in logs:
                if curmod:
                    if testing:
                        testing = False
                        if '/noter/' in log.path:
                            secondes = sanitize_temps(curtime, log.date)
                            u.timespent[curmod] = u.timespent.get(curmod,0) \
                                    + secondes
                    else:
                        if log.path in ('/','/login/'):
                            secondes = 600
                        else:
                            secondes = sanitize_temps(curtime, log.date)
                            u.timespent[curmod] = u.timespent.get(curmod,0) \
                                    + secondes
                    curmod = None
                if '/learning/' in log.path:
                    parts = log.path.split('/')
                    try:
                        curmod = parts[3]
                    except IndexError:
                        continue
                    if curmod:
                        curtime = log.date
                    else:
                        continue
                else:
                    if '/testing/' in log.path:
                        testing = True
                        parts = log.path.split('/')
                        granslug = parts[2]
                        try:
                            granule = Granule.objects.get(slug=granslug)
                        except Granule.DoesNotExist:
                            continue
                        curmod = granule.module.slug
                        curtime = log.date
                    else:
                        continue

            ligne = [s.encode("iso-8859-1") for s in [u.nom, 
                        u.prenom, 
                        u.login, 
                        u.email]]

            for module in modules:
                ligne.append(prettyprint(u.timespent.get(module.slug,0)))

            writer.writerow(ligne)

        return response
old_time_csv = visitor_is_at_least(COACH)(old_time_csv)

def time_csv(request):
    def prettyprint(secs):
        return "%02i:%02i:%02i" % (
                int(secs / 3600), 
                int((secs % 3600) / 60), 
                secs%60) 

    v = request.session['v']
    if not 'gid' in request.GET:
        return HttpResponseRedirect('/coaching/')
    else:
        try:
            g = Groupe.objects.get(pk=request.GET['gid'])
        except Groupe.DoesNotExist:
            return HttpResponseRedirect('/coaching/')
        if not g in v.groupes_list():
            return HttpResponseRedirect('/coaching/')
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=temps-g%s.csv' % request.GET['gid']
        writer = csv.writer(response,delimiter=';')
        modules = g.modules_list()

        ligne = [s.encode("iso-8859-1") for s in [ugettext('Last Name'),
                        ugettext('First Name'),
                        ugettext('Login'),
                        ugettext('Email'),]]
        for module in modules:
            ligne.append(module.titre(langue=v.langue).encode("iso-8859-1"))
        writer.writerow(ligne)

        for u in g.utilisateur_set.all():

            ligne = [s.encode("iso-8859-1") for s in [u.nom, 
                        u.prenom, 
                        u.login, 
                        u.email]]

            for module in modules:
                try:
                    temps = Tempsparmodule.objects.get(
                            utilisateur = u,
                            module = module)
                    tempspasse = temps.tempspasse
                except Tempsparmodule.DoesNotExist:
                    tempspasse = 0
                ligne.append(prettyprint(tempspasse))

            writer.writerow(ligne)

        return response
time_csv = visitor_is_at_least(COACH)(time_csv)
