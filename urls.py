from django.conf.urls.defaults import *
#from django.contrib import admin

#admin.autodiscover()

urlpatterns = patterns('',
    (r'^blah/', include('django.contrib.admin.urls')),
    #(r'^blah/(.*)', admin.site.root),
#    (r'^style/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jcb/learngest/web/media/style'}),
#    (r'^contents/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jcb/learngest/web/contents'}),
#    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jcb/learngest/web/media/js'}),
#    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jcb/learngest/web/media/img'}),
    (r'^login/', 'lg.session.views.login'),
    (r'^lostpw/', 'lg.session.views.lost_password'),
    (r'^logout/', 'lg.session.views.logout'),
    (r'^home/', 'lg.session.views.home'),
    (r'^coaching/', include ('lg.coaching.urls')),
    (r'^learning/', include ('lg.learning.urls')),
    (r'^testing/', include ('lg.testing.urls')),
#    (r'^$', 'lg.pages.views.page_detail'),
    (r'^$', 'lg.session.views.login'),
    (r'^(?P<section>[a-z0-9-]+)/(?P<slug>[a-z0-9-]*)', 'lg.pages.views.page_detail'),
)
