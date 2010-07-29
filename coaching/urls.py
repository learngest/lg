from django.conf.urls.defaults import *

urlpatterns = patterns('coaching.views',
    url(r'^$', 'menu', name='c_admin'),
    url(r'^lista/$', 'liste_utilisateurs', name='c_lista'),
    url(r'^csv/$', 'liste_csv', name='c_csv'),
    url(r'^timecsv/$', 'time_csv', name='c_timecsv'),
    url(r'^clients/$', 'liste_clients', name='c_client'),
    url(r'^detail/$', 'detail_utilisateur', name='c_detail'),
    url(r'^sendmail/$', 'send_email', name='c_sendmail'),
    url(r'^detail/module/$','detail_module'),
    url(r'^log/$', 'log_utilisateur', name='c_log'),
    url(r'^logins/$', 'create_logins', name='c_logins'),
    url(r'^ficha/(?P<utilisateur>[A-Za-z0-9-_.]+)/$',
        'profile_utilisateur_admin', name='c_ficha'),
    url(r'^echeance/$', 'liste_echeances', name='c_echeance'),
    url(r'^echeance/add/?$', 'add_echeance', name='c_echeance_add'),
    url(r'^echeance/manage/?$', 'maj_echeance', name='c_echeance_manage'),
    url(r'^work/$', 'liste_works', name='c_work'),
    url(r'^work/add/?$', 'add_work', name='c_work_add'),
    url(r'^work/manage/?$', 'maj_work', name='c_work_manage'),
    url(r'^logs/$', 'logs', name='c_logs'),
)

