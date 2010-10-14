import os
import sys

def setup_environment():
	current_directory = os.path.realpath(os.path.dirname(__file__))
	project_directory = os.path.realpath(os.path.join(current_directory, os.pardir))
	syspath_directory = os.path.realpath(os.path.join(project_directory, os.pardir))
	sys.path.insert(0, syspath_directory)
	os.environ['DJANGO_SETTINGS_MODULE'] = 'webui.settings'

setup_environment()

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
