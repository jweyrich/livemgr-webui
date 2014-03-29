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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from webui.common.auth.auth_user_profile import AuthUserProfileModel

class Profile(AuthUserProfileModel):
	class Meta:
		app_label = 'livemgr'
		db_table = 'auth_user_profile'
		managed = True
	language = models.CharField(_('language'), max_length=5, default='en')
	debug = models.BooleanField(_("enable debug"), default=False)
	per_page_acls = models.PositiveSmallIntegerField(default=10)
	per_page_users = models.PositiveSmallIntegerField(default=10)
	per_page_usergroups = models.PositiveSmallIntegerField(default=10)
	per_page_conversations = models.PositiveSmallIntegerField(default=10)
	per_page_badwords = models.PositiveSmallIntegerField(default=10)
	per_page_buddies = models.PositiveSmallIntegerField(default=10)
