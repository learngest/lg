from django.conf.urls.defaults import *

urlpatterns = patterns('testing.views',
    url(r'^$', 'test', name='t_test'),
    (r'^noter/$', 'noter'),
    (r'^(?P<slug>[a-z0-9-]+)/$', 'test'),
)
