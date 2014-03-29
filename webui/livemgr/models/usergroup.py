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

from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from webui.livemgr.models.rule import Rule

class UserGroup(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'usergroups'
		managed = False
		#ordering = ['groupname']
		verbose_name = _('usergroup')
		verbose_name_plural = _('usergroups')
		permissions = (
			("see_usergroup", "Can see usergroup"),
		)
	groupname = models.CharField(_("name"), max_length=64, unique=True)
	isactive = models.BooleanField(_("active"), default=True)
	isbuiltin = models.BooleanField(_("built-in"), default=False)
	description = models.TextField(_("description"), max_length=512, blank=True, default='')
	rules = models.ManyToManyField(Rule, through='GroupRule')
	user_count = lambda self: self.users.count()
	def __unicode__(self):
		return smart_unicode(self.groupname)

class UserGroupAdmin(admin.ModelAdmin):
	pass
