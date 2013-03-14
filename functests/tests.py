# -*- encoding: utf-8 -*-
"""
Functional tests for the learngest web apps
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings

from django_webtest import WebTest

from coaching.models import Utilisateur, Groupe


class LoginTest(WebTest):
    """
    Functional tests with webtest for the login/logout framework
    """
    fixtures = ['base.json', 'coaching.json',]

    def test_login_page(self):
        """
        Test login page exists
        """
        # Random user opens web browser and goes to login page
        login_page = self.app.get('/login/')
        self.assertEqual(login_page.status,"200 OK")
        # login pasge uses login.html template
        self.assertTemplateUsed(login_page, 'session/login.html')

    def test_bad_login(self):
        """
        Test unknown user cannot login
        """
        # Unknown user goes to login page and attempts to connect
        form = self.app.get(reverse('lg.session.views.login')).forms['login-form']
        form['login'] = 'unknownuser@foo.bar'
        form['password'] = '12345678'
        response = form.submit()
        self.assertTemplateUsed(response, 'session/login.html')
        self.assertContains(response, 
            _('Bad login. Please try again'))

