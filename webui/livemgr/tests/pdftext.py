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

"""
	Text extraction for the PDFs that reportlab writes, just enough to assert
	on what a report shows. It only understands uncompressed page streams (see
	uncompressed()) drawn with reportlab's standard fonts.
"""

from contextlib import contextmanager
from reportlab import rl_config
import re

try:
	unichr
except NameError: # Python 3
	unichr = chr

TOKEN = re.compile(r'\((?:\\[\s\S]|[^\\)])*\)|[-+]?(?:\d+\.?\d*|\.\d+)|/[^\s/\[\]()]+|[A-Za-z]+\*?|\S')
NUMBER = re.compile(r'^[-+]?(?:\d+\.?\d*|\.\d+)$')
ESCAPES = {'n': '\n', 'r': '\r', 't': '\t', 'b': '\b', 'f': '\f'}

@contextmanager
def uncompressed():
	"""Make reportlab write page streams as plain text."""
	saved = rl_config.pageCompression
	rl_config.pageCompression = 0
	try:
		yield
	finally:
		rl_config.pageCompression = saved

class Line(object):
	def __init__(self):
		self.fragments = [] # (text, '#rrggbb')

	@property
	def text(self):
		return u''.join(text for text, color in self.fragments)

	def __repr__(self):
		return 'Line(%r)' % self.text

def read_pages(content):
	"""Return the pages of a PDF, each one as a list of Line."""
	# Bytes map 1:1 to latin-1 code points, so this works on str and bytes alike.
	content = content.decode('latin-1')
	streams = re.findall(r'stream\r?\n(.*?)endstream', content, re.DOTALL)
	return [read_lines(stream) for stream in streams if 'BT' in stream]

def read_lines(stream):
	lines = []
	line = None
	color = '#000000'
	operands = []
	for token in TOKEN.findall(stream):
		if token.startswith('(') or NUMBER.match(token) or token.startswith('/') or token in '[]':
			operands.append(token)
			continue
		if token == 'BT':
			line = Line()
		elif token in ('ET', 'T*') and line is not None:
			if line.text.strip():
				lines.append(line)
			line = Line() if token == 'T*' else None
		elif token == 'rg':
			color = to_hex([float(n) for n in operands[-3:]])
		elif token == 'g':
			color = to_hex([float(operands[-1])] * 3)
		elif token in ('Tj', 'TJ') and line is not None:
			strings = [o for o in operands if o.startswith('(')]
			line.fragments.append((u''.join(decode_string(s) for s in strings), color))
		operands = []
	return lines

def decode_string(token):
	"""Decode a PDF literal string written with WinAnsiEncoding."""
	def unescape(match):
		escaped = match.group(1)
		if escaped[0] in '01234567':
			return unichr(int(escaped, 8))
		return ESCAPES.get(escaped, escaped)
	raw = re.sub(r'\\([0-7]{1,3}|[\s\S])', unescape, token[1:-1])
	# Django formats some values with non-breaking spaces (e.g. filesizeformat)
	return raw.encode('latin-1').decode('cp1252').replace(u'\xa0', u' ')

def to_hex(rgb):
	return '#%02x%02x%02x' % tuple(int(round(c * 255)) for c in rgb)
