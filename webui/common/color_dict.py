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

import copy

class color_dict(dict):
	DEFAULT_COLORS = [
		0x7CA380, 0xAD8282,
		0x0033CC, 0xFF0000, 0x00CC00,
		0xFFCC00, 0x660099, 0xFF9900,
		0x009999, 0x330099, 0xCC0099,
		0xFF6600, 0xFFFF00, 0x99FF00,
		# Original order:
		#0x00CC00, 0x009999, 0x0033CC,
		#0x330099, 0x660099, 0xCC0099,
		#0xFF0000, 0xFF6600, 0xFF9900,
		#0xFFCC00, 0xFFFF00, 0x99FF00
	]
	def __init__(self, colors=DEFAULT_COLORS, *args, **kwargs):
		super(color_dict, self).__init__(*args, **kwargs)
		self._colors = copy.deepcopy(colors)
	def __missing__(self, key):
		value = self._colors.pop(0)
		self[key] = value
		return value
	def get(self, key):
		#return '#%06x'%self._colors.pop(0) if len(self._colors)>0 else '#%06x'%0x7CA380
		return '#%06x' % self[key]
