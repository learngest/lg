# -*- encoding: utf-8 -*-

from django.contrib import admin
from lg.coaching.models import Client, Groupe, Utilisateur, Coached, Work, Echeance, AutresDocs

class ClientAdmin(admin.ModelAdmin):
    search_fields = ('nom',)
    ordering = ['nom']
admin.site.register(Client, ClientAdmin)

class GroupeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('nom',)}),
        (None, {'fields': ('administrateur','client')}),
        ('Cours', {'fields': ('cours',)}),
        ('Permissions', {'fields': ('is_demo', 'is_open')}),
    )
    list_filter = ('client','is_demo','is_open')
    list_display = ('client','nom','administrateur','is_demo','is_open')
    list_display_links = ('nom',)
    list_per_page = 30
    search_fields = ('nom',)
    filter_horizontal = ('cours',)
    ordering = ('client',)
admin.site.register(Groupe, GroupeAdmin)

class UtilisateurAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('login', 'is_staff')}),
        ('Groupe', {'fields': ('groupe',)}),
        ('Identité', {'fields': ('nom', 'prenom', 'email')}),
        ('Validité', {'fields': ('fermeture',)}),
        ('Langue',{'fields': ('langue',)}),
    )
    list_display = ('groupe','login', 'nom', 'prenom',
            'fermeture','creation','modification',
            'statut','is_valid','langue',)
    list_display_links = ('login','nom')
    list_filter = ('groupe','fermeture','langue')
    list_per_page = 30
    search_fields = ('login','nom','email')
    ordering = ['groupe','nom']
admin.site.register(Utilisateur, UtilisateurAdmin)

class CoachedAdmin(admin.ModelAdmin):
    pass
admin.site.register(Coached, CoachedAdmin)

class WorkAdmin(admin.ModelAdmin):
    pass
admin.site.register(Work, WorkAdmin)

class EcheanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Echeance, EcheanceAdmin)

class AutresDocsAdmin(admin.ModelAdmin):
    fieldsets = (
            (None, {'fields': ('groupe','cours',)}),
            (None, {'fields': ('titre','fichier',)}),
    )
    list_display = ('groupe','cours','titre',)
    list_display_links = ('titre',)
    list_filter = ('groupe','cours',)
admin.site.register(AutresDocs, AutresDocsAdmin)

