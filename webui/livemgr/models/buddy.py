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
from webui.livemgr.models.user import User

class Buddy(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'buddies'
		managed = False
		unique_together = ('user', 'username')
		#ordering = ['username', 'user']
		verbose_name = _('buddy')
		verbose_name_plural = _('buddies')
		permissions = (
			("see_buddy", "Can see buddy"),
		)
	username = models.CharField(_("username"), max_length=128)
	displayname = models.CharField(_("display name"), max_length=130, blank=True, default='')
	psm = models.CharField(_("status message"), max_length=130, blank=True, default='')
	#status = models.PositiveSmallIntegerField("status", choices=CHOICES_STATUS)
	status = models.CharField(_("status"), max_length=3, choices=User.CHOICES_STATUS)
	isblocked = models.BooleanField(_("blocked"), default=False)
	user = models.ForeignKey(User, db_column='user_id', verbose_name=_("user"), related_name="buddies")
	def __unicode__(self):
		return smart_unicode(self.username)

class BuddyAdmin(admin.ModelAdmin):
	pass
