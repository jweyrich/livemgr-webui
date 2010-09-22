import os
import sys

PATH = os.path.realpath(os.path.normpath(os.path.dirname(__file__)+'../../../'))

sys.path.append(PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'webui.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

