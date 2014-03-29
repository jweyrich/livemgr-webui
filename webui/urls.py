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

from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from webui import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'webui.controllers.handlers.error_500'

urlpatterns = patterns('',
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', admin.site.urls),

	# Internationalization
	(r'^i18n/', include('django.conf.urls.i18n')),
	(r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),

	# User defined
	(r'^media/(?P<path>.*)$', 'django.views.static.serve',
		{ 'document_root': settings.MEDIA_ROOT }),
	(r'^', include('webui.livemgr.urls',
		namespace='webui', app_name='livemgr')),
)
