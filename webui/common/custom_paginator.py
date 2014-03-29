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

from copy import deepcopy
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from math import ceil

class CustomPaginator:
	PER_PAGE = 25

	def __init__(self, queryset):
		self.queryset = queryset
		self.instance = None
		self._request = None
		self._group_by = None
		self._distinct = None
		self._count = None

	def instantiate(self, clazz, *args, **kwargs):
		self.instance = clazz(*args, **kwargs)
		return self

	def with_request(self, request):
		self._request = request
		return self

	def with_count(self, count):
		self._count = count
		return self

	def group_by(self, distinct=True, *field_names):
		self._group_by = field_names
		self._distinct = distinct
		# Tuple to list
		self.queryset.query.group_by = [field_names[i] for i in range(len(field_names))]
		return self

	def page(self, number, per_page):
		if not number:
			if not self._request:
				raise Exception('Requires with_request')
			number = self.get_page_from_request(self._request)
		if self._group_by and not self._count:
			qset = deepcopy(self.queryset).values(*self._group_by)
			if self._distinct:
				qset = qset.distinct()
			self._count = qset.count()
		per_page = per_page or self.PER_PAGE
		paginator = Paginator(self.instance.rows, per_page)
		if self._count:
			hits = max(1, self._count - paginator.orphans)
			paginator._num_pages = int(ceil(hits / float(per_page)))
			# The following line also avoids an extra (and wrong) COUNT(*) query.
			paginator._count = self._count
		try:
			current_page = paginator.page(number)
		except (EmptyPage, InvalidPage):
			page_number = 1
			current_page = paginator.page(page_number)
		paginator.limited_page_range = CustomPaginator.get_page_range(paginator.num_pages, number)
		return current_page

	@staticmethod
	def get_page_from_request(request):
		try:
			page = int(request.GET.get('page', '1'))
		except ValueError:
			page = 1
		return page

	@staticmethod
	def get_page_range(num_pages, page_number, range_gap=5):
		start = page_number - range_gap
		if start < range_gap:
			start = 1
			end = start + range_gap * 2 + 1
			if end > num_pages:
				end = num_pages + 1
		else:
			if page_number < num_pages - range_gap:
				end = page_number + range_gap + 1
			else:
				end = num_pages + 1
		return range(start, end)
