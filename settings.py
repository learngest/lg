# -*- encoding: utf8 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#import sys
#sys.path.append('/usr/local/src/django_apps/')

ADMINS = (
     ('JcB', 'jcbagneris@learngest.com'),
)

MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'lg0809'             # Or path to database file if using sqlite3.
DATABASE_USER = 'jcb'             # Not used with sqlite3.
DATABASE_PASSWORD = 'nikop00l'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Session management                                                                                              
SESSION_EXPIRE_AT_BROWSER_CLOSE = True                                                                            
SESSION_COOKIE_AGE = 21600 # 6h in seconds 

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
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lg.coaching.middleware.LastMiddleware',
    'lg.coaching.middleware.LogMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'lg.urls'

import os.path

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ALLOWED_INCLUDE_ROOTS = (os.path.join(os.path.dirname(PROJECT_PATH),'contents'),)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'lg.pages',
    'lg.learning',
    'lg.coaching',
    'lg.testing',
#    'mailer',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
)

