# -*- encoding: utf-8 -*-

"""Définit les classes Client, Groupe, Utilisateur, Coached et Log.
"""
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.conf import settings

from learning.models import Cours, Module
from testing.models import Granule

from listes import *

class Client(models.Model):
    """
    Le modèle de base Client.
    
    Définit la référence aux feuilles de style (CSS)
    et un champ libre pour les contacts etc.
    """
    
    nom = models.CharField(max_length=60, unique=True)
    style = models.CharField(max_length=20, null=True, blank=True)
    contacts = models.TextField()
    
    class Meta:
        ordering = ['nom']

    def __unicode__(self):
        return self.nom

class Groupe(models.Model):
    """
    Le modèle de base groupe (Groupe).

    Un groupe appartient à un Client (institution).
    Un groupe possède au plus un administrateur qui est un Utilisateur.
    L'administrateur peut avoir plusieurs groupes et peut gérer ses
    groupes (passer un étudiant d'un groupe à l'autre p. ex.)
    Un Utilisateur n'appartient qu'à un et un seul groupe.
    Drapeaux :
    - is_demo : les Utilisateurs du groupe ne peuvent pas faire de tests
    - is_open : les Utilisateurs du groupe peuvent consulter tous les cours, 
      indépendamment de leurs résultats aux tests.
    Un groupe is_demo est forcément is_open.
    Un groupe est inscrit à zéro, un ou plusieurs cours.
    """

    nom = models.CharField(max_length=60, unique=True)
    administrateur = models.ForeignKey('Utilisateur', blank=True, null=True, related_name='groupes')
    client = models.ForeignKey(Client)

    is_demo = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)

    cours = models.ManyToManyField(Cours, blank=True, null=True)

    class Meta:
        pass

    def __unicode__(self):
        return self.nom

    def save(self, force_insert=False, force_update=False):
        if self.is_demo:
            self.is_open=True
        super(Groupe, self).save(force_insert, force_update)

    def workdone(self):
        """ Renvoie la liste des fichiers de devoirs rendus
        """
        liste_work = []
        import os.path
        for c in self.cours.all():
            zipname = 'g%d-%s.zip' % (self.id, c.slug)
            zipfile = os.path.join(settings.MEDIA_ROOT,'workdone',zipname)
            if os.path.exists(zipfile):
                liste_work.append(zipname)
        return liste_work

    def modules_list(self):
        """
        Liste des modules des cours de ce groupe

        Renvoie une liste d'objets modules.
        """
        liste = []
        for c in self.cours.all():
            liste.extend([mc.module for mc in c.modulecours_set.all()])
        return liste

class Utilisateur(models.Model):
    """
    Le modèle de base utilisateur (Utilisateur).

    Un Utilisateur appartient à un et un seul Groupe.
    Un Utilisateur peut être :
    - administrateur (s'il est administrateur d'un ou plusieurs Groupes)
    - coach (s'il est responsable d'un ou plusieurs Cours pour un Groupe)
    - étudiant (rien de spécial).
    La date de création est automatique.
    La langue définit la langue d'interface, des supports et des tests.
    """

    #user = models.ForeignKey(User, unique=True, edit_inline = models.TABULAR, num_in_admin=1)
    login = models.CharField(max_length=20, unique=True, db_index=True)
    password = models.CharField(max_length=60, editable=False)

    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    email = models.EmailField()

    is_staff = models.BooleanField(default=False)
    
    creation = models.DateTimeField(editable=False)
    modification = models.DateTimeField(editable=False, blank=True, null=True)
    fermeture = models.DateTimeField(blank=True, null=True)
    
    lastw = models.DateTimeField(blank=True, null=True)
    nb_retards = models.IntegerField(blank=True, null=True)
    nb_valides = models.IntegerField(blank=True, null=True)
    nb_modules = models.IntegerField(blank=True, null=True)
    nb_actuel = models.IntegerField(blank=True, null=True)
    # le temps passé est un nombre de secondes
    tempspasse = models.IntegerField(blank=True, null=True)

    langue = models.CharField(max_length=5, choices=LISTE_LANGUES)
    
    groupe = models.ForeignKey(Groupe)

    class Meta:
        #unique_together = (("nom","prenom"),)
        ordering = ['groupe','nom']

    def __unicode__(self):
        return self.login

    def prenom_nom(self):
        return u'%s %s' % (self.prenom, self.nom)

    def nom_prenom(self):
        return u'%s %s' % (self.nom, self.prenom)

    def save(self, force_insert=False, force_update=False, change_password=False):
        """Surcharge save() pour donner les valeurs de :
        - date de création
        - date de modification
        - password hash à partir du password en clair
        """
        if not self.id:
            self.creation = datetime.datetime.now()
            self.nb_valides, self.nb_modules, \
                    self.nb_actuel, self.nb_retards = self.nperfs()
