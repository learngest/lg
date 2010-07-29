# -*- encoding: utf-8 -*-

import os.path

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

# Base
urlpatterns = patterns('session.views',
    url(r'^login/', 'login', name='login'),
    url(r'^democreate/', 'democreate', name='democreate'),
    url(r'^lostpw/', 'lost_password', name='lostpw'),
    url(r'^logout/', 'logout', name='logout'),
    url(r'^start/', 'home', name='v_home'),
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
    {'document_root': os.path.join(settings.PROJECT_PATH, 'web/media') }),

    (r'^upload/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': uploads_root }),
    )

# Applications
urlpatterns += patterns('',
    url(r'^blah/(.*)', admin.site.root, name='admin'),
    (r'^coaching/', include ('coaching.urls')),
    (r'^learning/', include ('learning.urls')),
    (r'^testing/', include ('testing.urls')),
    )

# Public pages - keep last or <section> would catch other urls
urlpatterns += patterns('',
    (r'^(?P<page>[a-z0-9-]*)', 'pages.views.page'),
    )

