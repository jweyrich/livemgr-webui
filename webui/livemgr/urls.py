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

from django.contrib.auth import views
from django.urls import re_path
from webui.livemgr.controllers import profiles, settings, acls, badwords, \
	conversations, groups, users, buddies, dashboard, license

# The application namespace, from Django 1.9 on (see webui/urls.py)
app_name = 'livemgr'

urlpatterns = [
	re_path(r'^$', dashboard.index, name='index'),
	# Dashboard
	re_path(r'^dashboard/$', dashboard.index, name='dashboard-index'),
	re_path(r'^dashboard/query/$', dashboard.query, name='dashboard-query'),
	# Acls
	re_path(r'^acls/$', acls.index, name='acls-index'),
	re_path(r'^acls/add/$', acls.add, name='acls-add'),
	re_path(r'^acls/delete/$', acls.delete_many, name='acls-delete-many'),
	re_path(r'^acls/(?P<object_id>\d+)/$', acls.edit, name='acls-edit'),
	re_path(r'^acls/(?P<object_id>\d+)/delete/$', acls.delete, name='acls-delete'),
	# Users
	re_path(r'^users/$', users.index, name='users-index'),
	re_path(r'^users/add/$', users.add, name='users-add'),
	re_path(r'^users/(?P<object_id>\d+)/$', users.edit, name='users-edit'),
	re_path(r'^users/(?P<object_id>\d+)/delete/$', users.delete, name='users-delete'),
#	re_path(r'^users/delete/$', users.delete_many, name='users-delete-many'),
	# Buddies
	re_path(r'^users/(?P<user_id>\d+)/contacts/$', buddies.index, name='buddies-index'),
	re_path(r'^users/(?P<user_id>\d+)/block/$', buddies.block, name='buddies-block-many'),
	re_path(r'^users/(?P<user_id>\d+)/unblock/$', buddies.unblock, name='buddies-unblock-many'),
	# Groups
	re_path(r'^groups/$', groups.index, name='groups-index'),
	re_path(r'^groups/add/$', groups.add, name='groups-add'),
	re_path(r'^groups/delete/$', groups.delete_many, name='groups-delete-many'),
	re_path(r'^groups/(?P<object_id>\d+)/$', groups.edit, name='groups-edit'),
	re_path(r'^groups/(?P<object_id>\d+)/delete/$', groups.delete, name='groups-delete'),
	# Conversations
	re_path(r'^conversations/$', conversations.index, name='conversations-index'),
	re_path(r'^conversations/(?P<object_id>\d+)/$', conversations.show, name='conversations-show'),
	re_path(r'^conversations/(?P<object_id>\d+)/report/pdf/$', conversations.report_pdf, name='conversations-report-pdf'),
	# Badwords
	re_path(r'^badwords/$', badwords.index, name='badwords-index'),
	re_path(r'^badwords/add/$', badwords.add, name='badwords-add'),
	re_path(r'^badwords/delete/$', badwords.delete_many, name='badwords-delete-many'),
	re_path(r'^badwords/disable/$', badwords.disable_many, name='badwords-disable-many'),
	re_path(r'^badwords/enable/$', badwords.enable_many, name='badwords-enable-many'),
	re_path(r'^badwords/(?P<object_id>\d+)/$', badwords.edit, name='badwords-edit'),
	re_path(r'^badwords/(?P<object_id>\d+)/delete/$', badwords.delete, name='badwords-delete'),
	# Settings
	re_path(r'^settings/$', settings.update, name='settings-update'),
	# License
	re_path(r'^license/$', license.index, name='license-index'),
	# Profiles
	re_path(r'^login/$', profiles.login,
		{'template_name': 'profiles/login.html'},
		name='profiles-login'),
#	re_path(r'^profiles/login/$', views.login,
#		{'template_name': 'profiles/login.html'},
#		name='profiles-login'),
	re_path(r'^logout/$', views.logout_then_login,
		{'login_url': '/login/'},
		name='profiles-logout'),
	re_path(r'^profile/update/$', profiles.update, name='profiles-update'),
#	re_path(r'^profiles/$', profiles.index, name='profiles-index'),
]
