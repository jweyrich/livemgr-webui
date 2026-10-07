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

from datetime import date, datetime
from django.utils import translation
from django.utils.safestring import SafeData
from webui.livemgr.models import Acl
from webui.livemgr.utils.formatters import format_acl_action, format_boolean, \
	format_user_status, ip_long_to_str, ip_str_to_long
from webui.livemgr.utils.local_datetime import adjust_date
from webui.livemgr.utils.resources import Resources
import unittest

class FormattersTest(unittest.TestCase):
	def test_format_boolean(self):
		self.assertEqual(format_boolean(True), Resources.tag_img_accept)
		self.assertEqual(format_boolean(False), Resources.tag_img_accept_gray)
		self.assertTrue(isinstance(format_boolean(True), SafeData))
		self.assertRaises(TypeError, format_boolean, None)

	def test_format_acl_action(self):
		self.assertEqual(format_acl_action(Acl.ACTION_ALLOW), Resources.tag_img_tick)
		self.assertEqual(format_acl_action(Acl.ACTION_BLOCK), Resources.tag_img_cross)
		self.assertRaises(TypeError, format_acl_action, 3)

	def test_format_user_status(self):
		self.assertEqual(format_user_status('NLN'), Resources.tag_img_status_online + ' Online')
		self.assertEqual(format_user_status('BSY'), Resources.tag_img_status_busy + ' Busy')
		self.assertEqual(format_user_status('BRB'), Resources.tag_img_status_away + ' Be right back')
		self.assertEqual(format_user_status('HDN'), Resources.tag_img_status_offline + ' Invisible')
		self.assertEqual(format_user_status('XXX'), '')
		self.assertTrue(isinstance(format_user_status('NLN'), SafeData))

	def test_format_user_status_is_translated(self):
		translation.activate('pt-br')
		try:
			self.assertEqual(format_user_status('AWY'),
				Resources.tag_img_status_away + u' Ausente')
		finally:
			translation.deactivate()

	def test_resources_point_to_media(self):
		self.assertEqual(Resources.tag_img_tick,
			"<img class='icon tick' src='/media/img/trans1x1.gif' />")

	def test_ip_long_to_str(self):
		# The backend stores the IPv4 address in network byte order
		self.assertEqual(ip_long_to_str(0x0100007F), '127.0.0.1')
		self.assertEqual(ip_long_to_str(0x0101A8C0), '192.168.1.1')
		self.assertEqual(ip_long_to_str(0), '0.0.0.0')
		self.assertEqual(ip_long_to_str(0xFFFFFFFF), '255.255.255.255')

	def test_ip_str_to_long(self):
		self.assertEqual(ip_str_to_long('127.0.0.1'), 0x0100007F)
		self.assertEqual(ip_str_to_long('192.168.1.1'), 0x0101A8C0)
		for ip in ('0.0.0.0', '10.1.2.30', '255.255.255.255'):
			self.assertEqual(ip_long_to_str(ip_str_to_long(ip)), ip)

class AdjustDateTest(unittest.TestCase):
	def test_start_of_day(self):
		self.assertEqual(adjust_date(date(2010, 5, 17)), datetime(2010, 5, 17, 0, 0, 0))

	def test_end_of_day(self):
		self.assertEqual(adjust_date(date(2010, 5, 17), True), datetime(2010, 5, 17, 23, 59, 59))
		self.assertEqual(adjust_date(date(2010, 12, 31), True), datetime(2010, 12, 31, 23, 59, 59))

	def test_rejects_non_dates(self):
		self.assertRaises(AssertionError, adjust_date, '2010-05-17')
