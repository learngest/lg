# -*- encoding: utf-8 -*-

import sys
import os.path

try:
    from local_settings import *
except ImportError:
    pass

try:
    from dev_settings import *
except ImportError:
    pass

try:
    from prod_settings import *
except ImportError:
    pass

LG_PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# test wether we're installed or working on dev version
try:
    import listes
except ImportError:
    sys.path.append(LG_PROJECT_PATH)

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'
DATETIME_FORMAT = "Y-m-d H:i:s"

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Session management                                                                                              
SESSION_EXPIRE_AT_BROWSER_CLOSE = True                                                                            
SESSION_COOKIE_AGE = 21600 # 6h in seconds 

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
#MEDIA_URL = 'http://localhost.localdomain:8000/upload/'
MEDIA_URL = '/upload/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

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

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(LG_PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'lg.pages',
    'lg.learning',
    'lg.coaching',
    'lg.testing',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
)

