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

from django import http
import types

class http_dict(dict):
	def __init__(self, method_dict):
		assert isinstance(method_dict, http.QueryDict)
		super(http_dict, self).__init__()
		self.dict = method_dict
	def from_fields(self, keylist):
		assert isinstance(keylist, types.ListType)
		count = 0
		for k in keylist:
			val = self.dict.get(k)
			if val:
				count += 1
			self[k] = val
		return count
