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

class Dashboard(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = ''
		managed = False
		verbose_name = _('dashboard')
		permissions = (
			("see_dashboard", "Can see dashboard"),
		)

class Support(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = ''
		managed = False
		verbose_name = _('support')
		permissions = (
			("see_support", "Can see support"),
		)
