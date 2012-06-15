from django.conf.urls.defaults import *

urlpatterns = patterns('lg.learning.views',
    url(r'^tdb/$', 'tdb', name='l_dashboard'),
    url(r'^profile/$', 'profile', name='l_profile'),
    (r'^module/(?P<slug>[a-z0-9-]+)/$', 'module'),
    (r'^devoir/$', 'devoir'),
    (r'^common/(?P<slug>[a-z0-9-]+)/$', 'help_support'),
    (r'^support/(?P<slug>[a-z0-9-]+)/$', 'support', {'ltyp': 'htm'}),
    (r'^anim/(?P<slug>[a-z0-9-]+)/$', 'support', {'ltyp': 'swf'}),
)
