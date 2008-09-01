# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import datetime
from urllib import quote

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import iri_to_uri

from lg.listes import *
from session.forms import LoginForm, LoginOnlyForm
from coaching.models import Utilisateur, Groupe, Work, Log
from learning.models import Cours, Module
from testing.models import Granule

def new_visitor_may_see_granule(view_func):
    """Decorator: tests that view's visitor exists and may take this granule's test.
    """

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        u = request.session['v']
        if not 'slug' in kwargs:
            return HttpResponseRedirect('/home/')
        # les groupes de demo n'ont pas de tests
        if u.groupe.is_demo:
            return HttpResponseRedirect('/home/')
        # test granule demandée existe
        try:
            granule = Granule.objects.get(slug=kwargs['slug'])
        except Granule.DoesNotExist:
            return HttpResponseRedirect('/home/')
        # test granule est dans la liste des granules du visiteur
        # et module est ouvert
        if granule in u.granules_list() and u.module_is_open(granule.module):
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('/home/')
    return _dec

def visitor_may_see_granule(view_func):
    """Decorator: tests that view's visitor exists and may take this granule's test.
    """

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        u = request.session['v']
        if not 'id' in request.GET:
            # pas de granule demandée, redirection vers /home
            return HttpResponseRedirect('/home/')
        id_gran = request.GET['id']
        # les groupes de demo n'ont pas de tests
        if u.groupe.is_demo:
            return HttpResponseRedirect('/home/')
        # test granule id est bien un entier
        try:
            id_gran = int(id_gran)
        except ValueError:
            return HttpResponseRedirect('/home/')
        # test granule demandée existe
        try:
            granule = Granule.objects.get(id=id_gran)
        except Granule.DoesNotExist:
            return HttpResponseRedirect('/home/')
        # test granule est dans la liste des granules du visiteur
        # et module est ouvert
        if granule in u.granules_list() and u.module_is_open(granule.module):
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('/home/')
    return _dec

def visitor_may_see_work(view_func):
    """Decorator: tests that view's visitor exists and may see this assignment."""

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        u = request.session['v']
        # checks that visitor's group course contains this assignment
        if not 'id' in request.GET:
            # pas de travail demandé, redirection vers /home
            return HttpResponseRedirect('/home/')
        id_work = request.GET['id']
        # test asignment id est bien un entier
        try:
            id_work = int(id_work)
        except ValueError:
            return HttpResponseRedirect('/home/')
        # test assignment demandé existe
        try:
            w = Work.objects.get(id=id_work)
        except Work.DoesNotExist:
            return HttpResponseRedirect('/home/')
        # test assignment est dans la liste des travaux à rendre, et non rendu
        if w in u.work_list() and not u.work_done(w):
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('/home/')
    return _dec

def new_visitor_may_see_module(view_func):
    """Decorator: tests that view's visitor exists and may see this module."""

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        u = request.session['v']
        # checks that visitor's group courses contain module
        if not 'slug' in kwargs:
            return HttpResponseRedirect('/home/')
        # test module demandé existe
        try:
            module = Module.objects.get(slug=kwargs['slug'])
        except Module.DoesNotExist:
            return HttpResponseRedirect('/home/')
        # test module est dans la liste des modules du visiteur
        # et module est ouvert
        if module in u.modules_list() and u.module_is_open(module):
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('/home/')
    return _dec

def visitor_may_see_module(view_func):
    """Decorator: tests that view's visitor exists and may see this module."""

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        u = request.session['v']
        # checks that visitor's group courses contain module
        if not 'id' in request.GET:
            # pas de module demandé, redirection vers /home
            return HttpResponseRedirect('/home/')
        id_mod = request.GET['id']
        # test module id est bien un entier
        try:
            id_mod = int(id_mod)
        except ValueError:
            return HttpResponseRedirect('/home/')
        # test module demandé existe
        try:
            module = Module.objects.get(id=id_mod)
        except Module.DoesNotExist:
            return HttpResponseRedirect('/home/')
        # test module est dans la liste des modules du visiteur
        # et module est ouvert
        if module in u.modules_list() and u.module_is_open(module):
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('/home/')
    return _dec

def visitor_is(level=ETUDIANT):
    """Decorator: tests that view's visitor exists and has given level."""

    def _dec(view_func):
        def _check_visitor(request, *args, **kwargs):
            if not 'v' in request.session:
                return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
            u = request.session['v']
            if u.status in (level, STAFF):
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect('/home/')
        return _check_visitor
    return _dec

def visitor_is_at_least(level=ETUDIANT):
    """Decorator: tests that view's visitor exists and has given level."""

    def _dec(view_func):
        def _check_visitor(request, *args, **kwargs):
            if not 'v' in request.session:
                return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
            u = request.session['v']
            if u.status >= level:
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect('/home/')
        return _check_visitor
    return _dec

def visitor_may_see_list(view_func):
    """Decorator: tests that a view's visitor exists and has a given status"""

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        u = request.session['v']
        if u.status in (kwargs['ltyp'], STAFF): 
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('/home/')
    return _dec

