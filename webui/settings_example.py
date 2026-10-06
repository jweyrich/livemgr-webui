# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Jardel Weyrich
#
# This file is part of livemgr-webui.
#
# livemgr-webui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# livemgr-webui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jardel Weyrich <jweyrich@gmail.com>

# Django settings for webui project.
from webui.settings import *
import django

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'livemgr',
        'USER': 'livemgr',
        'PASSWORD': 'livemgr',
        'HOST': 'db',
        'PORT': '',
    }
}

# webui.settings lists the middleware in MIDDLEWARE from Django 1.10 on
if django.VERSION >= (1, 10):
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
else:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

INSTALLED_APPS += (
    'debug_toolbar',
)

INTERNAL_IPS += ('<internal_ip_here>', '<another_here>', '<and_another_if_you_like>',)

LICENSE_FILE = os.path.join(ROOT, os.pardir, 'conf', 'certs', 'cert.pem')
KEYSERVER_HOST = os.environ.get('LIVEMGR_KEYSERVER_HOST', '127.0.0.1')
# The development KeyServer (tools/keyserver) uses a certificate issued by the
# licensing CA, which the system doesn't trust.
KEYSERVER_CA_FILE = os.environ.get('LIVEMGR_KEYSERVER_CA_FILE') or None

########################
# DJANGO DEBUG TOOLBAR #
########################

#DEBUG_TOOLBAR_PANELS = (
#    'debug_toolbar.panels.versions.VersionsPanel',
#    'debug_toolbar.panels.timer.TimerPanel',
#    'debug_toolbar.panels.settings.SettingsPanel',
#    'debug_toolbar.panels.headers.HeadersPanel',
#    'debug_toolbar.panels.request.RequestPanel',
#    'debug_toolbar.panels.templates.TemplatesPanel',
#    'debug_toolbar.panels.sql.SQLPanel',
#    'debug_toolbar.panels.signals.SignalsPanel',
#    'debug_toolbar.panels.logging.LoggingPanel',
#)

def show_toolbar(request):
    user = request.user
    if hasattr(user, 'profile'):
        return user.profile.debug
    return False

# django-debug-toolbar 1.x no longer intercepts redirects by default, and
# dropped HIDE_DJANGO_SQL. 1.6 no longer sets itself up: webui/urls.py adds its
# URLs when it is installed.
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}
