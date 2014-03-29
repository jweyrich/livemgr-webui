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

class Badword(models.Model):
	class Meta:
		app_label = 'livemgr'
		db_table = 'badwords'
		managed = False
		#ordering = ['badword']
		verbose_name = _('badword')
		verbose_name_plural = _('badwords')
		permissions = (
			("see_badword", "Can see badword"),
		)
	badword = models.CharField(_("badword"), max_length=128, unique=True)
	isregex = models.BooleanField(_("regular expression"), default=False)
	isenabled = models.BooleanField(_("enabled"), default=True)
	def __unicode__(self):
		return smart_unicode(self.badword)

class BadwordAdmin(admin.ModelAdmin):
	pass