#            self.nb_retards = self.nperfs()[3]
#            self.nb_actuel = self.nperfs()[2]
#            self.nb_valides = 0
#            self.nb_modules = self.nperfs()[1]
#            for c in self.cours_list():
#                self.nb_modules += c.modulecours_set.count()
        else:
            self.modification = datetime.datetime.now()

        # gestion mot de passe
        # si l'utilisateur n'existe pas, alors il faut sauvegarder le mot de 
        # passe en version chiffrée
        # si l'utilisateur existe et qu'on ne veut pas changer le mot de passe,
        # alors il faut récupérer la version chiffrée de celui-ci.
        try:
            u = Utilisateur.objects.get(id=self.id)
            if not change_password:
                self.password = u.password
        except Utilisateur.DoesNotExist:
            change_password=True

        if change_password:
            import sha, random, unicodedata
            salt = sha.new(str(random.random())).hexdigest()[:5]
            #password = unicodedata.normalize('NFKD',self.password).encode('ASCII','ignore')
            password = smart_str(self.password)
            hsh = sha.new(salt+password).hexdigest()
            self.password = '%s$%s' % (salt, hsh)
        
        super(Utilisateur, self).save(force_insert, force_update)

    def is_pwd_correct(self, raw_password):
        import sha, unicodedata
        salt, hsh = self.password.split('$')
        salt = smart_str(salt)
        #password = unicodedata.normalize('NFKD',raw_password).encode('ASCII','ignore')
        password = smart_str(raw_password)
        return hsh == sha.new(salt+password).hexdigest()

    def time_elapsed(self):
        if self.tempspasse:
            return smart_str(datetime.timedelta(seconds=self.tempspasse))
        else:
            return ''

    def is_valid(self):
        if self.fermeture:
            return datetime.datetime.now() < self.fermeture
        return True
    is_valid.short_description = 'Valide ?'
    is_valid.boolean = True

    _status = None

    def _get_status(self):
        if self._status is None:
            self._status = self.statut()
        return self._status

    status = property(_get_status)

    def statut(self):
        if self.is_staff:
            return STAFF
        if self.groupes.count() > 0:
            return ADMINISTRATEUR
        if self.coached.count() > 0:
            return COACH
        return 0
    statut.short_description = 'Statut'

    def cours_list(self):
        """Liste des cours que cet utilisateur peut consulter
        
        Si l'utilisateur est administrateur d'un groupe,
        il peut consulter les cours de ce groupe.
        S'il est coach d'un groupe-cours, il peut consulter
        ce cours + ceux auxquels est inscrit son groupe.
        S'il est étudiant, il peut consulter les cours auxquels
        est inscrit son groupe.

        Renvoie une liste d'objets cours.
        """
        if self.status == STAFF:
            return Cours.objects.select_related()
        liste = []
        g = self.groupe
        liste.extend(g.cours.select_related())
        if self.status in (ADMINISTRATEUR, COACH):
            for g in self.groupes_list():
                for c in g.cours.select_related():
                    try:
                        i = liste.index(c)
                    except ValueError:
                        liste.append(c)
