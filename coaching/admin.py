# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from django.utils.translation import ugettext_lazy as _
from coaching.models import Client, Groupe, UserProfile, Coached

class ClientAdmin(admin.ModelAdmin):
    search_fields = ('nom',)
    #ordering = ['nom']
admin.site.register(Client, ClientAdmin)

class GroupeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('nom',)}),
        (None, {'fields': ('administrateur','client')}),
        ('Cours', {'fields': ('cours',)}),
        ('Permissions', {'fields': ('is_demo', 'is_open')}),
    )
    list_display = ('client','nom','administrateur','is_demo','is_open')
    list_display_links = ('nom',)
    list_filter = ('client',)
    search_fields = ('nom',)
    filter_horizontal = ('cours',)
    #ordering = ('client',)
admin.site.register(Groupe, GroupeAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )
    list_filter = ('groupe', 'fermeture')
    search_field = ('__unicode__', 'last_name',)
    list_display = ('last_name',
                    'first_name',
                    '__unicode__',
                    'fermeture',
                    'groupe',
                    'modules_valides',
                    'nb_retards',
                    'nb_actuel',
                    )
    list_display_links = ('__unicode__',)
#    date_hierarchy = 'fermeture'

    def username(self, obj):
        return obj.user.username

    def password(self, obj):
        return obj.user.password

    def last_name(self, obj):
        return obj.user.last_name

    def first_name(self, obj):
        return obj.user.first_name

    def email(self, obj):
        return obj.user.email

    def modules_valides(self, obj):
        return "%d / %d" % (obj.nb_valides, obj.nb_modules)
        
admin.site.register(UserProfile, UserProfileAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    #verbose_name = 'Paramètres'
    fieldsets = (
            (None, {'fields': ('groupe', 'fermeture', 'langue')}),
    )

class CustomUserAdmin(UserAdmin):
    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('Information personnelle', {'fields': 
                ('last_name', 'first_name', 'email')}),
    )
    search_fields = ('username', 'last_name')
    list_display = ('last_name',
                    'first_name',
                    'username',
                    'fermeture',
                    'groupe',
                    'modules_valides',
                    'dont_en_retard',
                    'actuellement_en_retard',
                    )
    list_display_links = ('username',)
    inlines = [UserProfileInline,]
    ordering = ('last_name',)

    def fermeture(self, obj):
        return obj.get_profile().fermeture

    def groupe(self, obj):
        return obj.get_profile().groupe

    def modules_valides(self, obj):
        return "%d / %d" % (obj.get_profile().nb_valides, 
                            obj.get_profile().nb_modules)
        
    def dont_en_retard(self, obj):
        return obj.get_profile().nb_retards
        
    def actuellement_en_retard(self, obj):
        return obj.get_profile().nb_actuel


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class CoachedAdmin(admin.ModelAdmin):
    pass
admin.site.register(Coached, CoachedAdmin)

#class WorkAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(Work, WorkAdmin)
#
#class EcheanceAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(Echeance, EcheanceAdmin)
#
