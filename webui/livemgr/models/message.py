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

class Message(models.Model):
	class Type:
		UNKNOWN = 0 # never used
		MSG = 1
		FILE = 2
		TYPING = 3 # never used
		CAPS = 4 # never used
		WEBCAM = 5
		REMOTEDESKTOP = 6
		APPLICATION = 7
		EMOTICON = 8
		INK = 9
		NUDGE = 10
		WINK = 11
		VOICECLIP = 12
		GAMES = 13
		PHOTO = 14
	CHOICES_TYPES = (
		(Type.UNKNOWN, _('unknown')),
		(Type.MSG, _('msg')),
		(Type.FILE, _('file')),
		(Type.TYPING, _('typing')),
		(Type.CAPS, _('caps')),
		(Type.WEBCAM, _('webcam')),
		(Type.REMOTEDESKTOP, _('remotedesktop')),
		(Type.APPLICATION, _('application')),
		(Type.EMOTICON, _('emoticon')),
		(Type.INK, _('ink')),
		(Type.NUDGE, _('nudge')),
		(Type.WINK, _('wink')),
		(Type.VOICECLIP, _('voiceclip')),
		(Type.GAMES, _('games')),
		(Type.PHOTO, _('photo')),
	)
	class Meta:
		app_label = 'livemgr'
		db_table = 'messages'
		managed = False
		#ordering = ['-timestamp']
		verbose_name = _('message')
		verbose_name_plural = _('messages')
		permissions = (
			("see_message", "Can see message"),
		)
	conversation_id = models.IntegerField(_("conversation #"))
	timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
	#conversation = models.ForeignKey(Conversation, db_column='conversation_id',
	#								verbose_name="Conversation")
	# NOTE: Avoiding IPAddressField because it stores text instead of int
	clientip = models.IntegerField(_("client IP"))
	inbound = models.BooleanField(_("inbound"))
	type = models.IntegerField(_("type"), choices=CHOICES_TYPES)
	# NOTE: Avoiding EmailField because most protocols don't use email addresses
	localim = models.CharField(_("user"), max_length=128)
	remoteim = models.CharField(_("buddy"), max_length=128)
	filtered = models.BooleanField(_("filtered"))
	content = models.TextField(_("content"), max_length=2000)
	def __unicode__(self):
		return smart_unicode('%d %d %s %s %s' % (self.id, self.timestamp,
			self.conversation_id, self.localim, self.remoteim))

class MessageAdmin(admin.ModelAdmin):
	pass
