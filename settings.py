# -*- encoding: utf-8 -*-


# local only settings, not managed by git
from settings_nogit import *

import sys
sys.path.append('/usr/local/src/django_apps/')

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

DEFAULT_CHARSET = 'utf-8'

TIME_ZONE = 'Europe/Paris'

LANGUAGE_CODE = 'en-us'

USE_I18N = True

SITE_ID = 1

# User profile
AUTH_PROFILE_MODULE = 'coaching.UserProfile'

# Session management
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 86400 # 24h in seconds

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/jcb/learngest/web/upload/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
#MEDIA_URL = 'http://localhost.localdomain:8000/upload/'
MEDIA_URL = '/upload/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = '0+eqr)$n_fu=t05k63m$ly3!78wp@s$mlpm7gopkag#uz8$0uf'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
#    'middleware.SQLLogMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'lg.coaching.middleware.LastMiddleware',
#    'lg.coaching.middleware.LogMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'lg.urls'

import os.path

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ALLOWED_INCLUDE_ROOTS = (os.path.join(os.path.dirname(PROJECT_PATH),'contents'),)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
#    'lg.pages',
    'lg.learning',
    'lg.coaching',
#    'lg.testing',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'debug_toolbar',
)

DEBUG_TOOLBAR_PANELS = (
#    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
#    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

