from django.conf.urls.defaults import *

from lg.listes import *

urlpatterns = patterns('',
    (r'^tdb/$', 'lg.learning.views.tdb'),
    (r'^profile/$', 'lg.learning.views.profile'),
    (r'^module/(?P<slug>[a-z0-9-]+)/$', 'lg.learning.views.module'),
    (r'^devoir/$', 'lg.learning.views.devoir'),
    (r'^common/(?P<slug>[a-z0-9-]+)/$', 'lg.learning.views.help_support'),
    (r'^support/(?P<slug>[a-z0-9-]+)/$', 'lg.learning.views.support', {'ltyp': 'htm'}),
    (r'^anim/(?P<slug>[a-z0-9-]+)/$', 'lg.learning.views.support', {'ltyp': 'swf'}),
)
