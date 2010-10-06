from django.conf.urls.defaults import *

urlpatterns = patterns('testing.views',
    url(r'^$', 'test', name='t_test'),
    url(r'^noter/$', 'noter', name='t_noter'),
    (r'^(?P<slug>[a-z0-9-]+)/$', 'test'),
)
