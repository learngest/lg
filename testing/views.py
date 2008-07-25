# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

import os.path
import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from testing.models import Module, Granule, GranuleTitre, Enonce, Question, Reponse
from coaching.models import Utilisateur, Resultat, Valide
from session.views import new_visitor_may_see_granule, has_visitor


def output_exa(question):
    rep = " <input type=\"text\" size=\"15\" name=\"rep%d\" /> " % question.id
    return question.libel.replace("<REPONSE>",rep)

def output_num(question):
    return output_exa(question)

def output_qrm(question):
    import sys
    if sys.version_info[1]==3:
        reponses = '\n'.join(["<br /><input type=\"checkbox\" value=\"%s\" name=\"rep%d\" />&nbsp;%s" \
                            % (r.id, question.id, r) \
                            for r in question.reponse_set.all()])
    else:
        reponses = '\n'.join(["<br /><input type=\"checkbox\" value=\"%s\" name=\"rep%d\" />&nbsp;%s" \
                            % (r.id, question.id, r.valeur) \
                            for r in question.reponse_set.all()])
    hidden = "<br /><input type=\"hidden\" value=\"0\" name=\"rep%d\" />" % question.id
    return '\n'.join((question.libel,hidden,reponses))

def output_qcm(question):
    import sys
    if sys.version_info[1]==3:
        reponses = '\n'.join(["<br /><input type=\"radio\" value=\"%s\" name=\"rep%d\" />&nbsp;%s" \
                            % (r.id, question.id, r) \
                            for r in question.reponse_set.all()])
    else:
        reponses = '\n'.join(["<br /><input type=\"radio\" value=\"%s\" name=\"rep%d\" />&nbsp;%s" \
                            % (r.id, question.id, r.valeur) \
                            for r in question.reponse_set.all()])
    hidden = "<br /><input type=\"hidden\" value=\"0\" name=\"rep%d\" />" % question.id
    return '\n'.join((question.libel,hidden,reponses))

def test(request, slug=None, **kwargs):
    """View: test on granule and module.
    The visitor_may_see_granule decorator checks that the visitor
    is allowed to take this granule test (see Utilisateur.granules_list()
    in coaching.models)

    Returns a test made of n questions, n given in Assess.
    """
    # on a besoin de la langue dans laquelle afficher le contenu
    # elle peut être passée en GET (param l) sinon langue défaut du visiteur
    v = request.session['v']
    langue = request.GET.get('l',request.session['django_language'])
    # caractéristiques de la granule
    try:
        gr = Granule.objects.get(slug=slug)
    except Granule.DoesNotExist:
        HttpResponseRedirect('/home/')
    gt = gr.titre(langue)
    questions = Question.objects.filter(granule=gr).filter(langue=langue).order_by('?')[:gr.nbq]
    msg = None
    if not questions:
        questions = Question.objects.filter(granule=gr).filter(langue='fr').order_by('?')[:gr.nbq]
        msg = _('We are sorry, this content is not available in your preferred language.') 
    enonces = {}
    for q in questions:
        enonces.setdefault(q.enonce.id,{})
        enonces[q.enonce.id]['libel'] = q.enonce.libel
        if not 'questions' in enonces[q.enonce.id]:
            enonces[q.enonce.id]['questions'] = []
        #enonces[q.enonce.id]['questions'].append(getattr(locals(), "output_%s" % q.typq)(q))
        if q.typq == 'qcm':
            enonces[q.enonce.id]['questions'].append(output_qcm(q))
        elif q.typq == 'qrm':
            enonces[q.enonce.id]['questions'].append(output_qrm(q))
        else:
            enonces[q.enonce.id]['questions'].append(output_exa(q))
    return render_to_response('testing/test.html',
                                {'visiteur': v.prenom_nom(),
                                'client': v.groupe.client,
                                'admin': v.status,
                                'titre': gt,
                                'msg': msg,
                                'enonces': enonces.values(),})
test = new_visitor_may_see_granule(test)

def noter(request):
    """View: notes a test.
    """

    def clean(astring, bad=(' ','%')):
        for badchar in bad:
            astring = astring.replace(badchar,'')
        return astring

    if not request.method == 'POST':
        HttpResponseRedirect('/home/')
    max,total = (0,0)
    enonces = {}
    for quest,rep in request.POST.items():
        if not quest.startswith('rep'):
            continue
        try:
            q = Question.objects.get(id=quest.replace('rep',''))
        except Question.DoesNotExist:
            continue
        enonces.setdefault(q.enonce.id,{})
        enonces[q.enonce.id]['libel'] = q.enonce.libel
        if not 'questions' in enonces[q.enonce.id]:
            enonces[q.enonce.id]['questions'] = []
        qd = {}
        qd['libel'] = q.libel.replace("<REPONSE>","...")
        if rep:
            qd['reponse'] = rep
        else:
            qd['reponse'] = _('nothing')
        if q.typq == 'qrm':
            pass
        if q.typq == 'qcm':
            for r in q.reponse_set.all():
                if int(rep) == r.id:
                    total += r.points
                    qd['points'] = r.points
                    qd['reponse'] = r.valeur
                if r.points > 0:
                    max += r.points
            # si pas de réponse
            if not 'points' in qd:
                qd['points'] = 0
                qd['reponse'] = _('nothing')
        if q.typq == 'exa':
            r = q.reponse_set.all()[0]
            max += r.points
            if rep:
                rep = clean(rep).replace(',','.').rstrip('0')
                r.valeur = clean(r.valeur).replace(',','.').rstrip('0')
                if rep == r.valeur:
                    qd['points'] = r.points
                    total += r.points
                else:
                    qd['points'] = '0'
            else:
                qd['points'] = '0'
        if q.typq == 'num':
            r = q.reponse_set.all()[0]
            max += r.points
            # seuls les chiffres avant le séparateur décimal sont significatifs
            rep = rep.replace('%','')
            rep = rep.replace(',','.').strip()
            r.valeur = r.valeur.replace(',','.').strip()
            if rep.startswith(r.valeur.split('.')[0]):
                qd['points'] = r.points
                total += r.points
            else:
                qd['points'] = '0'
        enonces[q.enonce.id]['questions'].append(qd)
    try:
        score = float(total)/max*100
    except ZeroDivisionError:
        score = 0.
    u = request.session['v']
    try:
        g = q.granule
    except UnboundLocalError:
        return HttpResponseRedirect('/home/')
    r = Resultat(utilisateur=u, granule=g, score=score)
    r.save()
    valide = score >= q.granule.score_min
    if valide:
        Valide.objects.get_or_create(utilisateur=u, granule=g, defaults={'score': score})
        mvalide = True
        for gr in g.module.granule_set.all():
            if u.valide_set.filter(granule=gr).count() == 0:
                mvalide = False
                break
        if mvalide:
            Valide.objects.get_or_create(utilisateur=u, module=g.module, defaults={'score': score})
            #if settings.DEBUG: print "enregistrement Valide ok"
    u.lastw = datetime.datetime.now()
    uperfs = u.nperfs()
    u.nb_retards = uperfs[3]
    u.nb_valides = uperfs[0]
    request.session['v'] = u
    u.save()

    return render_to_response('testing/noter.html',
                                {'visiteur': u.prenom_nom(),
                                 'granule': g.slug,
                                'client': u.groupe.client,
                                'vgroupe': u.groupe,
                                'admin': u.status,
                                'total': total,
                                'max': max,
                                'valide': valide,
                                'enonces': enonces.values(),})
noter = has_visitor(noter)


