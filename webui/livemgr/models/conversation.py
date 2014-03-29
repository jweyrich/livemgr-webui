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

class Conversation(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'conversations'
		managed = False
		#ordering = ['user', '-timestamp', 'buddy']
		verbose_name = _('conversation')
		verbose_name_plural = _('conversations')
		permissions = (
			("see_conversation", "Can see conversation"),
		)
	user = models.ForeignKey(User, db_column='user_id', verbose_name=_("user"))
	timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
	status = models.PositiveSmallIntegerField(db_column='status', verbose_name=_("Status"))
	def __unicode__(self):
		return smart_unicode('%d %s %s %i' % (self.id, self.user, self.timestamp,
			self.status))

class ConversationAdmin(admin.ModelAdmin):
	pass
