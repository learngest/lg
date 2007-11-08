#!/usr/bin/python
import os,sys
try:
    import settings
except ImportError:
    print "Unable to import settings."
    sys.exit(1)
project_name = os.path.basename(settings.PROJECT_PATH)
settings_name = os.path.splitext(settings.__file__)[0]
sys.path.append(os.path.join(settings.PROJECT_PATH, '..'))
project_module = __import__(project_name, {}, {}, [''])
sys.path.pop()
# Set DJANGO_SETTINGS_MODULE appropriately.
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.%s' % (project_name, settings_name)
print "Django environment of project %s registered." % os.environ['DJANGO_SETTINGS_MODULE']

