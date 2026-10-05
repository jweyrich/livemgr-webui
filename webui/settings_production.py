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
import django

DEBUG = False
if django.VERSION < (1, 8): # Newer versions' template engine follows DEBUG
    TEMPLATE_DEBUG = False
# With DEBUG off, Django 1.5 fails every request (SuspiciousOperation, served
# by the 500 handler) whose Host header isn't listed here, and the default is
# an empty list. Django 1.4 accepted any host; keep that until the deployment's
# host names are known, then list them instead, e.g. ['livemgr.example.com'].
ALLOWED_HOSTS = ['*']
MEDIA_ROOT = '/usr/share/livemgr-webui/media'
LICENSE_FILE = ''
KEYSERVER_HOST = ''
