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
from webui.livemgr.models.usergroup import UserGroup

class GroupRule(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'grouprules'
		managed = False
		unique_together = ('rule', 'group')
		#ordering = ['rule', 'group']
		verbose_name = _('grouprule')
		verbose_name_plural = _('grouprules')
	rule = models.ForeignKey(Rule, db_column='rule_id', verbose_name=_("rule"))
	group = models.ForeignKey(UserGroup, db_column='group_id', verbose_name=_("group"))
	def __unicode__(self):
		return smart_unicode('%d %s %s' % (self.id, self.rule, self.group))

class GroupRuleAdmin(admin.ModelAdmin):
	pass
