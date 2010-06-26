from django.conf.urls.defaults import *

from lg.listes import *

urlpatterns = patterns('',
    url(r'^$', 'lg.testing.views.test', name='t_test'),
    (r'^noter/$', 'lg.testing.views.noter'),
    (r'^(?P<slug>[a-z0-9-]+)/$', 'lg.testing.views.test'),
)
