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

class Rule(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'rules'
		managed = False
		#ordering = ['rulename']
		verbose_name = _('rule')
		verbose_name_plural = _('rules')
		permissions = (
			("see_rule", "Can see rule"),
		)
	rulename = models.CharField(_("name"), max_length=128, unique=True)
	description = models.TextField(_("description"), max_length=512)
	def __unicode__(self):
		return smart_unicode(self.rulename)

class RuleAdmin(admin.ModelAdmin):
	pass

class LocalizedRules:
	RULES = [
		Rule(1, _('Conversation history'), _('Save instant message conversations')),
		Rule(2, _('Disclaimer'), _('Notify the user that the messages are being monitored')),
		Rule(3, _('Block file transfers'), _('Automatically reject file transfers')),
		Rule(4, _('Block unofficial messages'), ''),
		Rule(5, _('Block webcam'), ''),
		Rule(6, _('Block Remote Assistance'), ''),
		Rule(7, _('Block application sharing'), ''),
		Rule(8, _('Block custom emoticons'), ''),
		Rule(9, _('Block handwriting'), ''),
		Rule(10, _('Block nudges'), ''),
		Rule(11, _('Block winks'), ''),
		Rule(12, _('Block voice clips'), ''),
		Rule(13, _('Block encrypted messages'), ''),
		Rule(14, _('Badword filtering'), _('Filter messages based on defined badwords')),
		Rule(15, _('Block MSN Games'), ''),
		Rule(16, _('Block photo sharing'), '')
	]

