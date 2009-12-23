# -*- encoding: utf-8 -*-

import os.path

from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

# Base
urlpatterns = patterns('',
    (r'^login/', 'lg.session.views.login'),
    (r'^lostpw/', 'lg.session.views.lost_password'),
    (r'^logout/', 'lg.session.views.logout'),
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
    {'document_root': '/home/jcb/learngest/web/media' }),
    (r'^upload/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': uploads_root }),
    )

# Applications
urlpatterns += patterns('',
    (r'^home/', 'lg.session.views.home'),
    (r'^blah/(.*)', admin.site.root),
    (r'^coaching/', include ('lg.coaching.urls')),
    (r'^learning/', include ('lg.learning.urls')),
    (r'^testing/', include ('lg.testing.urls')),
    (r'^$', 'lg.session.views.login'),
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

