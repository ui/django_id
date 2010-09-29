#!/usr/bin/python
import os, site, sys

# fix markdown.py (and potentially others) using stdout
sys.stdout = sys.stderr

#Calculate the path based on the location of the WSGI script.
project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_env = os.path.dirname(project)

# add the virtual environment path
site.addsitedir('%s/env/lib/python2.6/site-packages' % project_env)

sys.path.append(project)
sys.path.insert(0, '%s/env/lib/python2.6/site-packages' % project_env)
sys.path.append('%s/apps' % project)
sys.path.append('%s/libraries' % project)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