#        else:
#            g = self.groupe
#            liste.extend(g.cours.select_related())
        return liste

    def modules_list(self):
        """Liste des modules que cet utilisateur peut consulter
        
        Si l'utilisateur est administrateur d'un groupe,
        il peut consulter les modules des cours de ce groupe.
        S'il est coach d'un groupe-cours, il peut consulter
        les modules de ce cours.
        S'il est étudiant, il peut consulter les modules des
        cours auxquels sont groupe est inscrit.

        Renvoie une liste d'objets modules.
        """
        if self.status == STAFF:
            return Module.objects.all()
        liste = []
        for c in self.cours_list():
            liste.extend([mc.module for mc in c.modulecours_set.all()])
        return liste

    def granules_list(self):
        """Liste des granules de test de cet utilisateur, ouvertes ou non
        
        Renvoie une liste d'objets granules.
        """
        if self.status == STAFF:
            return Granule.objects.all()
        liste = []
        for m in self.modules_list():
            liste.extend(m.granule_set.all())
        return liste

    def nb_essais(self, granule):
        return Resultat.objects.filter(utilisateur=self, granule=granule).count()

    def last_score(self, granule):
        try:
            q = Resultat.objects.filter(utilisateur=self, granule=granule).latest('date')
        except Resultat.DoesNotExist:
            return ('', 0)
        return (q.date, q.score)

    def best_score(self, granule):
        q = Resultat.objects.filter(utilisateur=self, granule=granule).order_by('-score')
        if q:
            return (q[0].date, q[0].score)
        else:
            return ('', 0)

    def valid_score(self, granule):
