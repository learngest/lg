#!/usr/bin/python
import os,sys
try:
    import lg.settings
except ImportError:
    curdir, filename = os.path.split(__file__)
    sys.path.insert(os.path.abspath(curdir))
    import lg.settings

from django.core.management import setup_environ
setup_environ(lg.settings)

