from django.conf.urls.defaults import *

from lg.listes import *
from coaching.models import Log

urlpatterns = patterns('',
    url(r'^$', 'lg.coaching.views.menu', name='c_admin'),
    url(r'^lista/$', 'lg.coaching.views.liste_utilisateurs', {'ltyp': ADMINISTRATEUR}, name='c_lista'),
    (r'^liste/$', 'lg.coaching.views.liste_utilisateurs', {'ltyp': COACH}),
    url(r'^csv/$', 'lg.coaching.views.liste_csv', name='c_csv'),
    url(r'^timecsv/$', 'lg.coaching.views.time_csv', name='c_timecsv'),
    url(r'^clients/$', 'lg.coaching.views.liste_clients', name='c_client'),
    url(r'^detail/$', 'lg.coaching.views.detail_utilisateur', name='c_detail'),
    url(r'^sendmail/$', 'lg.coaching.views.send_email', name='c_sendmail'),
    (r'^detail/module/$', 'lg.coaching.views.detail_module'),
    url(r'^log/$', 'lg.coaching.views.log_utilisateur', name='c_log'),
#    (r'^logs/$', 'lg.coaching.views.logs'),
    url(r'^logins/$', 'lg.coaching.views.create_logins', name='c_logins'),
    url(r'^ficha/(?P<utilisateur>[A-Za-z0-9-_.]+)/$', 'lg.coaching.views.profile_utilisateur_admin', name='c_ficha'),
    url(r'^echeance/$', 'lg.coaching.views.liste_echeances', name='c_echeance'),
    url(r'^echeance/add/?$', 'lg.coaching.views.add_echeance', name='c_echeance_add'),
    url(r'^echeance/manage/?$', 'lg.coaching.views.maj_echeance', name='c_echeance_manage'),
    url(r'^work/$', 'lg.coaching.views.liste_works', name='c_work'),
    url(r'^work/add/?$', 'lg.coaching.views.add_work', name='c_work_add'),
    url(r'^work/manage/?$', 'lg.coaching.views.maj_work', name='c_work_manage'),
)

log_dict = {
    'queryset': Log.objects.all(),
    'paginate_by': 23,
    'allow_empty': True,
}

urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^logs/$', 'object_list', log_dict, name='c_logs'),
)