#        try:
#            q = Valide.objects.get(utilisateur=self, granule=granule)
#        except Valide.DoesNotExist:
#            return ('', 0)
#        return (q.date, q.score)
        q = Valide.objects.filter(utilisateur=self, granule=granule).order_by('-score')
        if q:
            return (q[0].date, q[0].score)
        else:
            return ('', 0)

    def nb_granules_valides(self,module):
        return self.valide_set.filter(granule__in=module.granule_set.all()).count()

    def module_is_valide(self, module):
        """Renvoie True si le module est validé.
        """
        return self.valide_set.filter(module=module).count()>0

    def date_validation_module(self, module):
        """Renvoie la date de validation du module
        """
        q = self.valide_set.filter(module=module)
        if q:
            return q[0].date
        else:
            return None

    def cours_du_module(self, module):
        """Renvoie le cours auquel appartient ce module.
        """
        for c in self.cours_list():
            if module in [mc.module for mc in c.modulecours_set.all()]:
                return c
        return None

    def module_precedent(self, module):
        """Renvoie le module précédent dans le cours s'il existe.
        """
        c = self.cours_du_module(module)
        rang = module.rang(c)
        if c and rang:
            qc = c.modulecours_set.filter(rang__lt=rang)
            if qc:
                return list(qc)[-1].module
        return None

    def cours_precedent(self, module):
        """Renvoie le cours précédent celui qui contient module.
        """
        cours = self.cours_du_module(module)
        if cours:
            rang = self.cours_list().index(cours)
            if rang:
                return self.cours_list()[rang-1]
        return None

    def cours_is_valide(self, cours):
        """Renvoie True si tous les modules et dossiers du cours sont validés.
        """
        for module in [mc.module for mc in cours.modulecours_set.all()]:
            # si module sans question, on ne teste pas
            if module.granule_set.count()==0:
                continue
            if not self.module_is_valide(module):
                return False
        for devoir in Work.objects.filter(cours=cours, groupe=self.groupe):
            if not self.work_done(devoir):
                return False
        return True

    def work_list(self):
        """Renvoie la liste des travaux à rendre, tous cours confondus"""
        return Work.objects.filter(groupe=self.groupe)

    def work_done(self, devoir):
        """Renvoie True si ce devoir a été rendu"""
        try:
            w = WorkDone.objects.get(utilisateur=self,work=devoir)
        except WorkDone.DoesNotExist:
            return False
        return True

    def cours_is_open(self, cours):
        """Renvoie True si le cours précédent est validé ou si c'est le premier cours.
        """
        rang = self.cours_list().index(cours)
        if rang:
            return self.cours_is_valide(self.cours_list()[rang-1])
        return True

    def module_is_open(self, module):
        """Renvoie True si le module est consultable.

        Conditions:
        - tout est ouvert, ou
        - module précédent validé dans le cours
        - cours précédent validé et premier module du cours
        """
        if not module in self.modules_list():
            return False
        if self.groupe.is_open or self.status > ETUDIANT:
            return True
        if not self.module_precedent(module):
            cp = self.cours_precedent(module)
            if cp:
                if self.cours_is_valide(cp):
                    return True
                else:
                    return False
            # s'il n'y a pas de cours précédent, premier cours du premier module, 
            # donc ouvert
            else:
                return True
        if self.module_is_valide(self.module_precedent(module)):
            return True
        # si le module précédent n'a pas de questions, celui-ci est ouvert
        if self.module_precedent(module).granule_set.count()==0:
            return True
        return False

    def current_test(self,module):
        """Renvoie le test en cours sur un module.

        Si le module est ouvert et validé, dernier test travaillé
        Si module ouvert et non validé, premier test non validé
        Sinon rien
        """
        if self.module_is_open(module):
            if self.module_is_valide(module):
                g = self.resultat_set.filter(granule__in=module.granule_set.all()).latest('date')
                return g.granule
            else:
                for g in module.granule_set.all():
                    if not g in self.valide_set.filter(granule__in=module.granule_set.all()):
                        return g
        return None

    def echeance(self, cours, module):
        qu = self.echeance_set.filter(utilisateur__isnull=False)
        qg = self.groupe.echeance_set.filter(utilisateur__isnull=True)
        try:
            e = qu.get(module=module)
        except Echeance.DoesNotExist:
            try:
                e = qu.get(cours=cours,module__isnull=True)
            except Echeance.DoesNotExist:
                e = None
        if not e:
            try:
                e = qg.get(module=module)
            except Echeance.DoesNotExist:
                try:
                    e = qg.get(cours=cours,module__isnull=True)
                except Echeance.DoesNotExist:
                    e = None
        return e

    def old_stats_contenu(self,contenu):
        """Renvoie le nombre de consultations et la dernière consultation d'un support.
        """
        path, qstring = contenu.url().split('?')
        q = Log.objects.filter(utilisateur=self,path=path, qstring=qstring).count()
        if q:
            nb = q
            lastv = Log.objects.filter(utilisateur=self,path=path, qstring=qstring).latest('date').date
        else:
            nb = 0
            lastv = ''
        return (nb, lastv)

    def stats_contenu(self,contenu):
        """Renvoie le nombre de consultations et la dernière consultation d'un support.
        """
        q = Log.objects.filter(utilisateur=self,path=contenu.url()).count()
        if q:
            nb = q
            lastv = Log.objects.filter(utilisateur=self,path=contenu.url()).latest('date').date
        else:
            nb = 0
            lastv = ''
        return (nb, lastv)

    def nperfs(self):
        """Calcule des elts relatifs aux performances de l'étudiant :

        - nb de modules total
        - nb de modules validés
        - nb de modules validés en retard
        - nb de retards
        """
        valides, total, retards, troptard = (0,0,0,0)
        for c in self.cours_list():
            for m in [mc.module for mc in c.modulecours_set.all()]:
                total += 1
                e = self.echeance(c, m)
                if self.module_is_valide(m):
                    valides += 1
                    if e:
                        if self.date_validation_module(m):
                            if e.echeance < self.date_validation_module(m):
                                troptard += 1
                else:
                    if e:
                        if e.echeance < datetime.datetime.now():
                            retards += 1
        return (valides,total,retards,troptard)

    def perfs(self):
        """Calcule le nb de retards actuels de l'étudiant :
        """
        retards = 0
        for c in self.cours_list():
            for m in [mc.module for mc in c.modulecours_set.all()]:
                if not self.module_is_valide(m):
                    e = self.echeance(c, m)
                    if e:
                        if e.echeance < datetime.datetime.now():
                            retards += 1
        return retards

    def groupes_list(self):
        """Renvoie une liste des groupes coachés ou administrés par cet utilisateur """
        if not self.status >= COACH:
            return []
        if self.is_staff:
            return Groupe.objects.all()
        if self.status == ADMINISTRATEUR:
            return self.groupes.all()
        if self.status == COACH:
            seen = {}
            result = []
            for item in [gc.groupe for gc in self.coached.all()]:
                if item in seen: continue
                seen[item] = 1
                result.append(item)
            return result

