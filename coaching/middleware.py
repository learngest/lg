# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import datetime

from django.http import HttpResponseRedirect

from coaching.models import Log

class LastMiddleware(object):
    """Renvoie les derniers paramètres GET si ?last=1"""

    def process_request(self,request):
        if 'l' in request.GET and 'v' in request.session:
            try:
                last = Log.objects.filter(utilisateur=request.session['v'],path=request.path).latest('date')
                return HttpResponseRedirect('%s?%s' % (request.path,last.qstring))
            except Log.DoesNotExist:
                return HttpResponseRedirect('%s' % request.path)

class LogMiddleware(object):
    """Enregistre les pages visitées par les utilisateurs"""

    def process_request(self, request):
        if 'v' in request.session:
            for ignore in ('/js','/home','/style','/contents','/img','/favicon',
                            '/welcome','/products','/about'):
                if request.path.startswith(ignore):
                    return
            u = request.session['v']
            try:
                dernierlog = Log.objects.filter(utilisateur=u).latest('date')
                if request.path in ('/','/login/'):
                    # maj le temps passé si nécessaire
                    if dernierlog.path != '/logout/':
                        if dernierlog.path == '/testing/noter/':
                            ajout = 20
                        else:
                            ajout = 10*60
                        if u.tempspasse:
                            u.tempspasse += ajout
                        else:
                            u.tempspasse = ajout
                        request.session['v'] = u
                        u.save()
                    return
                else:
                    temps = datetime.datetime.now() - dernierlog.date
                    if u.tempspasse:
                        u.tempspasse += temps.days*86400 + temps.seconds
                    else:
                        u.tempspasse = temps.days*86400 + temps.seconds
                    request.session['v'] = u
                    u.save()
            except Log.DoesNotExist:
                pass

            Log.objects.create(utilisateur=request.session['v'],
                               date = datetime.datetime.now(),
                               path = request.path,
                               qstring = request.GET.urlencode())

