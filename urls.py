# -*- encoding: utf-8 -*-

import os.path

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

# Base
urlpatterns = patterns('',
    url(r'^login/', 'lg.session.views.login', name='login'),
    url(r'^lostpw/', 'lg.session.views.lost_password', name='lostpw'),
    url(r'^logout/', 'lg.session.views.logout', name='logout'),
    )

# Developpement
if settings.SITE_ID==1:
    contents_root = os.path.join(settings.PROJECT_PATH, settings.CONTENTS_PREFIX)
    contents_root = os.path.normpath(contents_root)
    uploads_root = os.path.join(settings.PROJECT_PATH, settings.MEDIA_ROOT)
    uploads_root = os.path.normpath(uploads_root)
    urlpatterns += patterns('',
    (r'^contents/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': contents_root }),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',

    # **************
    # TMP MEDIA PATH
    # **************
    # {'document_root': '/home/jcb/learngest/web/media' }),
    {'document_root': os.path.join(settings.PROJECT_PATH, 'web/media') }),

    (r'^upload/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': uploads_root }),
    )

# Product
urlpatterns += patterns('',
    url(r'^$', direct_to_template, { 'template': 'product/home.html', 'extra_context': { 'here': 'home', } }, name='home'),
    url(r'^news/$', direct_to_template, { 'template': 'product/news.html', 'extra_context': { 'here': 'news', } }, name='news'),
    url(r'^demo/$', direct_to_template, { 'template': 'product/demo.html', 'extra_context': { 'here': 'demo', } }, name='demo'),
    url(r'^overview/$', direct_to_template, { 'template': 'product/overview.html', 'extra_context': { 'here': 'overview', } }, name='overview'),
    url(r'^contributors/$', direct_to_template, { 'template': 'product/contributors.html', 'extra_context': { 'here': 'contributors', } }, name='contributors'),
    url(r'^legal/$', direct_to_template, { 'template': 'product/legal.html', }, name='legal'),
    )

# Applications
urlpatterns += patterns('',
    (r'^home/', 'lg.session.views.home'),
    (r'^blah/(.*)', admin.site.root),
    (r'^coaching/', include ('lg.coaching.urls')),
    (r'^learning/', include ('lg.learning.urls')),
    (r'^testing/', include ('lg.testing.urls')),
    # (r'^$', 'lg.session.views.login'),
    )

# Old media
if settings.SITE_ID==1:
    urlpatterns += patterns('',
    (r'^style/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/jcb/learngest/web/media/style'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/jcb/learngest/web/media/js'}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/jcb/learngest/web/media/img'}),
    )

# Presentation website - keep last or <section> would catch other urls
urlpatterns += patterns('',
    (r'^(?P<section>[a-z0-9-]+)/(?P<slug>[a-z0-9-]*)',
        'lg.pages.views.page_detail'),
    )

