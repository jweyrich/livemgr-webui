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

from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog
from django.views.static import serve
from webui import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'webui.controllers.handlers.error_500'

# Django 1.8 deprecates patterns() and views given as dotted paths.
urlpatterns = [
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
	# to INSTALLED_APPS to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),

	# Internationalization
	url(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^jsi18n/$', javascript_catalog, name='jsi18n'),

	# User defined
	url(r'^media/(?P<path>.*)$', serve,
		{ 'document_root': settings.MEDIA_ROOT }),
	url(r'^', include('webui.livemgr.urls',
		namespace='webui', app_name='livemgr')),
]
