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
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'livemgr',
        'USER': 'livemgr',
        'PASSWORD': 'livemgr',
        'HOST': '',
        'PORT': '',
    }
}

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
)

INTERNAL_IPS += ('10.1.1.16', '192.168.1.100', '192.168.1.101',)

LICENSE_FILE = os.path.join(ROOT, os.pardir, 'conf', 'certs', 'cert.pem')
KEYSERVER_HOST = '10.1.1.17'

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
# dropped HIDE_DJANGO_SQL.
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}