def has_visitor(view_func):
    """Decorator: tests that a view's request contains a visitor id."""

    def _dec(request, *args, **kwargs):
        if not 'v' in request.session:
            return HttpResponseRedirect('/login/?next=%s' % quote(request.get_full_path()))
        return view_func(request, *args, **kwargs)
    return _dec

def lost_password(request):
    import sha
    import random
    #from mailer.sender import send_mail
    from lg.utils import send_mail
    if request.method == 'POST':
        f = LoginOnlyForm(request.POST)
        if f.is_valid():
            try:
                u = Utilisateur.objects.get(login=f.cleaned_data['login'])
            except Utilisateur.DoesNotExist:
                msg = _('Bad login. Please try again.')
                return render_to_response('session/lostpw.html',
                        {'form': f,
                         'msg': msg,
                        })
            # build a new password, save it, and send it via email
            newpassword = sha.new(str(random.random())).hexdigest()[:8]
            u.password = newpassword
            u.save(change_password=True)
            fmail = open(settings.MEDIA_ROOT + 'logins/mail_newpass.txt')
            mailmsg = fmail.read()
            mailmsg = mailmsg.decode('iso-8859-1')
            mailmsg = mailmsg % {'nom': u.prenom_nom(),
                                 'password': newpassword,
                                 }
            send_mail(sender='info@learngest.com',
                      recipients=[u.email,'support@learngest.com'],
                      subject='Your login',
                      msg = mailmsg,
                      )
            msg = _('Your new password has just been sent to you. <a href="/">Back to login form</a>.')
            return render_to_response('session/lostpw.html',
                    {'form': f,
                     'msg': msg,
                    })
        else:
            return render_to_response('session/lostpw.html',
                    {'form': f,
                    })
    else:
        f = LoginOnlyForm()
        return render_to_response('session/lostpw.html',
                {'form': f,
                })

def login(request):
    """View: allow a visitor to log in, checking credentials provided.

    Checks cookie support.
    Sets and gets cookie if "remember me on this computer" is set.
    May redirect to a calling view, otherwise sends to /home/."""
    from base64 import encodestring, decodestring
    import datetime
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            f = LoginForm(request.POST)
            msg=''
            if f.is_valid():
                try:
                    u = Utilisateur.objects.get(login=f.cleaned_data['login'])
                except Utilisateur.DoesNotExist:
                    f = LoginForm()
                    msg = _('Bad login. Please try again.')
                    request.session.set_test_cookie()
                    return render_to_response('session/login.html',{'form': f, 'msg': msg})
                # tester mot de passe valide et utilisateur non périmé 
                if u.is_pwd_correct(f.cleaned_data['password']):
                    if u.is_valid():
                        # enregistrer l'heure de login
                        Log.objects.create(utilisateur=u,
                               date = datetime.datetime.now(),
                               path = '/login/',
                               qstring = '')
                        response = HttpResponse()
                        # renseigner les variables de session
                        request.session['v'] = u
                        request.session['django_language'] = u.langue
                        # traiter cookie "remember me"
                        if f.cleaned_data['remember']:
                            cookie_data = encodestring('%s:%s' % (f.cleaned_data['login'], 
                                f.cleaned_data['password']))
                            max_age = 30*24*60*60
                            expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
                            response.set_cookie('eMaster', cookie_data, max_age=max_age, expires=expires)
                        else:
                            # effacer le cookie s'il existe
                            response.delete_cookie('eMaster')
                        # retourner à la vue appelante
                        next = request.REQUEST.get('next','')
                        if next:
                            response.status_code = 302
                            response['Location'] = iri_to_uri(next)
                            return response
                        else:
                            response.status_code = 302
                            response['Location'] = '/home/'
                            return response
                    else:
                        msg = _('Sorry, expired account.')
                else:
                    msg = _('Password error. Please try again.')
            request.session.set_test_cookie()
            return render_to_response('session/login.html',{'form': f, 'msg': msg})
        else:
            msg = _('Your browser does not seem to accept cookies. Please change your settings and try again.')
            return render_to_response('msg.html',{'msg': msg})
    else:
        try:
            del request.session['v']
            del request.session['django_language']
        except KeyError:
            pass
        # recup login cookie s'il existe
        if 'eMaster' in request.COOKIES:
            cookie_data = decodestring(request.COOKIES['eMaster'])
            try:
                l,p = cookie_data.split(':')
            except ValueError:
                l,p = (None,None)
            f = LoginForm({'login': l, 'password': p, 'remember': True})
        else:
            f = LoginForm()
        request.session.set_test_cookie()
        return render_to_response('session/login.html',{'form': f})

def logout(request):
    """View: deletes visitor from session, displays farewell message."""

    try:
        del request.session['v']
        del request.session['django_language']
    except KeyError:
        pass
    msg = _('You have been logged out. Thanks for visiting us today. <br><a href="/login/">New login</a>')
    return render_to_response('msg.html',{'msg': msg})

def home(request):
    """View: selects an entry view suitable for visitor's level."""

    u = request.session['v']
    if u.status >= ADMINISTRATEUR:
        return HttpResponseRedirect('/coaching/')
    else:
        if u.status == COACH:
            return HttpResponseRedirect('/coaching/liste/')
    return HttpResponseRedirect('/learning/tdb/')
home = has_visitor(home) 

