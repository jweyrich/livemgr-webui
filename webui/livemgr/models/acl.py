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

class Acl(models.Model):
	ACTION_ALLOW = 1
	ACTION_BLOCK = 2
	CHOICES_ACTIONS = (
		(ACTION_ALLOW, _('Allow')),
		(ACTION_BLOCK, _('Block')),
	)
	class Meta:
		app_label = 'livemgr'
		db_table = 'acls'
		managed = False
		unique_together = ('localim', 'remoteim')
		#ordering = ['action', 'localim', 'remoteim']
		verbose_name = _('acl')
		verbose_name_plural = _('acls')
		permissions = (
			("see_acl", "Can see acl"),
		)
	localim = models.CharField(_("user"), max_length=128)
	remoteim = models.CharField(_("buddy"), max_length=128)
	action = models.PositiveSmallIntegerField(_("action"), choices=CHOICES_ACTIONS)
	#action = models.CharField("Action", max_length=5, choices=CHOICES_ACTIONS)
	def __unicode__(self):
		return smart_unicode('%d %s %s %s' % (self.id, self.action,
			self.localim, self.remoteim))

class AclAdmin(admin.ModelAdmin):
	pass
