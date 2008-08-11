from django.conf.urls.defaults import *

from lg.listes import *

urlpatterns = patterns('',
    (r'^$', 'lg.testing.views.test'),
    (r'^noter/$', 'lg.testing.views.noter'),
    (r'^(?P<slug>[a-z0-9-]+)/$', 'lg.testing.views.test'),
)
