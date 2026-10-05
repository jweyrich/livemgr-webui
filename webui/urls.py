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

from django.apps import apps
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve
from webui import settings
import django

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'webui.controllers.handlers.error_500'

# Django 1.9 reads the application namespace from the included URLconf's
# app_name, and deprecates passing it to include(). Older versions ignore it.
if django.VERSION >= (1, 9):
	livemgr_urls = include('webui.livemgr.urls', namespace='webui')
else:
	livemgr_urls = include('webui.livemgr.urls', namespace='webui', app_name='livemgr')

# Django 1.10 deprecates the javascript_catalog() view for JavaScriptCatalog,
# which serves every installed app's catalog unless told which packages to use.
# Name the project's app: its catalog lives in LOCALE_PATHS, which both views
# always include, so the output stays the same.
if django.VERSION >= (1, 10):
	from django.views.i18n import JavaScriptCatalog
	jsi18n_view = JavaScriptCatalog.as_view(packages=['webui.livemgr'])
else:
	from django.views.i18n import javascript_catalog as jsi18n_view

# Django 1.8 deprecates patterns() and views given as dotted paths.
urlpatterns = [
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
	# to INSTALLED_APPS to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# Django 1.9 deprecates include() for the admin's (patterns, app_name,
	# namespace) 3-tuple; url() takes it directly.
	url(r'^admin/', admin.site.urls),

	# Internationalization
	url(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^jsi18n/$', jsi18n_view, name='jsi18n'),

	# User defined
	url(r'^media/(?P<path>.*)$', serve,
		{ 'document_root': settings.MEDIA_ROOT }),
	url(r'^', livemgr_urls),
]

# django-debug-toolbar 1.6 no longer adds its URLs by itself. They're a
# (patterns, app_name, namespace) 3-tuple too, like the admin's.
if apps.is_installed('debug_toolbar'):
	import debug_toolbar
	urlpatterns += [
		url(r'^__debug__/', debug_toolbar.urls),
	]
