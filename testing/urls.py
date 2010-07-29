from django.conf.urls.defaults import *

from listes import *

urlpatterns = patterns('',
    url(r'^$', 'testing.views.test', name='t_test'),
    (r'^noter/$', 'testing.views.noter'),
    (r'^(?P<slug>[a-z0-9-]+)/$', 'testing.views.test'),
)