class Coached(models.Model):
    """
    Chaque cours délivré à un groupe peut avoir un coach.
    Il est alors Coached.

    Le coach est un objet Utilisateur.
    """
    cours = models.ForeignKey(Cours)
    groupe = models.ForeignKey(Groupe)
    coach = models.ForeignKey(Utilisateur, related_name='coached')

    class Meta:
        pass

    def __unicode__(self):
        return u'%s - %s - %s' % (self.groupe.nom, self.cours.slug, self.coach.nom)

class NonTrashManager(models.Manager):
    ''' Query only objects which have not been trashed. '''
    def get_query_set(self):
        return super(NonTrashManager, self).get_query_set().filter(trashed_at__isnull=True)

class TrashManager(models.Manager):
    ''' Query only objects which have been trashed. '''
    def get_query_set(self):
        return super(TrashManager, self).get_query_set().filter(trashed_at__isnull=False)

class Work(models.Model):
    """Devoir à rendre pour un groupe et un cours.
    """

    groupe = models.ForeignKey(Groupe)
    cours = models.ForeignKey(Cours)
    titre = models.CharField(max_length=100)
    libel = models.TextField(blank=True, null=True)
    fichier = models.FileField(upload_to='assignments/%Y/%m/%d',blank=True,null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    class Meta:
        pass

    def __unicode__(self):
        return u'%s - %s - %s' % (self.titre, self.groupe, self.cours)

    def delete(self, trash=True):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.datetime.now()
            self.save()
        else:
            super(Work, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()

class WorkDone(models.Model):
    """Devoir rendu par un utilisateur"""

    utilisateur = models.ForeignKey(Utilisateur)
    work = models.ForeignKey(Work)
    date = models.DateTimeField()
    fichier = models.FileField(upload_to='workdone')
    signature = models.CharField(max_length=54)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.utilisateur.login, self.work.titre, self.date)

class Echeance(models.Model):
    """Echéance d'un module pour un utilisateur"""

    echeance = models.DateTimeField()
    utilisateur = models.ForeignKey(Utilisateur, blank=True, null=True)
    groupe = models.ForeignKey(Groupe, blank=True, null=True)
    module = models.ForeignKey(Module, blank=True, null=True)
    cours = models.ForeignKey(Cours, blank=True, null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    class Admin:
        pass

    class Meta:
        pass

    def __unicode__(self):
        if self.utilisateur:
            if self.module:
                return u'%s - %s - %s' % (self.utilisateur.login, self.module, self.echeance)
            else:
                return u'%s - %s - %s' % (self.utilisateur.login, self.cours, self.echeance)
        else:
            if self.module:
                return u'%s - %s - %s' % (self.groupe, self.module, self.echeance)
            else:
                return u'%s - %s - %s' % (self.groupe, self.cours, self.echeance)

    def save(self, force_insert=False, force_update=False):
        if not self.groupe:
            u = self.utilisateur
            self.groupe = u.groupe
        if not self.cours:
            # recherche du cours à partir du groupe et du module
            for c in self.groupe.cours.all():
                if self.module in [mc.module for mc in c.modulecours_set.all()]:
                    self.cours = c
                    break
        # on ne peut pas dupliquer une échéance sur utilisateur-groupe-cours-module
        if self.utilisateur:
            if self.module:
                try:
                    e = Echeance.objects.get(utilisateur=self.utilisateur,
                                        groupe=self.groupe,
                                        module=self.module, cours=self.cours)
                    e.echeance = self.echeance
                    super (Echeance, e).save(force_insert, force_update)
                except Echeance.DoesNotExist:
                    super(Echeance, self).save(force_insert, force_update)
            else:
                try:
                    e = Echeance.objects.get(utilisateur=self.utilisateur,
                                        groupe=self.groupe,
                                        module__isnull=True, cours=self.cours)
                    e.echeance = self.echeance
                    super (Echeance, e).save(force_insert, force_update)
                except Echeance.DoesNotExist:
                    super(Echeance, self).save(force_insert, force_update)
        else:
            if self.module:
                try:
                    e = Echeance.objects.get(utilisateur__isnull=True,
                                        groupe=self.groupe,
                                        module=self.module, cours=self.cours)
                    e.echeance = self.echeance
                    super (Echeance, e).save(force_insert, force_update)
                except Echeance.DoesNotExist:
                    super(Echeance, self).save(force_insert, force_update)
            else:
                try:
                    e = Echeance.objects.get(utilisateur__isnull=True,
                                        groupe=self.groupe,
                                        module__isnull=True, cours=self.cours)
                    e.echeance = self.echeance
                    super (Echeance, e).save(force_insert, force_update)
                except Echeance.DoesNotExist:
                    super(Echeance, self).save(force_insert, force_update)

    def delete(self, trash=True):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.datetime.now()
            self.save()
        else:
            super(Echeance, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()

class Log(models.Model):
    """Enregistre l'activité des Utilisateurs (date, path et qstring de la page visitée)."""
    
    utilisateur = models.ForeignKey(Utilisateur)
    date = models.DateTimeField()
    path = models.CharField(max_length=100)
    qstring = models.CharField(max_length=50)

    class Meta:
        ordering = ('-date',)

class Resultat(models.Model):
    """Stocke tous les résultats des essais aux tests.
    """
    utilisateur = models.ForeignKey(Utilisateur)
    granule = models.ForeignKey(Granule)
    date = models.DateTimeField()
    score = models.IntegerField()

    class Meta:
        ordering = ('-date',)

    def __unicode__(self):
        return u"%s - %s - %s - %d" % (self.utilisateur, self.granule, self.date, self.score)

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            if not self.date:
                self.date = datetime.datetime.now()
        super(Resultat, self).save(force_insert, force_update)

class Valide(models.Model):
    """Stocke les granules et modules validés pour un utilisateur.
    """
    utilisateur = models.ForeignKey(Utilisateur)
    granule = models.ForeignKey(Granule, null=True)
    module = models.ForeignKey(Module, null=True)
    date = models.DateTimeField()
    score = models.IntegerField()

    def __unicode__(self):
        if self.granule:
            return u"%s - G : %s - %s - %d" % (self.utilisateur, self.granule, self.date, self.score)
        else:
            return u"%s - M : %s - %s - %d" % (self.utilisateur, self.module, self.date, self.score)

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            if not self.date:
                self.date = datetime.datetime.now()
        super(Valide, self).save(force_insert, force_update)

class Tempsparmodule(models.Model):
    """
    Stocke le temps passé par utilisateur et module
    """
    utilisateur = models.ForeignKey(Utilisateur)
    module = models.ForeignKey(Module)
    tempspasse = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s - %s - %d" % (self.utilisateur, self.module, self.tempspasse)
