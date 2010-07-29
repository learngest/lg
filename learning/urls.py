from django.conf.urls.defaults import *

from listes import *

urlpatterns = patterns('',
    url(r'^tdb/$', 'learning.views.tdb', name='l_dashboard'),
    url(r'^profile/$', 'learning.views.profile', name='l_profile'),
    (r'^module/(?P<slug>[a-z0-9-]+)/$', 'learning.views.module'),
    (r'^devoir/$', 'learning.views.devoir'),
    (r'^common/(?P<slug>[a-z0-9-]+)/$', 'learning.views.help_support'),
    (r'^support/(?P<slug>[a-z0-9-]+)/$', 'learning.views.support', {'ltyp': 'htm'}),
    (r'^anim/(?P<slug>[a-z0-9-]+)/$', 'learning.views.support', {'ltyp': 'swf'}),
)
