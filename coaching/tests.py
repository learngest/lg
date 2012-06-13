# -*- encoding: utf-8 -*-

"""
Tests du module coaching.

import de tous les modèles
>>> from lg.coaching.models import *
>>> from lg.learning.models import *
>>> from lg.testing.models import Granule

création d'un Client
les champs style et contact sont facultatifs
>>> client = Client.objects.create(nom="University")
>>> print client
University

création d'un Groupe pour le client
pour le moment, ce groupe n'a ni administrateur, ni cours
>>> groupe = Groupe.objects.create(nom="Students", client=client)
>>> print groupe
Students

si le groupe est demo, il est forcément open
>>> groupe.is_demo = True
>>> groupe.save()
>>> groupe.is_open
True
>>> groupe.is_demo = False
>>> groupe.is_open = False
>>> groupe.save()
>>> groupe.is_open
False

création d'un Utilisateur du groupe
cet utilisateur a le statut ETUDIANT
>>> u = Utilisateur(login='juser', password='juser', nom='User', prenom='John', email='juser@university.edu', langue='fr', groupe=groupe)
>>> u.save()

le mot de passe a été chiffré même si on ne l'a pas demandé car cet utilisateur n'existait pas
>>> print len(u.password)
46

changement du mot de passe, mais on ne demande pas sa sauvegarde,
l'ancien mot de passe doit être conservé
>>> oldpass = u.password
>>> u.password = 'toto'
>>> u.save()
>>> u.password == oldpass
True

si on demande la sauvegarde du mot de passe, il est modifé
>>> u.password = 'secret'
>>> u.save(change_password=True)
>>> u.password == oldpass
False

pas de date de fermeture, donc toujours valide
>>> u.is_valid()
True
>>> u.fermeture = datetime.datetime(2006, 1, 1, 0, 0, 0)
>>> u.is_valid()
False
>>> u.fermeture = None
>>> u.is_valid()
True

le statut est étudiant car :
 - il n'est pas staff
 - il n'est pas administrateur d'un Groupe
 - il n'est pas coach d'un GroupeCours
>>> u.statut()
0

création de cours, le groupe de l'utilisateur sera inscrit aux deux premiers
mais pas au troisième
>>> cours_un = Cours.objects.create(titre="Premier cours", rang=10)
>>> cours_deux = Cours.objects.create(titre="Deuxieme cours", rang=20)
>>> autre_cours = Cours.objects.create(titre="Autre cours", rang=10)

inscription du groupe aux cours
>>> groupe.cours = (cours_un, cours_deux,)
>>> groupe.save()

creation de modules
>>> module_un = Module.objects.create(slug='module-un')
>>> module_deux = Module.objects.create(slug='module-deux')
>>> module_trois = Module.objects.create(slug='module-trois')
>>> module_quatre = Module.objects.create(slug='module-quatre')
>>> module_cinq = Module.objects.create(slug='module-cinq')

ajout de modules aux cours
>>> ModuleCours.objects.create(cours=cours_un, module=module_un, rang=10)
<ModuleCours: Premier cours - module-un - 10>
>>> ModuleCours.objects.create(cours=cours_un, module=module_deux, rang=20)
<ModuleCours: Premier cours - module-deux - 20>
>>> ModuleCours.objects.create(cours=cours_deux, module=module_trois, rang=10)
<ModuleCours: Deuxieme cours - module-trois - 10>
>>> ModuleCours.objects.create(cours=cours_deux, module=module_quatre, rang=20)
<ModuleCours: Deuxieme cours - module-quatre - 20>
>>> ModuleCours.objects.create(cours=autre_cours, module=module_quatre, rang=10)
<ModuleCours: Autre cours - module-quatre - 10>
>>> ModuleCours.objects.create(cours=autre_cours, module=module_un, rang=30)
<ModuleCours: Autre cours - module-un - 30>

creation de granules
>>> granule10 = Granule.objects.create(slug='granule-10', module=module_un, nbq=6, score_min=80, rang=10)
>>> granule20 = Granule.objects.create(slug='granule-20', module=module_deux, nbq=6, score_min=80, rang=10)
>>> granule21 = Granule.objects.create(slug='granule-21', module=module_deux, nbq=6, score_min=80, rang=20)
>>> granule30 = Granule.objects.create(slug='granule-30', module=module_trois, nbq=6, score_min=80, rang=10)

=======================================
 Test des méthodes de Utilisateur
=======================================

>>> u.cours_list()
[<Cours: Premier cours>, <Cours: Deuxieme cours>]
>>> u.modules_list()
[<Module: module-un>, <Module: module-deux>, <Module: module-trois>, <Module: module-quatre>]
>>> u.granules_list()
[<Granule: granule-10>, <Granule: granule-20>, <Granule: granule-21>, <Granule: granule-30>]

creation de resultats sans validation pour le moment
le time.sleep() est nécessaire pour que les dates soient
différentes car l'unité est la seconde dans la base
>>> import time
>>> r = Resultat(utilisateur=u, granule=granule10, score=55)
>>> r.save()
>>> print r.score
55
>>> time.sleep(1)
>>> r = Resultat(utilisateur=u, granule=granule10, score=22)
>>> r.save()
>>> time.sleep(1)
>>> r = Resultat(utilisateur=u, granule=granule10, score=17)
>>> r.save()
>>> u.last_score(granule10)[1]
17
>>> print u.nb_essais(granule10)
3
>>> print u.nb_essais(granule20)                      
0
>>> print u.last_score(granule20)
('', 0)
>>> print u.best_score(granule10)[1]
55
>>> print u.best_score(granule20)   
('', 0)
>>> print u.valid_score(granule10)   
('', 0)
>>> print u.nb_granules_valides(module_un)
0
>>> print u.module_is_valide(module_un)
False
>>> u.cours_du_module(module_un)
<Cours: Premier cours>
>>> u.cours_du_module(module_quatre)
<Cours: Deuxieme cours>
>>> u.cours_du_module(module_cinq)
>>> print u.module_precedent(module_un)
None
>>> u.module_precedent(module_deux)
<Module: module-un>
>>> u.module_precedent(module_trois)
>>> u.module_precedent(module_quatre)
<Module: module-trois>
>>> u.cours_precedent(module_deux)
>>> u.cours_precedent(module_cinq)
>>> u.cours_precedent(module_trois)
<Cours: Premier cours>

rien n'est validé, seul le premier module du premier cours et ses granules
sont accessibles
>>> u.cours_is_valide(cours_un)
False
>>> u.cours_is_valide(cours_deux)
False
>>> u.module_is_open(module_un)
True
>>> u.module_is_open(module_deux)
False
>>> u.module_is_open(module_trois)
False
>>> u.module_is_open(module_quatre)
False

Un module auquel l'utilisateur n'est pas inscrit ne peut pas être ouvert
>>> u.module_is_open(module_cinq)
False

validation de la granule du premier module
>>> Resultat.objects.create(utilisateur=u, granule=granule10, score=85) # doctests: +ELLIPSIS
<Resultat: juser - granule-10 - ... - 85>
>>> Valide.objects.create(utilisateur=u, granule=granule10, score=85) # doctests: +ELLIPSIS
<Valide: juser - G : granule-10 - ... - 85>
>>> Valide.objects.create(utilisateur=u, module=module_un, score=85) # doctests: +ELLIPSIS
<Valide: juser - M : module-un - ... - 85>
>>> u.nb_essais(granule10)
4L
>>> u.nb_essais(granule20)
0L
>>> u.best_score(granule10)[1]
85L
>>> u.valid_score(granule10)[1]
85L
>>> u.valid_score(granule20)[1]
0
>>> u.nb_granules_valides(module_un)
1L
>>> u.nb_granules_valides(module_deux)
0L
>>> u.module_is_valide(module_un)
True
>>> u.module_is_valide(module_deux)
False
>>> u.module_is_valide(module_cinq)
False

le premier module est validé, donc le second est ouvert
le premier reste ouvert, les autres sont fermés
>>> u.module_is_open(module_un)
True
>>> u.module_is_open(module_deux)
True
>>> u.module_is_open(module_trois)
False
>>> u.module_is_open(module_quatre)
False
>>> u.module_is_open(module_cinq)
False

validation du deuxième module
>>> Resultat.objects.create(utilisateur=u, granule=granule20, score=82) # doctests: +ELLIPSIS
<Resultat: juser - granule-20 - ... - 82>
>>> Valide.objects.create(utilisateur=u, granule=granule20, score=82) # doctests: +ELLIPSIS
<Valide: juser - G : granule-20 - ... - 82>
>>> time.sleep(1)
>>> Resultat.objects.create(utilisateur=u, granule=granule21, score=100) # doctests: +ELLIPSIS
<Resultat: juser - granule-21 - ... - 100>
>>> Valide.objects.create(utilisateur=u, granule=granule21, score=100) # doctests: +ELLIPSIS
<Valide: juser - G : granule-21 - ... - 100>
>>> Valide.objects.create(utilisateur=u, module=module_deux, score=100) # doctests: +ELLIPSIS
<Valide: juser - M : module-deux - ... - 100>
>>> u.valid_score(granule21)[1]
100L

le deuxième module est validé, donc le premier cours est validé
et le premier module du deuxième cours (module trois) est ouvert
>>> u.nb_granules_valides(module_deux)
2L
>>> u.module_is_valide(module_un)
True
>>> u.module_is_valide(module_deux)
True
>>> u.module_is_valide(module_cinq)
False
>>> u.cours_is_valide(cours_un)
True
>>> u.cours_is_valide(cours_deux)
False
>>> u.module_is_open(module_un)
True
>>> u.module_is_open(module_deux)
True
>>> u.module_is_open(module_trois)
True
>>> u.module_is_open(module_quatre)
False
>>> u.module_is_open(module_cinq)
False

current_test
si le module est ouvert et validé, dernier test travaillé
si module ouvert et non validé, premier test non validé
sinon rien
>>> u.current_test(module_un)
<Granule: granule-10>
>>> u.current_test(module_deux)
<Granule: granule-21>
>>> u.current_test(module_trois)
<Granule: granule-30>
>>> u.current_test(module_quatre)
>>> u.current_test(module_cinq)

creation et tests d'échéances
echeance pour le groupe de cet utilisateur sur un cours
>>> Echeance.objects.create(echeance=datetime.datetime(2007, 9, 30),groupe=u.groupe,cours=cours_un)
<Echeance: Students - Premier cours - 2007-09-30 00:00:00>
>>> u.echeance(cours_un,module_un)
<Echeance: Students - Premier cours - 2007-09-30 00:00:00>
>>> u.echeance(cours_un,module_deux)
<Echeance: Students - Premier cours - 2007-09-30 00:00:00>
>>> u.echeance(cours_deux,module_trois)

echeance pour cet utilisateur sur un cours
>>> Echeance.objects.create(echeance=datetime.datetime(2007, 10, 1),utilisateur=u,cours=cours_un)
<Echeance: juser - Premier cours - 2007-10-01 00:00:00>
>>> u.echeance(cours_un,module_un)
<Echeance: juser - Premier cours - 2007-10-01 00:00:00>
>>> u.echeance(cours_un,module_deux)
<Echeance: juser - Premier cours - 2007-10-01 00:00:00>

echeance pour le groupe de cet utilisateur sur un module
>>> Echeance.objects.create(echeance=datetime.datetime(2007, 10, 31),groupe=u.groupe,module=module_trois)
<Echeance: Students - module-trois - 2007-10-31 00:00:00>
>>> u.echeance(cours_deux,module_trois)
<Echeance: Students - module-trois - 2007-10-31 00:00:00>
>>> u.echeance(cours_deux,module_quatre)

echeance pour cet utilisateur sur un module
>>> Echeance.objects.create(echeance=datetime.datetime(2007, 11, 1),utilisateur=u,module=module_trois)
<Echeance: juser - module-trois - 2007-11-01 00:00:00>
>>> u.echeance(cours_deux,module_trois)
<Echeance: juser - module-trois - 2007-11-01 00:00:00>

creation et tests de travaux à rendre
>>> w = Work.objects.create(groupe=u.groupe,cours=cours_un,titre='Blah')
>>> w
<Work: Blah - Students - Premier cours>
>>> u.work_list()
[<Work: Blah - Students - Premier cours>]
>>> u.work_done(w)
False

il y a un travail à rendre sur le cours-un, donc il n'est plus validé
tant que ce travail n'est pas rendu
>>> u.cours_is_valide(cours_un)
False

le premier module du cours deux n'est donc plus ouvert
>>> u.module_is_open(module_trois)
False

"""

