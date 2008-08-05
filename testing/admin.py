# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

from django.contrib import admin
from testing.models import Granule, GranuleTitre, Enonce

class GranuleAdmin(admin.ModelAdmin):
    list_display = ('module','rang','slug','nbq','score_min')
    ordering = ['module','rang']
admin.site.register(Granule, GranuleAdmin)

class GranuleTitreAdmin(admin.ModelAdmin):
    list_display = ('granule','langue','titre')
    list_filter = ('langue',)
admin.site.register(GranuleTitre, GranuleTitreAdmin)

class EnonceAdmin(admin.ModelAdmin):
    search_fields = ['libel']
    list_display = ('id','libel')
admin.site.register(Enonce, EnonceAdmin)

