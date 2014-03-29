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

from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
	def __init__(self, *args, **kwargs):
		canvas.Canvas.__init__(self, *args, **kwargs)
		self._saved_page_states = []
	def showPage(self):
		self._saved_page_states.append(dict(self.__dict__))
		self._startPage()
	def save(self):
		"""Add page info to each page (page x of y)"""
		num_pages = len(self._saved_page_states)
		for state in self._saved_page_states:
			self.__dict__.update(state)
			self.drawPageNumber(num_pages)
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)
	def drawPageNumber(self, page_count):
		"""Derived classes must implement it"""
		pass

def coord_tl(pagesize, x, y):
	return x, pagesize[1] - y
def coord_tr(pagesize, x, y):
	return pagesize[0] - x, pagesize[1] - y
