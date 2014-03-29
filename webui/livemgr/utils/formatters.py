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

from django.utils.safestring import mark_safe
from webui.livemgr.models.acl import Acl
from webui.livemgr.models.user import lookup_user_status
from webui.livemgr.utils.resources import Resources
import socket
import struct

def _default(value):
	raise "Unhandled value: %s" % value

def format_boolean(value):
	tag = {
		True: lambda x: Resources.tag_img_accept,
		False: lambda x: Resources.tag_img_accept_gray,
	}.get(value, _default)(value)
	if not tag:
		return ""
	return mark_safe(tag)

def format_acl_action(value):
	tag = {
		Acl.ACTION_ALLOW: lambda x: Resources.tag_img_tick,
		Acl.ACTION_BLOCK: lambda x: Resources.tag_img_cross,
	}.get(value, _default)(value)
	if not tag:
		return ""
	return mark_safe(tag)

def format_user_status(value):
	status = lookup_user_status(value)
	if not status:
		return ""
	tag = {
		'NLN': lambda x: Resources.tag_img_status_online,
		'BSY': lambda x: Resources.tag_img_status_busy,
		'IDL': lambda x: Resources.tag_img_status_away,
		'AWY': lambda x: Resources.tag_img_status_away,
		'BRB': lambda x: Resources.tag_img_status_away,
		'PHN': lambda x: Resources.tag_img_status_busy,
		'LUN': lambda x: Resources.tag_img_status_away,
		'HDN': lambda x: Resources.tag_img_status_offline,
		'FLN': lambda x: Resources.tag_img_status_offline,
	}.get(status[0], _default)(status[0])
	if not tag:
		return ""
	text = unicode(status[1]).encode('utf-8', 'strict')
	return mark_safe(tag + ' %s' % text)

def ip_long_to_str(ip_as_long):
	#return socket.inet_ntoa(struct.pack('L', socket.ntohl(ip_as_long)))
	# We decided to store it as BigEndian on the database
	return socket.inet_ntoa(struct.pack('I', ip_as_long))
