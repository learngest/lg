from django.conf.urls.defaults import *

from lg.listes import *
from coaching.models import Log

urlpatterns = patterns('',
    (r'^$', 'lg.coaching.views.menu'),
    (r'^lista/$', 'lg.coaching.views.liste_utilisateurs', {'ltyp': ADMINISTRATEUR}),
    (r'^liste/$', 'lg.coaching.views.liste_utilisateurs', {'ltyp': COACH}),
    (r'^csv/$', 'lg.coaching.views.liste_csv'),
    (r'^timecsv/$', 'lg.coaching.views.time_csv'),
    (r'^clients/$', 'lg.coaching.views.liste_clients'),
    (r'^detail/$', 'lg.coaching.views.detail_utilisateur'),
    (r'^sendmail/$', 'lg.coaching.views.send_email'),
    (r'^detail/module/$', 'lg.coaching.views.detail_module'),
    (r'^log/$', 'lg.coaching.views.log_utilisateur'),
#    (r'^logs/$', 'lg.coaching.views.logs'),
    (r'^logins/$', 'lg.coaching.views.create_logins'),
    (r'^ficha/(?P<utilisateur>[A-Za-z0-9-.]+)/$', 'lg.coaching.views.profile_utilisateur_admin'),
    (r'^echeance/$', 'lg.coaching.views.liste_echeances'),
    (r'^echeance/add/?$', 'lg.coaching.views.add_echeance'),
    (r'^echeance/manage/?$', 'lg.coaching.views.maj_echeance'),
    (r'^work/$', 'lg.coaching.views.liste_works'),
    (r'^work/add/?$', 'lg.coaching.views.add_work'),
    (r'^work/manage/?$', 'lg.coaching.views.maj_work'),
)

log_dict = {
    'queryset': Log.objects.all(),
    'paginate_by': 23,
    'allow_empty': True,
}

urlpatterns += patterns('django.views.generic.list_detail',
    (r'^logs/$', 'object_list', log_dict),
)
