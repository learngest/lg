from django.conf.urls.defaults import *

from listes import *
from coaching.models import Log

urlpatterns = patterns('',
    url(r'^$', 'coaching.views.menu', name='c_admin'),
#    url(r'^lista/$', 'coaching.views.liste_utilisateurs', {'ltyp': ADMINISTRATEUR}, name='c_lista'),
    url(r'^lista/$', 'coaching.views.liste_utilisateurs', name='c_lista'),
#    (r'^liste/$', 'coaching.views.liste_utilisateurs', {'ltyp': COACH}),
    url(r'^csv/$', 'coaching.views.liste_csv', name='c_csv'),
    url(r'^timecsv/$', 'coaching.views.time_csv', name='c_timecsv'),
    url(r'^clients/$', 'coaching.views.liste_clients', name='c_client'),
    url(r'^detail/$', 'coaching.views.detail_utilisateur', name='c_detail'),
    url(r'^sendmail/$', 'coaching.views.send_email', name='c_sendmail'),
    (r'^detail/module/$', 'coaching.views.detail_module'),
    url(r'^log/$', 'coaching.views.log_utilisateur', name='c_log'),
    url(r'^logins/$', 'coaching.views.create_logins', name='c_logins'),
    url(r'^ficha/(?P<utilisateur>[A-Za-z0-9-_.]+)/$', 'coaching.views.profile_utilisateur_admin', name='c_ficha'),
    url(r'^echeance/$', 'coaching.views.liste_echeances', name='c_echeance'),
    url(r'^echeance/add/?$', 'coaching.views.add_echeance', name='c_echeance_add'),
    url(r'^echeance/manage/?$', 'coaching.views.maj_echeance', name='c_echeance_manage'),
    url(r'^work/$', 'coaching.views.liste_works', name='c_work'),
    url(r'^work/add/?$', 'coaching.views.add_work', name='c_work_add'),
    url(r'^work/manage/?$', 'coaching.views.maj_work', name='c_work_manage'),
    url(r'^logs/$', 'coaching.views.logs', name='c_logs'),
)

